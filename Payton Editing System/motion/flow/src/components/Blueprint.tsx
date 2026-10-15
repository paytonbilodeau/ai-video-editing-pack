import React from 'react';
import {useCurrentFrame} from 'remotion';
import {ease, easeOut} from '../lib/anim';
import {pixel} from '../fonts';
import {T} from '../theme';

// Blueprint/schematic primitives (HOUSE STYLE v1, approved 2026-08-03):
// thin line-work that DRAWS ON, typewriter caps labels, scanline phase
// sweeps, measurement brackets, node dots. No fills, no shadows, no
// pops. Same mentorship palette; lucide stroke icons are native here.

export const CHAR_W = 0.72; // pixel-mono glyph width factor at letterSpacing .1em

// Faint mint dot grid + corner registration marks. Atmosphere layer.
export const BPGrid: React.FC = () => (
  <>
    <div
      style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: `radial-gradient(${T.good} 1.1px, transparent 1.3px)`,
        backgroundSize: '72px 72px',
        backgroundPosition: '36px 36px',
        opacity: 0.055,
      }}
    />
    {[
      [96, 226],
      [944, 226],
      [96, 1474],
      [944, 1474],
    ].map(([x, y], i) => (
      <div
        key={i}
        style={{
          position: 'absolute',
          left: x - 14,
          top: y - 14,
          width: 28,
          height: 28,
          opacity: 0.35,
        }}
      >
        <svg width={28} height={28}>
          <line x1={14} y1={0} x2={14} y2={28} stroke={T.dim} strokeWidth={2} />
          <line x1={0} y1={14} x2={28} y2={14} stroke={T.dim} strokeWidth={2} />
        </svg>
      </div>
    ))}
  </>
);

// Typewriter caps text. Anchored so finished text is centered at x, but
// characters appear left-to-right without shifting (fixed-width slot).
// Cursor blinks while typing, vanishes 12f after done.
export const BPType: React.FC<{
  x: number;
  y: number;
  text: string;
  at: number;
  size?: number;
  cps?: number;
  color?: string;
  spacing?: string;
}> = ({x, y, text, at, size = 36, cps = 22, color, spacing = '0.1em'}) => {
  const frame = useCurrentFrame();
  const chars = Math.max(0, Math.floor(((frame - at) * cps) / 30));
  const shown = text.slice(0, chars);
  const done = chars >= text.length;
  const cursorOn = !done || frame < at + (text.length * 30) / cps + 12;
  const w = text.length * size * CHAR_W;
  if (frame < at) {
    return null;
  }
  return (
    <div
      style={{
        position: 'absolute',
        left: x - w / 2,
        top: y,
        width: w + size,
        fontFamily: pixel,
        fontSize: size,
        letterSpacing: spacing,
        textTransform: 'uppercase',
        color: color ?? T.ink,
        whiteSpace: 'pre',
      }}
    >
      {shown}
      {cursorOn ? (
        <span
          style={{
            color: T.good,
            // eased blink (binary toggles read mechanical - Remotion craft)
            opacity: (() => {
              const c = frame % 18;
              return c < 7 ? 1 : c < 10 ? 1 - (c - 7) / 3 : c < 15 ? 0 : (c - 15) / 3;
            })(),
          }}
        >
          _
        </span>
      ) : null}
    </div>
  );
};

// Rectangle outline that draws itself on clockwise from the top-left.
export const BPRect: React.FC<{
  x: number; // center
  y: number; // center
  w: number;
  h: number;
  at: number;
  dur?: number;
  color?: string;
  strokeW?: number;
  r?: number;
}> = ({x, y, w, h, at, dur = 16, color, strokeW = 2.5, r = 14}) => {
  const frame = useCurrentFrame();
  const perim = 2 * (w + h);
  const p = easeOut(frame, at, dur);
  return (
    <svg
      style={{position: 'absolute', left: x - w / 2 - 4, top: y - h / 2 - 4}}
      width={w + 8}
      height={h + 8}
    >
      <rect
        x={4}
        y={4}
        width={w}
        height={h}
        rx={r}
        fill="none"
        stroke={color ?? T.cardEdge}
        strokeWidth={strokeW}
        strokeDasharray={perim}
        strokeDashoffset={perim * (1 - p)}
        opacity={frame >= at ? 1 : 0}
      />
    </svg>
  );
};

