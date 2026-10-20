// Flow physical-metaphor lane: real simulated matter, rendered as brand shapes.
//
// This is Flow's originality lane. Neither reference creator uses code-driven
// physics and standard Remotion does not ship it, so a beat built here cannot
// read as an imitation of anybody. It also makes the fill-level metaphor
// honest: Flow used to fake "the jar fills up" with an interpolated rectangle,
// and a faked fill never has the weight or the comic timing of matter that
// actually lands.
//
// Everything is driven by lib/physics.ts, which simulates once at a fixed
// timestep and hands back an array of per-frame transforms. Components here
// do nothing but look up `frames[frame]` and draw, so they are as
// deterministic as an interpolate() call and safe under parallel render
// workers.
//
// SFX SYNC LAW: a bake knows the exact frame of every impact. Scenes should
// pull cues from `collisionsToSfx(bake, beatStart)` rather than hand-timing
// them; that is what makes a physical beat sound frame-perfect for free.

import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {
  bake,
  bakedAt,
  type Bake,
  type PourSpec,
  type ScaleSpec,
  type StackSpec,
} from '../lib/physics';
import {pixel} from '../fonts';
import {T} from '../theme';
import {ease} from '../lib/anim';

// ---------------------------------------------------------------------------
// Shared body renderer
// ---------------------------------------------------------------------------

const Token: React.FC<{
  x: number;
  y: number;
  a: number;
  r: number;
  accent?: boolean;
}> = ({x, y, a, r, accent = true}) => (
  <div
    style={{
      position: 'absolute',
      left: x - r,
      top: y - r,
      width: r * 2,
      height: r * 2,
      borderRadius: 999,
      background: accent ? T.goodFill : T.ghost,
      border: `2px solid ${accent ? T.good : T.cardEdge}`,
      transform: `rotate(${a}rad)`,
      boxShadow: accent ? `0 0 16px ${T.goodDeep}` : undefined,
    }}
  />
);

const Block: React.FC<{
  x: number;
  y: number;
  a: number;
  hw: number;
  hh: number;
  accent?: boolean;
  label?: string;
}> = ({x, y, a, hw, hh, accent = false, label}) => (
  <div
    style={{
      position: 'absolute',
      left: x - hw,
      top: y - hh,
      width: hw * 2,
      height: hh * 2,
      borderRadius: 10,
      background: accent ? T.goodFill : T.card,
      border: `3px solid ${accent ? T.good : T.cardEdge}`,
      transform: `rotate(${a}rad)`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: pixel,
      // 34, not 26: scenes usually sit inside a 0.86 scale wrapper, which
      // would push 26 down to 22 on screen, under the readability floor.
      fontSize: 34,
      letterSpacing: '0.04em',
      color: accent ? T.bg : T.ink,
      boxSizing: 'border-box',
    }}
  >
    {label}
  </div>
);

// ---------------------------------------------------------------------------
// PourFill: proportion as physical quantity
// ---------------------------------------------------------------------------
// "Fill-level metaphors are the signature move" per the flow skill. Here the
// tokens genuinely pour, collide, and stack to a level the viewer can read.

