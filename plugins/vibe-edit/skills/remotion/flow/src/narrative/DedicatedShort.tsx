import React from 'react';
import {loadFont} from '@remotion/fonts';
import {AbsoluteFill,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
loadFont({family:'Dedicated Departure',url:staticFile('fonts/DepartureMono-Regular.woff2'),weight:'400'});
// The graphic owns [60,180). Camera changes at 60 remain covered immediately.
export const DedicatedShort:React.FC=()=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig();
 const fullGraphic=frame>=60&&frame<180;
 const local=Math.max(0,Math.min(1,(frame-66)/15));
 const caption=frame<60?'Keep the complete phrase':frame<180?'Cover the actual cut':'Return at the right moment';
 return <AbsoluteFill style={{background:fullGraphic?'#16382c':'#eee9df',color:fullGraphic?'white':'#16382c',fontFamily:'Dedicated Departure'}}>
  <div style={{position:'absolute',left:100,top:150,fontSize:35}}>SYNTHETIC SHORT</div>
  {fullGraphic?<div style={{position:'absolute',left:180,top:560,width:720,opacity:local,transform:`translateY(${(1-local)*24}px)`,fontSize:76,lineHeight:1.25}}>The background<br/>owns frame 60.</div>:<div style={{position:'absolute',left:250,top:480,width:580,height:580,borderRadius:290,border:'8px solid #16382c',display:'flex',alignItems:'center',justifyContent:'center',fontSize:58}}>CAMERA</div>}
  <div data-caption style={{position:'absolute',left:104,top:1420,width:812,height:91,display:'flex',alignItems:'center',fontSize:48,fontWeight:400,lineHeight:1.1,letterSpacing:-.3,color:'white',textShadow:'0 3px 7px #000e, 0 1px 2px #000c',WebkitTextStroke:'1px rgba(0,0,0,.62)',paintOrder:'stroke fill',whiteSpace:'nowrap'}}>{caption}</div>
  <div style={{position:'absolute',left:104,bottom:150,fontSize:25}}>Frame {frame} / {fps} fps · no speech</div>
 </AbsoluteFill>;
};
