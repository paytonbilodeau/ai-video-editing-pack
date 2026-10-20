// Behaviour harness for the two pure Flow libraries that carry real logic:
// the creative-lane router and the deterministic physics bake.
//
// These are the parts a render cannot prove. A render shows that pixels came
// out; it does not show that the router refuses to put two designed beats in
// a row, or that the same seed produces bit-identical body positions on a
// second run. That is what this file checks.
//
// Run it against compiled output (the repo has no test runner, so the
// contract is: compile the two libs with tsc, then point this at them).
// NODE_PATH is needed because the build lands outside the project, so
// matter-js has to be resolved from flow/node_modules explicitly:
//
//   cd flow
//   npx tsc src/lib/lanes.ts src/lib/physics.ts --outDir /tmp/flowcheck \
//     --module commonjs --target ES2022 --moduleResolution node \
//     --esModuleInterop --skipLibCheck --strict
//   NODE_PATH="$PWD/node_modules" node scripts/verify-flow-lanes-physics.mjs /tmp/flowcheck

import {createRequire} from 'node:module';
import path from 'node:path';
import process from 'node:process';

const outDir = process.argv[2] ?? '/tmp/flowcheck';
const require = createRequire(import.meta.url);

// tsc mirrors the source tree under outDir when more than one rootDir-relative
// path is compiled, so the libs may be at the root OR under lib/. Try both
// rather than making the caller care.
const load = (...candidates) => {
  for (const c of candidates) {
    try {
      return require(path.resolve(outDir, c));
    } catch (e) {
      if (e.code !== 'MODULE_NOT_FOUND' || !e.message.includes(c.replace(/\.js$/, ''))) {
        // A real error inside the module, not a missing file: surface it.
        if (e.code !== 'MODULE_NOT_FOUND') throw e;
      }
    }
  }
  return null;
};

const lanes = load('lanes.js', 'lib/lanes.js');
const physics = load('physics.js', 'lib/physics.js');
if (!lanes || !physics) {
  console.error(`could not load lanes/physics from ${outDir}`);
  process.exit(2);
}

let pass = 0;
let fail = 0;
const failures = [];

const check = (name, cond, detail = '') => {
  if (cond) {
    pass += 1;
    console.log(`  ok   ${name}`);
  } else {
    fail += 1;
    failures.push(`${name}${detail ? ` :: ${detail}` : ''}`);
    console.log(`  FAIL ${name}${detail ? ` :: ${detail}` : ''}`);
  }
};

// ---------------------------------------------------------------------------
console.log('\n# lane router');
// ---------------------------------------------------------------------------

// The real benchmark segment, so the harness exercises production input.
const benchBeats = [
  {
    id: 'human-loop',
    quote:
      "With the kinds of AI use I'm talking about, the AI isn't operating itself. A person is still in the loop, choosing the goal, guiding the model.",
    job: 'mechanism',
    start: 104.93,
    dur: 7.72,
  },
  {
    id: 'judging',
    quote:
      "Judging the output, editing it, and deciding what ships, which doesn't guarantee quality, but it keeps human taste and responsibility in the process.",
    job: 'criteria',
    start: 112.65,
    dur: 7.35,
  },
  {
    id: 'imagination',
    quote:
      "And I love image and video models because they let me create things I couldn't before. My imagination becomes the only limitation.",
    job: 'demo',
    start: 120.0,
    dur: 7.61,
    hasEvidenceAsset: true,
  },
  {
    id: 'better-test',
    quote:
      "So I'd say the better test is whether we can define success, measure what matters, catch a costly failure, and keep real people accountable where taste, trust, or consent really matter.",
    job: 'tradeoff',
    start: 127.61,
    dur: 11.85,
  },
];

const route = lanes.routeLanes(benchBeats);
console.log(
  route.map((d) => `    ${d.id} -> ${d.lane} (${d.technique})`).join('\n')
);

