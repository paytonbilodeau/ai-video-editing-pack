# Check a caption lane and camera handoff

Watch [the eight-second test](../../../../ASSETS.md#preview-mp4). At 30 fps, the full-screen graphic
owns frames 60 through 179. Its background appears at frame 60; the explanation
animates in afterward. Camera returns at frame 180. No speech is included.

The source is `flow/src/narrative/DedicatedShort.tsx`. In a separate copy of the
motion `flow` folder, with its dependencies ready, render:

```sh
npx remotion render src/index.ts DedicatedShort dedicated-short.mp4 --codec h264
```

Inspect frames 59, 60, 61, 179, 180 and 181. Then try a longer caption. Measure
the real font and split at a natural word boundary if it exceeds the lane.
Do not fix overflow by clipping it. Fit the lane to your real face, graphics
and platform controls before using it on footage.

This fixture checks frame ownership and legibility of these phrases. It does
not establish real speech alignment, perceptual audio quality or native editor
import. Other caption choices and clean-master requests remain valid.
