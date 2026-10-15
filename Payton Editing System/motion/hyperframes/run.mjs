#!/usr/bin/env node
import {spawnSync} from 'node:child_process';import {fileURLToPath} from 'node:url';import path from 'node:path';import fs from 'node:fs';
const root=path.dirname(fileURLToPath(import.meta.url));const bin=path.join(root,'node_modules','.bin',process.platform==='win32'?'hyperframes.cmd':'hyperframes');
if(!fs.existsSync(bin)){console.error('In a copied project runtime folder, run npm ci first. No automatic install was attempted.');process.exit(2);}
const result=spawnSync(bin,process.argv.slice(2),{stdio:'inherit',shell:false,env:{...process.env,HYPERFRAMES_NO_TELEMETRY:'1',DO_NOT_TRACK:'1',HYPERFRAMES_SKIP_SKILLS:'1'}});if(result.error){console.error(result.error.message);process.exit(1);}process.exit(result.status??1);
