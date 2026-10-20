---
name: javascript-animation
description: Create deterministic HTML Canvas motion graphics from local JavaScript: the Tech Motion template, seven public styles (cut-paper, crosshatch, riso, sketchbook, math, isometric, pixel), Playwright frame checks, PNG, MP4 or ProRes output, and embedding inside a Remotion composition. Use when the person asks for JavaScript animation, a procedural diagram or drawing, a code-driven scene, one of the seven styles, or a Canvas scene hosted in Remotion.
---

# JavaScript animation

Code-drawn graphics with exact frame control. `templates/payton-mentorship` is the Tech Motion template: a transparent 1080×1920 canvas, mint on neutral. `runtime/` is the adapted [cth9191/animate](https://github.com/cth9191/animate) kit under MIT: CLI, seven styles with demos, templates, Remotion adapter, tests. Node 22 or newer, FFmpeg for movies, and a pinned Playwright and Chromium runtime installed where and when the person chooses.

## Procedure

1. Read [README](README.md), [PAYTON GUIDE](<references/PAYTON GUIDE.md>), [profile](references/profile.md) and [CORE GUIDE](<references/CORE GUIDE.md>), then [runtime/GUIDE](runtime/GUIDE.md) for commands. Confirm the message, duration, dimensions, fps, format, transparency and audio from the brief and profile.
2. `node scripts/new-piece.mjs <new-dir>` starts the Tech Motion template. For a shipped style run `init --style <name>`, read its `STYLE.md` and `sample.webp`, start from its demo. Never substitute `sketchbook` for Sketch or Gentlemen. A custom style lives in the piece's `styles/<name>/kit.js`.
3. Set up once from this skill folder: `node runtime/tools/animate.mjs setup <runtime-dir>`, then `doctor --runtime <runtime-dir>`. Keep runtime, pieces and outputs outside the plugin, in new folders.
4. Author `src/` and `piece.json`: `renderFrame(seconds)` redraws the whole frame from absolute time and seeded randomness; `piece.json` must match `window.TIMELINE`. Then `build`, `check`, `storyboard` and `compare --reference` with an authorized still. Music-led work runs `beats` and corrects the grid by ear; voice-led work cues from a reviewed `voice.json`.
5. Render `--format png --alpha` or `--format prores --alpha` for transparency, `--format mp4` for opaque scenes with even dimensions. The seven demos paint opaque paper; the Tech Motion template clears each frame. Inspect start, transitions and end at full and phone size, with sound.
6. Inside Remotion, put the built `index.html` in `public/animation/` and mount `<AnimationFrame src={staticFile('animation/index.html')} />` from Flow's [JavaScriptAnimationFrame](../remotion/flow/src/components/JavaScriptAnimationFrame.tsx) (identical to [adapters/AnimationFrame.tsx](runtime/adapters/AnimationFrame.tsx)). Size the composition from `piece.json`, keep host duration within the source, add exported audio with `Audio`. Host fps may differ; the bridge maps each host frame to the nearest source frame and acknowledges it before Remotion continues. Test a short export with repeated and out-of-order frames; fall back to PNG frames with `Img` if iframes cannot embed. [remotion](../remotion/SKILL.md) owns the composition.
7. Deliver source, built HTML, exact frame rate, frames or movie, separate audio, technical report and remaining review limits.

## Files in this skill

| File | Use |
| --- | --- |
| [README](README.md) | Tech Motion route |
| [PAYTON GUIDE](<references/PAYTON GUIDE.md>) | Determinism, Remotion bridge, alpha |
| [CORE GUIDE](<references/CORE GUIDE.md>) | Seven-step workflow, safety notes |
| [profile](references/profile.md) | Colors, regions, movement |
| [new-piece.mjs](scripts/new-piece.mjs) | Template copier |
| [template](templates/payton-mentorship/), [brief](templates/payton-mentorship/brief.md) | Transparent Tech Motion proof |
| [runtime GUIDE](runtime/GUIDE.md) | Setup, timing, voice, beats, alpha, tests |
| [runtime WORKFLOW](runtime/WORKFLOW.md) | Upstream workflow |
| [styles README](runtime/styles/README.md), [styles](runtime/styles/) | Style hooks, reserved names, porting |
| [cut-paper](runtime/styles/cut-paper/STYLE.md), [crosshatch](runtime/styles/crosshatch/STYLE.md), [riso](runtime/styles/riso/STYLE.md), [sketchbook](runtime/styles/sketchbook/STYLE.md), [math](runtime/styles/math/STYLE.md), [isometric](runtime/styles/isometric/STYLE.md), [pixel](runtime/styles/pixel/STYLE.md) | Each: `STYLE.md`, `kit.js`, `sample.webp`, `demo/` |
| [kit](runtime/kit/) | core, morph, board, score |
| [adapters](runtime/adapters/) | `AnimationFrame.tsx`, `frame-bridge.js` |
| [templates](runtime/templates/) | `piece/`, `beat-cut/`, `style/kit.js` |
| [animate.mjs](runtime/tools/animate.mjs), [build.mjs](runtime/tools/build.mjs), [beats.mjs](runtime/tools/beats.mjs) | CLI, builder, beat analysis |
| [animation.test.mjs](runtime/tests/animation.test.mjs) | Offline tests; `ANIMATION_RUNTIME` adds browser runs |
| [package.json](runtime/package.json), [package-lock.json](runtime/package-lock.json) | Playwright 1.63.0 pin |
| [THIRD-PARTY](runtime/THIRD-PARTY.md), [LICENSE.upstream](runtime/LICENSE.upstream) | Upstream commit, changes, MIT license |

## Scope and honesty

A passing `check` proves repeatable frames in that browser, OS and font environment, not the story, picture or sound; pixel equality across platforms is not promised. Say which pieces were rendered and watched this session and which are only documented. Setup installs only pinned Playwright and Chromium, where and when the person chooses; no account, API key, global package or paid service is required; nothing uploads, spends or publishes. Recording, edit and profile stay untouched.
