import config from '../../../customer-config.json';
import React, {useId} from 'react';
import {useCurrentFrame, useVideoConfig, staticFile} from 'remotion';
import {loadFont} from '@remotion/fonts';
import {penLayout, progress, phase} from './pen';

loadFont({family: 'Gentlemen Title', url: staticFile('gentlemen/fonts/ArchivoBlack-Regular.ttf'), weight: '400'});
loadFont({family: 'Gentlemen Serif', url: staticFile('gentlemen/fonts/Bevan-Regular.ttf'), weight: '400'});
loadFont({family: 'Gentlemen Chapter', url: staticFile('gentlemen/fonts/Cinzel.ttf'), weight: '500'});

export const MINT = config.accent;
export const FOREST = config.deep;
export const time = () => useCurrentFrame() / useVideoConfig().fps;

export type InkProps = {
  text: string; x: number; y: number; size?: number; start?: number;
  duration?: number; end?: number; color?: string; rotate?: number;
  align?: 'left' | 'center' | 'right'; opacity?: number;
};

/** x/y use composition pixels. y is the handwriting baseline. */
export const Ink: React.FC<InkProps> = ({text, x, y, size = 110, start = 0,
  duration = 1.2, end = Infinity, color = MINT, rotate = 0, align = 'left', opacity = 1}) => {
  const t = time();
  const id = useId().replace(/:/g, '');
  const layout = penLayout(text, start, duration);
  const offset = align === 'center' ? -layout.width / 2 : align === 'right' ? -layout.width : 0;
  const o = phase(t, start, end) * opacity;
  if (o <= 0) return null;
  return <g opacity={o} transform={`translate(${x},${y}) rotate(${rotate}) scale(${size / 1000}) translate(${offset},0)`}>
    {layout.letters.map((letter, i) => <g key={i} transform={`translate(${letter.x},0)`}>
      <defs><mask id={`${id}-${i}`} maskUnits="userSpaceOnUse" x={-400} y={-1000} width={1800} height={1700}>
        {letter.strokes.map((stroke, j) => {
          const p = progress(t, stroke.from, stroke.to - stroke.from);
          return p <= 0 ? null : <path key={j} d={stroke.d} fill="none" stroke="white" strokeWidth={stroke.width}
            strokeLinecap="round" strokeLinejoin="round" pathLength={1000}
            strokeDasharray="1000 1000" strokeDashoffset={1000 * (1 - p)}/>;
        })}
      </mask></defs>
      <path d={letter.glyph.d} fill={color} mask={t < start + duration ? `url(#${id}-${i})` : undefined}/>
    </g>)}
  </g>;
};

export type DrawProps = {d: string; start?: number; duration?: number; end?: number; color?: string; width?: number; opacity?: number};
export const Draw: React.FC<DrawProps> = ({d, start = 0, duration = .5, end = Infinity, color = MINT, width = 3.5, opacity = 1}) => {
  const t = time();
  const p = progress(t, start, duration);
  if (p <= 0) return null;
  return <path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round"
    opacity={phase(t, start, end) * opacity} pathLength={1000} strokeDasharray="1000 1000" strokeDashoffset={1000 * (1 - p)}/>;
};

export const InkCanvas: React.FC<React.PropsWithChildren<{shadow?: boolean}>> = ({children, shadow = true}) => {
  const {width, height} = useVideoConfig();
  return <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{position: 'absolute', inset: 0, overflow: 'visible',
    filter: shadow ? 'drop-shadow(0 1.2px 1.5px rgba(0,0,0,.52))' : undefined}}>{children}</svg>;
};

export const Title: React.FC<{lines: string[]; kicker?: string; size?: number; y?: number; widthScale?: number; start?: number; end?: number}> =
  ({lines, kicker, size = 135, y = 310, widthScale = 1.32, start = 0, end = Infinity}) => {
    const t = time();
    const o = phase(t, start, end) * progress(t, start, .18);
    return <div style={{position: 'absolute', top: y, left: 0, width: '100%', textAlign: 'center', color: MINT, opacity: o}}>
      {kicker ? <div style={{fontFamily: 'Gentlemen Chapter', fontSize: 25, letterSpacing: 8, marginBottom: 33}}>{kicker}</div> : null}
      <div style={{fontFamily: 'Gentlemen Title', fontSize: size, lineHeight: .94, letterSpacing: 1.8,
        transform: `scaleX(${widthScale})`, textShadow: '0 -1px 0 #baffd8, 0 2px 0 #315e45, 0 3px 2px rgba(0,0,0,.6)'}}>
        {lines.map((s, i) => <div key={i}>{s}</div>)}
      </div>
    </div>;
  };

export const Location: React.FC<{left: string; right: string; y?: number; size?: number}> = ({left, right, y = 510, size = 65}) =>
  <div style={{position: 'absolute', left: 140, right: 140, top: y, display: 'flex', justifyContent: 'space-between',
    color: MINT, fontFamily: 'Gentlemen Title', fontSize: size, letterSpacing: 4, textShadow: '0 -1px #baffd8, 0 3px 2px #14271f'}}>
    <span style={{transform: 'scaleX(1.16)', transformOrigin: 'left'}}>{left}</span><span style={{transform: 'scaleX(1.16)', transformOrigin: 'right'}}>{right}</span>
  </div>;

export const Subtitle: React.FC<{text: string; y?: number; size?: number; maxWidth?: number}> = ({text, y, size = 49, maxWidth = 1580}) => {
  const {height} = useVideoConfig();
  return <div style={{position: 'absolute', top: y ?? height * .78, width: '100%', display: 'flex', justifyContent: 'center'}}>
    <div style={{fontFamily: 'Gentlemen Serif', fontSize: size, lineHeight: 1.22, color: MINT, textAlign: 'center', maxWidth,
      transform: 'scaleX(.90)', textShadow: '2px 3px 2px rgba(0,0,0,.72)'}}>{text}</div>
  </div>;
};
