import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {build,validateMeta,SKILL} from '../tools/build.mjs';
import {parse,withPiece,capture} from '../tools/animate.mjs';
const cli=path.join(SKILL,'tools/animate.mjs');
const temp=()=>fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()),'animation spaces '));
function fixture(base,{transparent=false,nondeterministic=false,fps=24,width=64}={}) {
 const dir=path.join(base,'piece with spaces');fs.mkdirSync(dir);
 const meta={style:'cut-paper',format:{width,height:64,fps,frames:fps,duration:1},build:['source.html']};
 fs.writeFileSync(path.join(dir,'piece.json'),JSON.stringify(meta));
 fs.writeFileSync(path.join(dir,'source.html'),`<!doctype html><canvas id="c" width="${width}" height="64"></canvas><script>
 const STYLE={}; window.TIMELINE=${JSON.stringify(meta.format)};
 let calls=0;
 window.renderFrame=t=>{const g=document.getElementById('c').getContext('2d');g.clearRect(0,0,64,64);${transparent?'':"g.fillStyle='#fff';g.fillRect(0,0,64,64);"}g.fillStyle='#00aa66';g.fillRect(Math.floor(t*24)${nondeterministic?'+calls++':''},8,16,16);};
 </script>`);
 return dir;
}
function run(args){return spawnSync(process.execPath,[cli,...args],{encoding:'utf8',timeout:120000});}
test('CLI rejects unknown switches and extra positional arguments',()=>{
 assert.throws(()=>parse(['render','piece','--unknown']),/unknown/);
 assert.throws(()=>parse(['build','a','b']),/unexpected/);
 assert.notEqual(run(['render','missing','--format','gif']).status,0);
 assert.notEqual(run(['render','missing','--format','mp4','--alpha']).status,0);
});
test('metadata fails closed for invalid bounds, nonfinite and mismatched duration',()=>{
 const good={width:64,height:64,fps:24,frames:24,duration:1};
 for(const bad of [{...good,fps:0},{...good,width:Infinity},{...good,frames:25},{...good,height:1.5},{...good,duration:-1}])assert.throws(()=>validateMeta(bad));
});
test('standalone build supports spaces and rejects traversal, output symlinks and source symlinks',()=>{
 const base=temp();try {
 const dir=fixture(base);assert.ok(build(dir).html.includes('animation:frame'));
 const file=path.join(dir,'piece.json'),meta=JSON.parse(fs.readFileSync(file));meta.build=['../external.html'];fs.writeFileSync(file,JSON.stringify(meta));assert.throws(()=>build(dir),/unsafe/);
 meta.build=['source.html'];fs.writeFileSync(file,JSON.stringify(meta));fs.unlinkSync(path.join(dir,'index.html'));fs.symlinkSync(path.join(dir,'source.html'),path.join(dir,'index.html'));assert.throws(()=>build(dir),/linked/);
 fs.unlinkSync(path.join(dir,'index.html'));fs.writeFileSync(path.join(base,'outside.html'),'outside');fs.unlinkSync(path.join(dir,'source.html'));fs.symlinkSync(path.join(base,'outside.html'),path.join(dir,'source.html'));assert.throws(()=>build(dir),/escapes/);
 } finally {fs.rmSync(base,{recursive:true,force:true});}
});
test('JSON script closing tags are escaped and custom styles are contained',()=>{
 const base=temp();try{const dir=fixture(base);fs.writeFileSync(path.join(dir,'beats.json'),JSON.stringify({bpm:120,offset:0,note:'</script><script>bad()'}));assert.ok(build(dir).html.includes('\\u003c/script>'));}finally{fs.rmSync(base,{recursive:true,force:true});}
});
test('init is additive and never replaces an existing destination',()=>{
 const base=temp();try {const dest=path.join(base,'new piece');assert.equal(run(['init',dest]).status,0);assert.notEqual(run(['init',dest]).status,0);assert.equal(run(['build',dest]).status,0);}finally{fs.rmSync(base,{recursive:true,force:true});}
});
test('local beat analysis preserves source, validates bounds and refuses an existing output',t=>{
 if(spawnSync('ffmpeg',['-version']).status!==0) {t.skip('FFmpeg is unavailable');return;}
 const base=temp();try {
 const rate=22050,seconds=4,n=rate*seconds,b=Buffer.alloc(44+n*2);
 b.write('RIFF');b.writeUInt32LE(36+n*2,4);b.write('WAVEfmt ',8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(rate,24);b.writeUInt32LE(rate*2,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write('data',36);b.writeUInt32LE(n*2,40);
 for(let i=0;i<n;i++){const phase=(i/rate)%0.5;const sample=phase<0.05?Math.sin(i/rate*2*Math.PI*440)*Math.exp(-phase*90):0;b.writeInt16LE(Math.round(sample*28000),44+i*2);}
 const src=path.join(base,'local beat track.wav'),out=path.join(base,'beats.json');fs.writeFileSync(src,b);
 const result=run(['beats',src,'--out',out,'--bpm','120','--duration','4']);assert.equal(result.status,0,result.stderr);
 const beats=JSON.parse(fs.readFileSync(out));assert.ok(Math.abs(beats.bpm-120)<1);assert.ok(beats.beats.length>=7);assert.deepEqual(fs.readFileSync(src),b);
 assert.notEqual(run(['beats',src,'--out',out]).status,0);
 assert.notEqual(run(['beats',src,'--out',path.join(base,'bad.json'),'--bpm','0']).status,0);
 }finally{fs.rmSync(base,{recursive:true,force:true});}
});
const runtime=process.env.ANIMATION_RUNTIME;
test('browser: repeat/out-of-order hashes, metadata disagreement, nondeterminism, PNG alpha and paths with spaces',{skip:!runtime},()=>{
 const base=temp();try {
 for(const opts of [{},{transparent:true,fps:30},{nondeterministic:true}]) {
  const sub=fs.mkdtempSync(path.join(base,'fixture ')),dir=fixture(sub,opts),out=path.join(sub,'render output');
  const result=run(['render',dir,'--runtime',runtime,'--out',out,...(opts.transparent?['--alpha']:[])]);
  if(opts.nondeterministic){assert.notEqual(result.status,0);assert.match(result.stderr,/non-deterministic/);}
  else {assert.equal(result.status,0,result.stderr);const report=JSON.parse(fs.readFileSync(path.join(out,'report.json')));assert.equal(report.alphaPresent,!!opts.transparent);assert.equal(fs.readdirSync(out).filter(f=>f.endsWith('.png')).length,opts.fps||24);}
 }
 const sub=fs.mkdtempSync(path.join(base,'bad meta ')),dir=fixture(sub);const file=path.join(dir,'source.html');fs.writeFileSync(file,fs.readFileSync(file,'utf8').replace('"fps":24','"fps":30').replace('"frames":24','"frames":30'));
 const mismatch=run(['check',dir,'--runtime',runtime,'--out',path.join(sub,'out')]);assert.notEqual(mismatch.status,0);assert.match(mismatch.stderr,/disagree/);
 const sub2=fs.mkdtempSync(path.join(base,'opaque ')),dir2=fixture(sub2);assert.notEqual(run(['render',dir2,'--runtime',runtime,'--out',path.join(sub2,'out'),'--alpha']).status,0);
 } finally {fs.rmSync(base,{recursive:true,force:true});}
});

test('browser: all seven shipped style demos build and seek', {skip:!runtime},()=>{
 const base=temp();try {
 for(const style of ['cut-paper','crosshatch','riso','sketchbook','math','isometric','pixel']) {
  const dir=path.join(base,style);assert.equal(run(['init',dir,'--style',style]).status,0);
  const result=run(['check',dir,'--runtime',runtime,'--out',path.join(base,style+' checks')]);
  assert.equal(result.status,0,style+': '+result.stderr);
 }
 }finally{fs.rmSync(base,{recursive:true,force:true});}
});
test('browser: iframe handshake maps 60fps host to 24fps source and rejects invalid host metadata', {skip:!runtime},async()=>{
 const base=temp();try {
 const dir=fixture(base);
 await withPiece(dir,runtime,async(page,t,{origin})=>{
  await page.setContent('<iframe id="animation"></iframe>');
  await page.evaluate(url=>{document.getElementById('animation').src=url;},origin+'/piece.html?export=1');
  await page.waitForFunction(()=>document.getElementById('animation').contentWindow?.ANIMATION_READY);
  const ack=await page.evaluate(async()=>{
   const node=document.getElementById('animation');
   await node.contentWindow.ANIMATION_READY;
   node.contentWindow.renderFrame=(seconds)=>{node.contentWindow.lastTime=seconds;};
   const request=frame=>new Promise(resolve=>{
    const id='fixture-'+frame;
    const listener=e=>{if(e.source===node.contentWindow&&e.data.id===id){window.removeEventListener('message',listener);resolve({...e.data,seconds:node.contentWindow.lastTime});}};
    window.addEventListener('message',listener);node.contentWindow.postMessage({type:'animation:frame',id,frame,fps:60,width:64,height:64},location.origin);
   });
   return [await request(30),await request(59),await request(60),await request(-1)];
  });
  assert.equal(ack[0].ok,true);assert.equal(ack[0].seconds,0.5);
  assert.equal(ack[1].ok,true);assert.equal(ack[1].seconds,23/24);
  assert.equal(ack[2].ok,false);assert.equal(ack[3].ok,false);
 });
 }finally{fs.rmSync(base,{recursive:true,force:true});}
});

test('browser: MP4 rejects odd dimensions before creating output', {skip:!runtime},()=>{
 const base=temp();try {
 const dir=fixture(base,{width:63}),out=path.join(base,'odd movie');
 const result=run(['render',dir,'--runtime',runtime,'--out',out,'--format','mp4']);
 assert.notEqual(result.status,0);assert.match(result.stderr,/requires even/);assert.equal(fs.existsSync(out),false);
 }finally{fs.rmSync(base,{recursive:true,force:true});}
});
test('browser: comparison grid follows displayed image width', {skip:!runtime},async()=>{
 const base=temp();try {
 const dir=fixture(base),reference=path.join(base,'reference.png'),out=path.join(base,'comparison');
 await withPiece(dir,runtime,async(page,t)=>{fs.writeFileSync(reference,(await capture(page,0,t)).bytes);});
 const result=run(['compare',dir,'--runtime',runtime,'--out',out,'--reference',reference]);assert.equal(result.status,0,result.stderr);
 await withPiece(dir,runtime,async(page)=>{
  const pixels=await page.evaluate(async png=>{const img=new Image();img.src='data:image/png;base64,'+png;await img.decode();const c=document.createElement('canvas');c.width=img.width;c.height=img.height;const g=c.getContext('2d');g.drawImage(img,0,0);return {line:[...g.getImageData(62,50,1,1).data],plain:[...g.getImageData(66,50,1,1).data]};},fs.readFileSync(path.join(out,'comparison.png')).toString('base64'));
  assert.ok(pixels.line[1]<230);assert.deepEqual(pixels.plain,[255,255,255,255]);
 });
 }finally{fs.rmSync(base,{recursive:true,force:true});}
});
