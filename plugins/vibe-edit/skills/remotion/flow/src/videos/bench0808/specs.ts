// Physics specs for benchmark direction C.
//
// These live in their own module, free of React and Remotion, because TWO
// consumers need the exact same numbers: dirC.tsx renders them, and
// scripts/bench-sfx.mjs bakes them to produce sfx-timeline.json. If the specs
// were inlined in the component, the SFX timeline would be hand-copied from
// the scene, which is precisely what the SFX Sync Law forbids.

import type {PourSpec, ScaleSpec, StackSpec} from '../../lib/physics';

export const FPS = 30;
const S = (sec: number) => Math.round(sec * FPS);

/** Phase windows in beat-local seconds. */
export const PHASES = {
  mostFail: {in: 0.3, out: 5.55},
  coding: {in: 5.55, out: 9.21},
  salt: {in: 9.21, out: 17.31},
  satisfy: {in: 17.31, out: 22.1},
} as const;

export const dur = (p: {in: number; out: number}): number =>
  S(p.out - p.in);

const rel = (p: {in: number}, t: number) => S(t - p.in);

// ---------------------------------------------------------------------------
// Phase 1: most cases do not pass
// ---------------------------------------------------------------------------
// The jar mouth is deliberately narrow relative to the pour spread, so MOST
// tokens miss it and fall out of frame. The failure rate is not animated, it
// is what the simulation actually does with these numbers, which is the whole
// point of the lane: the picture cannot disagree with the claim.

export const MOST_FAIL: Omit<PourSpec, 'kind'> = {
  jar: {x: 540, y: 1090, w: 250, h: 330},
  count: 34,
  radius: 20,
  startFrame: rel(PHASES.mostFail, 0.9),
  every: 4,
  spread: 360,
};
export const MOST_FAIL_SEED = 'bench-c-mostfail-v1';

// ---------------------------------------------------------------------------
// Phase 2: coding does
// ---------------------------------------------------------------------------
// Left pan is loaded first with the weak "most cases" weight; the heavy
// CODING weight lands on the spoken word and the beam commits.

// ONE weight per side, not two. The first version dropped two weights on the
// right ("100" and "%") 14 frames apart; the second landed while the beam was
// still swinging and bounced out of the tray. One solid weight also reads
// better: "CODING 100%" is a single claim, not two.
export const CODING_SCALE: Omit<ScaleSpec, 'kind'> = {
  pivot: {x: 540, y: 800},
  beamHalfWidth: 250,
  left: [{frame: 0, mass: 1}],
  right: [{frame: rel(PHASES.coding, 5.55), mass: 4}],
  panDrop: 200,
};
export const CODING_SEED = 'bench-c-coding-v1';

// ---------------------------------------------------------------------------
// Phase 3: a grain of salt
// ---------------------------------------------------------------------------
// The idiom is physical, so the metaphor is literal: real grains pour into a
// dish on the spoken words "grain of salt". Fine radius, tight spread, so it
// reads as salt rather than as the mint chips used in phase 1.

export const SALT: Omit<PourSpec, 'kind'> = {
  jar: {x: 540, y: 1235, w: 300, h: 150},
  count: 52,
  radius: 9,
  startFrame: rel(PHASES.salt, 14.9),
  every: 1,
  spread: 62,
};
export const SALT_SEED = 'bench-c-salt-v1';

// ---------------------------------------------------------------------------
// Phase 4: a few other things satisfy both
// ---------------------------------------------------------------------------

// The last block drops on "things" at 21.13s, leaving only 29 frames before
// the segment ends, so the spawn height is low enough that the tower is fully
// settled at the final frame. An unsettled ending fails the QA gate.
export const SATISFY: Omit<StackSpec, 'kind'> = {
  groundY: 1330,
  centerX: 540,
  // The last block drops on "things" at 21.13s with only 29 frames of segment
  // left. At a 240px spawn height the tower was still bleeding kinetic energy
  // on the final frame (harness: "settled 143/143"), which fails the
  // settled-ending rule. 90px lands each block in roughly 8 frames.
  spawnHeight: 90,
  blocks: [
    {w: 330, h: 92, frame: rel(PHASES.satisfy, 20.5), dx: -6},
    {w: 300, h: 92, frame: rel(PHASES.satisfy, 20.89), dx: 8},
    {w: 270, h: 92, frame: rel(PHASES.satisfy, 21.13), dx: -4},
  ],
};
export const SATISFY_SEED = 'bench-c-satisfy-v1';

/** Everything the SFX generator needs, in one place. */
export const SFX_SOURCES = [
  {
    name: 'mostFail',
    phase: PHASES.mostFail,
    seed: MOST_FAIL_SEED,
    spec: {kind: 'pour' as const, ...MOST_FAIL},
  },
  {
    name: 'coding',
    phase: PHASES.coding,
    seed: CODING_SEED,
    spec: {kind: 'scale' as const, ...CODING_SCALE},
  },
  {
    name: 'salt',
    phase: PHASES.salt,
    seed: SALT_SEED,
    spec: {kind: 'pour' as const, ...SALT},
  },
  {
    name: 'satisfy',
    phase: PHASES.satisfy,
    seed: SATISFY_SEED,
    spec: {kind: 'stack' as const, ...SATISFY},
  },
];
