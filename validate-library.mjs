import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import crypto from 'node:crypto';

const root=path.dirname(fileURLToPath(import.meta.url));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
const expectedNames=['AI Video Editing Pack'];
const errors=[];
if (JSON.stringify(manifest.systems.map(s=>s.name))!==JSON.stringify(expectedNames) || manifest.systems[0]?.id!=='01' || manifest.repository!=='paytonbilodeau/ai-video-editing-pack') errors.push('This repository must contain only the AI Video Editing Pack under its canonical repository name.');
const expected=new Set(manifest.files);
const actual=[];
function walk(dir) {
  for (const entry of fs.readdirSync(dir,{withFileTypes:true})) {
    const full=path.join(dir,entry.name);
    const rel=path.relative(root,full).split(path.sep).join('/');
    if (entry.isSymbolicLink()) { errors.push('Symlink forbidden: '+rel); continue; }
    if (dir===root && entry.isDirectory() && ['.build','.swiftpm'].includes(entry.name)) continue;
    if (['.git','node_modules','__pycache__','dist','.DS_Store','Thumbs.db'].includes(entry.name)) continue;
    if (entry.isDirectory()) walk(full);
    else actual.push(rel);
  }
}
walk(root);
for (const file of actual) {
  if (!expected.has(file)) errors.push('Undeclared file: '+file);
  const text=fs.readFileSync(path.join(root,file),'utf8');
  if (!text.trim()) errors.push('Empty file: '+file);
  if (/\/Users\/paytonbilodeau|\/Desktop\/Super Intelligence|gh[pousr]_[A-Za-z0-9]{20,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|-----BEGIN [A-Z ]*PRIVATE KEY-----/.test(text)) errors.push('Private path or credential pattern: '+file);
  if (file.endsWith('.json')) {
    try { JSON.parse(text); } catch { errors.push('Invalid JSON: '+file); }
  }
  if (file.endsWith('.md')) {
    for (const match of text.matchAll(/\]\((<[^>\n]+>|[^)\n]+)\)/g)) {
      let target=match[1].replace(/^<|>$/g,'');
      if (/^(https?:|mailto:|#|[A-Z][A-Z0-9_]+$)/.test(target)) continue;
      target=decodeURIComponent(target.split('#')[0]);
      const resolved=path.resolve(path.dirname(path.join(root,file)),target);
      if (!resolved.startsWith(root+path.sep) || !fs.existsSync(resolved)) errors.push('Broken or escaping link in '+file+': '+target);
    }
  }
}
for (const file of expected) if (!actual.includes(file)) errors.push('Missing declared file: '+file);
for (const file of actual) if (/^(0[1-468]|0[237]|1[123]) /.test(file) || /^(memory|private|customer|credentials)\//.test(file)) errors.push('Outside public editing scope: '+file);
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
const pluginRoot=path.join(root,'plugins/vibe-edit');
const bundle=JSON.parse(fs.readFileSync(path.join(pluginRoot,'bundle-manifest.json'),'utf8')).files;
const bundleErrors=[];
// 6.0.0 shipped with one stale bundle entry: the build rewrote this file after hashing. Pinned to its released bytes.
const knownReleased={'practice/synthetic-lamp/SHA256.json':'199f9d4bf69cafdbab5b652fc3eb9f7d1be4e725fe794363a80ad9664ba8dedd'};
for (const [file,digest] of Object.entries(bundle)) {
  const full=path.join(pluginRoot,file);
  if (!fs.existsSync(full)) { bundleErrors.push('Missing plugin file: '+file); continue; }
  const actualDigest=crypto.createHash('sha256').update(fs.readFileSync(full)).digest('hex');
  if (actualDigest!==digest && actualDigest!==knownReleased[file]) bundleErrors.push('Plugin file differs from its bundle manifest: '+file);
}
if (bundleErrors.length) { console.error('Plugin bundle validation failed:\n'+bundleErrors.join('\n')); process.exit(1); }
console.log('Plugin bundle manifest matches '+Object.keys(bundle).length+' files.');
const skills='plugins/vibe-edit/skills/';
const suites=[
 [skills+'javascript-animation/runtime',[process.execPath,'--test','tests/animation.test.mjs']],
 [skills+'setup/tools',['python3','-B','-m','unittest','discover','-s','tests','-p','test_*.py']],
 [skills+'edit/tools',['python3','-B','-m','unittest','discover','-s','tests','-p','test_*.py']],
 [skills+'editors/tools',['python3','-B','-m','unittest','discover','-s','tests','-p','test_*.py']],
 [skills+'pre-edit/tools',['python3','-B','-m','unittest','discover','-s','tests','-p','test_*.py']],
 [skills+'style/planning/tools',[process.execPath,'--test',...fs.readdirSync(path.join(root,skills+'style/planning/tools/tests')).filter(f=>f.endsWith('.test.mjs')).map(f=>'tests/'+f)]],
 [skills+'shorts/tools',['python3','-B','-m','unittest','discover','-s','tests','-p','test_*.py']]
];
if (!process.argv.includes('--structure-only')) {
  for (const [dir,command] of suites) {
    const run=spawnSync(command[0],command.slice(1),{cwd:path.join(root,dir),encoding:'utf8',timeout:240000});
    if (run.error || run.status!==0) {
      console.error(dir,run.error||run.stderr||run.stdout);process.exit(1);
    }
    process.stdout.write(dir+': '+(run.stderr||run.stdout).trim()+'\n');
  }
}
console.log('Public validation passed: Vibe Edit plugin (AI Video Editing Pack repository), '+actual.length+' declared files, no private-system folders, no broken internal links'+(process.argv.includes('--structure-only')?'':', seven editing tool suites')+'.');
