import React from 'react';
import {useCurrentFrame} from 'remotion';
import {ease, easeOut} from '../lib/anim';
import {pixel} from '../fonts';
import {T} from '../theme';

export type BarValue = {v: number; label?: string}; // v in 0..1

// Bar chart body: gray ghost columns to full height, colored bars grow
// up TOGETHER with ease-out, tone-on-tone rotated labels inside bars.
// x,y = origin (bottom-left of plot area), matching <Axes>.
export const Bars: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  values: BarValue[];
  tone?: 'good' | 'bad';
  delay?: number;
  grow?: number;
  ghost?: boolean;
  gap?: number;
}> = ({
  x,
  y,
  w,
  h,
  values,
  tone = 'good',
  delay = 0,
  grow = 34,
  ghost = true,
  gap = 16,
}) => {
  const frame = useCurrentFrame();
  const n = values.length;
  const bw = (w - gap * (n - 1)) / n;
  const fill = tone === 'good' ? T.goodFill : T.badFill;
  const deep = tone === 'good' ? T.goodDeep : T.badDeep;
  const ghostO = ease(frame, delay, 10);
  const g = easeOut(frame, delay + 6, grow);
  const labelO = ease(frame, delay + grow, 10);
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y - h,
        width: w,
        height: h,
      }}
    >
      {values.map((val, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: i * (bw + gap),
            bottom: 0,
            width: bw,
            height: h,
          }}
        >
          {ghost ? (
            <div
              style={{
                position: 'absolute',
                bottom: 0,
                width: '100%',
                height: '100%',
                background: T.ghost,
                borderRadius: '5px 5px 0 0',
                opacity: ghostO,
              }}
            />
          ) : null}
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              width: '100%',
              height: `${val.v * g * 100}%`,
              background: fill,
              borderRadius: '5px 5px 0 0',
            }}
          />
          {val.label ? (
            <div
              style={{
                position: 'absolute',
                left: '50%',
                bottom: 18,
                transform: 'translateX(-50%) rotate(180deg)',
                writingMode: 'vertical-rl',
                fontFamily: pixel,
                fontSize: Math.max(26, Math.min(30, bw * 0.4)),
                letterSpacing: '0.14em',
                color: deep,
                opacity: labelO,
              }}
            >
              {val.label}
            </div>
          ) : null}
        </div>
      ))}
    </div>
  );
};
