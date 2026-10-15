#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const target = process.argv[2];
if (!target || process.argv.length !== 3) {
  console.error('Usage: node new-piece.mjs <new-project-directory>');
  process.exit(2);
}
const dest = path.resolve(target);
if (fs.existsSync(dest)) {
  console.error(`Refusing to overwrite an existing path: ${dest}`);
  process.exit(1);
}
const source = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../templates/payton-mentorship');
fs.mkdirSync(path.dirname(dest), {recursive: true});
fs.cpSync(source, dest, {recursive: true, errorOnExist: true, force: false});
console.log(`Created Payton-derived JavaScript piece: ${dest}`);
