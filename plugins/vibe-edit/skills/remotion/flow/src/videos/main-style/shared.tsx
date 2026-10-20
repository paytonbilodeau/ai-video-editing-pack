import config from '../../../customer-config.json';
import React, {useEffect, useId, useState} from 'react';
import {AbsoluteFill, Img, cancelRender, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {setPalette} from '../../theme';
import {penLayout, inkWidth} from '../../components/gentlemen/pen';

export const M=config.accent, G=config.deep, W='#F9FCFA', MUTED='#BECAC2';
export const clamp=(n:number)=>Math.max(0,Math.min(1,n));
export const ease=(n:number)=>1-Math.pow(1-clamp(n),3);
export const p=(f:number,start:number,duration=16)=>ease((f-start)/duration);
export const appear=(f:number,a:number,b:number)=>Math.min(p(f,a,10),clamp((b-f)/7));
export const font='Shorts Sans';
let fontPromise:Promise<unknown>|undefined;
export const ShortsFontGate:React.FC<React.PropsWithChildren>=({children})=>{
 const [handle]=useState(()=>delayRender('Main2 shorts bundled fonts'));
 useEffect(()=>{
  fontPromise??=Promise.all([
   new FontFace(font,`url(${staticFile('fonts/InstrumentSans.woff2')})`,{weight:'100 900'}).load(),
   new FontFace('Shorts Title',`url(${staticFile('gentlemen/fonts/ArchivoBlack-Regular.ttf')})`).load(),
  ]).then(faces=>faces.forEach(face=>(document.fonts as FontFaceSet & {add:(face:FontFace)=>void}).add(face)));
  fontPromise.then(()=>continueRender(handle)).catch(cancelRender);
 },[handle]);
 return <>{children}</>;
};
export const T:React.FC<{x?:number;y:number;size?:number;fill?:string;anchor?:'start'|'middle'|'end';heavy?:boolean;children:React.ReactNode}>=({x=540,y,size=42,fill=W,anchor='middle',heavy=false,children})=><text x={x} y={y} fill={fill} fontSize={size} fontFamily={heavy?'Shorts Title':font} fontWeight={heavy?400:650} textAnchor={anchor}>{children}</text>;

// Reuses the approved central pen routes and filled glyphs without importing
// module-global font loaders. Font loading is owned by ShortsFontGate.
export const Hand:React.FC<{text:string;x?:number;y:number;size?:number;start:number;duration?:number;end:number}>=({text,x=540,y,size=148,start,duration=28,end})=>{
 const f=useCurrentFrame(),{fps}=useVideoConfig();const id=useId().replace(/:/g,'');
 const lay=penLayout(text,start/fps,duration/fps);const time=f/fps;
 if(f<start||f>=end)return null;
 return <g opacity={Math.min(1,(end-f)/5)} transform={`translate(${x},${y}) scale(${size/1000}) translate(${-lay.width/2},0)`}>
 {lay.letters.map((l,i)=><g key={i} transform={`translate(${l.x},0)`}><defs><mask id={`${id}-${i}`} maskUnits="userSpaceOnUse" x={-400} y={-1000} width={1800} height={1700}>
 {l.strokes.map((s,j)=><path key={j} d={s.d} fill="none" stroke="white" strokeWidth={s.width} strokeLinecap="round" strokeLinejoin="round" pathLength={1000} strokeDasharray="1000 1000" strokeDashoffset={1000*(1-clamp((time-s.from)/(s.to-s.from)))}/>)}</mask></defs>
 <path d={l.glyph.d} fill={M} mask={f<start+duration?`url(#${id}-${i})`:undefined}/></g>)}</g>;
};

export const Basis:React.FC<React.PropsWithChildren>=({children})=>{const {width}=useVideoConfig();return <ShortsFontGate><AbsoluteFill><div style={{position:"absolute",width:1080,height:1920,transform:`scale(${width/1080})`,transformOrigin:"0 0"}}>{children}</div></AbsoluteFill></ShortsFontGate>};