check('routes every beat', route.length === benchBeats.length);
check(
  'no lane twice in a row',
  route.every((d, i) => i === 0 || d.lane !== route[i - 1].lane),
  route.map((d) => d.lane).join(',')
);
check(
  'audit passes on the real segment',
  lanes.auditRoute(route).length === 0,
  lanes.auditRoute(route).join(' | ')
);
check(
  'the demo beat with a real asset routes to evidence',
  route.find((d) => d.id === 'imagination').lane === 'evidence'
);
check(
  'at least one physical beat (Variety Law + originality clause)',
  route.some((d) => d.lane === 'physical')
);
check(
  'at least 3 distinct lanes',
  new Set(route.map((d) => d.lane)).size >= 3
);

// Determinism: same input, same output, every time.
const routeAgain = lanes.routeLanes(benchBeats);
check(
  'router is deterministic across calls',
  JSON.stringify(route.map((d) => [d.lane, d.technique])) ===
    JSON.stringify(routeAgain.map((d) => [d.lane, d.technique]))
);

// Evidence gate: without a real asset, a demo beat must NOT go to evidence.
const noAsset = lanes.routeLanes([
  {...benchBeats[0]},
  {...benchBeats[2], hasEvidenceAsset: false},
  {...benchBeats[1], id: 'j2'},
  {...benchBeats[3], id: 'b2'},
]);
check(
  'no real asset means no evidence lane (never fabricate proof)',
  noAsset.find((d) => d.id === 'imagination').lane !== 'evidence',
  noAsset.find((d) => d.id === 'imagination').lane
);

// On-camera beats keep the face; full-bleed evidence is forbidden there.
const onCam = lanes.routeLanes([
  {...benchBeats[2], id: 'hook', onCamera: true, hasEvidenceAsset: true},
  {...benchBeats[0], id: 'a'},
  {...benchBeats[1], id: 'b'},
  {...benchBeats[3], id: 'c'},
]);
check(
  'on-camera beat never routes to full-bleed evidence',
  onCam.find((d) => d.id === 'hook').lane !== 'evidence',
  onCam.find((d) => d.id === 'hook').lane
);

// force wins outright.
const forced = lanes.routeLanes([
  {...benchBeats[0], force: 'physical'},
  {...benchBeats[1]},
  {...benchBeats[2], hasEvidenceAsset: true},
  {...benchBeats[3]},
]);
check('force override wins', forced[0].lane === 'physical');

// Anti-collapse: a video of nothing but mechanism beats must NOT come out
// all-designed. This is the cards-and-pills-every-beat complaint.
const allMechanism = Array.from({length: 8}, (_, i) => ({
  id: `m${i}`,
  quote: 'the way this works is a process: first the model, then the check',
  job: 'mechanism',
  start: i * 5,
  dur: 5,
}));
const collapsed = lanes.routeLanes(allMechanism);
const designedCount = collapsed.filter((d) => d.lane === 'designed').length;
check(
  'eight identical mechanism beats do not all become designed',
  designedCount <= Math.ceil(0.5 * 8),
  `${designedCount}/8 designed -> ${collapsed.map((d) => d.lane).join(',')}`
);
check(
  'anti-collapse route still passes its own audit',
  lanes.auditRoute(collapsed).length === 0,
  lanes.auditRoute(collapsed).join(' | ')
);

// Anti-clone: eight demo beats with assets must NOT all become evidence.
const allDemo = Array.from({length: 8}, (_, i) => ({
  id: `d${i}`,
  quote: "here's the tool, I used it, look at the output on screen",
  job: 'demo',
  start: i * 5,
  dur: 5,
  hasEvidenceAsset: true,
}));
const cloned = lanes.routeLanes(allDemo);
const evCount = cloned.filter((d) => d.lane === 'evidence').length;
check(
  'eight demo beats do not all become evidence (anti proof-reel)',
  evCount <= Math.ceil(0.4 * 8),
  `${evCount}/8 evidence -> ${cloned.map((d) => d.lane).join(',')}`
);

// Technique rotation: repeated lanes must not repeat their technique.
const techByLane = {};
for (const d of collapsed) {
  (techByLane[d.lane] ??= []).push(d.technique);
}
check(
  'technique rotates within a lane',
  Object.values(techByLane).every(
    (list) => list.length < 2 || new Set(list).size > 1
  ),
  JSON.stringify(techByLane)
);

