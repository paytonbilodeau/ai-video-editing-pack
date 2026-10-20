// Flow creative-lane router.
//
// Runs at BEAT-MAPPING time, before any scene code is written. Given the
// argument job each beat performs plus its verbatim spoken words, it picks
// which creative lane renders that beat. Routing is deterministic: the same
// beat list always produces the same lanes. There is no random variation,
// because "surprise me" is how a video ends up incoherent.
//
// The four lanes:
//   designed  - the board grammar (House Style v1 + Blueprint): cards,
//               charts, rails, checklists. Flow's native voice.
//   evidence  - footage as proof: real screen recording, real generated
//               asset, official logo card, device frame. Opaque, full-bleed.
//   physical  - a baked physics metaphor: matter that pours, stacks, tips.
//               Flow's originality lane; neither reference creator uses it.
//   hybrid    - a restrained designed board carrying ONE evidence or
//               physical element, usually under a camera move.
//
// Two failure modes this router exists to prevent:
//   1. Collapse back into cards-and-lines every beat (Payton, 2026-08-03:
//      "recurrent pattern (cards+pills every beat)", "not much change in
//      style"). Enforced by the designed cap + no-repeat rule.
//   2. Turning into a clone of a reference creator. Evidence is capped so
//      the video does not become a proof-reel; at least one physical beat
//      is mandatory so every video carries the device that is Flow's own.
//
// No Remotion import on purpose: this file is pure TypeScript so it can be
// exercised by a plain Node harness (scripts/verify-lanes.mjs).

export type Lane = 'designed' | 'evidence' | 'physical' | 'hybrid';

export const LANES: readonly Lane[] = [
  'designed',
  'evidence',
  'physical',
  'hybrid',
] as const;

// What the beat is DOING in the argument. This is the primary routing
// signal, because the job is a property of the reasoning, not of the words.
export type ArgumentJob =
  | 'define' // naming a thing or setting terms
  | 'claim' // asserting a position
  | 'proof' // showing that something is true
  | 'demo' // showing something working
  | 'compare' // A against B
  | 'mechanism' // how it works, the process
  | 'proportion' // how much, what share, how full
  | 'tradeoff' // what you give up to get something
  | 'criteria' // the test, the standard, the checklist
  | 'story' // a lived example
  | 'verdict' // the conclusion
  | 'enumerate'; // a list of named items

export type BeatBrief = {
  id: string;
  /** Exact spoken words from the Auphonic transcript. Never paraphrased. */
  quote: string;
  job: ArgumentJob;
  /** Seconds into the finished video. */
  start: number;
  /** Seconds on screen; covers the whole spoken passage (Duration Law). */
  dur: number;
  /**
   * True only when a REAL asset exists for this claim: a screen recording,
   * a genuine screenshot, an official logo, or something Payton actually
   * made. Never set this to reach for the evidence lane; a fabricated
   * proof shot is worse than no proof shot.
   */
  hasEvidenceAsset?: boolean;
  /**
   * Hook, pivot and verdict stay on Payton's face. Full-bleed evidence is
   * forbidden here; the graphics may still annotate around him.
   */
  onCamera?: boolean;
  /** Explicit override. Wins over everything, including quotas. */
  force?: Lane;
};

export type LaneDecision = {
  id: string;
  lane: Lane;
  /** The winning lane's score after all adjustments. */
  score: number;
  scores: Record<Lane, number>;
  /** Human-readable trace, so a beat map can explain itself in review. */
  why: string[];
  /**
   * Which technique variant to use inside the lane. Rotates per lane
   * occurrence so two designed beats in one video do not animate the same.
   */
  technique: string;
};

// ---------------------------------------------------------------------------
// Signal 1: argument job -> lane affinity
// ---------------------------------------------------------------------------

