import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, Card, Text, Underline, move, phase, sans} from './primitives';

// Synthetic teaching fixture. No narration or measured speech cues.
export const NarrativeExample:React.FC=()=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig(),t=frame/fps;
 const x=move(t,2.5,180,1060,1),w=move(t,2.5,660,640,1);
 const fade=1-phase(t,2.1,.35),reveal=phase(t,3.6,.45);
 return <AbsoluteFill style={{background:C.paper,color:C.ink}}>
  <div style={{position:'absolute',left:140,top:105}}><Text size={96}>Keep the useful idea.</Text></div>
  <Card x={x} y={330} w={w} h={430}>
   <Text size={62}>{t<3?'Source note':'Clear summary'}</Text>
   <div style={{position:'absolute',left:34,top:145,fontFamily:sans,fontSize:34,lineHeight:1.5}}>
    <div>Keep the useful idea.</div>
    <div style={{position:'absolute',left:0,top:65,opacity:fade}}>Remove the repeated detail.</div>
    
    <div style={{position:'absolute',left:0,top:75,opacity:reveal}}><Underline t={t} at={4.4} w={400}/></div>
   </div>
  </Card>
  <div style={{position:'absolute',left:180,top:410,width:700,opacity:phase(t,3.8),fontFamily:sans,fontSize:46,lineHeight:1.35}}>The same note moves.<br/>Its useful content stays.</div>
  <div style={{position:'absolute',left:140,bottom:90,fontFamily:sans,fontSize:27,color:C.muted}}>Synthetic example · invented timing · no spoken audio</div>
 </AbsoluteFill>;
};
