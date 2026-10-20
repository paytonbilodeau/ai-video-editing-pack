#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {build,contained,SKILL,validateMeta} from './build.mjs';

const usage = `JavaScript animation (local, no accounts or global installs)
  setup <new-runtime-directory>          Install locked Playwright and Chromium
  doctor --runtime <directory>           Check browser and FFmpeg encoders
  init <new-piece-directory> [--style cut-paper]
  build <piece-directory>
  check <piece-directory> --runtime <directory> --out <new-directory>
  render <piece-directory> --runtime <directory> --out <new-directory> [--format png|mp4|prores] [--alpha] [--audio]
  storyboard <piece-directory> --runtime <directory> --out <new-directory>
  compare <piece-directory> --runtime <directory> --out <new-directory> --reference <local-png-or-jpg> [--frame 0]
  beats <local-track> --out <new-json-file> [--bpm 120] [--duration 30]
Rendering executes the piece's local JavaScript. Inspect source before use.
Check reports technical results only; review picture, typography and sound yourself.`;
export function parse(argv) {
  const [command,...args] = argv, options = {}, positionals = [];
  const valued = new Set(['runtime','out','style','format','reference','frame','bpm','duration']);
  for (let i=0;i<args.length;i++) {
    if (!args[i].startsWith('--')) {positionals.push(args[i]);continue;}
    const key = args[i].slice(2);
    if (['alpha','audio'].includes(key)) options[key] = true;
    else if (valued.has(key) && args[i+1] && !args[i+1].startsWith('--')) options[key] = args[++i];
    else throw Error(`unknown or incomplete option: ${args[i]}`);
  }
  if (positionals.length > 1) throw Error('unexpected positional arguments');
  return {command, target:positionals[0], options};
}
function run(command,args,extra={}) {
  const r=spawnSync(command,args,{encoding:'utf8',timeout:120000,maxBuffer:16*1024*1024,...extra});
  if (r.error || r.status !== 0) throw Error(`${command} failed: ${r.error?.message || r.stderr || r.status}`);
  return r.stdout;
}
function newPath(value) {
  if (!value) throw Error('an explicit new output path is required');
  const full=path.resolve(value);
  if (fs.existsSync(full)) throw Error('output already exists; choose a new path');
  // Do not resolve outputs through a symlinked ancestor.
  for (let p=path.dirname(full);p!==path.dirname(p);p=path.dirname(p)) if (fs.existsSync(p) && fs.lstatSync(p).isSymbolicLink()) throw Error('linked output ancestor forbidden');
  if (full.startsWith(SKILL+path.sep)) throw Error('write projects and runtime outside the source skill');
  return full;
}
function playwright(runtime) {
  if (!runtime) throw Error('--runtime is required; run setup first');
  const root=fs.realpathSync(runtime), require=createRequire(path.join(root,'package.json'));
  const installed=require(path.join(root,'node_modules/playwright/package.json')).version;
  const pinned=JSON.parse(fs.readFileSync(path.join(SKILL,'package.json'),'utf8')).dependencies.playwright;
  if(installed!==pinned) throw Error(`Playwright version mismatch: expected ${pinned}`);
  process.env.PLAYWRIGHT_BROWSERS_PATH=path.join(root,'browsers');
  return require(path.join(root,'node_modules/playwright'));
}
export async function withPiece(dir,runtime,fn) {
  const {html,meta}=build(dir);
  // Serve only the assembled document. Block all network requests from authored code.
  const server=http.createServer((req,res)=>{if(req.url?.split('?')[0]!=='/piece.html'){res.writeHead(404).end();return;}res.setHeader('Content-Type','text/html');res.setHeader('Content-Security-Policy',"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src data:; connect-src 'none'; frame-src 'self'");res.end(html);});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const origin=`http://127.0.0.1:${server.address().port}`;
  let browser;
  try {
    browser=await playwright(runtime).chromium.launch();
    const page=await browser.newPage({viewport:{width:meta.format.width,height:meta.format.height},deviceScaleFactor:1,serviceWorkers:'block'});
    const errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    await page.route('**/*',route=>route.request().url().startsWith(origin+'/piece.html') ? route.continue() : route.abort());
    await page.goto(origin+'/piece.html?export=1');
    await page.waitForFunction(()=>window.TIMELINE && typeof window.renderFrame==='function',{},{timeout:15000});
    await page.evaluate(()=>window.ANIMATION_READY);
    const t=validateMeta(await page.evaluate(()=>{const t=window.TIMELINE;return {width:t.width,height:t.height,fps:t.fps,frames:t.frames,duration:t.duration};}));
    for(const key of ['width','height','fps','frames','duration']) if(t[key]!==meta.format[key]) throw Error(`page and piece.json metadata disagree: ${key}`);
    if(errors.length) throw Error('page errors: '+errors.join('; '));
    await fn(page,t,{origin,browser,assertClean:()=>{if(errors.length)throw Error('page errors: '+errors.join('; '));}});
  } finally {if(browser) await browser.close(); await new Promise(resolve=>server.close(resolve));}
}
export async function capture(page,frame,t) {
  if(!Number.isInteger(frame)||frame<0||frame>=t.frames) throw Error('frame outside timeline');
  const r=await page.evaluate(({frame,t})=>{
    window.renderFrame(frame/t.fps);
    const c=document.getElementById('c');
    if(c.width!==t.width||c.height!==t.height) throw Error('canvas dimensions disagree');
    const data=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
    let alphaMin=255,alphaMax=0;
    for(let i=3;i<data.length;i+=4){alphaMin=Math.min(alphaMin,data[i]);alphaMax=Math.max(alphaMax,data[i]);}
    return {png:c.toDataURL('image/png').split(',')[1],alphaMin,alphaMax};
  },{frame,t});
  const bytes=Buffer.from(r.png,'base64');
  return {bytes,sha256:createHash('sha256').update(bytes).digest('hex'),alphaMin:r.alphaMin,alphaMax:r.alphaMax};
}
async function check(page,t) {
  const frames=[...new Set([0,Math.floor(t.frames/4),Math.floor(t.frames/2),t.frames-1])];
  const hashes={};
  for(const frame of frames) hashes[frame]=(await capture(page,frame,t)).sha256;
  for(const frame of [...frames].reverse().concat(frames)) if((await capture(page,frame,t)).sha256!==hashes[frame]) throw Error(`non-deterministic seek at frame ${frame}`);
  return {technicalStatus:'passed',scope:'same browser, machine and fonts; sampled repeat and out-of-order seeks',frameHashes:hashes,visualReview:'not performed',audioReview:'not performed'};
}
function writeJson(file,data){fs.writeFileSync(file,JSON.stringify(data,null,2)+'\n');}
export async function main(argv=process.argv.slice(2)) {
  const {command,target,options:o}=parse(argv);
  if(!command||command==='help'){console.log(usage);return;}
  if(command==='setup') {
    if(Number(process.versions.node.split('.')[0])<22) throw Error('Node.js 22 or newer is required');
    const dest=newPath(target);fs.mkdirSync(dest,{recursive:true});
    for(const f of ['package.json','package-lock.json']) fs.copyFileSync(path.join(SKILL,f),path.join(dest,f));
    run(process.platform==='win32'?'npm.cmd':'npm',['ci','--ignore-scripts','--no-fund','--no-audit'],{cwd:dest,timeout:300000});
    run(process.execPath,[path.join(dest,'node_modules/playwright/cli.js'),'install','chromium'],{env:{...process.env,PLAYWRIGHT_BROWSERS_PATH:path.join(dest,'browsers')},timeout:300000});
    console.log('Installed pinned local runtime: '+dest);return;
  }
  if(command==='doctor') {
    const browser=await playwright(o.runtime).chromium.launch();console.log('Chromium '+browser.version());await browser.close();
    const encoders=run('ffmpeg',['-hide_banner','-encoders']);
    console.log(JSON.stringify({node:process.versions.node,libx264:/\blibx264\b/.test(encoders),prores_ks:/\bprores_ks\b/.test(encoders)}));return;
  }
  if(command==='init') {
    const dest=newPath(target),style=o.style||'cut-paper';
    if(!/^[a-z0-9-]+$/.test(style)||!fs.existsSync(path.join(SKILL,'styles',style,'kit.js'))) throw Error('unknown shipped style');
    fs.cpSync(path.join(SKILL,'styles',style,'demo'),dest,{recursive:true});
    const file=path.join(dest,'piece.json'),meta=JSON.parse(fs.readFileSync(file));meta.style=style;writeJson(file,meta);
    console.log('Created '+dest);return;
  }
  if(command==='build'){if(!target)throw Error('piece directory required');console.log(build(target).output);return;}
  if(command==='beats') {
    const output=newPath(o.out),source=fs.realpathSync(target);
    const bpm=Number(o.bpm||120),duration=Number(o.duration||30);
    if(!Number.isFinite(bpm)||bpm<30||bpm>300||!Number.isFinite(duration)||duration<1||duration>600)throw Error('invalid BPM or duration');
    fs.mkdirSync(path.dirname(output),{recursive:true});
    run(process.execPath,[path.join(SKILL,'tools/beats.mjs'),source,output,'--bpm',String(bpm),'--dur',String(duration)]);
    console.log(output);return;
  }
  if(!['check','render','storyboard','compare'].includes(command))throw Error('unknown command');
  if(!target)throw Error('piece directory required');
  const format=o.format||'png';
  if(!['png','mp4','prores'].includes(format))throw Error('invalid export format');
  if(o.alpha && format==='mp4')throw Error('MP4/H.264 does not preserve alpha; use PNG or ProRes 4444');
  const out=newPath(o.out);
  if(command==='render'&&format!=='png'){const encoders=run('ffmpeg',['-hide_banner','-encoders']);const encoder=format==='mp4'?'libx264':'prores_ks';if(!encoders.includes(encoder))throw Error('missing FFmpeg encoder: '+encoder);}
  await withPiece(target,o.runtime,async(page,t,{assertClean})=>{
    if(command==='render'&&format==='mp4'&&(t.width%2||t.height%2))throw Error('MP4/yuv420p requires even width and height');
    const report=await check(page,t);
    fs.mkdirSync(out,{recursive:true});
    if(command==='render') {
      let alpha=false,visible=false;
      for(let frame=0;frame<t.frames;frame++) {
        const r=await capture(page,frame,t);alpha ||= r.alphaMin<255;visible ||= r.alphaMax>0;
        fs.writeFileSync(path.join(out,`f${String(frame).padStart(6,'0')}.png`),r.bytes);
      }
      if(!visible)throw Error('render is entirely transparent');
      if(o.alpha&&!alpha)throw Error('source is opaque: author transparent canvas content; export does not remove backgrounds');
      if(o.audio) {
        const wav=await page.evaluate(async()=>{if(typeof window.renderAudioWav!=='function')throw Error('no audio renderer');return window.renderAudioWav();});
        fs.writeFileSync(path.join(out,'audio.wav'),Buffer.from(wav,'base64'));
      }
      if(format!=='png') {
        const codec=format==='mp4'?['-c:v','libx264','-crf','16','-pix_fmt','yuv420p']:['-c:v','prores_ks','-profile:v','4','-pix_fmt','yuva444p10le','-alpha_bits','16'];
        run('ffmpeg',['-n','-hide_banner','-loglevel','error','-framerate',String(t.fps),'-i',path.join(out,'f%06d.png'),...(o.audio?['-i',path.join(out,'audio.wav'),'-c:a',format==='mp4'?'aac':'pcm_s24le']:[]),...codec,'-frames:v',String(t.frames),'-t',String(t.duration),path.join(out,format==='mp4'?'animation.mp4':'animation.mov')],{timeout:300000});
      }
      Object.assign(report,{format,alphaPresent:alpha,alphaRequested:!!o.alpha,audioIncluded:!!o.audio});
    }
    if(command==='storyboard') {
      const png=await page.evaluate(()=>{if(typeof window.renderBoard!=='function')throw Error('piece lacks renderBoard');return window.renderBoard().toDataURL('image/png').split(',')[1];});
      fs.writeFileSync(path.join(out,'storyboard.png'),Buffer.from(png,'base64'));
    }
    if(command==='compare') {
      const frame=Number(o.frame||0),r=await capture(page,frame,t);
      if(!o.reference||!/^\.(png|jpe?g)$/i.test(path.extname(o.reference)))throw Error('local PNG/JPEG reference required');
      const ref=fs.readFileSync(o.reference).toString('base64'),mime=/\.png$/i.test(o.reference)?'image/png':'image/jpeg';
      const png=await page.evaluate(async({ref,ours,mime})=>{
        const a=new Image(),b=new Image();a.src='data:'+mime+';base64,'+ref;b.src='data:image/png;base64,'+ours;await Promise.all([a.decode(),b.decode()]);
        const c=document.createElement('canvas');c.width=1080;c.height=600;const g=c.getContext('2d');g.fillStyle='#222';g.fillRect(0,0,1080,600);
        for(const [img,x] of [[a,0],[b,540]]) {const scale=Math.min(520/img.width,560/img.height),dw=img.width*scale,dh=img.height*scale,left=x+10;g.drawImage(img,left,30,dw,dh);g.strokeStyle='#ff668899';for(let i=1;i<10;i++){g.beginPath();g.moveTo(left+i*dw/10,30);g.lineTo(left+i*dw/10,30+dh);g.stroke();}}
        g.fillStyle='#fff';g.font='18px sans-serif';g.fillText('Reference',10,22);g.fillText('Rendered frame',550,22);return c.toDataURL('image/png').split(',')[1];
      },{ref,ours:r.bytes.toString('base64'),mime});
      fs.writeFileSync(path.join(out,'comparison.png'),Buffer.from(png,'base64'));
    }
    assertClean();
    writeJson(path.join(out,'report.json'),{...report,timeline:t});
  });
  console.log('Technical checks passed. Output: '+out+'; visual/audio acceptance remains separate.');
}
if(process.argv[1] && pathToFileURL(path.resolve(process.argv[1])).href===import.meta.url) main().catch(error=>{console.error('ERROR: '+error.message);process.exitCode=1;});
