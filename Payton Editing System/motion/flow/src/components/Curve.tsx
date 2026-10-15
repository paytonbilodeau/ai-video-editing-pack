import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {evolvePath, getLength, getPointAtLength} from '@remotion/paths';
import {ease, fadeUp} from '../lib/anim';
import {pixel} from '../fonts';
import {T} from '../theme';

// Thick round-cap data line that draws itself on, with an optional
// pixel-caps annotation appearing at the end point ("+60%").
export const Curve: React.FC<{
  d: string;
  delay: number;
  drawDur?: number;
  color?: string;
  width?: number;
  endLabel?: string;
  endLabelDx?: number;
  endLabelDy?: number;
  endLabelTone?: string;
}> = ({
  d,
  delay,
  drawDur = 40,
  color = T.good,
  width = 13,
  endLabel,
  endLabelDx = 0,
  endLabelDy = -44,
  endLabelTone,
}) => {
  const frame = useCurrentFrame();
  const {fps, width: W, height: H} = useVideoConfig();
  const progress = ease(frame, delay, drawDur);
  const evolution = evolvePath(progress, d);
  const L = getLength(d);
  const end = getPointAtLength(d, L);
  if (!end) throw new Error('Curve requires a non-empty valid path.');
  return (
    <>
      <svg
        width={W}
        height={H}
        viewBox={`0 0 ${W} ${H}`}
        style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}
      >
        <path
          d={d}
          fill="none"
          stroke={color}
          strokeWidth={width}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={evolution.strokeDasharray}
          strokeDashoffset={evolution.strokeDashoffset}
        />
      </svg>
      {endLabel ? (
        <div
          style={{
            position: 'absolute',
            left: end.x + endLabelDx,
            top: end.y + endLabelDy,
            transform: 'translate(-50%, -50%)',
            fontFamily: pixel,
            fontSize: 34,
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            color: endLabelTone ?? T.ink,
            whiteSpace: 'nowrap',
            opacity: ease(frame, delay + drawDur - 6, 10),
          }}
        >
          {endLabel}
        </div>
      ) : null}
    </>
  );
};