const JOB_AFFINITY: Record<ArgumentJob, Record<Lane, number>> = {
  define: {designed: 8, evidence: 2, physical: 3, hybrid: 5},
  claim: {designed: 6, evidence: 4, physical: 5, hybrid: 7},
  proof: {designed: 3, evidence: 9, physical: 3, hybrid: 6},
  demo: {designed: 2, evidence: 10, physical: 2, hybrid: 5},
  compare: {designed: 7, evidence: 5, physical: 8, hybrid: 6},
  mechanism: {designed: 9, evidence: 3, physical: 5, hybrid: 6},
  proportion: {designed: 4, evidence: 3, physical: 10, hybrid: 6},
  tradeoff: {designed: 5, evidence: 3, physical: 9, hybrid: 7},
  criteria: {designed: 8, evidence: 3, physical: 6, hybrid: 6},
  story: {designed: 4, evidence: 6, physical: 6, hybrid: 8},
  verdict: {designed: 7, evidence: 4, physical: 5, hybrid: 6},
  enumerate: {designed: 8, evidence: 3, physical: 5, hybrid: 6},
};

// ---------------------------------------------------------------------------
// Signal 2: transcript language cues
// ---------------------------------------------------------------------------
// Each family that fires adds a bounded bonus to its lane and a smaller
// bonus to hybrid (language that pulls two ways is what hybrid is for).

type CueFamily = {name: string; lane: Lane; re: RegExp; weight: number};

