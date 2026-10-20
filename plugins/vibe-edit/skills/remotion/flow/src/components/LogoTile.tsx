import React from 'react';
import {Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {fadeUp, popStyle} from '../lib/anim';
import {pixel} from '../fonts';
import {T} from '../theme';

// App-icon style white tile. Brand logos: pass `src` (official SVG in
// public/logos/, never redrawn). Generic tools: pass `icon`.
// x,y = tile center (label hangs below).
export const LogoTile: React.FC<{
  x: number;
  y: number;
  label: string;
  src?: string;
  icon?: React.ReactNode;
  delay?: number;
  size?: number;
}> = ({x, y, label, src, icon, delay = 0, size = 165}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: 'translate(-50%, -50%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 20,
      }}
    >
      <div
        style={{
          width: size,
          height: size,
          borderRadius: Math.round(size * 0.17),
          background: T.tile,
          border: `2px solid ${T.cardEdge}`,
          boxShadow: T.shadow,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          ...popStyle(frame, fps, delay),
        }}
      >
        {src ? (
          <Img
            src={staticFile(src)}
            style={{width: size * 0.55, height: size * 0.55}}
          />
        ) : (
          icon
        )}
      </div>
      <div
        style={{
          fontFamily: pixel,
          fontSize: 27,
          letterSpacing: '0.14em',
          textTransform: 'uppercase',
          color: T.ink,
          whiteSpace: 'nowrap',
          ...fadeUp(frame, fps, delay + 6, 14),
        }}
      >
        {label}
      </div>
    </div>
  );
};
