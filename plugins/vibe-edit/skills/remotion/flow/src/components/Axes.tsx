import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {evolvePath} from '@remotion/paths';
import {ease, fadeUp} from '../lib/anim';
import {pixel} from '../fonts';
import {T} from '../theme';

// Chart axes: thin gray lines drawing on, small arrowheads, rotated
// letterspaced y-label, tick labels at the x extremes.
// x,y = the ORIGIN (bottom-left corner of the plot area).
export const Axes: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  delay?: number;
  drawDur?: number;
  yLabel?: string;
  xLabel?: string;
  x0?: string;
  x1?: string;
}> = ({x, y, w, h, delay = 0, drawDur = 16, yLabel, xLabel, x0, x1}) => {
  const frame = useCurrentFrame();
  const {fps, width: W, height: H} = useVideoConfig();
  const progress = ease(frame, delay, drawDur);
  const yPath = `M ${x} ${y} L ${x} ${y - h}`;
  const xPath = `M ${x} ${y} L ${x + w} ${y}`;
  const yEvo = evolvePath(progress, yPath);
  const xEvo = evolvePath(progress, xPath);
  const headOpacity = progress > 0.95 ? ease(frame, delay + drawDur - 2, 6) : 0;
  const labelStyle: React.CSSProperties = {
    fontFamily: pixel,
    textTransform: 'uppercase',
    color: T.muted,
    whiteSpace: 'nowrap',
  };
  return (
    <>
      <svg
        width={W}
        height={H}
        viewBox={`0 0 ${W} ${H}`}
        style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}
      >
        <path
          d={yPath}
          stroke={T.axis}
          strokeWidth={3}
          strokeLinecap="round"
          fill="none"
          strokeDasharray={yEvo.strokeDasharray}
          strokeDashoffset={yEvo.strokeDashoffset}
        />
        <path
          d={xPath}
          stroke={T.axis}
          strokeWidth={3}
          strokeLinecap="round"
          fill="none"
          strokeDasharray={xEvo.strokeDasharray}
          strokeDashoffset={xEvo.strokeDashoffset}
        />
        <g opacity={headOpacity}>
          <path
            d={`M ${x} ${y - h - 4} l -9 15 l 18 0 Z`}
            fill={T.axis}
          />
          <path
            d={`M ${x + w + 4} ${y} l -15 -9 l 0 18 Z`}
            fill={T.axis}
          />
        </g>
      </svg>
      {yLabel ? (
        <div
          style={{
            position: 'absolute',
            left: x - 58,
            top: y - h / 2,
            transform: 'translate(-50%, -50%) rotate(-90deg)',
            fontSize: 28,
            letterSpacing: '0.32em',
            ...labelStyle,
            opacity: ease(frame, delay + drawDur - 2, 10),
          }}
        >
          {yLabel}
        </div>
      ) : null}
      {xLabel ? (
        <div
          style={{
            position: 'absolute',
            left: x + w / 2,
            top: y + 30,
            transform: 'translateX(-50%)',
            fontSize: 27,
            letterSpacing: '0.25em',
            ...labelStyle,
            opacity: ease(frame, delay + drawDur - 2, 10),
          }}
        >
          {xLabel}
        </div>
      ) : null}
      {x0 ? (
        <div
          style={{
            position: 'absolute',
            left: x,
            top: y + 30,
            transform: 'translateX(-50%)',
            fontSize: 28,
            letterSpacing: '0.14em',
            ...labelStyle,
            opacity: ease(frame, delay + drawDur, 10),
          }}
        >
          {x0}
        </div>
      ) : null}
      {x1 ? (
        <div
          style={{
            position: 'absolute',
            left: x + w,
            top: y + 30,
            transform: 'translateX(-50%)',
            fontSize: 28,
            letterSpacing: '0.14em',
            ...labelStyle,
            opacity: ease(frame, delay + drawDur, 10),
          }}
        >
          {x1}
        </div>
      ) : null}
    </>
  );
};
