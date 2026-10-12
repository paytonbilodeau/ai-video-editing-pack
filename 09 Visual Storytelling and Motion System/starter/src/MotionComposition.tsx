import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Every state comes from the requested frame, including backward seeks.
export const MotionComposition: React.FC<{transparent: boolean}> = ({transparent}) => {
  const frame = useCurrentFrame();
  const left = interpolate(frame, [0, 18], [0, 1], clamp);
  const arrow = interpolate(frame, [24, 42], [0, 1], clamp);
  const right = interpolate(frame, [42, 60], [0, 1], clamp);
  const exit = interpolate(frame, [135, 149], [1, 0], clamp);
  const box: React.CSSProperties = {
    width: 470, height: 240, borderRadius: 24, background: '#ffffff',
    border: '6px solid #222222', display: 'grid', placeItems: 'center',
    fontSize: 52, fontWeight: 800, textAlign: 'center', whiteSpace: 'nowrap',
  };
  return (
    <AbsoluteFill style={{backgroundColor: transparent ? 'transparent' : '#eceff2',
      color: '#171717', fontFamily: 'Arial, sans-serif', alignItems: 'center',
      justifyContent: 'center'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 65, opacity: exit}}>
        <div style={{...box, opacity: left}}>ONE IDEA</div>
        <div style={{fontSize: 110, width: 150, textAlign: 'center', color: '#444444',
          opacity: arrow}}>→</div>
        <div style={{...box, opacity: right}}>CLEAR VISUAL</div>
      </div>
    </AbsoluteFill>
  );
};
