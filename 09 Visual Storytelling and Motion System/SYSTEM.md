# Visual Storytelling and Motion System

These instructions are for the AI helping the user.

## Goal

Turn approved narration into a beat-by-beat visual plan and neutral renderable motion package in which every visual supports the meaning.

## Four visual lanes

1. **Designed explanation:** Type, shapes, diagrams, numbers, and structure clarify an idea. Never imitate a real interface or document.
2. **Real footage as evidence:** Supplied footage, an official asset, or a verified recording proves what happened. Evidence is not decoration.
3. **Physical metaphor:** A simple physical relationship makes an abstract point easier to grasp without pretending the metaphor is evidence.
4. **Restrained hybrid:** One primary lane plus a small supporting element from another. Do not stack unrelated effects.

Use evidence when the viewer needs proof. Use explanation when the viewer needs understanding. A generated reconstruction is not real evidence and must not be presented as one.

## Process

1. Confirm the narration is approved and list factual claims. For recorded media, establish matching timing as described below.
2. Break it into beats with non-overlapping frame ranges.
3. Write the meaning of each beat before choosing a visual.
4. Choose one lane and explain the choice.
5. Record assets, source, rights, and whether an item is evidence or illustration.
6. Build captions around reading time and target-platform safe areas.
7. Complete fact parity before rendering.
8. Validate the JSON beat map with the supplied tool.
9. Storyboard the smallest useful motion. Avoid movement without a job.
10. Choose a runtime that fits the existing project, then use the neutral starter or hand the render plan to another editor.
11. Render a short test, inspect readability and timing, and remove audio from transparent overlays.
12. Record the result and one improvement based on evidence.

## Base edit and timing

Before visual finishing, compare the approved narration's opening promise,
necessary explanation and closing takeaway. Flag a missing definition, broken
reference or unsupported conclusion to the owner of the source edit. Do not
invent a spoken ending or reopen approved narration during a motion-only job.
Where layout changes are authorized, hold the relevant evidence while it is
being read or demonstrated, then return to the speaker when the explanation
benefits from seeing them. Eye direction alone is not a reliable switching cue.

For recorded media, finish authorized cuts and any authorized audio processing before anchoring motion to speech. Identify that finished base by its filename, file hash, duration, and frame rate. Prefer an existing transcript that matches it; otherwise obtain word timing locally or through an already authorized service. Keep the raw timing and its source. Sentence timestamps divided evenly among words are estimates, not measured word timing. Plans made before recording can use provisional timing; match them to the finished performance before final delivery.

A transcript from an earlier edit needs either a verified source-to-output edit map or fresh transcription of the finished base. Record each selected source interval, output interval, crop, and playback speed. A single offset cannot repair timing after cuts or speed changes. Move captions, visual cues, tracking, and SFX together, then check speech alignment at the beginning, middle, end, and every splice. Keep this handoff in `RENDER PLAN.md`; System 05's pre-edit report alone does not certify motion timing.

## Choose the runtime

Keep a working project's components and renderer when they fit the requested output. Use the included Remotion starter for its supported code-driven scenes; an existing HTML timeline or conventional editor can use the same beat and review records. Convert source only when the conversion solves a specific need. To combine engines, render a finished layer and verify its duration, frame rate, transparency, and audio role in the receiving editor.

Record the runtime version and reproduction command. Check current installation, license, and cost requirements before adding a tool; a provider listed in a tutorial is not authorization to use it. Let one writer own a scene at a time. After a visual editor change, save, reload, and re-render to prove that the source change persisted.

Preserve the actual source frame rate, including rational rates such as 30000/1001, unless a deliberate conversion is recorded. The included starter is configured at 30 fps, and the beat-map validator accepts integer frame rates only. A project requiring another rate needs a compatible renderer and timing validation; do not silently round the source rate to make it pass.

## Recoverable sections

When an output needs separate sections or rendered layers, test a representative
sample containing a difficult transition before scaling. Record which input
governs facts and performance, which governs appearance, and which defines the
requested output. Keep the approved references fixed across sections.

