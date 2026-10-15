import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Subtitle} from './index';

export type CaptionCue = {start: number; end: number; text: string};
/** Phrase captions keep the reference's calm serif treatment; no word bounce. */
export const CaptionTrack: React.FC<{cues: CaptionCue[]; y?: number; size?: number; maxWidth?: number}> = ({cues, ...style}) => {
  const t = useCurrentFrame() / useVideoConfig().fps;
  const cue = cues.find(c => t >= c.start && t < c.end);
  return cue ? <Subtitle text={cue.text} {...style}/> : null;
};