// Short beats cannot carry physics that has to settle.
const shorty = lanes.scoreBeat({
  id: 's',
  quote: 'it outweighs the cost',
  job: 'proportion',
  start: 0,
  dur: 1.4,
});
check(
  'sub-2.5s beat is penalised for physics',
  shorty.why.some((w) => w.includes('too short to settle'))
);

// ---------------------------------------------------------------------------
console.log('\n# physics bake');
// ---------------------------------------------------------------------------

const pourSpec = {
  spec: {
    kind: 'pour',
    jar: {x: 540, y: 1020, w: 420, h: 460},
    count: 26,
    radius: 21,
    startFrame: 8,
    every: 5,
    spread: 78,
  },
  seed: 'bench-pour-v1',
  fps: 30,
  durationInFrames: 300,
};

physics.clearBakeCache();
const b1 = physics.bake(pourSpec);
physics.clearBakeCache();
const b2 = physics.bake(pourSpec);

check('bake produces one entry per frame', b1.frames.length === 300);
check('bake produces bodies', b1.frames[299].length > 20, `${b1.frames[299].length} bodies`);
const sum1 = physics.bakeChecksum(b1);
const sum2 = physics.bakeChecksum(b2);
check(
  'same seed + same code => identical bake checksum',
  sum1 === sum2,
  `${sum1} vs ${sum2}`
);
console.log(`    pour checksum: ${sum1}`);

const b3 = physics.bake({...pourSpec, seed: 'bench-pour-v2'});
check(
  'a different seed produces a different world',
  physics.bakeChecksum(b3) !== sum1
);

check('collisions were captured', b1.collisions.length > 0, `${b1.collisions.length}`);
check(
  'collisions are throttled to <=2 per frame',
  Object.values(
    b1.collisions.reduce((acc, c) => {
      acc[c.frame] = (acc[c.frame] ?? 0) + 1;
      return acc;
    }, {})
  ).every((n) => n <= 2)
);
check(
  'scene settles before the end of the beat',
  b1.settledFrame < 299,
  `settled at ${b1.settledFrame}`
);

// Tokens must end up INSIDE the jar, not leaking through the walls.
const jar = pourSpec.spec.jar;
const finalTokens = b1.frames[b1.frames.length - 1].filter((x) => x.kind === 'token');
const leaked = finalTokens.filter(
  (t) =>
    t.x < jar.x - jar.w / 2 - 40 ||
    t.x > jar.x + jar.w / 2 + 40 ||
    t.y > jar.y + jar.h / 2 + 40
);
check(
  'no tokens leak through the vessel walls',
  leaked.length === 0,
  `${leaked.length} leaked of ${finalTokens.length}`
);

// SFX bridge: cues derived from the bake, spaced, and inside the beat.
const sfx = physics.collisionsToSfx(b1, 22.68, {minGap: 0.12, max: 24});
check('sfx cues generated from collisions', sfx.length > 0, `${sfx.length} cues`);
check(
  'sfx cues respect the minimum gap',
  sfx.every((e, i) => i === 0 || e.t - sfx[i - 1].t >= 0.119),
);
check(
  'sfx cues are inside the beat window',
  sfx.every((e) => e.t >= 22.68 && e.t <= 22.68 + 300 / 30 + 0.01)
);
check('sfx cues are capped', sfx.length <= 24);

// Scale metaphor bakes and actually tips.
physics.clearBakeCache();
const scale = physics.bake({
  spec: {
    kind: 'scale',
    pivot: {x: 540, y: 780},
    beamHalfWidth: 250,
    left: [{frame: 20, mass: 1}, {frame: 50, mass: 1}],
    right: [{frame: 90, mass: 1}, {frame: 120, mass: 1}, {frame: 150, mass: 2}],
    panDrop: 150,
  },
  seed: 'bench-scale-v1',
  fps: 30,
  durationInFrames: 260,
});
const beamStart = scale.frames[25].find((x) => x.kind === 'beam');
const beamEnd = scale.frames[259].find((x) => x.kind === 'beam');
check(
  'the beam actually tips as weight accumulates',
  Math.abs(beamEnd.a - beamStart.a) > 0.05,
  `${beamStart.a} -> ${beamEnd.a}`
);
check(
  'the beam tips toward the heavier (right) side',
  beamEnd.a > beamStart.a,
  `${beamStart.a} -> ${beamEnd.a}`
);
check('scale bake is bounded', scale.frames.length === 260);

