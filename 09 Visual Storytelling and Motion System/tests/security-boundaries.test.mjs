// Keep the avatar network and file-boundary checks in the normal library validation.
import '../../Payton Editing System/motion/skills/pr-to-video/scripts/fetch-people-avatars.test.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const here=path.dirname(fileURLToPath(import.meta.url));
const repo=path.resolve(here,'../..');
const sourceRoot=repo;
const src=p=>fs.readFileSync(path.join(sourceRoot,p),'utf8');
const skills='Payton Editing System/motion/skills/';
const caption=skills+'embedded-captions/scripts/';
const require=createRequire(import.meta.url);
function scratch(t){const d=fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'vibe-codeql-')));t.after(()=>fs.rmSync(d,{recursive:true,force:true}));return d;}
function moduleSource(p){return src(p).replace(/^import .*;\n/gm,'').replace(/\bexport /g,'').replaceAll('import.meta.url',JSON.stringify(pathToFileURL(path.join(repo,p)).href));}
function extractFunction(s,name){const start=s.indexOf('function '+name+'(');assert.ok(start>=0);let n=0;const brace=s.indexOf('{',start);for(let i=brace;i<s.length;i++){if(s[i]==='{')n++;if(s[i]==='}'&&!--n)return s.slice(start,i+1);}throw Error(name);}
for(const base of ['AI Video Editing Pack/skills/javascript-animation','Payton Editing System/motion/javascript/runtime']){
 const p=base+'/tools/build.mjs';
 for(const race of ['missing-file-created','checked-file-replaced','leaf-symlink'])test(`${base}: ${race} output stays intact`,t=>{
  const d=scratch(t),output=path.join(d,'index.html'),victim=path.join(d,'external.html');
  fs.writeFileSync(victim,'PRESERVE');fs.mkdirSync(path.join(d,'styles/cut-paper'),{recursive:true});
  fs.writeFileSync(path.join(d,'piece.json'),JSON.stringify({format:{width:64,height:64,fps:1,frames:1,duration:1},build:['head.html','style','tail.html']}));
  fs.writeFileSync(path.join(d,'head.html'),'<script>');fs.writeFileSync(path.join(d,'styles/cut-paper/kit.js'),'const STYLE = {};');fs.writeFileSync(path.join(d,'tail.html'),'</script>');
  if(race==='checked-file-replaced')fs.writeFileSync(output,'OLD');
  if(race==='leaf-symlink')fs.symlinkSync(victim,output);
  let triggered=false;
  const fakeFs={...fs,existsSync(q){if(q===output&&race==='missing-file-created'&&!triggered){triggered=true;fs.writeFileSync(output,'CONCURRENT');return false;}return fs.existsSync(q);},lstatSync(q){if(q===output&&!triggered){triggered=true;if(race==='missing-file-created'){fs.writeFileSync(output,'CONCURRENT');const e=new Error();e.code='ENOENT';throw e;}if(race==='checked-file-replaced'){const st=fs.lstatSync(q);fs.renameSync(q,path.join(d,'old-index.html'));fs.writeFileSync(q,'CONCURRENT');return st;}}return fs.lstatSync(q);}};
  const c={fs:fakeFs,path,vm,fileURLToPath,Buffer};vm.createContext(c);vm.runInContext(moduleSource(p)+'\nthis.build=build;',c);
  assert.throws(()=>c.build(d));assert.equal(fs.readFileSync(victim,'utf8'),'PRESERVE');assert.equal(fs.readFileSync(output,'utf8'),race==='leaf-symlink'?'PRESERVE':'CONCURRENT');
 });
 test(`${base}: normal build replaces stale tail and returns output`,t=>{
  const d=scratch(t);fs.mkdirSync(path.join(d,'styles/cut-paper'),{recursive:true});fs.writeFileSync(path.join(d,'piece.json'),JSON.stringify({format:{width:64,height:64,fps:1,frames:1,duration:1},build:['head.html','style','tail.html']}));
  fs.writeFileSync(path.join(d,'head.html'),'<script>');fs.writeFileSync(path.join(d,'styles/cut-paper/kit.js'),'const STYLE = {};');fs.writeFileSync(path.join(d,'tail.html'),'</script>');fs.writeFileSync(path.join(d,'index.html'),'OLD'.repeat(3000));
  const c={fs,path,vm,fileURLToPath,Buffer};vm.createContext(c);vm.runInContext(moduleSource(p)+'\nthis.build=build;',c);const out=c.build(d);assert.equal(fs.readFileSync(out.output,'utf8'),out.html);
 });
 test(`${base}: beat writer preserves file created during decode`,t=>{
  const d=scratch(t),input=path.join(d,'input.wav'),output=path.join(d,'beats.json');fs.writeFileSync(input,'fixture');
  const samples=new Float32Array(22050*4);for(let i=0;i<samples.length;i++)samples[i]=(i%11025<500)?Math.sin(i*.2)*.8:0;
  const fakeFs={...fs,existsSync(q){if(q===output){fs.writeFileSync(output,'CONCURRENT');return false;}return fs.existsSync(q);}};
  const c={fs:fakeFs,path,Buffer,process:{argv:['node','beats',input,output,'--dur','4','--bpm','120'],exit(n){throw Error('unexpected exit '+n);}},console:{log(){},error(){}},spawnSync(){return {status:0,stdout:Buffer.from(samples.buffer)};}};
  vm.createContext(c);assert.throws(()=>vm.runInContext(moduleSource(base+'/tools/beats.mjs'),c),e=>e.code==='EEXIST');assert.equal(fs.readFileSync(output,'utf8'),'CONCURRENT');
 });
}
test('pen event export preserves a file created after its initial check',t=>{
 const d=scratch(t),out=path.join(d,'events.json');const p='Payton Editing System/motion/flow/scripts/export-pen-events.cjs';
 const fakeFs={...fs,existsSync(q){if(q===out){fs.writeFileSync(out,'CONCURRENT');return false;}return true;},readFileSync(q){return String(q).endsWith('customer-config.json')?JSON.stringify({fps:24,duration:4,inkText:'Hi',inkStart:0,inkDuration:1}):'fixture';}};
 class FakeModule{constructor(){this.exports={penLayout:()=>({events:[{from:0,to:1,length:10}]})};}_compile(){}static _nodeModulePaths(){return [];}}
 const c={require(x){if(x==='node:fs')return fakeFs;if(x==='node:path')return path;if(x==='node:module')return FakeModule;if(x==='typescript')return {ModuleKind:{CommonJS:1},transpileModule:()=>({outputText:''})};throw Error(x);},__dirname:path.dirname(path.join(repo,p)),module:{},process:{argv:['node','events',out]}};
 assert.throws(()=>vm.runInNewContext(src(p),c),e=>e.code==='EEXIST');assert.equal(fs.readFileSync(out,'utf8'),'CONCURRENT');
});
test('stats handles reserved type and intent keys without prototype writes',()=>{
 const s=moduleSource(skills+'media-use/scripts/lib/stats.mjs');const c={readManifest:()=>[{type:'__proto__',source:'constructor',provenance:{provider:'toString'}}],readMisses:()=>[{type:'__proto__',intent:'triage-marker'},{type:'constructor',intent:'__proto__'}],readGlobalManifest:()=>[],statSync(){throw Error();}};
 vm.createContext(c);vm.runInContext(s+'\nthis.result=buildStats({projectDir:"fixture"});this.polluted=Object.prototype["triage-marker"];',c);
 assert.equal(c.polluted,undefined);assert.equal(c.result.by_type.__proto__,1);assert.equal(c.result.by_source.constructor,1);assert.equal(c.result.top_missed_intents.__proto__[0].intent,'triage-marker');
});
test('merged preferences retains reserved keys as own data and project override',()=>{
 const p=skills+'media-use/scripts/lib/prefs-store.mjs';const s=extractFunction(src(p),'validEntry')+'\n'+extractFunction(src(p),'mergedPreferences');
 const user=JSON.parse('{"preferences":{"__proto__":{"value":"user"},"constructor":{"value":"user"}}}');const project=JSON.parse('{"preferences":{"__proto__":{"value":"project"}}}');
 const c={isRecord:x=>x&&typeof x==='object'&&!Array.isArray(x),readPrefsFile:p=>p==='user'?user:project,userPrefsPath:()=> 'user',projectPrefsPath:()=> 'project'};vm.createContext(c);vm.runInContext(s+'\nthis.result=mergedPreferences("fixture");',c);assert.ok(Object.hasOwn(c.result,'__proto__'));assert.equal(c.result.__proto__.value,'project');assert.equal(c.result.constructor.value,'user');assert.equal(Object.getPrototypeOf(c.result).value,undefined);
});
test('caption groups do not treat inherited plane names as assigned planes',()=>{
 const p=caption+'make-composition.cjs';const c={renderCap:g=>g.id};vm.createContext(c);vm.runInContext(extractFunction(src(p),'buildGroupsHtml')+'\nthis.f=buildGroupsHtml;',c);assert.match(c.f([{plane:'constructor',id:'unassigned'}],{body:{css:''}}),/unassigned/);
});
test('cinematic plane map retains a literal __proto__ plane',()=>{
 const s=src(caption+'make-cinematic.cjs');const start=s.indexOf('  const planes =');const end=s.indexOf('  // multiple heroes',start);assert.ok(end>start);const c={C:JSON.parse('{"planes":{"__proto__":"left:0;"}}')};vm.createContext(c);vm.runInContext(s.slice(start,end)+'\nthis.result=planes;',c);assert.ok(Object.hasOwn(c.result,'__proto__'));assert.equal(c.result.__proto__.css,'left:0; text-align:center;');
});
test('occlusion CLI accepts reserved caption IDs without crashing or polluting',async t=>{
 const d=scratch(t),p=caption+'check-occlusion.cjs';fs.mkdirSync(path.join(d,'frames_fg'));fs.writeFileSync(path.join(d,'frames_fg/f_0001.png'),'mock alpha');fs.writeFileSync(path.join(d,'plan.json'),JSON.stringify({groups:[{id:'__proto__',hero:true,in:0},{id:'constructor',hero:true,in:0}]}));fs.writeFileSync(path.join(d,'_layout.json'),JSON.stringify({width:2,height:2,samples:[{frame_idx:1,t:1,caps:['__proto__','constructor'].map(id=>({id,cap_bbox:{x:0,y:0,w:2,h:2},words:[]}))}]}));
 const logs=[],exits=[];const sharp=()=>({ensureAlpha(){return this},extractChannel(){return this},raw(){return this},async toBuffer(){return {data:Buffer.alloc(4),info:{width:2,height:2}}}});
 const c={__dirname:path.dirname(path.join(repo,p)),Buffer,process:{argv:['node','occlusion',d],env:{},exit:n=>exits.push(n)},console:{log:m=>logs.push(m),error:m=>logs.push(m)},require(x){if(x==='fs')return {...fs,existsSync:q=>String(q).endsWith('node_modules/sharp')||fs.existsSync(q)};if(x==='path')return path;if(x==='os')return os;if(x==='child_process')return {};if(x.endsWith('node_modules/sharp'))return sharp;throw Error(x);}};vm.createContext(c);vm.runInContext(src(p).replace('main().catch(', 'globalThis.done=main().catch('),c);await c.done;assert.deepEqual(exits,[0],logs.join('\n'));assert.ok(logs.some(x=>x.includes('__proto__')));assert.ok(logs.some(x=>x.includes('constructor')));
});
for(const key of ['constructor','toString','__proto__'])test(`theme dispatch rejects inherited key ${key}`,()=>{
 const s=src(caption+'make-theme.cjs');const start=s.indexOf('if (!PARADIGMS');const alt=s.indexOf('if (!Object.hasOwn(PARADIGMS');const at=start>=0?start:alt;const end=s.indexOf('const fx =',at);const block=s.slice(at,end);assert.ok(block);
 for(const isBody of [true,false]){const c={PARADIGMS:{valid:()=>({})},SETPIECES:{valid:()=>({})},dna:{body:{paradigm:isBody?key:'valid'},hero:{setpiece:isBody?'valid':key}},heroInline:false,HEROLESS:false};assert.throws(()=>vm.runInNewContext(block,c),/unknown (body paradigm|setpiece)/);}
});
test('three exact GSAP fixture downloads have matching SRI',()=>{
 // Exact GSAP3.12.5 CDN bytes were verified when this pin was added.
 const integrity='sha384-g4NTh/Iv5PPU4xPyhEWqPcwtNXOvdaDI8LLnyYfyNZOjKJeYQyjzQ9X5275eBjpt';
 for(const tier of ['tier-1-title-card','tier-2-multi-scene','tier-3-data-driven']){const s=src(skills+`remotion-to-hyperframes/assets/test-corpus/${tier}/hf-src/index.html`);assert.ok(s.includes(`integrity="${integrity}" crossorigin="anonymous"`));}
});

