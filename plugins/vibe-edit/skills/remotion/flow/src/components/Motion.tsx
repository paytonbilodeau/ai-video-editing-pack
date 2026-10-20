// Flow motion primitives: idle drift, camera moves, textured dissolves and
// hand-drawn annotation.
//
// PROVENANCE
// The mechanics here are adapted from the Remocn registry
// (https://github.com/Remocn/remocn, MIT, pinned at commit
// 0797bfe319bd2dae06eea5a9f67591e1b31392e5), specifically the `drift`,
// `focus-pull`, `grain-dissolve` and `ink-arrow` items. Nothing is a
// verbatim copy: Remocn targets React 19 + Tailwind + `@/` path aliases and
// carries its own visual identity, none of which exists in Flow. What
// transferred is the IDEA of each device and, for `focus-pull`, the shape of
// its blur/scale/brightness curve. Everything is re-expressed against Flow's
// palette proxy, Departure Mono, and the deterministic useCurrentFrame model.
// Full attribution and the update procedure live in
// .claude/skills/flow/references/upstream-provenance.md.
//
// WEBGL DECISION (important, do not silently revert)
// Remocn's own `grain-dissolve` and `dither-dissolve` render through
// `@paper-design/shaders-react`, i.e. a WebGL context. Flow's deliverable is
// a transparent ProRes 4444 master, and a WebGL canvas is the single most
// common way to lose the alpha channel in a headless render (it also drags
// in a shader runtime and needs `--gl=angle` babysitting). So the dissolve
// below is reimplemented with an SVG filter instead: feTurbulence is defined
// by the SVG spec to produce identical output for a given seed and
// baseFrequency, so it is just as deterministic, it composites through the
// normal alpha path, and it adds ZERO dependencies. If a future effect
// genuinely needs WebGL, prove it against the alpha QA gate first.

import React from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  random,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {T} from '../theme';

const clamp = {
  extrapolateLeft: 'clamp' as const,
  extrapolateRight: 'clamp' as const,
};

// ---------------------------------------------------------------------------
// Drift: nothing on screen is ever perfectly frozen
// ---------------------------------------------------------------------------
// Adapted from Remocn `drift`. Their version is a pure scale ramp across the
// whole composition duration; this one adds pan and an explicit window so a
// beat can drift a single element rather than the entire frame, and it
// defaults far gentler because Flow drifts things the viewer is READING.
//
// House rule from the flow skill: drift decorative elements and evidence
// assets. Never drift text while it is being read.