// REGRESSION: the first version used bare plank pans, and every weight slid
// off and fell out of frame while the beam still "tipped" correctly. The
// picture disagreed with the simulation. Weights must end up IN their tray.
const lastScale = scale.frames[259];
const pans = lastScale.filter((x) => x.kind === 'pan');
const weights = lastScale.filter((x) => x.kind === 'block');
const seated = weights.filter((w) =>
  pans.some((p) => Math.abs(w.x - p.x) < 130 && p.y - w.y > -20 && p.y - w.y < 220)
);
check(
  'every weight ends up seated in a pan, not fallen past it',
  seated.length === weights.length,
  `${seated.length}/${weights.length} seated; pans at ${pans
    .map((p) => `(${p.x},${p.y})`)
    .join(' ')}; weights at ${weights.map((w) => `(${w.x},${w.y})`).join(' ')}`
);

// REGRESSION: a stack whose blocks spawn at a fixed height materialise inside
// the block below and get flung apart. They must end up stacked and settled.
physics.clearBakeCache();
const stack = physics.bake({
  spec: {
    kind: 'stack',
    groundY: 1330,
    centerX: 540,
    spawnHeight: 150,
    blocks: [
      {w: 330, h: 92, frame: 10, dx: -6},
      {w: 300, h: 92, frame: 24, dx: 8},
      {w: 270, h: 92, frame: 38, dx: -4},
    ],
  },
  seed: 'bench-c-satisfy-v1',
  fps: 30,
  durationInFrames: 110,
});
const finalBlocks = stack.frames[109].filter((x) => x.kind === 'block');
check('all stack blocks present at the end', finalBlocks.length === 3);
check(
  'stack blocks stay near the centre (no explosion)',
  finalBlocks.every((b) => Math.abs(b.x - 540) < 120),
  finalBlocks.map((b) => `${b.x}`).join(',')
);
check(
  'stack blocks come to rest flat, not tilted',
  finalBlocks.every((b) => Math.abs(b.a) < 0.12),
  finalBlocks.map((b) => b.a.toFixed(3)).join(',')
);
check(
  'stack blocks rest above the ground line, stacked',
  finalBlocks.every((b) => b.y < 1335 && b.y > 1050),
  finalBlocks.map((b) => `${b.y}`).join(',')
);
check(
  'stack settles before the beat ends',
  stack.settledFrame < 109,
  `settled at ${stack.settledFrame}`
);

// Playback lookup clamps instead of throwing.
check(
  'bakedAt clamps past the end',
  physics.bakedAt(scale, 99999).length === scale.frames[259].length
);
check('bakedAt clamps before the start', physics.bakedAt(scale, -50).length > 0);

// ---------------------------------------------------------------------------
console.log('\n# shipped benchmark specs (direction C)');
// ---------------------------------------------------------------------------
// The checks above use synthetic specs. That is not enough: a scene can ship
// numbers that fail even when the engine is correct, which is exactly what
// happened here (two weights dropped 14 frames apart on the same pan, the
// second landing mid-swing and bouncing out). These checks bake the ACTUAL
// specs Direction C renders, so tuning a scene cannot silently break it.

const specs = load('specs.js', 'videos/bench0808/specs.js');
if (!specs) {
  console.log('  skip  specs.js not compiled into outDir');
}

