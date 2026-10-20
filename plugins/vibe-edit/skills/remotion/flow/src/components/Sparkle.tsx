import React from 'react';
import {useCurrentFrame} from 'remotion';
import {ease} from '../lib/anim';
import {T} from '../theme';

// Idle twinkling plus-mark. Loops forever; purely decorative.
export const Sparkle: React.FC<{
  x: number;
  y: number;
  size?: number;
  phase?: number;
  period?: number;
  delay?: number;
  color?: string;
}> = ({x, y, size = 26, phase = 0, period = 42, delay = 0, color = T.muted}) => {
  const frame = useCurrentFrame();
  const tt = ((frame + phase) % period) / period;
  const pulse = 0.25 + 0.65 * Math.abs(Math.sin(tt * Math.PI));
  const appear = ease(frame, delay, 10);
  const bar = Math.max(4, Math.round(size * 0.24));
  return (
    <svg
      width={size}
      height={size}
      style={{
        position: 'absolute',
        left: x - size / 2,
        top: y - size / 2,
        opacity: pulse * appear,
        transform: `scale(${0.8 + 0.25 * Math.abs(Math.sin(tt * Math.PI))})`,
      }}
    >
      <rect
        x={(size - bar) / 2}
        y={0}
        width={bar}
        height={size}
        rx={2}
        fill={color}
      />
      <rect
        x={0}
        y={(size - bar) / 2}
        width={size}
        height={bar}
        rx={2}
        fill={color}
      />
    </svg>
  );
};
