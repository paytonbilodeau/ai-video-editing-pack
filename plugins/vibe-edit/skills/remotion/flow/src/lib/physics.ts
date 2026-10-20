// Deterministic physics baking for Flow's physical-metaphor lane.
//
// WHY BAKE AT ALL
// Remotion renders frames out of order and in parallel workers. A live
// physics engine stepped inside a component would produce a different world
// depending on which frames a worker happened to touch, so the render would
// flicker and never reproduce. The fix is to simulate ONCE, up front, at a
// fixed timestep, store every frame's body transforms in an array, and have
// the component read `frames[frameIndex]`. Playback then becomes a pure
// lookup and is as deterministic as any interpolate() call.
//
// PROVENANCE
// The fixed-timestep-then-index approach is the pattern endorsed by
// Remotion's creator in https://github.com/orgs/remotion-dev/discussions/4373
// ("Physics Engine, Baking") and carried on remotion.dev/docs/third-party.
// This file is an independent implementation of that idea against
// matter-js 0.20.0 (MIT). hylarucoder/remotion-physics demonstrates the same
// endorsed pattern but carries NO license grant, so it was read only as a
// behavioural reference and none of its source is reproduced here.
//
// DETERMINISM RULES OBSERVED
//   - Fixed delta of 1000/fps ms, subdivided into fixed sub-steps. Never a
//     wall-clock delta.
//   - Every initial condition comes from a seeded PRNG derived from a string
//     seed, never Math.random().
//   - No matter-js API that draws on Common.random() is used; bodies are
//     placed explicitly.
//   - Bakes are memoised by a key built from every input, so re-entry during
//     a multi-worker render returns the identical array.
//
// COST
// Bounded on purpose: a bake is capped at MAX_FRAMES and MAX_BODIES. A 12s
// scene with 60 tokens bakes in well under a second and is then free.

import {Bodies, Body, Composite, Engine, Events} from 'matter-js';

export type BodyKind = 'token' | 'block' | 'wall' | 'pan' | 'beam' | 'pivot';

export type BakedBody = {
  /**
   * Stable index within THIS bake, assigned in creation order. Deliberately
   * not matter-js's `Body.id`: that comes from a module-global counter which
   * keeps incrementing across bakes, so it differs between two runs of the
   * same seed and is useless both as a determinism input and as a React key.
   */
  id: number;
  kind: BodyKind;
  x: number;
  y: number;
  /** Rotation in radians. */
  a: number;
  /** Circle radius, when the body is round. */
  r?: number;
  /** Half-extents, when the body is a box. */
  hw?: number;
  hh?: number;
};

export type BakedCollision = {
  /** Frame index within the bake. */
  frame: number;
  /** Impact speed; use it to pick a loud vs quiet SFX cue. */
  speed: number;
  kinds: [BodyKind, BodyKind];
};

export type Bake = {
  frames: BakedBody[][];
  collisions: BakedCollision[];
  /** First frame after which nothing moves meaningfully. */
  settledFrame: number;
  /** Echoed back for QA and for the report. */
  seed: string;
  fps: number;
};

/** Hard ceilings so a metaphor beat can never blow up a render. */
const MAX_FRAMES = 1200; // 40s at 30fps
const MAX_BODIES = 240;
const SUB_STEPS = 4;
/** Below this total kinetic energy the scene counts as settled. */
const SETTLE_EPSILON = 0.35;
const SETTLE_HOLD_FRAMES = 8;

// ---------------------------------------------------------------------------
// Seeded PRNG
// ---------------------------------------------------------------------------
// Self-contained on purpose: this file must be runnable by a plain Node
// harness for the determinism check, without pulling in Remotion's React
// entrypoint. Same algorithm shape as any string-seeded hash: FNV-1a to a
// 32-bit state, then mulberry32 for the stream.

const hashSeed = (seed: string): number => {
  let h = 0x811c9dc5;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
};

