import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {fadeUp} from '../lib/anim';
import {pixel} from '../fonts';
import {tone, Tone} from '../theme';

export type Seg = {t: string; tone?: Tone};
export type LockLine = {segs: Seg[]; size?: number};

// The signature text element: pixel-mono ALL CAPS, letterspaced,
// emphasis = recolor single tokens inside an otherwise gray/ink line.
export const Lockup: React.FC<{
  y: number;
  lines: LockLine[];
  size?: number;
  delay?: number;
  stagger?: number;
}> = ({y, lines, size = 88, delay = 0, stagger = 7}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div
      style={{
        position: 'absolute',
        top: y,
        left: 0,
        right: 0,
        textAlign: 'center',
        fontFamily: pixel,
        textTransform: 'uppercase',
      }}
    >
      {lines.map((ln, li) => {
        const s = ln.size ?? size;
        return (
          <div
            key={li}
            style={{
              fontSize: s,
              letterSpacing: '0.12em',
              lineHeight: 1.2,
              marginTop: li === 0 ? 0 : Math.round(s * 0.42),
              ...fadeUp(frame, fps, delay + li * stagger, 26),
            }}
          >
            {ln.segs.map((sg, si) => (
              <span key={si} style={{color: tone(sg.tone)}}>
                {sg.t}
              </span>
            ))}
          </div>
        );
      })}
    </div>
  );
};
