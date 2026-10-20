// Flow evidence lane: footage and real artifacts used as proof.
//
// WHAT THIS IS FOR
// Every other Flow component ILLUSTRATES a claim. These components SHOW it.
// A screen recording of the thing actually working, a real generated image,
// an official logo on the spoken brand name. Before this file, a Flow master
// overlay could never carry a piece of real evidence; the whole system was
// designed graphics only.
//
// PROVENANCE AND LICENSING BOUNDARY
// The mechanics are derived from the Remotion Recorder
// (https://github.com/remotion-dev/recorder, pinned at commit
// b722f625b7fcb691b8b283484dfb07cf6500985a). That repository ships NO
// LICENSE file and its package.json declares no license; its README points
// at the Remotion license, which is free for individuals and companies up to
// three people (the terms Flow already operates under) but is not an open
// source grant. Because reuse is therefore not clearly permitted, NOTHING
// here is copied. The Recorder was read as a reference for which mechanics
// matter -- word-level caption timing, claim-synced B-roll, screen-recording
// dress-up, layout switching between face and proof -- and each one is
// reimplemented against Flow's own architecture. Flow keeps MasterTrack,
// Departure Mono, the palette proxy and the safe-zone laws; none of the
// Recorder's identity, layout engine or component code is present.
// See .claude/skills/flow/references/upstream-provenance.md.
//
// THE RULE THIS LANE MUST NEVER BREAK
// Evidence is only evidence if it is real. If there is no genuine artifact
// for a claim, the beat does not get this lane. A mocked-up screenshot of a
// product is a fabrication, and it also violates the official-logo rule.
// The creative-lane router enforces this with `hasEvidenceAsset`.

import React from 'react';
import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {pixel} from '../fonts';
import {T} from '../theme';
import {ease, easeOut, popStyle} from '../lib/anim';
import {Drift} from './Motion';

const clamp = {
  extrapolateLeft: 'clamp' as const,
  extrapolateRight: 'clamp' as const,
};

export const SAFE = {
  left: 100,
  right: 930,
  top: 220,
  /** Nothing readable below this: platform caption lane + control rail. */
  bottom: 1500,
  centerX: 540,
} as const;

// ---------------------------------------------------------------------------
// Word-level captions
// ---------------------------------------------------------------------------
// The Auphonic word transcript is already Flow's timing authority for beat
// placement. This turns the same array into on-screen phrase cards, which is
// the one Recorder mechanic with the highest lift for Payton's format.
//
// DELIBERATE DIVERGENCE FROM THE REFERENCE GRAMMAR: reference creators park
// captions in the bottom third. Flow may not -- the bottom 420px is the
// platform's own caption and control lane, so anything there gets covered.
// Flow captions sit just above that boundary instead.

export type Word = {w: string; s: number; e: number};

export type CaptionCard = {
  words: Word[];
  /** Seconds, absolute in the finished video. */
  start: number;
  end: number;
  text: string;
};

export type GroupOptions = {
  maxWords?: number;
  maxChars?: number;
  /** Split when the gap between words exceeds this (seconds). */
  gap?: number;
  /** Hard ceiling on how long one card may sit (seconds). */
  maxDur?: number;
};

/**
 * Group word timings into short phrase cards. Pure, deterministic, and
 * exported so a beat map can be checked without rendering anything.
 */
export const groupWords = (
  words: Word[],
  opts: GroupOptions = {}
): CaptionCard[] => {
  const {maxWords = 4, maxChars = 26, gap = 0.42, maxDur = 2.2} = opts;
  const cards: CaptionCard[] = [];
  let cur: Word[] = [];

  const flush = () => {
    if (!cur.length) {
      return;
    }
    cards.push({
      words: cur,
      start: cur[0].s,
      end: cur[cur.length - 1].e,
      text: cur.map((w) => w.w).join(' '),
    });
    cur = [];
  };

  for (let i = 0; i < words.length; i++) {
    const w = words[i];
    const prev = cur[cur.length - 1];
    const wouldChars =
      cur.reduce((n, x) => n + x.w.length + 1, 0) + w.w.length;
    const tooLong = cur.length && w.e - cur[0].s > maxDur;
    const bigGap = prev && w.s - prev.e > gap;
    if (
      cur.length >= maxWords ||
      wouldChars > maxChars ||
      tooLong ||
      bigGap
    ) {
      flush();
    }
    cur.push(w);
    // Sentence-final punctuation always closes a card: it is a real boundary.
    if (/[.!?]$/.test(w.w)) {
      flush();
    }
  }
  flush();
  return cards;
};

