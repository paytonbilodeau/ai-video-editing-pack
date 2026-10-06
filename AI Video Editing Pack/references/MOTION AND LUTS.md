# Motion and LUTs

Use this when the clean cut is ready and graphics or a look fit the brief. Start with a native editor
title or annotation, then choose a separate motion tool only if the shot needs
it. Keep the graphic editable and test it over the actual moving footage.

## Turn a reference into an original visual

Ask what the reference contributes: layout, type, material, movement, pace,
or how it explains a concept. Note the source and permission in
[PROJECT INTAKE](../templates/PROJECT%20INTAKE.md). Write one plain-language
visual brief: what appears, when, where, why, how it exits, and what must stay
visible. Make a short representative sample. Check its entrance, settled
state, reading time, exit, sound, and return to the recording. Do not copy an
exact frame, private style recipe, or unlicensed asset.

Native titles are the first test. For a more involved graphic, choose one
optional adapter and verify current requirements before installation:

| Route | Practical first test | Current source and limit |
|---|---|---|
| [JavaScript animation](../skills/javascript-animation/SKILL.md) | Use the bundled local CLI to initialize one of seven styles, build, check and render a short piece. Use its frame adapter inside Remotion or import PNG/ProRes into the editor. | Pinned MIT upstream and optional locked Playwright setup. Shipped styles are opaque; alpha requires authored transparent content. No account or paid provider is required. |
| Remotion (4.0.532 on October 3, 2026; 5.0 unreleased) | After approval, run `npx create-video@latest`, pin the exact version, make one short composition, and render a sample for import into the editor. Install the vendor's agent skills with `npx skills add remotion-dev/skills` so the assistant can check the current API before coding. | [Remotion docs](https://www.remotion.dev/docs). React and TypeScript; free for individuals and companies of up to three people, otherwise a [company license](https://www.remotion.dev/docs/license/pricing). `@remotion/captions` builds word-by-word pages from transcript JSON; `@remotion/media` is the current video and audio component. |
| HyperFrames (0.8.x, Apache 2.0) | After approval, follow the [current quick start](https://github.com/heygen-com/hyperframes/blob/main/docs/quickstart.mdx): `npx skills add heygen-com/hyperframes`, run `npx hyperframes doctor` (gate on `.ok` in the JSON; the command always exits 0), `lint` while authoring, `check` as the final gate, then `render`. Pin the version; it publishes several releases a week. | HTML, CSS and GSAP rendered through headless Chrome and FFmpeg; local rendering has no per-render fee; hosted rendering, publishing and telemetry are separate paid or data-sending features to leave off unless chosen. Fonts must be local `@font-face` files; anything visible at frame zero must be in static CSS. |

Install only the tools the project needs. Pin the tool and dependencies
for a project whose look must reproduce. A browser preview is not a final
encoded export. Import the sample, inspect motion and alpha over the shot,
then watch and listen to the final render.

Hand the graphic to the editor as video with an alpha channel, at the timeline's
frame rate and size, video only, named with its in-point timecode. Remotion:
`npx remotion render <comp> out.mov --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png --muted`.
HyperFrames: `--format mov` (ProRes 4444) or `--format webm` for VP9 alpha, or
`--format png-sequence` for compositing apps. Resolve, Premiere and Final Cut
read ProRes 4444 alpha; confirm it on import (Resolve: Clip Attributes > Alpha
mode) and check one frame over the footage. Route by task: native titles and
caption tools for a graphic that appears once and must stay editable by a
person; Remotion when a component library exists or exact transcript cues
matter; HyperFrames when an HTML and GSAP look or its caption workflows fit.
Masks of a person are always made in the editor.

## Put a graphic behind the person

The method is the same in every editor. Track 1 holds the original footage and
its audio, the only voice path. Track 2 holds the graphic. Track 3 holds a
duplicate of the footage trimmed to the overlap, with a person mask that keeps
the subject and makes the rest transparent; mute its audio. Then review at full
size and phone size and scrub the overlap at 2x for flicker.

- DaVinci Resolve Studio: Color page Magic Mask on the duplicate (click the
  subject, track forward and back), add an Alpha Output and connect the key,
  refine with Matte Finesse; Resolve 21 can render the mask in place as an
  external matte for reuse (documented). Magic Mask is Studio-only.
- Premiere Pro 26: Object Mask on the duplicate (one click, track; Smooth edge
  mode for hair); a feathered pen mask tracked forward when it misfires.
- Final Cut Pro 12: Magnetic Mask on the connected duplicate (click, Analyze;
  negative Feather tightens hair); Auto Mask for recognized objects. Mask data
  does not travel through FCPXML (reported).
- CapCut: Video > Remove BG > Auto removal on the duplicated top layer.

Check hair and beard edges for chewing or halo, hands and held objects that
segmenters drop intermittently, motion blur across the matte edge, and complete
occlusion when the subject crosses the graphic. When the mask fails, use a
layout that never intersects the subject: side by side, a framed inset, a
pull-back with negative space, or a full-frame cutaway with the voice
continuing. A graphic the viewer cannot read behind a moving head helps no one.

## Build a look, then decide if a LUT helps

A `.cube` LUT is a global RGB mapping. It cannot recognize faces, masks,
windows, movement, or which warm color is skin rather than lighting. An
unrelated reference image can inspire a look, but a valid LUT file does not
prove an accurate match. If one shot needs a local fix, grade it in the editor
instead of forcing the change into a global LUT.

1. Record each source camera's known color space/gamma and intended output
   space. If unknown, label the assumption and test it on source frames.
   Normalize the footage into a common working space before a creative look.
   Keep the technical transform separate from the creative LUT.
2. Supply several ungraded frames from the actual footage plus the authorized
   reference. A matched ungraded/graded pair is stronger than an unrelated
   still. Set aside at least one clip or frame that was not used to build the
   look.
3. Describe a bounded transform: contrast, warmth or hue shifts, saturation,
   highlight roll-off, shadow detail, and protection for skin and neutral
   objects. Make one small test. Resolve Studio's vendor MCP can generate a
   `.cube` from a declared transform where available; an editor's manual
   grading controls remain a valid route.
4. Load the LUT on a duplicate node after normalization. Check that it loads,
   then compare it off/on using waveform, RGB parade, vectorscope, skin,
   neutrals, highlight/shadow detail and any clipping. A syntax/load pass is
   only the first gate.
5. Test the held-out clip and neighboring shots. Keep exposure, white balance,
   windows, keys and skin repair as shot-specific editable adjustments outside
   the LUT. Reject hue breaks or damage that needs extensive repair.
6. Deliver the checked graded export for the person to review when ready. Save the LUT's intended
   input/output spaces, tested sources, version and observed limits. Do not
   claim it will match every future camera or train a model.

With a lone reference of unknown provenance, promise creative resemblance.
Exact matching is an observed result on tested footage, not a property of the
`.cube` file.

## Protect each derivative's visible area

An approved horizontal graphic may fail in a vertical crop. For each requested
output, open the current destination's safe-area guidance or overlay, then
inspect actual frames with captions, faces, logos, UI controls and screen
demonstrations together. There is no universal safe-zone rectangle across
platforms and placements. Review the encoded derivative before approval.
