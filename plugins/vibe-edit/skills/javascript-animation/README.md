# The custom JavaScript motion route

This includes the actual Payton mint/neutral time → frame → sequence template, plus the complete public seven-style runtime. It produces deterministic HTML Canvas graphics. Use Node22+, npm and FFmpeg for MP4 export. A separate local browser runtime is created only when chosen.

From a copy of this skill folder, use new names for every output:

```sh
node runtime/tools/animate.mjs setup ./local-runtime
node runtime/tools/animate.mjs doctor --runtime ./local-runtime
node scripts/new-piece.mjs ./first-piece
node runtime/tools/animate.mjs build ./first-piece
node runtime/tools/animate.mjs check ./first-piece --runtime ./local-runtime --out ./check-01
node runtime/tools/animate.mjs render ./first-piece --runtime ./local-runtime --out ./render-01 --format mp4
```

Open the generated MP4 and HTML. The supplied nine-second portrait example explains time, a single frame and the sequence. It is silent and uses a transparent Canvas; the MP4 is opaque. Preserve alpha using the runtime's supported alpha output or import the Canvas frame bridge into Remotion, then verify the actual native editor.

Edit `first-piece/src/customer-config.js`, its scene timing and drawing code. The template's palette and proportions are the real starting style. Build updates generated `index.html`, while authored `src` files stay editable. `new-piece` refuses an existing directory.

For the other styles, media/voice timing, beat analysis, comparison, alpha export and Remotion adapter, read the complete [runtime guide](runtime/GUIDE.md). The seven additional looks are cut-paper, crosshatch, riso, sketchbook, math, isometric and pixel; their licenses and provenance remain in the runtime. A deterministic check proves repeatable frames in that browser/font environment. It does not approve the story or audio.