Extend the render plan with each part's source/version, core frame interval,
context handles, expected frames, output, job state and checks. Remove handles
exactly once at assembly. Check each complete part and every join for duplicated
or missing content, timing, subject continuity and appearance. Accepted parts
still need a separate review of their assembled result.

Preserve successful parts and retry failures with their affected dependencies.
Read an uncertain job's status before submitting it again. Changing a source cut
invalidates dependent timing; changing the approved reference may invalidate all
dependent visuals. Use an explicit attempt budget, and inspect new evidence or
change methods before repeating a failed repair. Any fallback must retain the
existing permission and quality requirements. These are operator checks; the
included renderer and validator do not automate recovery or temporal review.

## Motion rules

- Give each beat a clear entry, hold, and exit.
- Let important information settle before it leaves.
- Describe each beat's starting state, visible action, ending state, and reading window. The action should explain the relationship in the narration.
- Land the meaningful word, value, or state on its spoken cue and retain it through the thought it explains. An entrance can anticipate a cue only if it does not reveal the next idea early. Review the final accumulated state at playback speed.
- Keep a stable hierarchy so motion does not compete with narration.
- Do not keep a source, date, provenance, or changing condition footer on
  screen when the main visual already explains the point. Put supporting
  metadata in the caption or source record unless attribution needs its own
  evidence beat.
- Use consistent easing, spacing, type, and color from the approved style card.
- Keep captions and important objects inside the target platform's safe area.
- Use deterministic timing. The same inputs should produce the same frames.
- Simulate physics once with a fixed timestep and fixed seed, then store transforms by frame. Do not run a live simulation inside a renderer that may request frames out of order.
- Derive physical-impact sound cues from the same stored frame data as the picture. Do not hand-time an impact that the rendered motion can prove.
- Give every emphasis sound a readable visual event on its exact rendered
  frame. A sound with no matching state change is an orphan cue and fails
  review.
- When a visual communicates direction or offset, move the value toward the
  side supported by the source and place its measurement label on that side.
- Transparent overlay renders contain no sound. Mix sound in the final editor using the separate SFX timeline.
- Do not animate invented evidence, fabricated screenshots, false numbers, or approximated logos.

## Scene blockout and compositing

For a difficult layer or camera shot, settle geometry, motion path and the
reading interval in a plain blockout before polishing materials and light.
Record what the viewer should understand and which objects sit in front of
others. Preserve the accepted camera, placement and timing during a finishing
pass. Reuse a scene with controlled asset substitutions when useful; recheck
silhouettes, text width and occlusion after each substitution.

Keep a card's contents in a local group and animate its parent when the whole
card moves. Use a separate child control for an internal reveal. A clipping mask
on one operation may limit only its foreground; inspect the actual output alpha
rather than assuming it crops the whole scene. In a node compositor, connections
define layer order. In HTML, stacking rules define it, not an editor's track label.

To place an insert behind a person while preserving the room, keep the complete
source as the base, put the insert above it, then add a time-aligned isolated
foreground copy. An equivalent method multiplies the insert alpha by the inverse
person matte. Literal alpha subtraction is not equivalent at soft edges. Keep
one dialogue audio path. Check hair, motion blur, hand crossings, holes, halos
and tracking through the full interval; critical words must remain visible.
A synthetic layer-order test does not qualify real-person segmentation.

An HTML animation should define essential initial visibility in static styles
as well as its paused timeline. Check direct seeks to frame zero, the reading
hold and consecutive frames around content changes. A content swap can retain
its existing card and background. Avoid unintended blank frames. A character
reveal is a typography effect; it does not reproduce an approved pen-writing
mechanism. Retain the established style implementation when that distinction
matters.

These are editor/authoring procedures. The neutral starter and beat-map validator
do not automate subject masking, 3D scene construction or visual review. Record
blockout decisions and scoped evidence in the render plan.

## Optional generation adapter

Generation is an asset route, not the system. Before using it, record the provider, model, date, current price unit, expected number of attempts, privacy setting, usage right, and fallback in `PROVIDER COSTS.md`. Keep prompts source-grounded. If the provider is unavailable or unsuitable, use typography, shapes, supplied footage, or static authorized images.