export type Emphasis = {
  /** Case-insensitive, punctuation-insensitive word match. */
  word: string;
  kind?: 'accent' | 'strike';
};

const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9']/g, '');

export const WordCaptions: React.FC<{
  cards: CaptionCard[];
  /** Seconds. Absolute card times are converted to beat-local frames. */
  beatStart: number;
  y?: number;
  size?: number;
  emphasis?: Emphasis[];
  /** Hide the pill and render bare caps type. */
  bare?: boolean;
}> = ({cards, beatStart, y = 1330, size = 40, emphasis = [], bare = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = beatStart + frame / fps;

  const active = cards.find((c) => t >= c.start - 0.06 && t < c.end + 0.22);
  if (!active) {
    return null;
  }

  const localIn = Math.round((active.start - 0.06 - beatStart) * fps);
  const o = ease(frame, localIn, 3);
  const emap = new Map(emphasis.map((e) => [norm(e.word), e.kind ?? 'accent']));

  return (
    <div
      style={{
        position: 'absolute',
        left: SAFE.left,
        width: SAFE.right - SAFE.left,
        top: y,
        display: 'flex',
        justifyContent: 'center',
        opacity: o,
      }}
    >
      <div
        style={{
          fontFamily: pixel,
          fontSize: size,
          letterSpacing: '0.06em',
          textTransform: 'uppercase',
          textAlign: 'center',
          lineHeight: 1.25,
          color: T.ink,
          padding: bare ? 0 : '16px 28px',
          borderRadius: bare ? 0 : 18,
          background: bare ? 'transparent' : 'rgba(10,11,11,0.78)',
          border: bare ? 'none' : `2px solid ${T.cardEdge}`,
          maxWidth: SAFE.right - SAFE.left,
          transform: `translateY(${(1 - o) * 8}px)`,
        }}
      >
        {active.words.map((w, i) => {
          const kind = emap.get(norm(w.w));
          return (
            <span
              key={`${w.s}-${i}`}
              style={{
                color: kind === 'accent' ? T.good : T.ink,
                textDecoration:
                  kind === 'strike' ? 'line-through' : undefined,
                textDecorationThickness: kind === 'strike' ? 4 : undefined,
                marginRight: 12,
                whiteSpace: 'nowrap',
              }}
            >
              {w.w}
            </span>
          );
        })}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Full-bleed evidence
// ---------------------------------------------------------------------------
// Opaque and edge to edge. Reference grammar: when the proof appears it
// REPLACES the frame rather than floating beside the face, so the viewer
// reads it as "this is the thing" rather than "here is a decoration".

export type EvidenceSource =
  | {kind: 'image'; src: string}
  | {kind: 'video'; src: string; startFrom?: number; muted?: boolean};

const SourceLayer: React.FC<{
  source: EvidenceSource;
  fit?: 'cover' | 'contain';
}> = ({source, fit = 'cover'}) => {
  const style: React.CSSProperties = {
    width: '100%',
    height: '100%',
    objectFit: fit,
  };
  if (source.kind === 'image') {
    return <Img src={source.src} style={style} />;
  }
  return (
    <OffthreadVideo
      src={source.src}
      startFrom={source.startFrom ?? 0}
      muted={source.muted ?? true}
      style={style}
    />
  );
};

export const EvidenceBeat: React.FC<{
  source: EvidenceSource;
  /** Idle drift so a still asset is never frozen. Set 0 to disable. */
  drift?: number;
  panX?: number;
  panY?: number;
  fit?: 'cover' | 'contain';
  /** Darkens the asset so overlaid type stays readable. */
  scrim?: number;
  children?: React.ReactNode;
}> = ({source, drift = 0.05, panX = 0, panY = -18, fit = 'cover', scrim = 0, children}) => {
  return (
    <AbsoluteFill style={{backgroundColor: T.bg}}>
      {drift > 0 ? (
        <Drift grow={drift} panX={panX} panY={panY}>
          <SourceLayer source={source} fit={fit} />
        </Drift>
      ) : (
        <SourceLayer source={source} fit={fit} />
      )}
      {scrim > 0 ? (
        <AbsoluteFill
          style={{backgroundColor: `rgba(10,11,11,${Math.min(0.85, scrim)})`}}
        />
      ) : null}
      {children}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Screen callout: make an abstract claim concrete on real footage
// ---------------------------------------------------------------------------
// The reference device is a rectangle drawn over the part of the UI that
// matters, sometimes with a label. Flow draws it in the blueprint voice
// (accent stroke, corner ticks, caps label) so it belongs to this system
// rather than looking like a screen-recorder watermark.

export const ScreenCallout: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  at: number;
  dur?: number;
  label?: string;
  color?: string;
  /** Label above or below the box. */
  labelSide?: 'top' | 'bottom';
}> = ({x, y, w, h, at, dur = 12, label, color, labelSide = 'top'}) => {
  const frame = useCurrentFrame();
  if (frame < at) {
    return null;
  }
  const p = easeOut(frame, at, dur);
  if (p <= 0) {
    return null;
  }
  const stroke = color ?? T.good;
  const tick = 22;
  // Box draws on by growing from the centre, then the corner ticks land.
  const cw = w * p;
  const ch = h * p;
  const left = x - cw / 2;
  const top = y - ch / 2;
  const ticksOn = p > 0.75;

  return (
    <>
      <div
        style={{
          position: 'absolute',
          left,
          top,
          width: cw,
          height: ch,
          border: `4px solid ${stroke}`,
          borderRadius: 8,
          boxShadow: `0 0 26px ${stroke}55`,
        }}
      />
      {ticksOn
        ? [
            [left - 2, top - 2, 1, 1],
            [left + cw - tick + 2, top - 2, -1, 1],
            [left - 2, top + ch - tick + 2, 1, -1],
            [left + cw - tick + 2, top + ch - tick + 2, -1, -1],
          ].map(([lx, ly], i) => (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: lx as number,
                top: ly as number,
                width: tick,
                height: tick,
                border: `4px solid ${stroke}`,
                borderRadius: 4,
                opacity: 0.9,
              }}
            />
          ))
        : null}
      {label && p > 0.6 ? (
        <div
          style={{
            position: 'absolute',
            left: x,
            top: labelSide === 'top' ? top - 56 : top + ch + 18,
            transform: 'translateX(-50%)',
            fontFamily: pixel,
            fontSize: 28,
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            color: T.bg,
            background: stroke,
            padding: '8px 16px',
            borderRadius: 8,
            whiteSpace: 'nowrap',
          }}
        >
          {label}
        </div>
      ) : null}
    </>
  );
};

// ---------------------------------------------------------------------------
// Crop / zoom into a region of an asset
// ---------------------------------------------------------------------------
// Screen recordings are almost always too wide to read on a phone. This
// pushes into the region that carries the claim, on a deterministic ramp.

export const CropZoom: React.FC<{
  children: React.ReactNode;
  /** Region of interest in composition coordinates. */
  focus: {x: number; y: number; scale: number};
  at: number;
  dur?: number;
  /** Hold the zoom, or come back out at `out`. */
  out?: number;
  outDur?: number;
}> = ({children, focus, at, dur = 22, out, outDur = 18}) => {
  const frame = useCurrentFrame();
  const inP = interpolate(frame, [at, at + dur], [0, 1], clamp);
  const outP =
    out === undefined
      ? 0
      : interpolate(frame, [out, out + outDur], [0, 1], clamp);
  const p = Math.max(0, inP - outP);
  const s = 1 + (focus.scale - 1) * p;
  const tx = (SAFE.centerX - focus.x) * p;
  const ty = (960 - focus.y) * p;
  return (
    <AbsoluteFill
      style={{
        transform: `scale(${s}) translate(${tx / s}px, ${ty / s}px)`,
        transformOrigin: '540px 960px',
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Device frame
// ---------------------------------------------------------------------------
// A reusable bezel so product UI reads as "here is the app" rather than
// "here is a raw screenshot". Drawn, not photographed, so it inherits the
// palette and never carries another company's industrial design.

export const DeviceFrame: React.FC<{
  x?: number;
  y?: number;
  w?: number;
  h?: number;
  at?: number;
  chrome?: 'phone' | 'browser';
  /** Caption strip under the device, e.g. what the asset is. */
  caption?: string;
  children: React.ReactNode;
}> = ({
  x = SAFE.centerX,
  y = 880,
  w = 560,
  h = 1000,
  at = 0,
  chrome = 'phone',
  caption,
  children,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const bezel = chrome === 'phone' ? 18 : 12;
  const barH = chrome === 'browser' ? 54 : 0;

  return (
    <div
      style={{
        position: 'absolute',
        left: x - w / 2,
        top: y - h / 2,
        width: w,
        height: h,
        ...popStyle(frame, fps, at),
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: chrome === 'phone' ? 52 : 20,
          background: T.card,
          border: `${bezel}px solid ${T.ghost}`,
          boxShadow: T.shadow,
          overflow: 'hidden',
        }}
      >
        {chrome === 'browser' ? (
          <div
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              top: 0,
              height: barH,
              background: T.termBg,
              borderBottom: `2px solid ${T.termEdge}`,
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              paddingLeft: 18,
            }}
          >
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                style={{
                  width: 14,
                  height: 14,
                  borderRadius: 999,
                  background: T.termDim,
                  opacity: 0.7,
                }}
              />
            ))}
          </div>
        ) : null}
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: barH,
            bottom: 0,
            overflow: 'hidden',
          }}
        >
          {children}
        </div>
        {chrome === 'phone' ? (
          <div
            style={{
              position: 'absolute',
              left: '50%',
              top: 14,
              transform: 'translateX(-50%)',
              width: 132,
              height: 26,
              borderRadius: 999,
              background: T.ghost,
            }}
          />
        ) : null}
      </div>
      {caption ? (
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: h + 24,
            textAlign: 'center',
            fontFamily: pixel,
            fontSize: 28,
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            color: T.muted,
            opacity: ease(frame, at + 8, 8),
          }}
        >
          {caption}
        </div>
      ) : null}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Claim-synced asset switching
