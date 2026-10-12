import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';

// Use a separate renderer process. This never opens a person's browser profile.
const require = createRequire(import.meta.url);
const explicit = process.env.REMOTION_BROWSER_EXECUTABLE;
if (explicit && !fs.existsSync(explicit)) {
  console.error('REMOTION_BROWSER_EXECUTABLE does not point to an installed browser.');
  process.exit(1);
}
const candidates = process.platform === 'darwin'
  ? ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
  : process.platform === 'win32'
    ? [process.env.PROGRAMFILES, process.env['PROGRAMFILES(X86)'], process.env.LOCALAPPDATA]
      .filter(Boolean).map(root => path.join(root, 'Google', 'Chrome', 'Application', 'chrome.exe'))
    : ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'];
const browser = explicit || candidates.find(p => fs.existsSync(p));
const overlay = process.argv.slice(2).includes('--overlay');
const args = ['render', 'src/index.ts', 'NeutralMotion',
  overlay ? 'out/neutral-motion.mov' : 'out/neutral-motion.mp4', '--muted'];
if (overlay) args.push('--props=overlay-props.json', '--codec=prores',
  '--prores-profile=4444', '--pixel-format=yuva444p10le', '--image-format=png');
if (browser) args.push('--browser-executable=' + browser);
console.log(browser ? 'Using an installed browser in a separate rendering process.'
  : 'Using Remotion\'s managed headless browser; first use may download it.');
const cli = path.join(path.dirname(require.resolve('@remotion/cli/package.json')), 'remotion-cli.js');
const result = spawnSync(process.execPath, [cli, ...args], {stdio: 'inherit'});
if (result.error) console.error(result.error.message);
process.exit(result.status ?? 1);
