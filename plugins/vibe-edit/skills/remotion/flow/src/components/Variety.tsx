import React from 'react';
import {useCurrentFrame, useVideoConfig, interpolate, Easing} from 'remotion';
import {Check, X, FlagTriangleRight} from 'lucide-react';
import {ease, easeOut, fadeUp, popStyle} from '../lib/anim';
import {pixel} from '../fonts';
import {T, tone, Tone} from '../theme';

// Big number that counts up. For stats, subscriber counts, percentages.
export const Counter: React.FC<{
  x: number;
  y: number;
  value: number;
  delay?: number;
  dur?: number;
  size?: number;
  prefix?: string;
  suffix?: string;
  toneName?: Tone;
  label?: string;
}> = ({x, y, value, delay = 0, dur = 45, size = 150, prefix = '', suffix = '', toneName = 'good', label}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = easeOut(frame, delay, dur);
  const n = Math.round(value * p);
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: 'translate(-50%, -50%)',
        textAlign: 'center',
        fontFamily: pixel,
      }}
    >
      <div
        style={{
          fontSize: size,
          letterSpacing: '0.06em',
          color: tone(toneName),
          opacity: ease(frame, delay, 8),
        }}
      >
        {prefix}
        {n.toLocaleString('en-US')}
        {suffix}
      </div>
      {label ? (
        <div
          style={{
            fontSize: Math.max(30, size * 0.24),
            letterSpacing: '0.16em',
            textTransform: 'uppercase',
            color: T.muted,
            marginTop: 10,
            ...fadeUp(frame, fps, delay + 10, 14),
          }}
        >
          {label}
        </div>
      ) : null}
    </div>
  );
};

// Horizontal progress meter that fills to pct (0..1), with % readout.
export const Meter: React.FC<{
  x: number;
  y: number;
  w: number;
  pct: number;
  delay?: number;
  dur?: number;
  h?: number;
  label?: string;
  toneName?: Tone;
}> = ({x, y, w, pct, delay = 0, dur = 40, h = 46, label, toneName = 'good'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = easeOut(frame, delay + 4, dur) * pct;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, fontFamily: pixel}}>
      {label ? (
        <div
          style={{
            fontSize: 32,
            letterSpacing: '0.16em',
            textTransform: 'uppercase',
            color: T.muted,
            marginBottom: 18,
            ...fadeUp(frame, fps, delay, 12),
          }}
        >
          {label}
        </div>
      ) : null}
      <div style={{display: 'flex', alignItems: 'center', gap: 26}}>
        <div
          style={{
            flex: 1,
            height: h,
            borderRadius: h / 2,
            background: T.ghost,
            overflow: 'hidden',
            opacity: ease(frame, delay, 8),
          }}
        >
          <div
            style={{
              width: `${p * 100}%`,
              height: '100%',
              borderRadius: h / 2,
              background: tone(toneName) === T.good ? T.goodFill : tone(toneName),
            }}
          />
        </div>
        <div style={{fontSize: 46, color: tone(toneName), minWidth: 130, textAlign: 'right'}}>
          {Math.round(p * 100)}%
        </div>
      </div>
    </div>
  );
};

export type CheckItem = {t: string; ok?: boolean};

// Staggered checklist. ok=true gets an accent check, ok=false a muted X.
// Negativity is carried by the X mark, not by red (brand palettes).
export const Checklist: React.FC<{
  x: number;
  y: number;
  items: CheckItem[];
  delay?: number;
  gap?: number;
  size?: number;
  stagger?: number;
}> = ({x, y, items, delay = 0, gap = 34, size = 40, stagger = 14}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: 'translateX(-50%)',
        display: 'flex',
        flexDirection: 'column',
        gap,
        fontFamily: pixel,
      }}
    >
      {items.map((it, i) => (
        <div
          key={i}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 24,
            ...fadeUp(frame, fps, delay + i * stagger, 20),
          }}
        >
          {it.ok === false ? (
            <X size={size * 1.05} color={T.bad} strokeWidth={3} />
          ) : (
            <Check size={size * 1.05} color={T.good} strokeWidth={3} />
          )}
          <span
            style={{
              fontSize: size,
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: it.ok === false ? T.muted : T.ink,
              whiteSpace: 'nowrap',
            }}
          >
            {it.t}
          </span>
        </div>
      ))}
    </div>
  );
};

// A pictogram that travels from fromX to toX with a gentle bob, along a
// dashed track, with an optional finish flag that pops on arrival.
// Pass any lucide icon as `icon` (e.g. PersonStanding, Rocket, Car).
export const Mover: React.FC<{
  fromX: number;
  toX: number;
  y: number;
  icon: React.ReactNode;
  delay?: number;
  dur?: number;
  flag?: boolean;
  bob?: number;
}> = ({fromX, toX, y, icon, delay = 0, dur = 50, flag = true, bob = 7}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = interpolate(frame, [delay, delay + dur], [0, 1], {
    easing: Easing.inOut(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const cx = fromX + (toX - fromX) * p;
  const bobY = Math.sin(frame * 0.55) * bob * (p > 0 && p < 1 ? 1 : 0.3);
  const arrived = p >= 0.99;
  return (
    <>
      <svg
        style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}
        width="100%"
        height="100%"
      >
        <line
          x1={fromX}
          y1={y + 52}
          x2={toX + 40}
          y2={y + 52}
          stroke={T.axis}
          strokeWidth={3}
          strokeDasharray="3 16"
          strokeLinecap="round"
          opacity={ease(frame, delay, 10)}
        />
      </svg>
      {flag ? (
        <div
          style={{
            position: 'absolute',
            left: toX + 46,
            top: y - 6,
            transform: 'translate(-50%, -50%)',
            ...popStyle(frame, fps, arrived ? frame - 1 : delay + dur),
          }}
        >
          <FlagTriangleRight size={54} color={T.good} strokeWidth={2.4} />
        </div>
      ) : null}
      <div
        style={{
          position: 'absolute',
          left: cx,
          top: y + bobY,
          transform: 'translate(-50%, -50%)',
          opacity: ease(frame, delay, 8),
        }}
      >
        {icon}
      </div>
    </>
  );
};
