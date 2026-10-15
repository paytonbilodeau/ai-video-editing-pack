---
name: gentlemen-style
description: Payton-derived mint marker handwriting, wide title treatment, serif captions and stroke-synchronized quiet sound.
---

# The Gentlemen Style

Use the complete [visual specification](references/style-spec.md) and the actual `flow/src/components/gentlemen/` implementation. The palette, chosen font substitutes, central-pen reveal and selected 85/15 recorded-contact sound preserve the tested system. This is a separately implemented inspired treatment, not Netflix software, footage, fonts, branding or endorsement.

**Handwriting:** Reenie Beanie glyph outlines are revealed through central stroke masks. Each stroke gets timing from its length with small pen lifts; `penLayout()` is shared by picture and sound. Use the `Ink` component, not a typewriter, rectangular wipe or outline tracing. Keep the completed note still. One clean crossing stroke cancels a previous value. The glyph set fails explicitly for unsupported characters; compile and inspect an appropriate licensed font before another language.

**Titles:** Archivo Black, wide, pale/mint fill with restrained shallow shadow. Cinzel supplies a small chapter line. **Captions:** Bevan with slight horizontal compression, fill plus subtle shadow, no rim, outline, bevel or bouncing words. Use only when this chosen style owns captions; do not duplicate native captions.

**Sound:** `tools/gentlemen_selected_sound.py` retains the real Feather squeak/Thin nib 85/15 amplitude blend, derived from the included CC0 recordings. Export current pen events, render a 48kHz independent WAV, and align it to the same composition start. Empty holds stay silent. The standard active reference is about −39 dBFS; the quieter narrated starting treatment applies a single −6 dB gain. Neither value guarantees the right listening balance with new speech. Rebalance under actual dialogue and listen. Never loop an old demonstration stem beneath new writing.

**Tracking:** `tools/gentlemen_track.py` tracks a textured planar quadrilateral with SIFT/RANSAC, writes per-frame validity and errors, and does not promise a face/clothing/general-object tracker. Hide or manually repair invalid frames; do not hold the last valid position through failure. Test against the actual source. The included generated planar fixture is a technical example only.

**Output:** a finished MP4 is opaque; a ProRes4444 PNG-rendered `yuva444p10le` overlay can retain alpha. Keep overlay video-only and writing WAV separate. On macOS, use the Apple normalization route only when required by the target editor, preserving the requested frame rate. Check actual blank/partial/settled alpha, complete decode and final native import. An XML file or browser preview is not native editor acceptance.

For generated character images, use the customer's own authorized references and desired wardrobe/setting. Keep original imagined scenes labeled. No private portrait library or source-show captures are included. `[inkText]`, colors, cue times and customer identity are editable; preserve the tested mechanism.
