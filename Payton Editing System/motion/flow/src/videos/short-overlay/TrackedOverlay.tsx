import React from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {InkCanvas, Ink, Draw} from '../../components/gentlemen';
type Track={frames:Array<{valid:boolean;quad?:number[][]}>};
import {InkProps,DrawProps} from '../../components/gentlemen';

export const TrackedOverlay: React.FC<{track:Track;ink?:InkProps[];draw?:DrawProps[];openRight?:number;openBottom?:number}>=({track,ink=[],draw=[],openRight=1,openBottom=1})=> {
  const f = useCurrentFrame();
  const record = track.frames[f];
  if (!record?.valid || !record.quad) return null;
  const q = record.quad;
  const edge = (a: number[], b: number[], p: number) => [a[0] * (1-p) + b[0] * p, a[1] * (1-p) + b[1] * p];
  // The handler occludes the lower-right corner. Leave this section open
  // instead of drawing through his jacket. This is a shot-specific mask.
  const outline = `M${q[0]} L${q[1]} L${edge(q[1], q[2], openRight)} M${edge(q[3], q[2], openBottom)} L${q[3]} L${q[0]}`;
  const tip = [q[0][0] * .35 + q[3][0] * .65 - 5, q[0][1] * .35 + q[3][1] * .65];
  const control = [tip[0] - 105, tip[1] + 45];
  const dx = tip[0] - control[0], dy = tip[1] - control[1];
  const norm = Math.max(1e-9,Math.hypot(dx, dy)), ux = dx / norm, uy = dy / norm;
  const a = [tip[0] - ux * 24 - uy * 10, tip[1] - uy * 24 + ux * 10];
  const b = [tip[0] - ux * 24 + uy * 10, tip[1] - uy * 24 - ux * 10];
  return <InkCanvas>
    <Draw d={outline} start={.2} duration={.8} width={3.2}/>
    <Draw d={`M421,555 C465,650 ${control.join(',')} ${tip.join(',')}`} start={1.05} duration={.57} width={3.3}/>
    <Draw d={`M${a.join(',')} L${tip.join(',')} L${b.join(',')}`} start={1.62} duration={.12} width={3.3}/>
    {ink.map((p, i) => <Ink key={i} {...p}/>)}
    {draw.map((p, i) => <Draw key={i} {...p}/>)}
  </InkCanvas>;
};