test('bundled SFX child files stay in the selected library, including symlinks',async t=>{
 const d=scratch(t),library=path.join(d,'user library'),external=path.join(d,'outside.mp3');fs.mkdirSync(path.join(library,'nested'),{recursive:true});fs.writeFileSync(external,'private marker');fs.writeFileSync(path.join(library,'nested/good.mp3'),'audio');fs.symlinkSync(external,path.join(library,'linked.mp3'));
 const mod=await import(pathToFileURL(path.join(sourceRoot,skills+'media-use/scripts/lib/bundled-sfx-provider.mjs')).href);
 for(const file of ['../outside.mp3',external,'nested/../../outside.mp3','linked.mp3','C:\\outside.mp3']){fs.writeFileSync(path.join(library,'manifest.json'),JSON.stringify({tone:{file}}));assert.equal(mod.inspectBundledSfxAssets(library).ok,false,file);await assert.rejects(()=>mod.bundledSfxProvider.search('tone',{libraryDir:library}));}
 fs.writeFileSync(path.join(library,'manifest.json'),JSON.stringify({tone:{file:'nested/good.mp3'}}));assert.equal(mod.inspectBundledSfxAssets(library).ok,true);assert.equal((await mod.bundledSfxProvider.search('tone',{libraryDir:library})).localPath,fs.realpathSync(path.join(library,'nested/good.mp3')));
});
test('DNA child selectors reject traversal and outward symlinks, retain nested DNA',t=>{
 const d=scratch(t);fs.mkdirSync(path.join(d,'scripts'));fs.mkdirSync(path.join(d,'dna/nested'),{recursive:true});fs.writeFileSync(path.join(d,'outside.json'),'{"marker":"outside"}');fs.writeFileSync(path.join(d,'dna/nested/good.json'),'{"name":"good"}');fs.symlinkSync(path.join(d,'outside.json'),path.join(d,'dna/linked.json'));
 const c={require:x=>x==='fs'?fs:x==='path'?path:require(x),__dirname:path.join(d,'scripts'),module:{exports:{}}};vm.createContext(c);vm.runInContext(src(caption+'lib-dna.cjs'),c);
 for(const name of ['../outside','linked','/tmp/outside','C:\\outside'])assert.throws(()=>c.module.exports.load(name),/inside|escape|unknown|ENOENT/);
 assert.equal(c.module.exports.load('nested/good').name,'good');
});
test('template child selectors reject traversal and outward symlinks, retain archives',t=>{
 const d=scratch(t),root=path.join(d,'templates');fs.mkdirSync(path.join(root,'_archive/good'),{recursive:true});fs.mkdirSync(path.join(d,'outside'));fs.writeFileSync(path.join(d,'outside/template.html'),'external');fs.writeFileSync(path.join(root,'_archive/good/template.html'),'good');fs.symlinkSync(path.join(d,'outside'),path.join(root,'linked'));
 const c={TEMPLATES:root,path,fs,console:{error(){}},process:{exit(){throw Error('unknown template');}}};vm.createContext(c);vm.runInContext(extractFunction(src(caption+'make-composition.cjs'),'findTemplate')+'\nthis.find=findTemplate;',c);
 for(const name of ['../outside','linked','/tmp/outside','C:\\outside'])assert.throws(()=>c.find(name));assert.equal(fs.readFileSync(c.find('_archive/good'),'utf8'),'good');
});
test('theme DNA child selectors reject traversal and outward symlinks',t=>{
 const d=scratch(t);fs.mkdirSync(path.join(d,'themes/nested'),{recursive:true});fs.writeFileSync(path.join(d,'outside.json'),'{"marker":"outside"}');fs.writeFileSync(path.join(d,'themes/nested/good.json'),'{"name":"good"}');fs.symlinkSync(path.join(d,'outside.json'),path.join(d,'themes/linked.json'));
 const s=src(caption+'make-theme.cjs');const fn=extractFunction(s,'loadThemeDna');
 const c={SKILL:d,path,fs};vm.createContext(c);vm.runInContext(fn+'\nthis.load=loadThemeDna;',c);for(const name of ['../outside','linked','/tmp/outside','C:\\outside'])assert.throws(()=>c.load(name));assert.equal(c.load('nested/good').name,'good');
});
test('layout frame index must be a positive integer before reading a PNG',async t=>{
 const d=scratch(t),p=caption+'check-occlusion.cjs';fs.mkdirSync(path.join(d,'frames_fg'));fs.writeFileSync(path.join(d,'plan.json'),'{}');
 for(const frame_idx of ['../../../outside',0,1.5]){
  fs.writeFileSync(path.join(d,'_layout.json'),JSON.stringify({width:2,height:2,samples:[{frame_idx,t:1,caps:[]}]}));const logs=[],exits=[];
  const c={__dirname:path.dirname(path.join(repo,p)),Buffer,process:{argv:['node','occlusion',d],env:{},exit:n=>exits.push(n)},console:{log:m=>logs.push(m),error:(...m)=>logs.push(m.join(' '))},require(x){if(x==='fs')return {...fs,existsSync:q=>String(q).endsWith('node_modules/sharp')||fs.existsSync(q)};if(x==='path')return path;if(x==='os')return os;if(x==='child_process')return {};if(x.endsWith('node_modules/sharp'))return ()=>{throw Error('PNG read must not start')};throw Error(x);}};
  vm.createContext(c);vm.runInContext(src(p).replace('main().catch(', 'globalThis.done=main().catch('),c);await c.done;assert.deepEqual(exits,[1],String(frame_idx));assert.ok(logs.some(x=>x.includes('positive integer')));
 }
});
