import React from 'react';
import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';
loadFont({family:'Inter',url:staticFile('fonts/Inter-700.woff2'),weight:'700'});
import {AbsoluteFill, Composition, registerRoot, getInputProps, useCurrentFrame, useVideoConfig, interpolate} from 'remotion';
import {Ink, InkCanvas} from '../../components/gentlemen';
// Portable portrait-short overlay, derived from the actual production compositor. Two compositions:
//  Short-ink: one Gentlemen handwriting note as a short transparent window (legacy, kept for parity).
//  Short-overlay: the full-length transparent 2160x3840 overlay for one short: hook card, phrase captions, one Ink note.
// All times are seconds from the short's first frame. Caption y is the BOTTOM edge of the caption block in 4K coordinates
// (a measured safe position per layout); the hook card top is in 4K coordinates too.
type InkP = {text: string; x: number; y: number; size: number; start: number; duration: number; end: number; align?: 'left'|'center'|'right'};
type Cue = {start: number; end: number; text: string; y: number};
type OverlayP = {frames: number; fps?:number; hook: {text: string; start: number; end: number; top: number}; cues: Cue[]; ink?: InkP | null};
// Helvetica Neue is customer-provided when licensed; portable demo uses supplied OFL Inter.
const FONT = (getInputProps() as {fontFamily?:string}).fontFamily || 'Inter';

const Note: React.FC = () => {
  const p = getInputProps() as InkP & {frames: number};
  return <AbsoluteFill><InkCanvas shadow>
    <Ink text={p.text} x={p.x} y={p.y} size={p.size} start={p.start} duration={p.duration} end={p.end} align={p.align ?? 'left'}/>
  </InkCanvas></AbsoluteFill>;
};

const Hook: React.FC<{h: OverlayP['hook']}> = ({h}) => {
  const t = useCurrentFrame() / useVideoConfig().fps;
  if (t < h.start || t >= h.end) return null;
  const o = Math.min(interpolate(t, [h.start, h.start + .15], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
                     interpolate(t, [h.end - .2, h.end], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const rise = interpolate(t, [h.start, h.start + .15], [24, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', top: h.top + rise, left: 0, width: '100%', display: 'flex', justifyContent: 'center', opacity: o}}>
    <div style={{background: '#FFFFFF', color: '#000000', borderRadius: 34, padding: '0 62px', height: 190, display: 'flex', alignItems: 'center',
      fontFamily: FONT, fontWeight: 700, fontSize: 108, lineHeight: 1, whiteSpace: 'nowrap', maxWidth: 1760, boxShadow: '0 18px 60px rgba(0,0,0,.35)'}}>{h.text}</div>
  </div>;
};

const Captions: React.FC<{cues: Cue[]}> = ({cues}) => {
  const t = useCurrentFrame() / useVideoConfig().fps;
  const c = cues.find(q => t >= q.start && t < q.end);
  if (!c) return null;
  return <div style={{position: 'absolute', bottom: 3840 - c.y, left: 0, width: '100%', display: 'flex', justifyContent: 'center'}}>
    <div style={{maxWidth: 1640, textAlign: 'center', color: '#FFFFFF', fontFamily: FONT, fontWeight: 700, fontSize: 92, lineHeight: 1.1,
      textShadow: '0 4px 7px rgba(0,0,0,.70), 0 2px 3px rgba(0,0,0,.85), 0 0 26px rgba(0,0,0,.45)', WebkitTextStroke: '1.4px rgba(0,0,0,.5)',
      paintOrder: 'stroke fill'}}>{c.text}</div>
  </div>;
};

const Overlay: React.FC = () => {
  const p = getInputProps() as OverlayP;
  return <AbsoluteFill>
    <Captions cues={p.cues}/>
    <Hook h={p.hook}/>
    {p.ink ? <InkCanvas shadow><Ink text={p.ink.text} x={p.ink.x} y={p.ink.y} size={p.ink.size} start={p.ink.start} duration={p.ink.duration} end={p.ink.end} align={p.ink.align ?? 'left'}/></InkCanvas> : null}
  </AbsoluteFill>;
};

const props = getInputProps() as Partial<OverlayP>;
registerRoot(() => <>
  <Composition id="Short-ink" component={Note} width={2160} height={3840} fps={props.fps ?? 30} durationInFrames={props.frames ?? 180} defaultProps={{}}/>
  <Composition id="Short-overlay" component={Overlay} width={2160} height={3840} fps={props.fps ?? 30} durationInFrames={props.frames ?? 180} defaultProps={{}}/>
</>);
