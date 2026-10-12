# Motion and LUTs

Motion should help the viewer understand the point. Use the person's existing
assets and tools first. Offer motion setup during onboarding so it is ready when
needed, then choose the right tool for each graphic. Native editor graphics,
Remotion, HyperFrames and the bundled JavaScript kit can work together.

Start with [MOTION TOOL SETUP](MOTION%20TOOL%20SETUP.md) for a plain-language
choice, optional setup, and a short first render. The assistant performs the
technical steps after the person chooses what to add.

## Turn a reference into an original visual

Ask what the reference contributes: layout, type, material, movement, pace,
or how it explains a concept. Note the source and permission in
[PROJECT INTAKE](../templates/PROJECT%20INTAKE.md). Write one plain-language
visual brief: what appears, when, where, why, how it exits, and what must stay
visible. Make a short representative sample. Check its entrance, settled
state, reading time, exit, sound, and return to the recording. Do not copy an
exact frame, private style recipe, or unlicensed asset.

## Choose and combine the motion tools

| Route | A useful fit | Editable source retained |
|---|---|---|
| Native editor | A title, pointer, crop or mask tied closely to the footage. | The editor's project and controls. |
| Remotion | Reusable React layouts, repeated data-driven scenes and frame-timed sequences. | React/TypeScript project and locked dependencies. |
| HyperFrames | HTML/CSS compositions, designed explainers and seekable animation. | HTML project, local assets and locked dependencies. |
| [JavaScript animation](../skills/javascript-animation/SKILL.md) | Procedural drawings, diagrams and the seven supplied public styles. | Scene code, drawing kits and piece configuration. |

These are complementary choices. A JavaScript scene can run through its
Remotion adapter; a checked rendered layer from any route can be placed in the
editor. Use one tool to own each scene and one clear final assembly. Converting a
working project adds work, so do it only for a useful capability.

The [setup guide](MOTION%20TOOL%20SETUP.md) includes all three code-based routes.
Set up one, several, or none according to the person's choice. Never require
three tool installations before their first edit.

### Hand a graphic to the editor

For an overlay, author transparent corners and render a format that carries an
alpha channel. Ordinary H.264 MP4 does not preserve transparency. Remotion's
[transparent-video guide](https://www.remotion.dev/docs/transparent-videos)
documents ProRes 4444 with PNG frames and `yuva444p10le`. HyperFrames documents
MOV, WebM and RGBA PNG-sequence outputs in its [CLI guide](https://hyperframes.heygen.com/packages/cli).
The JavaScript kit can supply PNG frames or ProRes from transparent source.

Use the timeline's frame rate and dimensions. Keep graphic sound separate when
that avoids duplicated dialogue. Test a short sample over dark, light and actual
moving footage in the receiving editor. Check the encoded result, not only a
browser preview. Retain the source and render command so a revision is easy.
Shipped opaque examples do not become transparent merely by choosing MOV.

For a graphic behind a person, prefer the editor's native mask when it fits.
Other authorized masks or mattes can work too; their edges and timing need the
same final composite review.

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

## Connect the visible event to its sound

Name the action and resulting state, then identify the actual event frame in the
animation. Keep timeline time, composition-local time and frame rate explicit.
Group a card's picture, border and label under one parent transform so they move
together. Check the entrance, settled reading hold, exit and available caption space.

Choose a cue for a reason, such as one click for a selection. Keep it independently
editable; every entrance does not need a whoosh. At normal playback speed:

`timeline useful onset = clip start + useful onset within asset - source trim-in`

Use the same units throughout. For an event at 2.0 seconds and an asset with
0.2 seconds of leading silence, start the untrimmed clip at 1.8 seconds, or trim
away that silence and start at 2.0 seconds. Account for retiming separately and
check available handles before moving a clip earlier.

Inspect the rendered frame before, at and after the event, plus the hold and exit.
Check the actual composite at phone size and listen to the exported cue with
dialogue. A waveform can verify timing without proving a pleasing mix. Read
native keys and placement back instead of relying only on an API return value.
After a timing change, recheck dependent sound, fades and encoder padding.

If a rendered replacement is needed for playback, retain the editable source and
record its revision, replacement file, start frame and duration. Verify frame
rate, endpoints, alpha treatment and contact timing over the real footage.
