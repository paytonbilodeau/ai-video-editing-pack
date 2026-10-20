import React from 'react';
import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

loadFont({family:'Seamless Serif',url:staticFile('fonts/InstrumentSerif-Regular.ttf'),weight:'400'});
loadFont({family:'Seamless Serif',url:staticFile('fonts/InstrumentSerif-Italic.woff2'),weight:'400',style:'italic'});
loadFont({family:'Seamless Sans',url:staticFile('fonts/InstrumentSans.woff2'),weight:'100 900'});
export const C={paper:'#F7F8F2',outer:'#E5E7DF',ink:'#192B23',green:'#0F583D',mint:'#DAEBDD',muted:'#69766D',line:'#CAD2C8',white:'#FFFFFF',red:'#9D5144'};
export const serif='Seamless Serif';
export const sans='Seamless Sans';
export const clamp=(x:number)=>Math.max(0,Math.min(1,x));
export const ease=(x:number)=>{const p=clamp(x);return p*p*(3-2*p)};
export const out=(x:number)=>1-Math.pow(1-clamp(x),3);
export const phase=(t:number,at:number,d=.45)=>out((t-at)/d);
export const move=(t:number,at:number,a:number,b:number,d=.65)=>a+(b-a)*ease((t-at)/d);
export const Box:React.FC<React.PropsWithChildren<{x:number;y:number;w?:number;h?:number;style?:React.CSSProperties}>>=({x,y,w,h,style,children})=><div style={{position:'absolute',left:x,top:y,width:w,height:h,...style}}>{children}</div>;
export const Re:React.FC<React.PropsWithChildren<{t:number;at:number;d?:number;dy?:number;style?:React.CSSProperties}>>=({t,at,d=.45,dy=24,style,children})=>{const p=phase(t,at,d);return <div style={{opacity:p,transform:`translateY(${(1-p)*dy}px)`,...style}}>{children}</div>};
export const Label:React.FC<React.PropsWithChildren<{style?:React.CSSProperties}>>=({children,style})=><div style={{fontFamily:sans,fontSize:24,fontWeight:600,letterSpacing:3,textTransform:'uppercase',color:C.muted,...style}}>{children}</div>;
export const Pill:React.FC<React.PropsWithChildren<{dark?:boolean;style?:React.CSSProperties}>>=({children,dark,style})=><div style={{display:'inline-flex',alignItems:'center',gap:12,fontFamily:sans,fontSize:28,lineHeight:1.3,padding:'12px 24px',borderRadius:40,background:dark?C.green:C.mint,color:dark?C.white:C.green,...style}}>{children}</div>;
export const Card:React.FC<React.PropsWithChildren<{x:number;y:number;w:number;h:number;active?:boolean;style?:React.CSSProperties}>>=({x,y,w,h,active,style,children})=><Box x={x} y={y} w={w} h={h} style={{background:active?C.mint:C.white,border:`2px solid ${active?C.green:'#E2E7DF'}`,borderRadius:22,boxShadow:'0 12px 26px rgba(31,48,35,.055)',padding:34,boxSizing:'border-box',...style}}>{children}</Box>;
export const Text:React.FC<React.PropsWithChildren<{size?:number;style?:React.CSSProperties}>>=({children,size=58,style})=><div style={{fontFamily:serif,fontSize:size,fontWeight:400,lineHeight:1.08,color:C.ink,...style}}>{children}</div>;
export const Underline:React.FC<{t:number;at:number;w:number;color?:string}>=({t,at,w,color=C.green})=><svg width={w} height={18} style={{overflow:'visible',display:'block'}}><path d={`M 3 11 Q ${w*.5} 2 ${w-3} 9`} pathLength={1} stroke={color} strokeWidth={5} fill="none" strokeLinecap="round" strokeDasharray={1} strokeDashoffset={1-phase(t,at,.5)}/></svg>;
export const Path:React.FC<{t:number;at:number;d:string;color?:string;width?:number;duration?:number;dash?:boolean}>=({t,at,d,color=C.green,width=4,duration=.55,dash})=><svg width={1920} height={1080} style={{position:'absolute',inset:0,overflow:'visible',pointerEvents:'none'}}><path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={dash?'.008 .013':1} strokeDashoffset={dash?0:1-phase(t,at,duration)} opacity={dash?phase(t,at,duration):1}/></svg>;
export const Lines:React.FC<{t:number;at:number;n?:number;w?:number;color?:string}>=({t,at,n=5,w=440,color=C.line})=><div style={{display:'flex',flexDirection:'column',gap:17}}>{Array.from({length:n},(_,i)=><div key={i} style={{height:i===0?14:8,width:w*(i===n-1?.63:1)*phase(t,at+i*.1,.5),background:color,borderRadius:6}}/>)}</div>;
export const Title:React.FC<{label:string;children:React.ReactNode;size?:number}>=({label,children,size=92})=><Box x={144} y={155} w={1632}><Label>{label}</Label><Text size={size} style={{marginTop:25}}>{children}</Text></Box>;

// Motion changes only the content plane. Keep the stage and any presenter fixed.
// Cubic smoothstep and velocity-coupled directional blur are reproduction choices,
// not a claim about the original creator's source code.
export type Axis='left'|'right'|'up'|'down';
export function plane(t:number,start:number,end:number,dir:Axis,nextDir:Axis) {
  const q=ease((t-start+.166667)/.333334),r=ease((t-end+.166667)/.333334);
  const vector=(v:Axis)=>v==='left'?[2050,0]:v==='right'?[-2050,0]:v==='up'?[0,1180]:[0,-1180];
  const a=vector(dir),b=vector(nextDir);const x=a[0]*(1-q)-b[0]*r,y=a[1]*(1-q)-b[1]*r;
  const rawIn=clamp((t-start+.166667)/.333334),rawOut=clamp((t-end+.166667)/.333334);
  const speedIn=6*rawIn*(1-rawIn),speedOut=6*rawOut*(1-rawOut);
  return {x,y,bx:Math.abs(a[0])/2050*speedIn*26+Math.abs(b[0])/2050*speedOut*26,by:Math.abs(a[1])/1180*speedIn*26+Math.abs(b[1])/1180*speedOut*26};
}