// ---------------------------------------------------------------------------
// Reference grammar: cut on the NOUN. Say the brand, show the brand. This
// takes a list of {at, node} in beat-local frames and shows exactly one,
// hard-cutting between them so the switch lands on the spoken word.

export type AssetCut = {
  /** Beat-local frame this asset takes over on. */
  at: number;
  node: React.ReactNode;
  /** The spoken word this cut is anchored to, recorded for QA. */
  anchor?: string;
};

export const AssetSwitch: React.FC<{
  cuts: AssetCut[];
  /** Frames of cross-dissolve. 0 (default) is a hard cut, which is correct. */
  blend?: number;
}> = ({cuts, blend = 0}) => {
  const frame = useCurrentFrame();
  const ordered = [...cuts].sort((a, b) => a.at - b.at);
  let idx = -1;
  for (let i = 0; i < ordered.length; i++) {
    if (frame >= ordered[i].at) {
      idx = i;
    }
  }
  if (idx < 0) {
    return null;
  }
  if (blend <= 0) {
    return <AbsoluteFill>{ordered[idx].node}</AbsoluteFill>;
  }
  const o = interpolate(
    frame,
    [ordered[idx].at, ordered[idx].at + blend],
    [0, 1],
    clamp
  );
  return (
    <AbsoluteFill>
      {idx > 0 ? (
        <AbsoluteFill style={{opacity: 1 - o}}>{ordered[idx - 1].node}</AbsoluteFill>
      ) : null}
      <AbsoluteFill style={{opacity: o}}>{ordered[idx].node}</AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Layout switching: face / proof / board
// ---------------------------------------------------------------------------
// The Recorder's most transferable structural idea: one timeline that
// reassigns the frame between the presenter, the proof, and the designed
// board, rather than three separate edits.
//
// FLOW CONSTRAINT PRESERVED: 'face' does NOT mean Flow renders Payton. In a
// master overlay, 'face' means this stretch is fully transparent so his
// actual footage shows through untouched. Hook, pivot and verdict stay his.

export type LayoutMode = 'face' | 'proof' | 'board' | 'split';

export type LayoutSegment = {
  /** Beat-local frame this mode begins. */
  at: number;
  mode: LayoutMode;
  proof?: React.ReactNode;
  board?: React.ReactNode;
};

export const LayoutSwitch: React.FC<{segments: LayoutSegment[]}> = ({
  segments,
}) => {
  const frame = useCurrentFrame();
  const ordered = [...segments].sort((a, b) => a.at - b.at);
  let cur: LayoutSegment | null = null;
  for (const s of ordered) {
    if (frame >= s.at) {
      cur = s;
    }
  }
  if (!cur || cur.mode === 'face') {
    return null; // transparent: the talking head owns the frame
  }

  // IMPORTANT: the active segment is wrapped in a Sequence so its children
  // see SEGMENT-LOCAL frames (0 = the frame this layout took over). Without
  // this, a segment's internal anchors are measured against the whole
  // composition, so everything inside it has already "happened" the moment
  // the segment appears: on the first Direction B render every credit chip
  // popped in simultaneously instead of accumulating on its spoken word, and
  // a quoted line showed up 2.8 seconds before it was said. Segment children
  // should therefore express their anchors as S(spokenTime - segment.at).
  const body =
    cur.mode === 'proof' ? (
      <AbsoluteFill>{cur.proof}</AbsoluteFill>
    ) : cur.mode === 'board' ? (
      <AbsoluteFill>{cur.board}</AbsoluteFill>
    ) : (
      // 'split': proof on top, board beneath, both inside the safe zone.
      <AbsoluteFill>
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: 0,
            height: 1000,
            overflow: 'hidden',
          }}
        >
          {cur.proof}
        </div>
        <div
          style={{position: 'absolute', left: 0, right: 0, top: 1000, bottom: 0}}
        >
          {cur.board}
        </div>
      </AbsoluteFill>
    );

  return (
    <Sequence from={cur.at} layout="none">
      {body}
    </Sequence>
  );
};

