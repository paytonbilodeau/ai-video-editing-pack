#!/usr/bin/env node
// Compatibility entry for the repository quality workflow only.
// The tool lives at plugins/vibe-edit/skills/javascript-animation/runtime/tools/animate.mjs.
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const real = path.resolve(here, '../../../../plugins/vibe-edit/skills/javascript-animation/runtime/tools/animate.mjs');
const result = spawnSync(process.execPath, [real, ...process.argv.slice(2)], { stdio: 'inherit' });
process.exit(result.status ?? 1);
