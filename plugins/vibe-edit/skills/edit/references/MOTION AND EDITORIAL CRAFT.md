# Give the visual a job

Use the sibling [motion system](../../style/references/MOTION%20OVERVIEW.md) for the complete style recipes, working components and assets. Keep style, production engine, colorway and delivery format distinct. A JavaScript scene can be used inside Remotion; an existing approved composition does not need to be rebuilt merely to change tools.

Before adding a visual, state the spoken point, what the viewer must notice, what changes on screen and when that change is complete. Reveal one focus at a time. Build an action, relationship or comparison, not decorative movement that runs beside the narration. Keep the presenter as the narrative spine and return to useful footage when the visual's job is done. Density examples are not quotas.

Study supplied references for rhythm and sound as well as still-frame composition. Keep a small style/source map: source time, observed treatment, intended adaptation and constraint. Do not copy private footage, paid tutorial text or restricted logos. A concept or script reference is not evidence that the recorded performance contains the same words/actions.

Tie motion and sound to actual events in the locked timeline. If an impact occurs at 2.0 seconds and the sound asset has a 0.2-second lead-in, begin the asset at 1.8 seconds; inspect the actual audible onset rather than aligning file starts. Music sets a broader mood/rhythm while effects clarify specific visible actions. Use quiet texture under narration, no pen sound during a settled hold, and preserve deliberate demo audio.

## Text and composition preflight

Render actual longest/lowest/overhanging glyphs in the real font and canvas. Compare settled glyph ink against an unclipped reference, not only DOM rectangles. Partial reveal can be intentional before completion; settled clipping is a defect unless the design explicitly calls for it. Preserve essential words around a presenter matte without removing meaningful depth.

Derive diagram nodes, labels and connector anchors from one layout. Test longer labels, inspect true glyph clearance and keep underlines/checkmarks off the text unless crossing it is the point. Inspect entrance, partial reveal, settled hold and exit separately, then contiguous transition frames and normal-speed playback.

Change presenter sides when the explanation changes state, not on a timer. Use grouped transforms for a small scale/position repair to an accepted composition. Preserve approved layers, timing and sound. For tracked masks/behind-head inserts, inspect the whole cue for edge drift, hair/hands collisions and room continuity. A successful render is not proof of legibility, motion quality or tasteful pacing.

Keep every rendered replacement's editable source. For a failed part, rerender only that part and its changed dependencies. A revision log must say what changed and which actual frames/audio verified it. Do not call a requested refinement finished until its resulting pixels or sound demonstrate it.

## Native Fusion relationships

Graph placement is organizational; connections determine compositing. Merge Background is the lower image and Foreground is the overlaid image. The blue effect mask limits that foreground operation, not the complete result. A card's image, text and accents should share the relevant mask and move under a parent Transform; a mask on an earlier background does not automatically constrain later merges. Keep independent inner transforms only for actual content changes.

For a behind-presenter insert, keep the original full-frame shot underneath, the insert in the middle and a time-aligned foreground subject matte on top. An equivalent inverse-matte insert multiplies alpha by the inverse subject matte; subtracting alpha can damage soft edges. Preserve the room, one dialogue path, matching crop/time/speed and the full hand/head movement. A few polygon keys are not proof of hair segmentation. Test the hardest turn, hair edge, hand crossing and motion blur, then inspect the whole cue.

An image flattened against white is not transparent. Check alpha/premultiplication over light, dark and actual footage. For an uncertain 3D treatment, block out framing, occlusion, camera travel and timing before materials/lighting; a flat screenshot on ImagePlane3D is still a plane, not reconstructed geometry. Merge3D/Renderer3D and the intended camera must be connected and rendered; viewer lights and final render lights are distinct.

Use Text+ Follower for verified character timing, explicit word starts for word sequencing and a parent Transform for a whole title. Keep reading holds still. Check every animated channel's actual cue after inserting a preset; moving one curve need not move the others. Spatial path handles shape the route, while Spline curves shape speed. Keep a drawn connector's geometry fixed and animate its stroke rather than accidentally morphing the route. Native curves and easing require actual frame checks, not only a checkbox.

Use proxy resolution for processing, source proxies for decoding and render cache for heavy completed effects as appropriate. Restore final quality and original-media paths before delivery. A cache indicator is not proof of real-time playback or correct output. Failed standalone Fusion saves/renders do not justify claiming a visual result from node readback alone; use a verified native timeline render path.

## Native spline and reusable composition checks

In the tested Resolve Python API, BezierSpline LH/RH coordinates are offsets from a key's frame and value. Exported `.comp` handle coordinates are absolute. For a value1 key at frame24 whose right horizontal handle reaches frame54, the API right handle is `{1:30, 2:0}`. Inspect `GetInput` over the intended hold and rendered movement; a key-list round trip alone can miss unwanted overshoot. A setter returning `None` can still have applied keys, so check state.

Retain the full exported Fusion composition and reimport it to test editability. A rendered substitute can be used when native playback fails, but keep its native source, version, frame span and replacement file together. State which timeline layer is a rendered substitute. Lossy H.264 may vary pixels during a stationary hold, so use both native parameter checks and a stated visual tolerance.

For new music, ambience and SFX, use [Openverse sourcing](../../hyperframes/workflows/media-use/references/openverse-audio.md).
Keep accepted sound, align cues to actual visual actions and check final credits.