// ---------------------------------------------------------------------------
// Big-number reveal
// ---------------------------------------------------------------------------
// Typographic scale AS the whole argument, no chart. Flow already has
// Counter for a count-up; this is the other thing: a flat, held figure.

export const BigFigure: React.FC<{
  value: string;
  label?: string;
  y?: number;
  at?: number;
  size?: number;
}> = ({value, label, y = 820, at = 0, size = 190}) => {
  const frame = useCurrentFrame();
  const p = easeOut(frame, at, 10);
  return (
    <>
      <div
        style={{
          position: 'absolute',
          left: SAFE.left,
          width: SAFE.right - SAFE.left,
          top: y,
          textAlign: 'center',
          fontFamily: pixel,
          fontSize: size,
          lineHeight: 1,
          letterSpacing: '0.02em',
          color: T.good,
          opacity: p,
          transform: `scale(${0.93 + p * 0.07})`,
          transformOrigin: '50% 50%',
        }}
      >
        {value}
      </div>
      {label ? (
        <div
          style={{
            position: 'absolute',
            left: SAFE.left,
            width: SAFE.right - SAFE.left,
            top: y + size + 26,
            textAlign: 'center',
            fontFamily: pixel,
            fontSize: 34,
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            color: T.muted,
            opacity: ease(frame, at + 6, 8),
          }}
        >
          {label}
        </div>
      ) : null}
    </>
  );
};
