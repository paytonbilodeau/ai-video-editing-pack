import React from 'react';
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

// Master mode: ONE full-length overlay clip covering the whole video.
// Each beat fades in over the talking head, plays its scene (opaque
// background included), and fades back out to transparent. Render the
// master comp with the ProRes 4444 alpha flag trio; Payton drags one
// file onto his timeline at 0:00.

export const FadeWrap: React.FC<{
  dur: number; // in frames
  fadeIn?: number;
  fadeOut?: number;
  children: React.ReactNode;
}> = ({dur, fadeIn = 7, fadeOut = 10, children}) => {
  const frame = useCurrentFrame();
  // fadeIn/fadeOut of 0 mean HARD CUT: fully opaque on the boundary
  // frame. (Clamping 0 into a 1-2 frame fade leaves transparent frames
  // at the cut and the talking head flickers through - caught on send5.)
  const inO =
    fadeIn <= 0
      ? 1
      : interpolate(frame, [0, fadeIn], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
  const outO =
    fadeOut <= 0
      ? 1
      : interpolate(frame, [dur - Math.max(2, fadeOut), dur - 1], [1, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
  const o = Math.min(inO, outO);
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

export type Beat = {
  start: number; // seconds into the FINAL video
  dur: number; // seconds on screen
  node: React.ReactNode; // a scene element, rendered with its Background
  fadeIn?: number; // frames
  fadeOut?: number; // frames
};

export const MasterTrack: React.FC<{beats: Beat[]}> = ({beats}) => {
  const {fps} = useVideoConfig();
  return (
    <>
      {beats.map((b, i) => {
        const durF = Math.round(b.dur * fps);
        return (
          <Sequence key={i} from={Math.round(b.start * fps)} durationInFrames={durF}>
            <FadeWrap dur={durF} fadeIn={b.fadeIn} fadeOut={b.fadeOut}>
              {b.node}
            </FadeWrap>
          </Sequence>
        );
      })}
    </>
  );
};
