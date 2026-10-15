const fs=require('node:fs'),path=require('node:path'),Module=require('node:module'),ts=require('typescript');
const project=path.resolve(__dirname,'..');const config=JSON.parse(fs.readFileSync(path.join(project,'customer-config.json')));
const source=path.join(project,'src/components/gentlemen/pen.ts');
const js=ts.transpileModule(fs.readFileSync(source,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,resolveJsonModule:true,esModuleInterop:true}}).outputText;
const m=new Module(source,module);m.filename=source;m.paths=Module._nodeModulePaths(path.dirname(source));m._compile(js,source);
const {penLayout}=m.exports;const layout=penLayout(config.inkText,config.inkStart,config.inkDuration);
const fps=config.fps,duration=config.duration;const events=layout.events.map(x=>({start:x.from,end:x.to,length:x.length}));
// Include the actual underline in the same picture schedule.
events.push({start:2.5,end:2.95,length:720});
const motion=Array.from({length:Math.round(duration*fps)},(_,f)=>events.reduce((sum,s)=>sum+Math.max(0,Math.min(f/fps,s.end)-Math.max((f-1)/fps,s.start))/(s.end-s.start)*s.length,0));
const dest=process.argv[2];if(!dest)throw new Error('Usage: node scripts/export-pen-events.cjs <new-events.json>');if(fs.existsSync(dest))throw new Error('Refusing existing output');fs.writeFileSync(dest,JSON.stringify({fps,duration,motion,strokes:events.map(({start,end})=>({start,end}))},null,2),{flag:"wx"});
