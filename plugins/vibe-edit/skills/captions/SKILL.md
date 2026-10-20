---
name: captions
description: Add captions to a locked edit from real speech timing, in the ownership the person chooses: a clean master with editable sidecar files, assistant-made phrase captions, single-line dedicated-short captions, or cinematic captions embedded behind the speaker. Use when a person asks for captions, subtitles, SRT or VTT files, word timing, or captions behind the subject.
---

# Captions

Captions come after cut, sound and grade are locked, from the words spoken in the final timeline. Four ownership choices, one readability check. The person's profile at `Vibe Edit Settings/EDITING PROFILE.md` (5.x used `Vibe Editor Settings/`) and their current request override Payton-derived defaults; an approved style is never swapped for a historical one.

## Procedure

1. Read the profile. Confirm the locked export, rational frame rate, destination and ownership. Clean master means no burned captions.
2. Word timing: [video_word_timing.py](../edit/tools/video_word_timing.py) loads real Auphonic or Whisper word times without interpolation. [transcribe_local.py](../edit/tools/transcribe_local.py) estimates through an installed faster-whisper model, downloading nothing. After a cut, remap through the exact retained spans. Transcribed timing stays an estimate until checked against the recording; fix names and numbers by listening.
3. Deliver the chosen ownership:
   - **Clean master plus sidecars** for CapCut or their editor: clean export, SRT/VTT, word JSON, caption band left clear, no later burned layer.
   - **Phrase captions** in the editor: short natural groups, white type, soft shadow, subtle stroke, stable band clear of face and screen. Rules: [CAPTIONS AND FORMATS.md](<../edit/references/CAPTIONS AND FORMATS.md>); measured history: [caption-calibration.json](../edit/profiles/caption-calibration.json).
   - **Dedicated-short single line**: [dedicated-short-finishing.md](../style/references/tech-motion/references/dedicated-short-finishing.md). Measure the longest phrase in the real font, split at a word boundary, refit the lane.
   - **Embedded cinematic captions**: [embedded/GUIDE.md](embedded/GUIDE.md). One single-subject clip, footage untouched, one catalog identity, verbatim rail by default, one earned embed. Needs Node, FFmpeg and the sibling [HyperFrames runtime](../hyperframes/README.md) via `HYPERFRAMES_ROOT`; first run wants a matting model download and a Whisper engine, each the person's choice.
   - [rsvp_captions.py](../edit/tools/rsvp_captions.py): optional word-at-a-time style; strict timing by default.
4. Check at phone size with sound: names spelled right; eyes, mouth, controls and results clear; no overflow; nothing lost over bright clothing or screens.
5. Report what was burned, what shipped as files, which timings stay estimates, and what was watched.

## Files in this skill