if (specs) {
  for (const src of specs.SFX_SOURCES) {
    physics.clearBakeCache();
    const b = physics.bake({
      spec: src.spec,
      seed: src.seed,
      fps: specs.FPS,
      durationInFrames: specs.dur(src.phase),
    });
    const last = b.frames[b.frames.length - 1];

    check(
      `[${src.name}] bakes to the full phase length`,
      b.frames.length === specs.dur(src.phase),
      `${b.frames.length} vs ${specs.dur(src.phase)}`
    );

    // Determinism on the real spec, not just a test fixture.
    const c1 = physics.bakeChecksum(b);
    physics.clearBakeCache();
    const c2 = physics.bakeChecksum(
      physics.bake({
        spec: src.spec,
        seed: src.seed,
        fps: specs.FPS,
        durationInFrames: specs.dur(src.phase),
      })
    );
    check(`[${src.name}] deterministic across bakes`, c1 === c2, `${c1} vs ${c2}`);
    console.log(`    ${src.name} checksum: ${c1}`);

    if (src.spec.kind === 'scale') {
      const pans = last.filter((x) => x.kind === 'pan');
      const weights = last.filter((x) => x.kind === 'block');
      const seated = weights.filter((w) =>
        pans.some(
          (p) => Math.abs(w.x - p.x) < 130 && p.y - w.y > -20 && p.y - w.y < 220
        )
      );
      check(
        `[${src.name}] every weight seated in a pan at the final frame`,
        seated.length === weights.length && weights.length > 0,
        `${seated.length}/${weights.length} seated`
      );
      const beamFirst = b.frames[1].find((x) => x.kind === 'beam');
      const beamLast = last.find((x) => x.kind === 'beam');
      check(
        `[${src.name}] beam commits toward the heavier side`,
        beamLast.a > beamFirst.a + 0.05,
        `${beamFirst.a} -> ${beamLast.a}`
      );
    }

    if (src.spec.kind === 'stack') {
      const blocks = last.filter((x) => x.kind === 'block');
      check(
        `[${src.name}] all blocks present and settled flat at the final frame`,
        blocks.length === src.spec.blocks.length &&
          blocks.every((x) => Math.abs(x.a) < 0.12),
        `${blocks.length} blocks, angles ${blocks.map((x) => x.a.toFixed(3)).join(',')}`
      );
      check(
        `[${src.name}] scene is settled by the final frame`,
        b.settledFrame < b.frames.length - 1,
        `settled ${b.settledFrame}/${b.frames.length - 1}`
      );
    }

    if (src.spec.kind === 'pour') {
      const jar = src.spec.jar;
      const tokens = last.filter((x) => x.kind === 'token');
      const inside = tokens.filter(
        (t) =>
          Math.abs(t.x - jar.x) < jar.w / 2 &&
          t.y > jar.y - jar.h / 2 &&
          t.y < jar.y + jar.h / 2 + 30
      );
      check(
        `[${src.name}] some tokens land in the vessel`,
        inside.length > 0,
        `${inside.length}/${tokens.length} inside`
      );
      // The "most cases do not pass" beat must ACTUALLY fail most tokens,
      // otherwise the picture contradicts the spoken claim.
      if (src.name === 'mostFail') {
        check(
          'mostFail: a minority of tokens land in the jar (claim matches physics)',
          inside.length < tokens.length / 2,
          `${inside.length}/${tokens.length} landed`
        );
      }
    }
  }

  // The SFX bridge over the real specs, as it will be written to disk.
  const allCues = specs.SFX_SOURCES.flatMap((src) => {
    physics.clearBakeCache();
    const b = physics.bake({
      spec: src.spec,
      seed: src.seed,
      fps: specs.FPS,
      durationInFrames: specs.dur(src.phase),
    });
    return physics.collisionsToSfx(b, src.phase.in, {minGap: 0.12, max: 24});
  });
  check('shipped specs produce SFX cues', allCues.length > 0, `${allCues.length} cues`);
  check(
    'all shipped cues fall inside the 22.10s segment',
    allCues.every((c) => c.t >= 0 && c.t <= 22.1),
    `range ${Math.min(...allCues.map((c) => c.t))}..${Math.max(...allCues.map((c) => c.t))}`
  );
}

// ---------------------------------------------------------------------------
console.log(
  `\n${fail === 0 ? 'PASS' : 'FAIL'}  ${pass} passed, ${fail} failed`
);
if (fail) {
  console.log(failures.map((f) => `  - ${f}`).join('\n'));
  process.exit(1);
}