export const Drift: React.FC<{
  children: React.ReactNode;
  /** Total scale gained across the window. 0.03 to 0.06 reads best. */
  grow?: number;
  /** Horizontal pan in px across the window. */
  panX?: number;
  /** Vertical pan in px across the window. */
  panY?: number;
  /** Frames. Defaults to the enclosing Sequence duration. */
  dur?: number;
  /** Start scaled up and settle down instead of pushing in. */
  reverse?: boolean;
}> = ({children, grow = 0.04, panX = 0, panY = 0, dur, reverse = false}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const span = Math.max(1, dur ?? durationInFrames);
  const p = interpolate(frame, [0, span], [0, 1], clamp);
  const s = reverse ? 1 + grow * (1 - p) : 1 + grow * p;
  return (
    <AbsoluteFill
      style={{
        transform: `translate(${panX * p}px, ${panY * p}px) scale(${s})`,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// CameraMove: focus pull / push through, as an in-scene device
// ---------------------------------------------------------------------------
// Remocn ships focus-pull as a @remotion/transitions presentation, which
// assumes TransitionSeries. Flow does not use TransitionSeries: beats live on
// MasterTrack, and the interesting camera work happens INSIDE one long state
// machine. So the same blur/scale/brightness relationship is re-expressed as
// a windowed wrapper any scene can nest.

export type CameraKind = 'focus-in' | 'focus-out' | 'push-through' | 'settle';

export const CameraMove: React.FC<{
  children: React.ReactNode;
  /** Frame the move starts on. */
  at: number;
  /** Length of the move in frames. 18-30 reads as a camera, faster reads as a glitch. */
  dur?: number;
  kind?: CameraKind;
  /** Peak blur in px. Keep low on text. */
  blur?: number;
  /** Peak scale change. */
  scale?: number;
}> = ({children, at, dur = 24, kind = 'focus-in', blur = 12, scale = 0.06}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [at, at + dur], [0, 1], clamp);

  let style: React.CSSProperties;
  if (kind === 'focus-in') {
    // Resolves from soft and slightly large into sharp and settled. The
    // brightness lift on the way in is what sells it as an optical move
    // rather than a CSS blur; that relationship is Remocn's observation.
    style = {
      opacity: interpolate(p, [0, 0.28], [0, 1], clamp),
      transform: `scale(${interpolate(p, [0, 1], [1 + scale, 1], {
        ...clamp,
        easing: Easing.out(Easing.cubic),
      })})`,
      filter: `blur(${interpolate(p, [0, 0.62], [blur, 0], {
        ...clamp,
        easing: Easing.out(Easing.quad),
      })}px) brightness(${interpolate(p, [0, 0.7], [1.22, 1], clamp)})`,
    };
  } else if (kind === 'focus-out') {
    style = {
      opacity: interpolate(p, [0.5, 0.92], [1, 0], clamp),
      transform: `scale(${interpolate(p, [0, 1], [1, 1 + scale], {
        ...clamp,
        easing: Easing.in(Easing.cubic),
      })})`,
      filter: `blur(${interpolate(p, [0.08, 0.7], [0, blur], {
        ...clamp,
        easing: Easing.in(Easing.quad),
      })}px) brightness(${interpolate(p, [0.1, 0.7], [1, 1.25], clamp)})`,
    };
  } else if (kind === 'push-through') {
    // A committed move past the subject: scale keeps going, blur peaks in
    // the middle rather than at an end.
    style = {
      transform: `scale(${interpolate(p, [0, 1], [1, 1 + scale * 2.2], {
        ...clamp,
        easing: Easing.bezier(0.19, 1, 0.22, 1),
      })})`,
      filter: `blur(${interpolate(p, [0, 0.5, 1], [0, blur * 0.6, 0], clamp)}px)`,
    };
  } else {
    // 'settle': the restrained default. A whisper of a push that lands.
    style = {
      transform: `scale(${interpolate(p, [0, 1], [1 + scale * 0.5, 1], {
        ...clamp,
        easing: Easing.bezier(0.19, 1, 0.22, 1),
      })})`,
    };
  }

  return <AbsoluteFill style={style}>{children}</AbsoluteFill>;
};

// ---------------------------------------------------------------------------
// GrainDissolve: textured phase transition, no WebGL
// ---------------------------------------------------------------------------
// Sweeps an alpha threshold across fractal noise so the layer erodes in
// grain rather than crossfading. Use it as a PHASE transition inside a state
// machine, which is the alternative to crossfade Payton asked for after the
// context video. Alpha-safe: this is an ordinary SVG filter in the normal
// compositing path.

let dissolveSeq = 0;

export const GrainDissolve: React.FC<{
  children: React.ReactNode;
  /** Frame the dissolve starts. */
  at: number;
  dur?: number;
  /** 'in' materialises the layer, 'out' erodes it away. */
  direction?: 'in' | 'out';
  /** Noise scale. Lower = bigger, softer clumps. */
  frequency?: number;
  /** Integer seed; same seed always yields the same grain (SVG spec). */
  seed?: number;
}> = ({
  children,
  at,
  dur = 18,
  direction = 'in',
  frequency = 0.016,
  seed = 4,
}) => {
  const frame = useCurrentFrame();
  // Stable per-instance filter id. useState-free so it cannot drift between
  // render workers; the counter only needs to be unique within one frame's
  // React tree.
  const idRef = React.useRef<string | null>(null);
  if (idRef.current === null) {
    dissolveSeq += 1;
    idRef.current = `flow-dissolve-${dissolveSeq}`;
  }
  const id = idRef.current;

  const p = interpolate(frame, [at, at + dur], [0, 1], clamp);
  const t = direction === 'in' ? p : 1 - p;

  // Fully settled: drop the filter entirely so a held frame costs nothing
  // and cannot pick up filter edge artefacts.
  if (t >= 1) {
    return <AbsoluteFill>{children}</AbsoluteFill>;
  }
  if (t <= 0) {
    return null;
  }

  // Steep slope = crisp grain edge. Intercept sweeps the threshold so more
  // of the noise field clears the alpha cut as t rises.
  const slope = 9;
  const intercept = -slope * (1 - t) + 0.5;

  return (
    <AbsoluteFill>
      <svg width={0} height={0} style={{position: 'absolute'}}>
        <defs>
          <filter id={id} x="0%" y="0%" width="100%" height="100%">
            <feTurbulence
              type="fractalNoise"
              baseFrequency={frequency}
              numOctaves={3}
              seed={seed}
              stitchTiles="stitch"
              result="noise"
            />
            <feColorMatrix in="noise" type="luminanceToAlpha" result="lum" />
            <feComponentTransfer in="lum" result="mask">
              <feFuncA type="linear" slope={slope} intercept={intercept} />
            </feComponentTransfer>
            <feComposite in="SourceGraphic" in2="mask" operator="in" />
          </filter>
        </defs>
      </svg>
      <AbsoluteFill style={{filter: `url(#${id})`}}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Ink annotation: the hand-drawn voice
// ---------------------------------------------------------------------------
// Remocn's ink set builds a brush ribbon along a seeded-wobble cubic bezier
// and reveals it on a stop-motion stepped ramp. That is the idea worth
// having; the implementation here is Flow's own, using Remotion's `random()`
// as the seeded source (already the approved determinism primitive in this
// codebase) instead of Remocn's private hash helper, and drawing with
// stroke-dashoffset rather than a generated ribbon polygon.
//
// GOTCHA honoured: a zero-length path with round linecaps renders as a stray
// DOT. Every primitive below returns null until its start frame.

/** Quantise progress into visible steps: the stop-motion / hand-drawn feel. */
const stepped = (p: number, steps: number): number =>
  steps <= 1 ? p : Math.round(p * steps) / steps;

const wobblePath = (
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  seedKey: string,
  bow: number
): string => {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.hypot(dx, dy) || 1;
  const nx = -dy / len;
  const ny = dx / len;
  const jitter = len * 0.05;
  const j = (k: string) => (random(`${seedKey}:${k}`) - 0.5) * 2 * jitter;
  const c1x = x1 + dx * 0.3 + nx * bow * len + j('c1x');
  const c1y = y1 + dy * 0.3 + ny * bow * len + j('c1y');
  const c2x = x1 + dx * 0.7 + nx * bow * len + j('c2x');
  const c2y = y1 + dy * 0.7 + ny * bow * len + j('c2y');
  return `M ${x1} ${y1} C ${c1x} ${c1y}, ${c2x} ${c2y}, ${x2} ${y2}`;
};

export const InkUnderline: React.FC<{
  x1: number;
  y1: number;
  x2: number;
  y2?: number;
  at: number;
  dur?: number;
  color?: string;
  width?: number;
  seed?: string;
  /** 0 = smooth draw, 6-10 = hand-drawn stop-motion. */
  steps?: number;
}> = ({
  x1,
  y1,
  x2,
  y2,
  at,
  dur = 14,
  color,
  width = 7,
  seed = 'ink',
  steps = 7,
}) => {
  const frame = useCurrentFrame();
  if (frame < at) {
    return null; // never emit a zero-length round-capped path
  }
  const raw = interpolate(frame, [at, at + dur], [0, 1], clamp);
  const p = stepped(raw, steps);
  if (p <= 0) {
    return null;
  }
  const d = wobblePath(x1, y1, x2, y2 ?? y1, seed, 0.035);
  const len = Math.hypot(x2 - x1, (y2 ?? y1) - y1) * 1.25;
  return (
    <svg
      width={1080}
      height={1920}
      style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}
    >
      <path
        d={d}
        fill="none"
        stroke={color ?? T.good}
        strokeWidth={width}
        strokeLinecap="round"
        strokeDasharray={len}
        strokeDashoffset={len * (1 - p)}
      />
    </svg>
  );
};

export const InkArrow: React.FC<{
  from: {x: number; y: number};
  to: {x: number; y: number};
  at: number;
  dur?: number;
  color?: string;
  width?: number;
  /** Positive bows one way, negative the other. */
  bow?: number;
  seed?: string;
  steps?: number;
  headSize?: number;
}> = ({
  from,
  to,
  at,
  dur = 16,
  color,
  width = 6,
  bow = 0.14,
  seed = 'arrow',
  steps = 8,
  headSize = 26,
}) => {
  const frame = useCurrentFrame();
  if (frame < at) {
    return null;
  }
  const raw = interpolate(frame, [at, at + dur], [0, 1], clamp);
  const p = stepped(raw, steps);
  if (p <= 0) {
    return null;
  }
  const d = wobblePath(from.x, from.y, to.x, to.y, seed, bow);
  const len = Math.hypot(to.x - from.x, to.y - from.y) * 1.35;
  const stroke = color ?? T.good;

  // Head only once the shaft has essentially arrived, so it never floats.
  const headOn = p > 0.82;
  const ang = Math.atan2(to.y - from.y, to.x - from.x);
  const spread = 0.62;
  const hx1 = to.x - Math.cos(ang - spread) * headSize;
  const hy1 = to.y - Math.sin(ang - spread) * headSize;
  const hx2 = to.x - Math.cos(ang + spread) * headSize;
  const hy2 = to.y - Math.sin(ang + spread) * headSize;

  return (
    <svg
      width={1080}
      height={1920}
      style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}
    >
      <path
        d={d}
        fill="none"
        stroke={stroke}
        strokeWidth={width}
        strokeLinecap="round"
        strokeDasharray={len}
        strokeDashoffset={len * (1 - p)}
      />
      {headOn ? (
        <path
          d={`M ${hx1} ${hy1} L ${to.x} ${to.y} L ${hx2} ${hy2}`}
          fill="none"
          stroke={stroke}
          strokeWidth={width}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      ) : null}
    </svg>
  );
};

export const ScribbleCircle: React.FC<{
  cx: number;
  cy: number;
  rx: number;
  ry?: number;
  at: number;
  dur?: number;
  color?: string;
  width?: number;
  seed?: string;
  steps?: number;
  /** How many times the pen goes round. 1.6 reads best. */
  laps?: number;
}> = ({
  cx,
  cy,
  rx,
  ry,
  at,
  dur = 20,
  color,
  width = 6,
  seed = 'circ',
  steps = 9,
  laps = 1.6,
}) => {
  const frame = useCurrentFrame();
  if (frame < at) {
    return null;
  }
  const raw = interpolate(frame, [at, at + dur], [0, 1], clamp);
  const p = stepped(raw, steps);
  if (p <= 0) {
    return null;
  }
  const RY = ry ?? rx * 0.62;
  // One continuous wobbled ellipse, sampled so the wobble is stable per
  // seed. Sampling (rather than an <ellipse>) is what makes it read hand-drawn.
  const N = 96;
  const pts: string[] = [];
  for (let i = 0; i <= N; i++) {
    const t = (i / N) * Math.PI * 2 * laps - Math.PI / 2;
    const wob = 1 + (random(`${seed}:${i % 24}`) - 0.5) * 0.075;
    const x = cx + Math.cos(t) * rx * wob;
    const y = cy + Math.sin(t) * RY * wob;
    pts.push(`${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`);
  }
  const d = pts.join(' ');
  const len = (rx + RY) * 3.4 * laps;
  return (
    <svg
      width={1080}
      height={1920}
      style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}
    >
      <path
        d={d}
        fill="none"
        stroke={color ?? T.good}
        strokeWidth={width}
        strokeLinecap="round"
        strokeDasharray={len}
        strokeDashoffset={len * (1 - p)}
      />
    </svg>
  );
};
