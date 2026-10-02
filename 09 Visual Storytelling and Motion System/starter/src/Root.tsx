import React from 'react';
import {Composition} from 'remotion';
import {MotionComposition} from './MotionComposition';

export const Root: React.FC = () => {
  return (
    <Composition
      id="NeutralMotion"
      component={MotionComposition}
      durationInFrames={150}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
