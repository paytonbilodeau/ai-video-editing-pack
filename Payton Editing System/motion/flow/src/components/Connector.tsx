import React from 'react';
import {useCurrentFrame, useVideoConfig, interpolate} from 'remotion';
import {
  evolvePath,
  getLength,
  getPointAtLength,
  getTangentAtLength,
} from '@remotion/paths';
import {ease} from '../lib/anim';
import {pixel} from '../fonts';
import {T} from '../theme';

export type Packet = {
  color: string;
  start: number; // frame the packet departs
  dur: number; // frames for one trip
  dir?: 1 | -1; // 1 = along path direction
  loop?: boolean;
};

// Thin ink line that draws itself on, with optional arrowhead, floating
// pixel-caps label, and square "data packet" dots traveling along it.
// dashed=true gives the callout style (fades in instead of drawing).
export const Connector: React.FC<{
  d: string;
  delay: number;
  drawDur?: number;
  color?: string;
  width?: number;
  arrow?: boolean;
  label?: string;
  labelAt?: number; // 0..1 along the path
  labelDx?: number;
  labelDy?: number;
  packets?: Packet[];
  dashed?: boolean;
}> = ({
  d,
  delay,
  drawDur = 16,
  color = T.ink,
  width = 3.5,
  arrow = false,
  label,
  labelAt = 0.5,
  labelDx = 0,
  labelDy = -52,
  packets = [],
  dashed = false,
}) => {
  const frame = useCurrentFrame();
  const {width: W, height: H} = useVideoConfig();
  const progress = ease(frame, delay, drawDur);
  const evolution = evolvePath(progress, d);
  const L = getLength(d);

  const labelPos = getPointAtLength(d, L * labelAt);
  const labelOpacity = ease(frame, delay + drawDur - 4, 10);

  const end = getPointAtLength(d, L);
  const tan = getTangentAtLength(d, Math.max(0, L - 1));
  if (!end || !tan || !labelPos) throw new Error('Connector requires a non-empty valid path.');
  const angle = (Math.atan2(tan.y, tan.x) * 180) / Math.PI;
  const arrowOpacity =
    progress > 0.96 ? ease(frame, delay + drawDur - 2, 6) : 0;

  return (
    <>
      <svg
        width={W}
        height={H}
        viewBox={`0 0 ${W} ${H}`}
        style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}
      >
        {dashed ? (
          <path
            d={d}
            fill="none"
            stroke={color}
            strokeWidth={width}
            strokeLinecap="round"
            strokeDasharray="12 16"
            opacity={progress}
          />
        ) : (
          <path
            d={d}
            fill="none"
            stroke={color}
            strokeWidth={width}
            strokeLinecap="round"
            strokeDasharray={evolution.strokeDasharray}
            strokeDashoffset={evolution.strokeDashoffset}
          />
        )}
        {arrow ? (
          <g
            opacity={arrowOpacity}
            transform={`translate(${end.x}, ${end.y}) rotate(${angle})`}
          >
            <path d="M 2 0 L -20 -11 L -20 11 Z" fill={color} />
          </g>
        ) : null}
        {packets.map((p, i) => {
          if (frame < p.start) {
            return null;
          }
          let t: number;
          if (p.loop) {
            t = ((frame - p.start) / p.dur) % 1;
          } else {
            t = ease(frame, p.start, p.dur);
          }
          const tt = (p.dir ?? 1) === 1 ? t : 1 - t;
          const pos = getPointAtLength(d, L * tt);
          if (!pos) throw new Error('Connector packet is outside a valid path.');
          const edgeFade = interpolate(Math.min(t, 1 - t), [0, 0.12], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const o = edgeFade;
          return (
            <rect
              key={i}
              x={pos.x - 9}
              y={pos.y - 9}
              width={18}
              height={18}
              rx={4}
              fill={p.color}
              opacity={o}
            />
          );
        })}
      </svg>
      {label ? (
        <div
          style={{
            position: 'absolute',
            left: labelPos.x + labelDx,
            top: labelPos.y + labelDy,
            transform: 'translate(-50%, -50%)',
            fontFamily: pixel,
            fontSize: 31,
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            color: T.label,
            background: T.labelBg,
            padding: '5px 14px',
            borderRadius: 6,
            opacity: labelOpacity,
            whiteSpace: 'nowrap',
          }}
        >
          {label}
        </div>
      ) : null}
    </>
  );
};
