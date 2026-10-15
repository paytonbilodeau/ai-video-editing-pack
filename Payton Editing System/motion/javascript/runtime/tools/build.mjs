// Adapted from cth9191/animate (MIT), pinned in THIRD-PARTY.md.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
export const SKILL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DEFAULT = ['src/head.html','kit/core.js','style','src/scenes.js','src/bridges.js','kit/morph.js','kit/board.js','kit/score-head.js','src/score.js','kit/score-tail.js'];
export function contained(root, relative) {
  if (typeof relative !== 'string' || !relative || relative.includes('\\') || relative.split('/').includes('..') || path.isAbsolute(relative)) throw Error('unsafe relative path');
  const base = fs.realpathSync(root), full = path.resolve(base, relative);
  if (!full.startsWith(base + path.sep)) throw Error('path escapes root');
  const real = fs.realpathSync(full);
  if (!real.startsWith(base + path.sep)) throw Error('linked path escapes root');
  return real;
}
export function validateMeta(t) {
  if (!t || typeof t !== 'object') throw Error('missing timeline metadata');
  for (const [key, max] of [['width',4096],['height',4096],['fps',120],['frames',36000]]) {
    if (!Number.isInteger(t[key]) || t[key] < 1 || t[key] > max) throw Error(`invalid metadata: ${key}`);
  }
  if (!Number.isFinite(t.duration) || t.duration <= 0 || Math.abs(t.duration * t.fps - t.frames) > 0.01) throw Error('invalid metadata: duration/frames mismatch');
  return t;
}
function json(value) { return JSON.stringify(value).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029'); }
export function build(dir) {
  const root = fs.realpathSync(dir);
  const meta = JSON.parse(fs.readFileSync(contained(root,'piece.json'),'utf8'));
  validateMeta(meta.format);
  const style = meta.style || 'cut-paper';
  if (!/^[a-z0-9][a-z0-9-]*$/.test(style)) throw Error('invalid style name');
  const parts = meta.build ?? (meta.scenes ? DEFAULT.flatMap(p => p === 'src/scenes.js' ? meta.scenes : [p]) : DEFAULT);
  if (!Array.isArray(parts) || !parts.length || parts.length > 100) throw Error('invalid build parts');
  const resolve = part => {
    if (part === 'style') return fs.existsSync(path.join(root,'styles',style,'kit.js')) ? contained(root,`styles/${style}/kit.js`) : contained(SKILL,`styles/${style}/kit.js`);
    return contained(part?.startsWith('kit/') ? SKILL : root,part);
  };
  let html = parts.map(p => fs.readFileSync(resolve(p),'utf8').trimEnd()).join('\n') + '\n';
  if ((html.match(/<script>/g)||[]).length !== 1 || (html.match(/<\/script>/g)||[]).length !== 1) throw Error('expected one inline script');
  if (!/\bconst STYLE\s*=/.test(html)) throw Error('missing STYLE hooks');
  if (/data:[a-z]+\/|https?:\/\//i.test(html)) throw Error('external or embedded source URL forbidden; use local assets');
  const inject = [];
  for (const [name, variable] of [['beats.json','BEATS'],['voice.json','VOICE']]) {
    if (fs.existsSync(path.join(root,name))) inject.push(`const ${variable} = ${json(JSON.parse(fs.readFileSync(contained(root,name),'utf8')))};`);
  }
  const assets = {}, mime = {png:'image/png',jpg:'image/jpeg',jpeg:'image/jpeg',webp:'image/webp'};
  if (fs.existsSync(path.join(root,'assets'))) {
    for (const name of fs.readdirSync(contained(root,'assets'))) {
      const type = mime[path.extname(name).slice(1).toLowerCase()];
      if (type) assets[name] = `data:${type};base64,${fs.readFileSync(contained(root,`assets/${name}`)).toString('base64')}`;
    }
  }
  inject.push(`const ASSETS = {}; window.ASSETS_READY = Promise.all(Object.entries(${json(assets)}).map(([k,u]) => {const i=new Image(); i.src=u; ASSETS[k]=i; return i.decode();}));`);
  html = html.replace('<script>','<script>\n' + inject.join('\n'));
  const bridge = fs.readFileSync(path.join(SKILL,'adapters/frame-bridge.js'),'utf8');
  html = html.replace('</script>', '\n' + bridge + '\n</script>');
  new vm.Script(html.match(/<script>([\s\S]*)<\/script>/)[1]);
  // Carry the network policy into previews and Remotion's same-origin public folder.
  const csp = `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src data:; connect-src 'none'; frame-src 'self'; base-uri 'none'; form-action 'none'">`;
  html = /<head(?:\s[^>]*)?>/i.test(html) ? html.replace(/<head(?:\s[^>]*)?>/i, match => match + csp) : /^<!doctype[^>]*>/i.test(html) ? html.replace(/^<!doctype[^>]*>/i, match => match + csp) : csp + html;
  const output = path.join(root,'index.html');
  if (fs.existsSync(output) && fs.lstatSync(output).isSymbolicLink()) throw Error('refusing linked build output');
  fs.writeFileSync(output,html);
  return {html,meta,output};
}
