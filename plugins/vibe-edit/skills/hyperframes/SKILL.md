---
name: hyperframes
description: Build, check and render HTML/GSAP video compositions with the pinned local HyperFrames runtime, four reviewed templates, a neutral starter and 23 upstream workflows for explainers, overlays, decks, motion graphics and Remotion ports. Use when a person asks for HyperFrames, an HTML or GSAP animation, a browser-rendered overlay for their editor, or names one of the workflows in this skill.
---

# HyperFrames

HyperFrames renders video from HTML: `data-*` attributes set timing, one paused GSAP timeline drives motion and the framework owns media playback, so frames are deterministic and seekable. [run.mjs](run.mjs) pins HyperFrames 0.8.150 with telemetry and skill refresh off. Output: MP4 or ProRes 4444 overlay. The person's profile at `Vibe Edit Settings/EDITING PROFILE.md` (5.x used `Vibe Editor Settings/`) and their current request override Payton-derived defaults.

## Procedure

1. Read the profile, [README.md](README.md) and the [portable contract](workflows/hyperframes/references/portable-contract.md). Confirm deliverable, canvas, frame rate, overlay or not.
2. Node 22+, npm, FFmpeg and a Chrome path are required. Work in a copy outside the plugin. `npm ci --ignore-scripts`, any `@latest` upgrade and any network skill refresh are the person's choice; nothing installs on its own.
3. Existing project: only the requested operation. Quick graphic: a template or the starter. Fresh build: the routing table in [workflows/hyperframes/GUIDE.md](workflows/hyperframes/GUIDE.md), then the matched workflow.
4. Local media, fonts and scripts only; static root canvas, animated inner wrappers, timeline registered after construction.
5. Run `node run.mjs check --dir <project> --strict`, render at the project frame rate, inspect frame zero, every join and the final frame. MP4 is opaque; an alpha MOV is proven only by import into the person's editor.
6. Deliver the project folder, render, commands run, and what was watched.

Upstream guides name each other as skills (`/hyperframes-core`, `$media-use`). Here those are the `workflows/<name>/GUIDE.md` folders below; `/embedded-captions` is [../captions/embedded/GUIDE.md](../captions/embedded/GUIDE.md). A guide's upload, publish, provider or refresh step is an available action, not permission.

## Files in this skill

| Item | Use |
| --- | --- |
| [README.md](README.md) | Runtime notes, commands, provider boundary. |
| [run.mjs](run.mjs), [package.json](package.json), [package-lock.json](package-lock.json) | Pinned CLI wrapper and lockfile. |
| [starter/README.md](starter/README.md) | Neutral five-second graphic; first test project. |
| [templates/motion-wide/index.html](templates/motion-wide/index.html) | 12 s 16:9 word, line and media reveal. |
| [templates/motion-portrait/index.html](templates/motion-portrait/index.html) | The same reveal at 9:16. |
| [templates/gentlemen-hybrid/index.html](templates/gentlemen-hybrid/index.html) | Base, handwriting alpha and marker sound; [layered-job.json](templates/gentlemen-hybrid/layered-job.json) needs `assets/overlay.mov` from the [asset bundle](../../ASSETS.md). |
| [templates/alpha-proof/index.html](templates/alpha-proof/index.html) | Transparency fixture for alpha import. |

## Workflows

| Workflow | Use when |
| --- | --- |
| [hyperframes](workflows/hyperframes/GUIDE.md) | Entry point and routing table. |
| [hyperframes-core](workflows/hyperframes-core/GUIDE.md) | Composition contract; read before writing HTML. |
| [hyperframes-cli](workflows/hyperframes-cli/GUIDE.md) | init, check, preview, render, doctor; build failures. |
| [hyperframes-registry](workflows/hyperframes-registry/GUIDE.md) | Registry blocks, components, `hyperframes.json`. |
| [hyperframes-keyframes](workflows/hyperframes-keyframes/GUIDE.md) | Seek-safe zooms, camera moves, masks, 3D. |
| [hyperframes-animation](workflows/hyperframes-animation/GUIDE.md) | Motion rules, blueprints, transitions, runtime adapters. |
| [hyperframes-audio](workflows/hyperframes-audio/GUIDE.md) | Mixing placed audio: fades, ducking, effects. |
| [hyperframes-creative](workflows/hyperframes-creative/GUIDE.md) | Design specs, palettes, typography, narration. |
| [media-use](workflows/media-use/GUIDE.md) | Sourcing or generating media; treating dull footage. |
| [general-video](workflows/general-video/GUIDE.md) | Custom or multi-scene piece when nothing else fits. |
| [motion-graphics](workflows/motion-graphics/GUIDE.md) | Short unnarrated unit: kinetic type, stat, logo. |
| [slideshow](workflows/slideshow/GUIDE.md) | Navigable deck, not an MP4; confirm first. |
| [talking-head-recut](workflows/talking-head-recut/GUIDE.md) | Graphic overlay cards on untouched footage. |
| [faceless-explainer](workflows/faceless-explainer/GUIDE.md) | Topic or notes into an invented-visual explainer. |
| [product-launch-video](workflows/product-launch-video/GUIDE.md) | Product URL or brief into a promo. |
| [pr-to-video](workflows/pr-to-video/GUIDE.md) | Pull request into a code-change explainer. |
| [remotion-to-hyperframes](workflows/remotion-to-hyperframes/GUIDE.md) | Explicit Remotion port only. |
| [figma](workflows/figma/GUIDE.md) | Figma frames and tokens into a composition. |
| [improve-animations](workflows/improve-animations/GUIDE.md) | Read-only motion audit with plans. |
| [review-animations](workflows/review-animations/GUIDE.md) | Review animation code against a craft bar. |
| [find-animation-opportunities](workflows/find-animation-opportunities/GUIDE.md) | Read-only search for missing motion. |
| [animation-vocabulary](workflows/animation-vocabulary/GUIDE.md) | Name a motion effect from a description. |
| [music-to-video](workflows/music-to-video/GUIDE.md) | Beat-synced video from a track; masks in the asset bundle. |

## License and provenance

The workflows are Apache-2.0 upstream HyperFrames skills: [license](../../licenses/HyperFrames-Apache-2.0.txt), [THIRD-PARTY.md](../../THIRD-PARTY.md). Substitutions recorded there: Pixabay SFX replaced by procedural sounds, 66 texture masks replaced by abstract masks, GSAP under its own license. Masks and the Gentlemen overlay are in the optional [asset bundle](../../ASSETS.md). Model downloads and providers follow [optional providers](<../style/tools/OPTIONAL PROVIDERS.md>).

## Scope and honesty

No render promises a result; the person judges the frames. The templates and starter were built against the pinned runtime; the guides are upstream documentation, not routes tested here. No uploads, spending, publishing, permission changes or installs without the person's choice. Originals stay untouched; work in copies.
