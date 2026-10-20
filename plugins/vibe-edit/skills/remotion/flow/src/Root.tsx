import React from 'react';
import {Composition} from 'remotion';
import config from '../customer-config.json';
import {NarrativeExample} from './narrative/Example';
import {DedicatedShort} from './narrative/DedicatedShort';
import {Tech, Gentlemen, Editorial, SketchLayers, GentlemenOverlay} from './Examples';
export const Root:React.FC=()=> <><Composition id="NarrativeMotion" component={NarrativeExample} width={1920} height={1080} fps={30} durationInFrames={240}/><Composition id="DedicatedShort" component={DedicatedShort} width={1080} height={1920} fps={30} durationInFrames={240}/>{[ ['TechMotion',Tech],['Gentlemen',Gentlemen],['Editorial',Editorial],['SketchLayers',SketchLayers],['GentlemenOverlay',GentlemenOverlay] ].map(([id,C])=><Composition key={id as string} id={id as string} component={C as React.FC} width={1920} height={1080} fps={config.fps} durationInFrames={Math.round(config.duration*config.fps)}/>)}</>;
