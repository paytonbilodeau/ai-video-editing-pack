import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {easeOut} from '../lib/anim';
import {T} from '../theme';

const GRAIN = `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix type='saturate' values='0'/></filter><rect width='240' height='240' filter='url(%23n)'/></svg>")`;

// Paper world: flat off-white + faint film grain + soft vignette.
// transparent=true renders nothing (alpha overlay exports).
export const Background: React.FC<{transparent?: boolean}> = ({
  transparent,
}) => {
  if (transparent) {
    return null;
  }
  return (
    <AbsoluteFill style={{backgroundColor: T.bg}}>
      <AbsoluteFill style={{backgroundImage: GRAIN, opacity: T.grain}} />
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(140% 110% at 50% 40%, transparent 58%, rgba(60,60,60,0.09) 100%)',
        }}
      />
    </AbsoluteFill>
  );
};

// Quarter-second white flash that opens a cutaway (place LAST in the scene).
export const Flash: React.FC<{transparent?: boolean}> = ({transparent}) => {
  const frame = useCurrentFrame();
  if (transparent) {
    return null;
  }
  const o = easeOut(frame, 0, 8, 1, 0);
  if (o <= 0.01) {
    return null;
  }
  return (
    <AbsoluteFill style={{backgroundColor: T.flash, opacity: o}} />
  );
};