export const PourFill: React.FC<{
  spec: Omit<PourSpec, 'kind'>;
  seed: string;
  /** Frames. Defaults to the enclosing Sequence duration. */
  dur?: number;
  label?: string;
  /** Caps line under the vessel. */
  caption?: string;
  /** Draw the vessel outline. Off if the scene draws its own. */
  vessel?: boolean;
  /**
   * Frame the vessel appears. Defaults to shortly before the first token, so
   * an empty jar does not sit on screen telegraphing what is about to happen
   * (caught on the first Direction C render, where it hung there for 5s).
   */
  vesselAt?: number;
  /** Receives the bake so the caller can emit SFX from real collisions. */
  onBake?: (b: Bake) => void;
}> = ({spec, seed, dur, label, caption, vessel = true, vesselAt, onBake}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const total = dur ?? durationInFrames;
  const b = bake({
    spec: {kind: 'pour', ...spec},
    seed,
    fps,
    durationInFrames: total,
  });
  onBake?.(b);
  const bodies = bakedAt(b, frame);
  const {jar} = spec;
  const showAt = vesselAt ?? Math.max(0, spec.startFrame - 12);

  return (
    <>
      {vessel && frame >= showAt ? (
        <>
          {/* Vessel drawn as an open-topped blueprint frame. */}
          <div
            style={{
              position: 'absolute',
              left: jar.x - jar.w / 2 - 13,
              top: jar.y - jar.h / 2,
              width: jar.w + 26,
              height: jar.h + 13,
              borderLeft: `6px solid ${T.good}`,
              borderRight: `6px solid ${T.good}`,
              borderBottom: `6px solid ${T.good}`,
              borderRadius: '10px 10px 26px 26px',
              opacity: 0.85,
            }}
          />
          {label ? (
            <div
              style={{
                position: 'absolute',
                left: jar.x - jar.w / 2 - 120,
                width: jar.w + 240,
                top: jar.y - jar.h / 2 - 70,
                textAlign: 'center',
                fontFamily: pixel,
                fontSize: 36,
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                color: T.ink,
                opacity: ease(frame, showAt + 2, 10),
              }}
            >
              {label}
            </div>
          ) : null}
        </>
      ) : null}

      {bodies.map((body) =>
        body.kind === 'token' ? (
          <Token
            key={body.id}
            x={body.x}
            y={body.y}
            a={body.a}
            r={body.r ?? 18}
          />
        ) : null
      )}

      {caption ? (
        <div
          style={{
            position: 'absolute',
            left: 100,
            width: 830,
            top: jar.y + jar.h / 2 + 46,
            textAlign: 'center',
            fontFamily: pixel,
            fontSize: 30,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            color: T.muted,
            opacity: ease(frame, Math.max(0, b.settledFrame - 20), 12),
          }}
        >
          {caption}
        </div>
      ) : null}
    </>
  );
};

// ---------------------------------------------------------------------------
// TippingScale: a tradeoff you can watch resolve
// ---------------------------------------------------------------------------
// Weights land on each pan as they are spoken; the beam tips toward whichever
// side is genuinely heavier. Nothing about the outcome is animated by hand,
// so the visual argument cannot disagree with the stated one.

