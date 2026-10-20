---
name: remotion
description: Render coded motion graphics with Remotion. Flow is the included library behind Tech Motion, Gentlemen handwriting and layered Sketch; a neutral starter checks the engine; examples cover Narrative Motion, the dedicated short and the 3D pan transition. Use when a chosen look renders in Remotion, when the person asks for Flow, a Remotion composition or overlay, a transparent ProRes render, or a JavaScript Canvas scene hosted inside a Remotion composition.
---

# Remotion

Renders the looks the [style skill](../style/SKILL.md) chooses. Flow, in `flow/`, is the Remotion library: diagram components, the full Gentlemen pen, glyph and caption set, the `JavaScriptAnimationFrame` bridge, bundled fonts with notices, scripts and `customer-config.json`. Tech Motion is the default look here; Gentlemen and Sketch layers render here too. `starter/` is a neutral engine check. Node 22 or newer is required.

## Procedure

1. Confirm the look and beat plan from the style skill and its guide. Read [flow/README.md](flow/README.md). Check Node, npm and FFmpeg; reuse the person's working Remotion project when it fits.
2. Decide where to work. A quick reproduction can run inside `flow/` as is. Anything customized (edited `customer-config.json`, new scenes, dependencies, renders) lives in a copy of `flow/` or `starter/` in the person's workspace, because the plugin folder is replaced on update. Install from the pinned lock only when the person chooses: `npm ci --ignore-scripts --no-audit --no-fund`. Remotion may download its render browser; its license applies, see [THIRD-PARTY](../../THIRD-PARTY.md).
3. Edit `customer-config.json` (palette, accent, deep green, background, font, words, fps, duration). Defaults are mint `#72DFA5`, dark green `#0F583D` and a neutral base; the profile wins. Match the project's frame rate. Type-check with `npm exec -- tsc --noEmit`.
4. Render with `npm exec -- remotion render src/index.ts <Composition> <new-file> --codec=h264 --crf=17`; compositions are `TechMotion`, `Gentlemen`, `Editorial`, `SketchLayers`, `GentlemenOverlay`, `NarrativeMotion`, `DedicatedShort`. Overlays use ProRes 4444, PNG frames, `yuva444p10le` and `--muted`; H.264 is opaque. For Gentlemen, export pen events with `scripts/export-pen-events.cjs` and render the marker WAV with the style skill's `gentlemen_selected_sound.py`, kept separate.
5. For a JavaScript scene from the [javascript-animation skill](../javascript-animation/SKILL.md), put its `index.html` in `public/animation/` and mount `<AnimationFrame src={staticFile('animation/index.html')} />` from [JavaScriptAnimationFrame.tsx](flow/src/components/JavaScriptAnimationFrame.tsx) at the piece's size. The bridge waits for each frame's acknowledgement; never a free-playing iframe. Test a short export with repeated and out-of-order frames. The optional swivel teaser follows [pan-3d-transition](references/pan-3d-transition.md) to a new output name.
6. Deliver the render, exact command and versions, the editable project, and a check in the receiving editor: alpha, frame rate, start and end frames, longest caption, narration balance. A browser preview or finished MP4 is not native acceptance.

## Files in this skill

| File | Use |
| --- | --- |
| [flow/README.md](flow/README.md) | Setup, commands, overlay route |
| [package.json](flow/package.json), [package-lock.json](flow/package-lock.json), [remotion.config.ts](flow/remotion.config.ts), [tsconfig.json](flow/tsconfig.json) | Pinned Remotion 4.0.499, PNG frames |
| [customer-config.json](flow/customer-config.json) | Palette, words, font, fps, duration |
| [Examples.tsx](flow/src/Examples.tsx), [Root.tsx](flow/src/Root.tsx), [index.ts](flow/src/index.ts) | The registered compositions |
| [components](flow/src/components/) | Components, `gentlemen/`, JavaScript bridge |
| [lib](flow/src/lib/) | Animation, lanes, master track, physics |
| [narrative](flow/src/narrative/) | Narrative Motion, dedicated short, primitives |
| [videos](flow/src/videos/), [main-style README](flow/src/videos/main-style/README.md) | Portrait captions, short-overlay compositor |
| [fonts.ts](flow/src/fonts.ts), [theme.ts](flow/src/theme.ts) | Font loading, four palettes |
| [public/fonts](flow/public/fonts/), [public/gentlemen/fonts](flow/public/gentlemen/fonts/) | Bundled fonts with OFL and MIT notices |
| [public/sketch](flow/public/sketch/) | Sketch practice layers and notice |
| [scripts](flow/scripts/) | Pen-event export, QA sheet, benches |
| [starter](starter/), [render.mjs](starter/scripts/render.mjs), [overlay-props.json](starter/overlay-props.json) | Neutral Remotion 4.0.535 engine check |
| [pan-3d-transition](references/pan-3d-transition.md), [pan_3d_transition.py](tools/pan_3d_transition.py), [insert_3d_transition.py](tools/insert_3d_transition.py) | Optional swivel teaser |
| [narrative-motion example](examples/narrative-motion/README.md) | Retained-object test; preview in [asset bundle](../../ASSETS.md) |
| [dedicated-short example](examples/dedicated-short/README.md) | Caption lane and camera handoff test |

## Scope and honesty

A rendered example proves its code path rendered once in the tested environment, not that a new composition is accurate or an editor imports its alpha. Say which renders were made and checked this session and which are only documented. Install nothing, download no browser and accept no license without the person's choice; nothing uploads, spends or publishes. Footage, approved cuts and the profile stay untouched; renders go to new names.