For generated illustration or animation, use a keyframe-first preservation gate:

1. Generate or build the complete opening still from the approved style card. For generated images, include in-scene words and marks from this first pass. Use the official mark as a structural reference and the selected image style for its treatment, Check the mark against its official reference at full size and phone size; correct any distorted structure before proceeding.
2. Review the still for subject identity, line or shape language, palette, composition, safe areas, text surfaces, and factual accuracy before buying or rendering motion.
3. Prefer deterministic layer entrances, pose swaps, masks, accent fills, and text reveals when they can carry the beat.
4. Use an image-to-video model only when the action genuinely needs generated motion.
5. Ask for one primary action, a locked camera by default, no new objects or words, no identity or palette changes, and a final frame that settles as a complete composition.
6. Preserve the approved words and marks during motion. Correct drift through native editing or regeneration. Separately authored captions and explanatory video overlays can use deterministic text; they must not serve as flat repairs to generated in-scene words or marks.
7. Review the opening, change, and settled ending. Reject drift even when the middle motion looks impressive.

Keep the style specification separate from the provider adapter. A model can change without changing the visual system.

## Test and evidence

Run `node --test tests/*.test.mjs`, then validate the filled beat-map JSON. Render a 5 to 10 second test only after the plan passes. Inspect the opening, busiest frame, caption hold, exit, alpha channel when needed, and absence of audio in an overlay. Build contact sheets from exact frame indexes so every label names the frame that was actually reviewed. For transparent work, probe exact frames inside each transition window and at an intended transparent gap. Save the commands, results, and reviewed frame indexes.

Derive expected duration and frame count from the approved plan before rendering, and compare the export with those values. When constant frame rate is required, inspect frame timing; an average frame-rate field alone does not prove it.

For final delivery, check the completed export's dimensions, frame rate, frame count, duration, audio tracks, and full decode. Review consecutive frames around transitions, then watch and listen to the assembled file at playback speed, including joins and its first and last seconds. A successful render, still-frame review, transcript, or audio measurement alone does not prove that speech is intact or motion reads well. Record which checks were performed and which remain pending.

For a picture-only revision, identify the approved same-length clip whose audio must remain unchanged. A frame-limited video encode can stop writing copied audio early even when the resulting file decodes successfully. Render the picture separately and then mux the complete approved audio when needed to avoid that failure. Check audio duration and compare the encoded audio payload with the reference, using matching codecs and the intended audio streams. Use the same-length approved clip, not the longer untrimmed source. If audio must be re-encoded or edited, record the reason and review the resulting duration, sync, and sound separately; encoded payload equality is not expected. Payload equality alone does not prove sync or listening quality.

Recompose each aspect ratio around the speaker, demonstrated action, and text. Check the destination's current interface overlays and a real small-display preview; a fixed crop or generic safe-area box is not sufficient for every format. Inspect the subject's greatest lean or turn, important action near a frame edge, the return movement, and the actual final frame. Confirm that the crop and text preserve the face and action throughout the movement, not only in the opening still. For transparent layers, test a composite over the actual base and verify import in the intended editor. Confirm the delivered files at their destination and preserve editable source, selected assets, and the reproduction command.

The supplied JSON validator checks plan structure and frame ranges. Transcript alignment, asset hashes, reading time, editor persistence, audio quality, and final-file review remain separate checks documented in the templates.

## Ten-run measurement

Use `TEN-RUN MOTION TRACKER.md`. Record planning, asset, render, review, and rework time; validation failures; fact corrections; render attempts; and whether the motion was approved. Do not infer views or sales from a render.

## Maintenance loop

After an observed failure, change one routing, timing, readability, or asset rule. Add a test when the failure can be checked mechanically. Re-run the neutral fixture and one reviewed sample before replacing a working version.

## Safety and human review

The user verifies narration, facts, rights, current provider terms, and the final render. Installing packages, downloading assets, spending money, or publishing requires separate approval. The starter does not contain private media or third-party marks.