export const TippingScale: React.FC<{
  spec: Omit<ScaleSpec, 'kind'>;
  seed: string;
  dur?: number;
  leftLabel?: string;
  rightLabel?: string;
  /** Labels drawn on the blocks, in drop order per side. */
  leftItems?: string[];
  rightItems?: string[];
  onBake?: (b: Bake) => void;
}> = ({
  spec,
  seed,
  dur,
  leftLabel,
  rightLabel,
  leftItems = [],
  rightItems = [],
  onBake,
}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const total = dur ?? durationInFrames;
  const b = bake({
    spec: {kind: 'scale', ...spec},
    seed,
    fps,
    durationInFrames: total,
  });
  onBake?.(b);
  const bodies = bakedAt(b, frame);
  const {pivot, beamHalfWidth} = spec;

  const beam = bodies.find((x) => x.kind === 'beam');
  const blocks = bodies.filter((x) => x.kind === 'block');
  // Blocks are created left-side-first, then right, in spec order.
  const labelFor = (i: number): string | undefined => {
    if (i < spec.left.length) {
      return leftItems[i];
    }
    return rightItems[i - spec.left.length];
  };

  return (
    <>
      {/* Column */}
      <div
        style={{
          position: 'absolute',
          left: pivot.x - 7,
          top: pivot.y,
          width: 14,
          height: 300,
          background: T.cardEdge,
          borderRadius: 6,
        }}
      />
      {/* Beam */}
      {beam ? (
        <div
          style={{
            position: 'absolute',
            left: pivot.x - beamHalfWidth,
            top: pivot.y - 7,
            width: beamHalfWidth * 2,
            height: 14,
            background: T.good,
            borderRadius: 8,
            transform: `rotate(${beam.a}rad)`,
            transformOrigin: '50% 50%',
            boxShadow: `0 0 20px ${T.goodDeep}`,
          }}
        />
      ) : null}
      {/* Pivot */}
      <div
        style={{
          position: 'absolute',
          left: pivot.x - 17,
          top: pivot.y - 17,
          width: 34,
          height: 34,
          borderRadius: 999,
          background: T.ink,
        }}
      />
      {/* Pans, plus the hanger lines back to the beam ends. */}
      {bodies
        .filter((x) => x.kind === 'pan')
        .map((pan, i) => (
          <React.Fragment key={pan.id}>
            <div
              style={{
                position: 'absolute',
                left: pan.x - (pan.hw ?? 95),
                top: pan.y - (pan.hh ?? 8),
                width: (pan.hw ?? 95) * 2,
                height: (pan.hh ?? 8) * 2,
                background: T.ink,
                borderRadius: 6,
              }}
            />
            <div
              style={{
                position: 'absolute',
                left: pan.x - 1,
                top: pivot.y,
                width: 2,
                height: Math.max(0, pan.y - pivot.y),
                background: T.cardEdge,
              }}
            />
            {(i === 0 ? leftLabel : rightLabel) ? (
              <div
                style={{
                  position: 'absolute',
                  left: pan.x - 150,
                  width: 300,
                  top: pan.y + 26,
                  textAlign: 'center',
                  fontFamily: pixel,
                  fontSize: 28,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  color: T.muted,
                }}
              >
                {i === 0 ? leftLabel : rightLabel}
              </div>
            ) : null}
          </React.Fragment>
        ))}
      {/* Weights */}
      {blocks.map((blk, i) => (
        <Block
          key={blk.id}
          x={blk.x}
          y={blk.y}
          a={blk.a}
          hw={blk.hw ?? 30}
          hh={blk.hh ?? 30}
          accent={i >= spec.left.length}
          label={labelFor(i)}
        />
      ))}
    </>
  );
};

// ---------------------------------------------------------------------------
// BlockStack: accumulation you can feel
// ---------------------------------------------------------------------------
// For "these things add up" beats. Each named item drops on its spoken
// anchor and the tower genuinely settles, wobble included.

export const BlockStack: React.FC<{
  spec: Omit<StackSpec, 'kind'>;
  seed: string;
  dur?: number;
  labels?: string[];
  accentFrom?: number;
  onBake?: (b: Bake) => void;
}> = ({spec, seed, dur, labels = [], accentFrom = Infinity, onBake}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const total = dur ?? durationInFrames;
  const b = bake({
    spec: {kind: 'stack', ...spec},
    seed,
    fps,
    durationInFrames: total,
  });
  onBake?.(b);
  const bodies = bakedAt(b, frame);
  const blocks = bodies.filter((x) => x.kind === 'block');
  // The ground line appears just before the first block, not from frame 0:
  // a bare rule sitting on an empty board reads as a stray element.
  const groundAt = Math.max(
    0,
    Math.min(...spec.blocks.map((x) => x.frame)) - 8
  );

  return (
    <>
      {frame >= groundAt ? (
        <div
          style={{
            position: 'absolute',
            left: 100,
            width: 830,
            top: spec.groundY,
            height: 5,
            background: T.cardEdge,
          }}
        />
      ) : null}
      {blocks.map((blk, i) => (
        <Block
          key={blk.id}
          x={blk.x}
          y={blk.y}
          a={blk.a}
          hw={blk.hw ?? 40}
          hh={blk.hh ?? 30}
          accent={i >= accentFrom}
          label={labels[i]}
        />
      ))}
    </>
  );
};