| Item | Use |
| --- | --- |
| [embedded/GUIDE.md](embedded/GUIDE.md) | Decision gate, pipeline, visual QA and gates. |
| [CATALOG.md](embedded/CATALOG.md) | The 35 identities; pick one here, never ask about modes. |
| [dna/README.md](embedded/dna/README.md) | Ten cinematic DNAs as JSON; bright scenes want `ink`. |
| [themes/README.md](embedded/themes/README.md) | Themed looks as JSON; `anchor` is the quiet verbatim default. |
| [modes/cinematic/README.md](embedded/modes/cinematic/README.md) | Cinematic compiler notes, [engine.html](embedded/modes/cinematic/engine.html), the [cinematic-cream spec](embedded/modes/cinematic/cinematic-cream/spec.md), archived references. |
| [modes/standard/_anatomy.md](embedded/modes/standard/_anatomy.md), [_motion.md](embedded/modes/standard/_motion.md) | Retired standard engine and motion recipes; rail wiring reference. OFL fonts: [fonts.css](embedded/modes/standard/fonts/fonts.css), [build-fonts-css.cjs](embedded/modes/standard/fonts/build-fonts-css.cjs). |
| [prepare.sh](embedded/scripts/prepare.sh) | Runs [matte.cjs](embedded/scripts/matte.cjs), [transcribe.cjs](embedded/scripts/transcribe.cjs), [audio-envelope.cjs](embedded/scripts/audio-envelope.cjs), then [safe-zones.cjs](embedded/scripts/safe-zones.cjs). |
| Compilers | [make-cinematic.cjs](embedded/scripts/make-cinematic.cjs), [make-composition.cjs](embedded/scripts/make-composition.cjs), [make-theme.cjs](embedded/scripts/make-theme.cjs), [lib-dna.cjs](embedded/scripts/lib-dna.cjs), [fill-timings.cjs](embedded/scripts/fill-timings.cjs), [fit-fonts.cjs](embedded/scripts/fit-fonts.cjs), [measure-layout.cjs](embedded/scripts/measure-layout.cjs), [inject-fonts.cjs](embedded/scripts/inject-fonts.cjs), [gen-stroke-path.py](embedded/scripts/gen-stroke-path.py). |
| QA gates | [preview-frames.cjs](embedded/scripts/preview-frames.cjs), [check-timing.cjs](embedded/scripts/check-timing.cjs), [check-occlusion.cjs](embedded/scripts/check-occlusion.cjs), [check-overflow.cjs](embedded/scripts/check-overflow.cjs), [check-rail-climax.cjs](embedded/scripts/check-rail-climax.cjs). |
| Render | [render-and-composite.sh](embedded/scripts/render-and-composite.sh), [render-theme.sh](embedded/scripts/render-theme.sh). |
| Tests | [make-theme.test.mjs](embedded/scripts/make-theme.test.mjs), [preview-frames.test.mjs](embedded/scripts/preview-frames.test.mjs), fixture [heroless/theme.json](embedded/scripts/fixtures/heroless/theme.json) with [transcript.json](embedded/scripts/fixtures/heroless/transcript.json). |
| [aesthetic-principles.md](embedded/references/aesthetic-principles.md) | Eighteen rules separating designed from preset captions. |
| [anti-patterns.md](embedded/references/anti-patterns.md) | Default mistakes and fixes. |
| [rail.md](embedded/references/rail.md) | The plain lower-third rail carrying most text. |
| [composition-craft.md](embedded/references/composition-craft.md) | Laying an embed into the scene. |
| [caption-grouping.md](embedded/references/caption-grouping.md) | Word timing into phrase groups. |
| [layout-heuristics.md](embedded/references/layout-heuristics.md) | Wall and crown positions from sampled frames. |
| [scene-types.md](embedded/references/scene-types.md) | Which surface the text sits on. |
| [direction-catalog.md](embedded/references/direction-catalog.md) | Ten aesthetic directions by tone, shot, platform. |
| [typography-presets.md](embedded/references/typography-presets.md) | Five `cap-*` styles by semantic role. |
| [typographic-moves.md](embedded/references/typographic-moves.md) | Per-group typography beyond presets. |
| [motion-vocabulary.md](embedded/references/motion-vocabulary.md) | Ten word-entry moves and exit rules. |
| [bespoke-vs-presets.md](embedded/references/bespoke-vs-presets.md) | When to override presets or clone a render. |
| [failure-modes.md](embedded/references/failure-modes.md) | Known breakages in matting, timing, render. |
| [reference-bar.md](embedded/references/reference-bar.md) | Positive checks before shipping. |
| [champion.html](embedded/references/example-renders/champion.html), [memory-wall.html](embedded/references/example-renders/memory-wall.html) | Archived examples; each expects a local `source.mp4`. |
| [char-widths.json](embedded/assets/fonts/char-widths.json) | Measured glyph widths for font fitting. |
| [HersheyScript1.svg](embedded/assets/strokefonts/HersheyScript1.svg), [HersheyScriptMed.svg](embedded/assets/strokefonts/HersheyScriptMed.svg) | Stroke fonts for draw-on paths; attribution inside. |
| [embedded/.gitignore](embedded/.gitignore) | Keeps project outputs out of the skill folder. |

## Scope and honesty

Captions promise no retention gain; the person judges them on their footage. The edit-side tools carry tests; the embedded engine is an upstream HyperFrames skill ([Apache-2.0](../../licenses/HyperFrames-Apache-2.0.txt), [THIRD-PARTY.md](../../THIRD-PARTY.md)) with path adapters, documented rather than tested on every machine. No upload, provider, model download, publication or permission change without the person's choice. Recording and clean master stay untouched; embedded captions ship as a separate file.
