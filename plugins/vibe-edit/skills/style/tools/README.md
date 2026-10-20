# Motion tools

Choose only the tools needed for your current edit. Keep your source media and customer profile outside this pack. Run in a new working copy and use new output names. Python3.10+ and FFmpeg are common requirements. The sound tools need NumPy and SciPy; font compilation also needs fontTools, svgpathtools and scikit-image; planar tracking needs OpenCV and NumPy. Install chosen dependencies in a project-local virtual environment, not into the editor or system Python.

| Job | Real implementation | What to verify |
| --- | --- | --- |
| Selected handwriting sound | `gentlemen_selected_sound.py` and four material helpers | Visible pen event timing, silent holds, actual narration balance |
| Procedural cues | `flow_sfx.py` | Cue time and creative need; no automatic background bed |
| Compile licensed marker font | `gentlemen_compile_font.py FONT NEW.json` | Glyph coverage, stroke direction and completed outline |
| Track a rigid textured plane | `gentlemen_track.py` | Four corners, invalid frames, occlusion and drift; not face tracking |
| Instance still mask | `vision_segment.swift` | All detected foreground instances may include objects |
| Per-frame person mask | `person_segment.swift` | Hair/shoulders/motion and source alignment; macOS Vision, not Resolve Magic Mask |
| Native card/mask/parent exercise | `native_fusion_fixture.py` | A new empty scratch Fusion comp only; editor version/API may differ |
| Portrait layouts and captions | `render_short.py`, `hook_rule.py`, Flow `short-overlay` | Measured crops and text bounds on the actual customer source |
| Optional swivel teaser | `pan_3d_transition.py`, `insert_3d_transition.py` | Native frame/audio sync; historical stream-copy insertion is not frame-exact proof |
| Timed generated illustrations | `overlay_visuals.py` | Actual manifest times, aspect ratio, final length and audio |

## Handwriting sound

```sh
python3 -m venv .venv
.venv/bin/python -m pip install numpy scipy
.venv/bin/python gentlemen_selected_sound.py --events ../flow/pen-events.json --output marker.wav
```

The event JSON contains `fps`, `duration`, one nonnegative motion value for every frame and `strokes` with start/end/length. Export from the actual visible text using `flow/scripts/export-pen-events.cjs`; changing the text requires fresh events. Keep the included CC0 source recordings and attribution. The generated stem is separate from narration and should be lowered once as needed, not enhanced again with a full dialogue chain.

## Person behind graphics, without replacing the room

On macOS with Swift/Vision available:

```sh
swift person_segment.swift upright-source.mp4 new-mask.mov 540 960
```

This is the actual per-frame person-segmentation mechanism, with dimensions supplied by the customer and source presentation times retained. The source must be upright with identity display transform; normalize an oriented phone clip into a new working file first. The matte contains no source speech. It is a grayscale person mask, not a ready-to-use alpha overlay. Multiply the **graphic's** alpha by one minus this mask and leave the original video/room below it. The optional [mask compositor](mask_graphics.py) does that with matching input times. Inspect the full result before trusting it.

`vision_segment.swift input.png new-mask.png` instead finds all foreground instances. These routes have different behavior. Neither can guarantee clean hair or track a hidden person. If the mask fails, fix it or move the graphic.

## Actual portrait-short compositor

Run `python3 render_short.py /path/to/new-project demo`. The [example project](../../shorts/examples/portrait-short/README.md) supplies the full schema. It retains measured full/split/inset layouts, complete-short hook timing or the first screen-share cutoff, one phrase-caption owner and optional handwritten note. The customer profile may override the hook preference. Source frame rate must match `layouts.json.fps`. The renderer keeps the supplied duration/ranges; it does not decide which speech to cut.

The overlay has an explicit2160×3840 design grid. Measure customer crops, longest text, caption clearance and source orientation. The supplied OFL Inter font is a disclosed portable replacement for system Helvetica. Source audio is cut and encoded to AAC without enhancement, so it is not byte-identical to the original source. The final check compares against that independent extracted audio reference. Previewing captions is not caption approval.

## Native Fusion exercise

Open your own **new scratch project/timeline** containing a five-second empty Fusion clip with only MediaOut. Through Resolve's documented scripting context, set `EXPECTED_PROJECT` to that exact scratch name and `OUTPUT_DIR` to a new evidence folder, then run the script with `resolve` and `project` objects. The script refuses a different selected project or a populated comp. It creates the actual card, clipping mask, stripe, parent transform and foreground-occlusion graph, checks spline values and exports `.comp`. It saves only that explicitly selected scratch project; it does not start a render or add a render job. API LH/RH keyframe offsets differ from exported-comp handles. Inspect holds and reopen/import before using it on customer work. No actual customer project is tested by the bundled receipt.

Read [optional providers](OPTIONAL%20PROVIDERS.md) for generative adapters. Their code is included for completeness; they are not silently enabled.

## Layered interchange

From `motion`, run `python3 tools/layered_fcpxml.py hyperframes/templates/gentlemen-hybrid/layered-job.json new-layered.fcpxml`. This retains the original picture/alpha/sound-layer FCPXML mechanism with explicit rational FPS and customer paths. The supplied job uses the synthetic five-second sample. Media references are absolute to that working copy; moving it requires relinking. Validate media metadata and the actual editor import before using the result. An XML parser accepting the file is not native acceptance.