export const makeRng = (seed: string): (() => number) => {
  let a = hashSeed(seed);
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

const rngRange = (rng: () => number, min: number, max: number): number =>
  min + rng() * (max - min);

// ---------------------------------------------------------------------------
// Scene specifications
// ---------------------------------------------------------------------------

export type PourSpec = {
  kind: 'pour';
  /** Vessel rectangle in composition pixels. */
  jar: {x: number; y: number; w: number; h: number};
  /** How many tokens fall in total. */
  count: number;
  /** Token radius in pixels. */
  radius: number;
  /** Frame index of the first token; tokens then arrive every `every`. */
  startFrame: number;
  every: number;
  /** Horizontal spread of the spout, in pixels. */
  spread?: number;
};

export type ScaleSpec = {
  kind: 'scale';
  /** Pivot point of the beam. */
  pivot: {x: number; y: number};
  beamHalfWidth: number;
  /** Weights dropped onto the left and right pans, as [frame, mass] pairs. */
  left: {frame: number; mass: number}[];
  right: {frame: number; mass: number}[];
  /** How far the pans hang below the beam ends. */
  panDrop?: number;
};

export type StackSpec = {
  kind: 'stack';
  /** Ground line y in composition pixels. */
  groundY: number;
  centerX: number;
  blocks: {w: number; h: number; frame: number; dx?: number}[];
  /**
   * How far above the ground a block spawns, in pixels. Governs how long it
   * falls, so it is the knob for making a stack SETTLE inside a short beat:
   * a 700px drop needs roughly 30 frames, a 320px drop about 15. Default is
   * deliberately modest because an unsettled ending fails QA.
   */
  spawnHeight?: number;
};

export type PhysicsSpec = PourSpec | ScaleSpec | StackSpec;

export type BakeOptions = {
  spec: PhysicsSpec;
  seed: string;
  fps: number;
  durationInFrames: number;
  /** Composition width; used for the invisible side walls. */
  width?: number;
  height?: number;
  gravity?: number;
};

// ---------------------------------------------------------------------------
// Bake cache
// ---------------------------------------------------------------------------

const cache = new Map<string, Bake>();

const cacheKey = (o: BakeOptions): string =>
  JSON.stringify([
    o.spec,
    o.seed,
    o.fps,
    o.durationInFrames,
    o.width ?? 1080,
    o.height ?? 1920,
    o.gravity ?? 1,
  ]);

/** Test hook: clears memoised bakes so a determinism check starts clean. */
export const clearBakeCache = (): void => {
  cache.clear();
};

// ---------------------------------------------------------------------------
// The bake
// ---------------------------------------------------------------------------

export const bake = (options: BakeOptions): Bake => {
  const key = cacheKey(options);
  const hit = cache.get(key);
  if (hit) {
    return hit;
  }
  const result = simulate(options);
  cache.set(key, result);
  return result;
};

type Tracked = {body: Body; kind: BodyKind; r?: number; hw?: number; hh?: number};

const simulate = (options: BakeOptions): Bake => {
  const {
    spec,
    seed,
    fps,
    width = 1080,
    height = 1920,
    gravity = 1,
  } = options;
  const totalFrames = Math.min(MAX_FRAMES, Math.max(1, options.durationInFrames));
  const rng = makeRng(seed);

  const engine = Engine.create();
  engine.gravity.y = gravity;
  // Fixed iteration counts: leaving these at defaults is fine, but pinning
  // them documents that solver effort is part of the deterministic input.
  engine.positionIterations = 6;
  engine.velocityIterations = 4;
  engine.constraintIterations = 2;

  const tracked: Tracked[] = [];
  /** Bodies that enter the world later, keyed by the frame they appear on. */
  const pending: {frame: number; make: () => void}[] = [];
  /** Scale pans, as tray part groups that must move together. */
  let trays: {floor: Body; wallL: Body; wallR: Body}[] = [];

  const addStatic = (
    x: number,
    y: number,
    w: number,
    h: number,
    kind: BodyKind,
    visible: boolean,
    angle = 0
  ) => {
    const b = Bodies.rectangle(x, y, w, h, {
      isStatic: true,
      angle,
      friction: 0.6,
      restitution: 0.02,
    });
    Composite.add(engine.world, b);
    if (visible) {
      tracked.push({body: b, kind, hw: w / 2, hh: h / 2});
    }
    return b;
  };

  if (spec.kind === 'pour') {
    const {jar, count, radius, startFrame, every, spread = 70} = spec;
    const wall = 26;
    // Jar floor and two walls, drawn by the component, simulated here.
    addStatic(jar.x, jar.y + jar.h / 2, jar.w, wall, 'wall', true);
    addStatic(jar.x - jar.w / 2, jar.y, wall, jar.h, 'wall', true);
    addStatic(jar.x + jar.w / 2, jar.y, wall, jar.h, 'wall', true);

    const n = Math.min(count, MAX_BODIES);
    for (let i = 0; i < n; i++) {
      const frameAt = startFrame + i * every;
      const dx = rngRange(rng, -spread, spread);
      const vx = rngRange(rng, -0.6, 0.6);
      const spin = rngRange(rng, -0.08, 0.08);
      pending.push({
        frame: frameAt,
        make: () => {
          const b = Bodies.circle(jar.x + dx, jar.y - jar.h / 2 - 90, radius, {
            restitution: 0.22,
            friction: 0.35,
            frictionAir: 0.006,
            density: 0.0016,
          });
          Body.setVelocity(b, {x: vx, y: 0});
          Body.setAngularVelocity(b, spin);
          Composite.add(engine.world, b);
          tracked.push({body: b, kind: 'token', r: radius});
        },
      });
    }
  } else if (spec.kind === 'scale') {
    const {pivot, beamHalfWidth, left, right, panDrop = 150} = spec;
    // A tipping beam is modelled as a single rotating body pinned at the
    // pivot. Rather than a constraint (which needs tuning to stay stable
    // over a short beat), the beam angle is integrated directly from the
    // torque of whatever has landed on each pan. That keeps the motion
    // readable and bounded, which matters more than rigid-body purity for
    // a 6-second metaphor.
    addStatic(pivot.x, pivot.y, 34, 34, 'pivot', true);
    // Pans and beam are tracked as synthetic bodies updated per frame.
    const beam = Bodies.rectangle(pivot.x, pivot.y, beamHalfWidth * 2, 14, {
      isStatic: true,
    });
    Composite.add(engine.world, beam);
    tracked.push({body: beam, kind: 'beam', hw: beamHalfWidth, hh: 7});

    // Each pan is a TRAY, not a plank: a floor plus two short side walls,
    // all moved together. A bare plank lets weights slide off as the beam
    // tips, which is exactly what happened on the first render of this
    // scene - the blocks tumbled past the pans and out of frame.
    const PAN_HW = 95;
    const PAN_WALL = 46;
    const makeTray = (cx: number, cy: number) => {
      const floor = Bodies.rectangle(cx, cy, PAN_HW * 2, 16, {
        isStatic: true,
        friction: 0.9,
      });
      const wallL = Bodies.rectangle(
        cx - PAN_HW,
        cy - PAN_WALL / 2,
        12,
        PAN_WALL,
        {isStatic: true, friction: 0.9}
      );
      const wallR = Bodies.rectangle(
        cx + PAN_HW,
        cy - PAN_WALL / 2,
        12,
        PAN_WALL,
        {isStatic: true, friction: 0.9}
      );
      Composite.add(engine.world, [floor, wallL, wallR]);
      tracked.push({body: floor, kind: 'pan', hw: PAN_HW, hh: 8});
      return {floor, wallL, wallR};
    };
    const trayL = makeTray(pivot.x - beamHalfWidth, pivot.y + panDrop);
    const trayR = makeTray(pivot.x + beamHalfWidth, pivot.y + panDrop);
    trays = [trayL, trayR];

    // Weights spawn just above their own tray and fall a short distance, so
    // they land in the tray instead of arriving with enough speed to bounce
    // out of it. Jitter is small for the same reason.
    const drop = (side: -1 | 1, frameAt: number, mass: number, idx: number) => {
      const jitter = rngRange(rng, -14, 14);
      pending.push({
        frame: frameAt,
        make: () => {
          const size = 44 + mass * 14;
          const b = Bodies.rectangle(
            pivot.x + side * beamHalfWidth + jitter,
            pivot.y + panDrop - 130 - idx * (size + 12),
            size,
            size,
            {restitution: 0.02, friction: 0.9, density: 0.002 * mass}
          );
          Composite.add(engine.world, b);
          tracked.push({body: b, kind: 'block', hw: size / 2, hh: size / 2});
        },
      });
    };
    left.forEach((w, i) => drop(-1, w.frame, w.mass, i));
    right.forEach((w, i) => drop(1, w.frame, w.mass, i));
  } else {
    const {groundY, centerX, blocks, spawnHeight = 150} = spec;
    addStatic(centerX, groundY + 20, width, 40, 'wall', true);
    // Running height of the tower so far. Block i must spawn ABOVE whatever
    // is already stacked, otherwise it materialises inside the previous block
    // and the solver flings them apart. A fixed spawn height only works for
    // the first block.
    let stackTop = 0;
    blocks.slice(0, MAX_BODIES).forEach((blk) => {
      const jitter = rngRange(rng, -6, 6);
      const spawnY = groundY - stackTop - spawnHeight - blk.h / 2;
      stackTop += blk.h;
      pending.push({
        frame: blk.frame,
        make: () => {
          const b = Bodies.rectangle(
            centerX + (blk.dx ?? 0) + jitter,
            spawnY,
            blk.w,
            blk.h,
            {restitution: 0.02, friction: 0.95, density: 0.002}
          );
          Composite.add(engine.world, b);
          tracked.push({body: b, kind: 'block', hw: blk.w / 2, hh: blk.h / 2});
        },
      });
    });
  }

  // Off-screen containment so nothing escapes and the sim stays bounded.
  addStatic(-200, height / 2, 40, height * 3, 'wall', false);
  addStatic(width + 200, height / 2, 40, height * 3, 'wall', false);
  addStatic(width / 2, height + 400, width * 3, 40, 'wall', false);

  // Collision capture. Throttled per frame so a settling pile does not emit
  // forty cues on one frame and blow up the SFX timeline.
  const collisions: BakedCollision[] = [];
  let currentFrame = 0;
  let collisionsThisFrame = 0;
  const kindOf = (b: Body): BodyKind =>
    tracked.find((t) => t.body.id === b.id)?.kind ?? 'wall';

  Events.on(engine, 'collisionStart', (evt) => {
    for (const pair of evt.pairs) {
      if (collisionsThisFrame >= 2) {
        return;
      }
      const {bodyA, bodyB} = pair;
      const rel = Math.hypot(
        bodyA.velocity.x - bodyB.velocity.x,
        bodyA.velocity.y - bodyB.velocity.y
      );
      if (rel < 1.1) {
        continue; // resting contact chatter, not an audible impact
      }
      collisions.push({
        frame: currentFrame,
        speed: Number(rel.toFixed(3)),
        kinds: [kindOf(bodyA), kindOf(bodyB)],
      });
      collisionsThisFrame += 1;
    }
  });

  const delta = 1000 / fps / SUB_STEPS;
  const frames: BakedBody[][] = [];
  let settledFrame = totalFrames - 1;
  let quietRun = 0;

  const scaleSpec = spec.kind === 'scale' ? spec : null;

  for (let f = 0; f < totalFrames; f++) {
    currentFrame = f;
    collisionsThisFrame = 0;

    for (const p of pending) {
      if (p.frame === f) {
        p.make();
      }
    }

    for (let s = 0; s < SUB_STEPS; s++) {
      Engine.update(engine, delta);
    }

    // The beam is kinematic: its angle follows the mass imbalance so the
    // tip reads clearly. Recomputed from world state, so still a pure
    // function of the simulation.
    if (scaleSpec) {
      const beamT = tracked.find((t) => t.kind === 'beam');
      const panLT = tracked.filter((t) => t.kind === 'pan')[0];
      const panRT = tracked.filter((t) => t.kind === 'pan')[1];
      if (beamT && panLT && panRT && trays.length === 2) {
        const px = scaleSpec.pivot.x;
        let mL = 0;
        let mR = 0;
        for (const t of tracked) {
          if (t.kind !== 'block') {
            continue;
          }
          if (t.body.position.x < px) {
            mL += t.body.mass;
          } else {
            mR += t.body.mass;
          }
        }
        const total = mL + mR;
        const targetAngle =
          total === 0 ? 0 : ((mR - mL) / total) * 0.34;
        // Critically damped approach so the beam eases instead of snapping.
        const nextAngle =
          beamT.body.angle + (targetAngle - beamT.body.angle) * 0.12;
        Body.setAngle(beamT.body, nextAngle);
        const hw = scaleSpec.beamHalfWidth;
        const drop = scaleSpec.panDrop ?? 150;
        // Move every part of each tray together, keeping the walls in the
        // same relative place, so a weight sitting in a tray stays in it.
        const place = (
          tray: {floor: Body; wallL: Body; wallR: Body},
          cx: number,
          cy: number
        ) => {
          Body.setPosition(tray.floor, {x: cx, y: cy});
          Body.setPosition(tray.wallL, {x: cx - 95, y: cy - 23});
          Body.setPosition(tray.wallR, {x: cx + 95, y: cy - 23});
        };
        place(
          trays[0],
          px - Math.cos(nextAngle) * hw,
          scaleSpec.pivot.y - Math.sin(nextAngle) * hw + drop
        );
        place(
          trays[1],
          px + Math.cos(nextAngle) * hw,
          scaleSpec.pivot.y + Math.sin(nextAngle) * hw + drop
        );
      }
    }

    const snapshot: BakedBody[] = tracked.map((t, idx) => ({
      id: idx,
      kind: t.kind,
      x: round(t.body.position.x),
      y: round(t.body.position.y),
      a: round(t.body.angle, 4),
      ...(t.r === undefined ? {} : {r: t.r}),
      ...(t.hw === undefined ? {} : {hw: t.hw, hh: t.hh}),
    }));
    frames.push(snapshot);

    // Settle detection: total kinetic energy of the dynamic bodies.
    const remaining = pending.some((p) => p.frame > f);
    const energy = tracked.reduce(
      (sum, t) =>
        t.body.isStatic
          ? sum
          : sum + Math.hypot(t.body.velocity.x, t.body.velocity.y),
      0
    );
    if (!remaining && energy < SETTLE_EPSILON) {
      quietRun += 1;
      if (quietRun >= SETTLE_HOLD_FRAMES && settledFrame === totalFrames - 1) {
        settledFrame = f;
      }
    } else {
      quietRun = 0;
    }
  }

  return {frames, collisions, settledFrame, seed, fps};
};

const round = (n: number, dp = 2): number => {
  const m = 10 ** dp;
  return Math.round(n * m) / m;
};

// ---------------------------------------------------------------------------
// Playback helper
// ---------------------------------------------------------------------------

/** Clamped lookup, so holding past the bake shows the settled last frame. */
export const bakedAt = (b: Bake, frame: number): BakedBody[] =>
  b.frames[Math.max(0, Math.min(b.frames.length - 1, Math.floor(frame)))] ?? [];

// ---------------------------------------------------------------------------
// SFX bridge
// ---------------------------------------------------------------------------
// SFX SYNC LAW: every cue time must be DERIVED from the scene, never
// estimated. A bake already knows the exact frame of every impact, so a
// physical beat can emit its own cues with zero hand-timing.

export type SfxEvent = {t: number; sound: string; gain?: number};

/**
 * Turn bake collisions into sfx-timeline.json events.
 * `beatStart` is the beat's start time in the finished video, in seconds.
 */
export const collisionsToSfx = (
  b: Bake,
  beatStart: number,
  opts: {
    /** Cue for a light impact. */
    soft?: string;
    /** Cue for a heavy impact. */
    hard?: string;
    /** Speed above which an impact counts as hard. */
    hardAbove?: number;
    /** Minimum gap between emitted cues, in seconds. Keeps beats sparse. */
    minGap?: number;
    /** Ceiling on emitted cues for this beat. */
    max?: number;
  } = {}
): SfxEvent[] => {
  const {
    soft = 'tick',
    hard = 'thump',
    hardAbove = 4.5,
    minGap = 0.12,
    max = 24,
  } = opts;
  const out: SfxEvent[] = [];
  let lastT = -Infinity;
  for (const c of b.collisions) {
    const t = Number((beatStart + c.frame / b.fps).toFixed(3));
    if (t - lastT < minGap) {
      continue;
    }
    out.push({
      t,
      sound: c.speed >= hardAbove ? hard : soft,
      gain: Number(Math.min(1, 0.35 + c.speed / 12).toFixed(2)),
    });
    lastT = t;
    if (out.length >= max) {
      break;
    }
  }
  return out;
};

/** Stable checksum of a bake, for the render-determinism QA gate. */
export const bakeChecksum = (b: Bake): string => {
  let h = 0x811c9dc5;
  const feed = (s: string) => {
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 0x01000193);
    }
  };
  for (const f of b.frames) {
    for (const body of f) {
      feed(`${body.id}:${body.x}:${body.y}:${body.a};`);
    }
  }
  feed(`|c${b.collisions.length}|s${b.settledFrame}`);
  return (h >>> 0).toString(16).padStart(8, '0');
};
