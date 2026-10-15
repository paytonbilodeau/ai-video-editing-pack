import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {fadeUp} from '../lib/anim';
import {serifItalic} from '../fonts';
import {T} from '../theme';

// Small serif-italic conversational aside, optionally led by a legend chip.
// e.g. [red chip] "= risk of death"
export const Aside: React.FC<{
  y: number;
  text: string;
  chip?: 'good' | 'bad';
  delay?: number;
  size?: number;
}> = ({y, text, chip, delay = 0, size = 38}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div
      style={{
        position: 'absolute',
        top: y,
        left: 0,
        right: 0,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 20,
        ...fadeUp(frame, fps, delay, 18),
      }}
    >
      {chip ? (
        <div
          style={{
            width: size * 0.92,
            height: size * 0.92,
            borderRadius: 9,
            background: chip === 'good' ? T.goodFill : T.badFill,
            border: `3px solid ${chip === 'good' ? T.good : T.bad}`,
          }}
        />
      ) : null}
      <div
        style={{
          fontFamily: serifItalic,
          fontStyle: 'italic',
          fontSize: size,
          color: T.ink,
        }}
      >
        {text}
      </div>
    </div>
  );
};