// Straight dashed leader line that draws on, with an optional node dot
// that travels along it (loops) once drawn.
export const BPLeader: React.FC<{
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  at: number;
  dur?: number;
  node?: boolean;
  nodeStart?: number;
  color?: string;
}> = ({x1, y1, x2, y2, at, dur = 14, node = false, nodeStart = 0, color}) => {
  const frame = useCurrentFrame();
  const len = Math.hypot(x2 - x1, y2 - y1);
  const p = easeOut(frame, at, dur);
  const tp = node && frame > nodeStart ? ((frame - nodeStart) % 44) / 44 : -1;
  const nx = x1 + (x2 - x1) * tp;
  const ny = y1 + (y2 - y1) * tp;
  return (
    <>
      <svg style={{position: 'absolute', inset: 0}} width={1080} height={1920}>
        <line
          x1={x1}
          y1={y1}
          x2={x1 + (x2 - x1) * p}
          y2={y1 + (y2 - y1) * p}
          stroke={color ?? T.dim}
          strokeWidth={2.5}
          strokeDasharray="6 12"
          strokeLinecap="round"
          opacity={frame >= at ? 0.9 : 0}
        />
      </svg>
      {tp >= 0 && tp <= 1 ? (
        <div
          style={{
            position: 'absolute',
            left: nx - 7,
            top: ny - 7,
            width: 14,
            height: 14,
            borderRadius: 999,
            background: T.goodFill,
          }}
        />
      ) : null}
    </>
  );
};

// Horizontal measurement bracket |——————| with end ticks, draws from left.
export const BPMeasure: React.FC<{
  x: number; // left edge
  y: number;
  w: number;
  at: number;
  dur?: number;
  mint?: boolean;
}> = ({x, y, w, at, dur = 22, mint = false}) => {
  const frame = useCurrentFrame();
  const p = easeOut(frame, at, dur);
  const cw = w * p;
  const col = mint ? T.goodFill : T.dim;
  return (
    <svg style={{position: 'absolute', left: x, top: y - 20}} width={w + 6} height={40}>
      <line x1={1.5} y1={4} x2={1.5} y2={36} stroke={col} strokeWidth={3} opacity={frame >= at ? 1 : 0} />
      <line x1={1.5} y1={20} x2={1.5 + cw} y2={20} stroke={col} strokeWidth={mint ? 5 : 3} />
      {p >= 0.99 ? <line x1={1.5 + w} y1={4} x2={1.5 + w} y2={36} stroke={col} strokeWidth={3} /> : null}
    </svg>
  );
};

// Check / X strokes that draw on (blueprint verdict marks).
export const BPMark: React.FC<{
  x: number;
  y: number;
  at: number;
  kind: 'check' | 'x';
  size?: number;
}> = ({x, y, at, kind, size = 54}) => {
  const frame = useCurrentFrame();
  if (frame < at) {
    return null;
  }
  const p = easeOut(frame, at, 12);
  const s = size / 2;
  const col = kind === 'check' ? T.goodFill : T.muted;
  const l1 = kind === 'check' ? {x1: -s, y1: 0, x2: -s * 0.2, y2: s * 0.7} : {x1: -s, y1: -s, x2: s, y2: s};
  const l2 = kind === 'check' ? {x1: -s * 0.2, y1: s * 0.7, x2: s, y2: -s * 0.6} : {x1: s, y1: -s, x2: -s, y2: s};
  const p1 = Math.min(1, p * 2);
  const p2 = Math.max(0, p * 2 - 1);
  return (
    <svg style={{position: 'absolute', left: x - s - 4, top: y - s - 4}} width={size + 8} height={size + 8}>
      <line
        x1={l1.x1 + s + 4}
        y1={l1.y1 + s + 4}
        x2={l1.x1 + s + 4 + (l1.x2 - l1.x1) * p1}
        y2={l1.y1 + s + 4 + (l1.y2 - l1.y1) * p1}
        stroke={col}
        strokeWidth={5}
        strokeLinecap="round"
      />
      {p2 > 0 ? (
        <line
          x1={l2.x1 + s + 4}
          y1={l2.y1 + s + 4}
          x2={l2.x1 + s + 4 + (l2.x2 - l2.x1) * p2}
          y2={l2.y1 + s + 4 + (l2.y2 - l2.y1) * p2}
          stroke={col}
          strokeWidth={5}
          strokeLinecap="round"
        />
      ) : null}
    </svg>
  );
};

