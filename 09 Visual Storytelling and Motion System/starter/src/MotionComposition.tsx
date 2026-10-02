import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {theme} from './theme';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export const MotionComposition: React.FC = () => {
  const frame = useCurrentFrame();
  const cardX = interpolate(frame, [0, 30], [-520, 0], clamp);
  const gateScale = interpolate(frame, [45, 65], [0.86, 1], clamp);
  const receiptOpacity = interpolate(frame, [92, 112], [0, 1], clamp);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.background,
        color: theme.ink,
        fontFamily: 'Arial, sans-serif',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div style={{display: 'flex', alignItems: 'center', gap: 96}}>
        <div
          style={{
            width: 460,
            height: 250,
            border: `8px solid ${theme.ink}`,
            borderRadius: 28,
            display: 'grid',
            placeItems: 'center',
            transform: `translateX(${cardX}px)`,
            fontSize: 52,
            fontWeight: 800,
          }}
        >
          OUTPUT
        </div>
        <div
          style={{
            width: 180,
            height: 360,
            border: `12px solid ${theme.accent}`,
            borderRadius: 90,
            display: 'grid',
            placeItems: 'center',
            transform: `scale(${gateScale})`,
            fontSize: 46,
            fontWeight: 800,
          }}
        >
          CHECK
        </div>
        <div
          style={{
            width: 330,
            padding: 36,
            border: `6px solid ${theme.approved}`,
            borderRadius: 20,
            opacity: receiptOpacity,
            fontSize: 44,
            fontWeight: 800,
          }}
        >
          RECEIPT
        </div>
      </div>
    </AbsoluteFill>
  );
};
