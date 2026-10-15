import React from 'react';
import {Composition} from 'remotion';
import config from '../customer-config.json';
import {Tech, Gentlemen, Editorial, SketchLayers, GentlemenOverlay} from './Examples';
export const Root:React.FC=()=> <>{[ ['TechMotion',Tech],['Gentlemen',Gentlemen],['Editorial',Editorial],['SketchLayers',SketchLayers],['GentlemenOverlay',GentlemenOverlay] ].map(([id,C])=><Composition key={id as string} id={id as string} component={C as React.FC} width={1920} height={1080} fps={config.fps} durationInFrames={Math.round(config.duration*config.fps)}/>)}</>;
