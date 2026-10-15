import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {popStyle} from '../lib/anim';
import {pixel} from '../fonts';
import {T} from '../theme';

// White paper card node: outline icon + pixel-caps label. x,y = center.
export const Card: React.FC<{
  x: number;
  y: number;
  icon: React.ReactNode;
  label: string;
  delay?: number;
  w?: number;
}> = ({x, y, icon, label, delay = 0, w = 330}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        marginLeft: -w / 2,
        transform: 'translateY(-50%)',
      }}
    >
      <div
        style={{
          background: T.card,
          border: `2px solid ${T.cardEdge}`,
          borderRadius: 18,
          boxShadow: T.shadow,
          padding: '38px 18px 32px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 24,
          ...popStyle(frame, fps, delay),
        }}
      >
        {icon}
        <div
          style={{
            fontFamily: pixel,
            fontSize: 30,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: T.ink,
            textAlign: 'center',
            lineHeight: 1.45,
          }}
        >
          {label}
        </div>
      </div>
    </div>
  );
};
