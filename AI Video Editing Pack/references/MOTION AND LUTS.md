# Motion and LUTs

Use this after the clean cut has human approval. Start with a native editor
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
| Remotion | After approval, run `npx create-video@latest`, install the generated project's dependencies, make one short composition, and render a sample for import into the editor. | [Remotion docs](https://www.remotion.dev/docs). It uses React/TypeScript; check current Node/OS and [license terms](https://www.remotion.dev/docs/license/pricing) before team or hosted use. |
| HyperFrames | After approval, follow the [current quick start](https://github.com/heygen-com/hyperframes/blob/main/docs/quickstart.mdx): `npx skills add heygen-com/hyperframes`, select Core Skills, run `npx hyperframes doctor`, then preview a small project. Use the installed CLI's current render help and [render guide](https://github.com/heygen-com/hyperframes/blob/main/docs/guides/rendering.mdx) for the chosen project. | Local render can avoid hosted credits; optional generation, agents or hosted rendering may have costs and data flows. Check Chrome/FFmpeg prerequisites and third-party terms. |

Do not install both just because they are listed. Pin the tool and dependencies
for a project whose look must reproduce. A browser preview is not a final
encoded export. Import the sample, inspect motion and alpha over the shot,
then watch and listen to the final render.

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
6. Ask the person to approve the actual graded export. Save the LUT's intended
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