const CUES: CueFamily[] = [
  {
    name: 'evidence:deixis',
    lane: 'evidence',
    weight: 3,
    // Pointing at something that exists on screen.
    re: /\b(look at|here'?s|here is|this is what|watch|show you|check out|on screen)\b/i,
  },
  {
    name: 'evidence:firsthand',
    lane: 'evidence',
    weight: 3,
    // Payton did the thing himself; the artifact is therefore real.
    re: /\b(i (?:used|made|built|generated|created|shipped|ran|tried|tested))\b/i,
  },
  {
    name: 'evidence:artifact',
    lane: 'evidence',
    weight: 2,
    re: /\b(screenshot|screen recording|dashboard|the app|the tool|the model|output|result)\b/i,
  },
  {
    name: 'physical:quantity',
    lane: 'physical',
    weight: 3,
    re: /\b(more|less|most|half|double|twice|fills?|full|empty|enough|too much|too many|percent|share)\b/i,
  },
  {
    name: 'physical:balance',
    lane: 'physical',
    weight: 4,
    re: /\b(outweighs?|tips?|balance|weigh(?:s|ing)?|heavier|lighter|trade[- ]?off|costly|worth it|stack(?:s|ed|ing)?|pile|pour|overflow)\b/i,
  },
  {
    name: 'physical:numeric',
    lane: 'physical',
    weight: 2,
    re: /(\b\d+(\.\d+)?\s*%|\b\d+\s*(?:x|times)\b|\b(?:one|two|three|four|five)\s+(?:in|out of)\s+\w+)/i,
  },
  {
    name: 'designed:process',
    lane: 'designed',
    weight: 3,
    re: /\b(first|then|next|step|stage|process|loop|pipeline|system|the way (?:it|this) works|how it works)\b/i,
  },
  {
    name: 'designed:reasoning',
    lane: 'designed',
    weight: 2,
    re: /\b(because|which means|so that|the reason|therefore|in other words|the point is)\b/i,
  },
  {
    name: 'designed:agency',
    lane: 'designed',
    weight: 2,
    // Somebody doing a sequence of deliberate acts: a board of verbs.
    re: /\b(choosing|guiding|judging|editing|deciding|reviewing|checking|defining|measuring)\b/i,
  },
];

/** Cap so one cue-stuffed sentence cannot bulldoze the job signal. */
const CUE_CAP = 6;
const HYBRID_SPILL = 0.35;

// ---------------------------------------------------------------------------
// Technique rotation inside a lane (anti-repetition at the craft level)
// ---------------------------------------------------------------------------
// Two designed beats in one video must not animate identically. The router
// hands each beat a technique name; scene code is expected to honor it.

const TECHNIQUES: Record<Lane, string[]> = {
  designed: [
    'board-accumulate', // elements land one at a time and stay
    'rail-mutate', // a persistent rail whose active step moves
    'grid-reflow', // FLIP re-layout into a new grouping
    'measure-annotate', // blueprint brackets + drawn marks
  ],
  evidence: [
    'fullbleed-drift', // opaque asset, slow Ken Burns
    'callout-zoom', // crop/zoom into a region with a drawn callout
    'device-frame', // asset nested in phone/browser chrome
    'asset-switch', // claim-synced swap on the spoken noun
  ],
  physical: [
    'pour-fill', // tokens pour into a vessel until it reads full
    'tip-scale', // a beam tips as weight accumulates on one side
    'stack-settle', // blocks drop and settle into a tower
    'scatter-gather', // matter falls, then collects into a shape
  ],
  hybrid: [
    'board-with-proof', // designed board carrying one real asset
    'board-with-matter', // designed board carrying one physical element
    'camera-move-board', // designed board under a focus/push move
    'annotated-footage', // real footage with drawn blueprint annotation
  ],
};

export const laneTechnique = (lane: Lane, occurrence: number): string => {
  const list = TECHNIQUES[lane];
  return list[occurrence % list.length];
};

// ---------------------------------------------------------------------------
// Quotas (per video, applied when there are enough beats to shape)
// ---------------------------------------------------------------------------

export type LaneQuota = {
  minPhysical: number;
  maxEvidenceRatio: number;
  maxDesignedRatio: number;
  minDistinctLanes: number;
};

export const DEFAULT_QUOTA: LaneQuota = {
  // Variety Law: at least one playful concrete-metaphor beat per video.
  // Also Flow's originality clause: physical is the lane neither reference
  // creator has, so every video carries at least one.
  minPhysical: 1,
  // Anti-clone: a proof-reel is somebody else's format.
  maxEvidenceRatio: 0.4,
  // Anti-collapse: this is the cards-and-pills-every-beat complaint.
  maxDesignedRatio: 0.5,
  minDistinctLanes: 3,
};

/** Below this many beats, quotas are advisory only; there is no room. */
const QUOTA_MIN_BEATS = 4;

// ---------------------------------------------------------------------------
// Scoring
// ---------------------------------------------------------------------------

const emptyScores = (): Record<Lane, number> => ({
  designed: 0,
  evidence: 0,
  physical: 0,
  hybrid: 0,
});

/** Raw per-beat scores before any sequencing constraint. Pure and stable. */
export const scoreBeat = (
  b: BeatBrief
): {scores: Record<Lane, number>; why: string[]} => {
  const scores = emptyScores();
  const why: string[] = [];

  const aff = JOB_AFFINITY[b.job];
  for (const lane of LANES) {
    scores[lane] = aff[lane];
  }
  why.push(`job=${b.job}`);

  // Language cues, each family capped in aggregate per lane.
  const cueTotals = emptyScores();
  for (const cue of CUES) {
    if (!cue.re.test(b.quote)) {
      continue;
    }
    const room = CUE_CAP - cueTotals[cue.lane];
    if (room <= 0) {
      continue;
    }
    const add = Math.min(cue.weight, room);
    cueTotals[cue.lane] += add;
    scores[cue.lane] += add;
    scores.hybrid += add * HYBRID_SPILL;
    why.push(`cue ${cue.name} +${add}`);
  }

  // Hard gates.
  if (!b.hasEvidenceAsset) {
    scores.evidence -= 12;
    why.push('no real asset: evidence gated');
  }
  if (b.onCamera) {
    scores.evidence -= 12;
    scores.hybrid += 1;
    why.push('on-camera beat: face owns it, no full-bleed evidence');
  }

  // A very short beat cannot carry a simulation that has to settle.
  if (b.dur < 2.5) {
    scores.physical -= 6;
    why.push('beat under 2.5s: too short to settle physics');
  }

  return {scores, why};
};

// Deterministic ordering helper: highest score, then fixed lane order.
const bestLane = (
  scores: Record<Lane, number>,
  exclude?: Lane
): Lane => {
  let best: Lane = exclude === 'designed' ? 'hybrid' : 'designed';
  let bestVal = -Infinity;
  for (const lane of LANES) {
    if (lane === exclude) {
      continue;
    }
    if (scores[lane] > bestVal) {
      bestVal = scores[lane];
      best = lane;
    }
  }
  return best;
};

// ---------------------------------------------------------------------------
// The router
// ---------------------------------------------------------------------------

export const routeLanes = (
  beats: BeatBrief[],
  quota: LaneQuota = DEFAULT_QUOTA
): LaneDecision[] => {
  const n = beats.length;
  const scored = beats.map((b) => ({beat: b, ...scoreBeat(b)}));

  // Pass 1: greedy left-to-right, no lane twice in a row.
  const lanes: Lane[] = [];
  for (let i = 0; i < n; i++) {
    const {beat, scores} = scored[i];
    if (beat.force) {
      lanes.push(beat.force);
      continue;
    }
    const prev = i > 0 ? lanes[i - 1] : undefined;
    lanes.push(bestLane(scores, prev));
  }

  const forced = new Set(
    beats.filter((b) => b.force).map((b) => b.id)
  );

  // Pass 2: quota repair. Only runs when there are enough beats to shape.
  if (n >= QUOTA_MIN_BEATS) {
    const count = (lane: Lane) => lanes.filter((l) => l === lane).length;

    // Would flipping beat i to `to` break the no-repeat rule?
    const legal = (i: number, to: Lane): boolean => {
      if (forced.has(beats[i].id)) {
        return false;
      }
      if (lanes[i] === to) {
        return false;
      }
      if (i > 0 && lanes[i - 1] === to) {
        return false;
      }
      if (i < n - 1 && lanes[i + 1] === to) {
        return false;
      }
      return true;
    };

    // Regret = how much score we give up by moving beat i to `to`.
    const regret = (i: number, to: Lane): number =>
      scored[i].scores[lanes[i]] - scored[i].scores[to];

    // Cheapest legal flip into `to`, deterministic on ties (lowest index).
    const cheapestFlipTo = (to: Lane): number => {
      let bestIdx = -1;
      let bestRegret = Infinity;
      for (let i = 0; i < n; i++) {
        if (!legal(i, to)) {
          continue;
        }
        const r = regret(i, to);
        if (r < bestRegret) {
          bestRegret = r;
          bestIdx = i;
        }
      }
      return bestIdx;
    };

    // 2a. Mandatory physical beats (Variety Law + originality clause).
    let guard = 0;
    while (count('physical') < quota.minPhysical && guard++ < n) {
      const i = cheapestFlipTo('physical');
      if (i < 0) {
        break;
      }
      lanes[i] = 'physical';
      scored[i].why.push('quota: video needs a physical-metaphor beat');
    }

    // 2b. Caps. Move the lowest-margin over-quota beat to its next-best
    // legal lane. Margin = how strongly this beat wanted its lane.
    const enforceCap = (lane: Lane, ratio: number, reason: string) => {
      const cap = Math.max(1, Math.ceil(ratio * n));
      let g = 0;
      while (count(lane) > cap && g++ < n) {
        let victim = -1;
        let victimMargin = Infinity;
        for (let i = 0; i < n; i++) {
          if (lanes[i] !== lane || forced.has(beats[i].id)) {
            continue;
          }
          const alt = bestLane(
            scored[i].scores,
            lane
          );
          if (!legal(i, alt)) {
            continue;
          }
          const margin = scored[i].scores[lane] - scored[i].scores[alt];
          if (margin < victimMargin) {
            victimMargin = margin;
            victim = i;
          }
        }
        if (victim < 0) {
          break;
        }
        const alt = bestLane(scored[victim].scores, lane);
        lanes[victim] = alt;
        scored[victim].why.push(`quota: ${reason}`);
      }
    };

    enforceCap(
      'evidence',
      quota.maxEvidenceRatio,
      'evidence capped so the video is not a proof-reel'
    );
    enforceCap(
      'designed',
      quota.maxDesignedRatio,
      'designed capped so beats do not collapse into cards-and-lines'
    );

    // 2c. Distinct-lane floor.
    let g2 = 0;
    while (
      new Set(lanes).size < quota.minDistinctLanes &&
      g2++ < LANES.length
    ) {
      const missing = LANES.filter((l) => !lanes.includes(l));
      if (!missing.length) {
        break;
      }
      const to = missing[0];
      const i = cheapestFlipTo(to);
      if (i < 0) {
        break;
      }
      lanes[i] = to;
      scored[i].why.push(
        `quota: video needs at least ${quota.minDistinctLanes} distinct lanes`
      );
    }
  }

  // Pass 3: final no-repeat sweep. Quota repair can, in rare shapes,
  // reintroduce a neighbour collision; fix it against the weaker beat.
  for (let i = 1; i < n; i++) {
    if (lanes[i] !== lanes[i - 1]) {
      continue;
    }
    if (forced.has(beats[i].id)) {
      continue;
    }
    const alt = bestLane(scored[i].scores, lanes[i]);
    if (i < n - 1 && lanes[i + 1] === alt) {
      // Picking `alt` would just move the collision; take the next option.
      const second = LANES.filter(
        (l) => l !== lanes[i] && l !== alt
      ).sort((a, b) => scored[i].scores[b] - scored[i].scores[a])[0];
      lanes[i] = second ?? alt;
    } else {
      lanes[i] = alt;
    }
    scored[i].why.push('no-repeat: neighbour used the same lane');
  }

  // Technique rotation, counted per lane in running order.
  const seen: Record<Lane, number> = {
    designed: 0,
    evidence: 0,
    physical: 0,
    hybrid: 0,
  };

  return scored.map((s, i) => {
    const lane = lanes[i];
    const technique = laneTechnique(lane, seen[lane]);
    seen[lane] += 1;
    return {
      id: s.beat.id,
      lane,
      score: s.scores[lane],
      scores: s.scores,
      why: s.why,
      technique,
    };
  });
};

// ---------------------------------------------------------------------------
// Review helper
// ---------------------------------------------------------------------------

/** One line per beat, for pasting into a beat map during review. */
export const explainRoute = (decisions: LaneDecision[]): string =>
  decisions
    .map(
      (d) =>
        `${d.id.padEnd(14)} ${d.lane.padEnd(9)} ${d.technique.padEnd(18)} ${d.why.join('; ')}`
    )
    .join('\n');

/** Quota check for QA. Returns [] when the route is compliant. */
export const auditRoute = (
  decisions: LaneDecision[],
  quota: LaneQuota = DEFAULT_QUOTA
): string[] => {
  const problems: string[] = [];
  const n = decisions.length;
  const lanes = decisions.map((d) => d.lane);
  for (let i = 1; i < n; i++) {
    if (lanes[i] === lanes[i - 1]) {
      problems.push(
        `beats ${decisions[i - 1].id} and ${decisions[i].id} both use ${lanes[i]}`
      );
    }
  }
  if (n < QUOTA_MIN_BEATS) {
    return problems;
  }
  const count = (l: Lane) => lanes.filter((x) => x === l).length;
  if (count('physical') < quota.minPhysical) {
    problems.push(
      `only ${count('physical')} physical beats; need ${quota.minPhysical}`
    );
  }
  if (count('evidence') > Math.max(1, Math.ceil(quota.maxEvidenceRatio * n))) {
    problems.push(`evidence over cap (${count('evidence')}/${n})`);
  }
  if (count('designed') > Math.max(1, Math.ceil(quota.maxDesignedRatio * n))) {
    problems.push(`designed over cap (${count('designed')}/${n})`);
  }
  if (new Set(lanes).size < quota.minDistinctLanes) {
    problems.push(
      `only ${new Set(lanes).size} distinct lanes; need ${quota.minDistinctLanes}`
    );
  }
  return problems;
};