// Scanline phase sweep: a thin mint line sweeps down the content band;
// swap content at the midpoint of the sweep (pass `mid` to children via
// opacity toggling in the scene).
export const BPScan: React.FC<{at: number; dur?: number; y0?: number; y1?: number}> = ({
  at,
  dur = 10,
  y0 = 500,
  y1 = 1420,
}) => {
  const frame = useCurrentFrame();
  if (frame < at || frame > at + dur) {
    return null;
  }
  const p = (frame - at) / dur;
  const y = y0 + (y1 - y0) * p;
  return (
    <>
      <div
        style={{
          position: 'absolute',
          left: 90,
          top: y,
          width: 900,
          height: 3,
          background: T.goodFill,
          opacity: 0.85,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 90,
          top: y + 3,
          width: 900,
          height: 26,
          background: `linear-gradient(${T.goodFill}22, transparent)`,
        }}
      />
    </>
  );
};

// Scanline-gated visibility: content A shows before the sweep midpoint,
// content B after.
export const scanned = (frame: number, at: number, dur = 10): boolean =>
  frame >= at + dur / 2;

// Blinking mint node dot with a slow opacity pulse.
export const BPNode: React.FC<{x: number; y: number; at: number; size?: number}> = ({
  x,
  y,
  at,
  size = 16,
}) => {
  const frame = useCurrentFrame();
  const o = ease(frame, at, 8);
  const pulse = 0.65 + 0.35 * Math.sin((frame - at) * 0.18);
  return (
    <div
      style={{
        position: 'absolute',
        left: x - size / 2,
        top: y - size / 2,
        width: size,
        height: size,
        borderRadius: 999,
        background: T.goodFill,
        opacity: o * pulse,
      }}
    />
  );
};

// Bracket-masked title (Tony's [CALORIE BUR... reveal): brackets slide
// apart while the text un-clips between them.
export const BracketTitle: React.FC<{
  x: number;
  y: number;
  text: string;
  at: number;
  size?: number;
  color?: string;
}> = ({x, y, text, at, size = 34, color}) => {
  const frame = useCurrentFrame();
  const w = text.length * size * 0.9 + size;
  const p = easeOut(frame, at, 20);
  const half = (w / 2) * p;
  return (
    <div style={{position: 'absolute', left: x, top: y}}>
      <div
        style={{
          position: 'absolute',
          left: -half - size * 0.5,
          top: 0,
          fontFamily: pixel,
          fontSize: size,
          color: T.good,
          opacity: ease(frame, at, 6),
        }}
      >
        [
      </div>
      <div
        style={{
          position: 'absolute',
          left: half + size * 0.1,
          top: 0,
          fontFamily: pixel,
          fontSize: size,
          color: T.good,
          opacity: ease(frame, at, 6),
        }}
      >
        ]
      </div>
      <div
        style={{
          position: 'absolute',
          left: -w / 2,
          top: 0,
          width: w,
          textAlign: 'center',
          fontFamily: pixel,
          fontSize: size,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          whiteSpace: 'nowrap',
          color: color ?? T.muted,
          clipPath: `inset(0 ${50 - 50 * p}% 0 ${50 - 50 * p}%)`,
        }}
      >
        {text}
      </div>
    </div>
  );
};
