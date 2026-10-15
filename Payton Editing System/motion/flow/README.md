# Render Payton's actual motion building blocks

Use a **new working copy of the whole motion folder**. Node22 or newer and npm are required. Remotion may download its render browser on the first render. The included Remotion code is subject to [Remotion's license](https://www.remotion.dev/license), including its company-size/commercial licensing rules. Setup does not buy or activate a license.

From the copied `motion/flow` folder:

```sh
npm ci --ignore-scripts --no-audit --no-fund
npm exec -- tsc --noEmit
npm exec -- remotion render src/index.ts TechMotion tech.mp4 --codec=h264 --crf=17
npm exec -- remotion render src/index.ts Gentlemen gentlemen.mp4 --codec=h264 --crf=17
npm exec -- remotion render src/index.ts Editorial editorial.mp4 --codec=h264 --crf=17
npm exec -- remotion render src/index.ts SketchLayers sketch.mp4 --codec=h264 --crf=17
```

Each is a silent five-second 1920×1080 example at30fps by default. Open the actual MP4. The Tech example reveals three cards; Gentlemen writes then holds; Editorial draws a fine rule; Sketch moves a paper behind an original generated folder. These are synthetic practice examples, not an actual edited customer video. Original PNGs stay in `public/sketch/`.

Change `customer-config.json` for wording, mint/deep green, background, font selection, frame rate and duration. Your external editing profile remains the source of preferences. Changing duration alone does not retime a story; inspect the entrance, hold and ending. Choose a font you have licensed and load it explicitly in `src/fonts.ts` or the Gentlemen font loader. Existing palette names and all components remain available.

## Keep layers editable

```sh
npm exec -- remotion render src/index.ts GentlemenOverlay ink.mov --codec=prores --prores-profile=4444 --image-format=png --pixel-format=yuva444p10le --muted
node scripts/export-pen-events.cjs pen-events.json
python3 ../tools/gentlemen_selected_sound.py --events pen-events.json --output marker.wav
```

The last command needs the Python sound dependencies in [tools](../tools/README.md). It uses the actual selected85% Feather squeak/15% Thin nib blend and silent holds. Keep WAV separate from video; for narrated shorts the retained starting preference is another6dB below this standard stem, applied **once**, then judged under the actual voice. The selected-sound implementation accepts integer frame rates that divide48000; fractional rates are deliberately rejected. A fractional project needs an independently checked timing/audio adaptation, not a rounded FPS label.

Import `ink.mov` above your video and `marker.wav` on a separate track in a duplicated timeline. Check the real editor's alpha interpretation, frame rate, start/end and narration. A movie rendering does not prove a native-editor import.

## Included code

`src/components/` contains the original cards, connectors, counters, charts, Blueprint/Variety/Motion/Evidence/Physical components, JavaScript frame bridge and full Gentlemen pen glyphs/components. `src/lib/` includes animation, geometry, physics and the legacy lane planner. `StepRail` retains the real step-indicator mechanism with actual canvas centering. Its optional FPS input avoids silently changing existing callers.

The historical lane planner remains available for reproducing that approach, including its old variety quotas. It is **not the default editorial authority**. The current brief and customer profile decide whether a graphic is useful; no quota requires motion, proof images or physics. `NEED_BASED_QUOTA` documents the relaxed limits, but `routeLanes` still alternates choices by design. Skip that planner when it conflicts with the story.

`src/videos/short-overlay/` retains the actual portrait hook/caption/pen compositor and tracked-plane annotation. [The tools guide](../tools/README.md) explains the customer project schema. A supplied OFL Inter font replaces a nonredistributable system Helvetica font in that portable example. Use your licensed Helvetica if matching that precise typography matters.

`skills/flow/references/production-manual.md` and `skills/gentlemen-style/references/` in the parent folder preserve the detailed recipes. Shared editorial/caption geometry lives in the sibling editing module.
