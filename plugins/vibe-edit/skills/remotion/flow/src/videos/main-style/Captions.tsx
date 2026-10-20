import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Basis,font} from './shared';
export const Captions:React.FC<{rows:Array<{startFrame:number;endFrame:number;text:string}>}>=({rows})=>{
 const f=useCurrentFrame();const row=rows.find(x=>f>=x.startFrame&&f<x.endFrame);
 return <Basis>{row&&<div style={{position:'absolute',left:140,top:1530,width:800,height:164,display:'flex',alignItems:'center',justifyContent:'center',whiteSpace:'pre-line',fontFamily:font,fontWeight:740,fontSize:52,lineHeight:1.2,textAlign:'center',color:'#fff',textShadow:'0 4px 18px rgba(0,0,0,.95),0 1px 4px #000',WebkitTextStroke:'.65px rgba(0,0,0,.55)'}}>{row.text}</div>}</Basis>
};
