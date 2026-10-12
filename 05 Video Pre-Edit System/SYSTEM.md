# Video Pre-Edit System

These instructions are for the AI helping the user.

## Goal

Create a reversible, reviewable first edit that removes the easy work without making creative decisions for the editor.

The included `tools/video_pre_edit.py` is the maintained reference implementation. It uses local FFmpeg and ffprobe. Its core does not need a Python package or paid API.

## Safe default

Make a cut only because:

- FFmpeg detected a quiet pause using the approved threshold and padding;
- the speaker used an exact agreed restart marker and local timed words found it;
- the user supplied an exact `--cut START-END` range;
- the dry plan implements the user's already authorized cut rules.

A dry plan is evidence of intended changes, not permission to invent new ones.

Do not guess that a repeated idea is a bad take. Teaching and natural speech repeat useful points, and similarity alone can delete wanted content.

## Process

1. Reuse the source, editing profile, working pace and authority already given. Follow the core [setup flow](../AI%20Video%20Editing%20Pack/references/SETUP%20FLOW.md). Fill `PRE-EDIT BRIEF.md` yourself from those facts; ask only for missing decisions.
2. Inspect the named source. Use a flattened SDR working copy with one video and one audio track and keep the original unchanged. If a copy is needed, offer to create it through the existing editor within the authorized scope.
3. Check Python 3.11+, FFmpeg, ffprobe and the encoder. Explain missing dependencies and offer to install them from their documented sources. Carry forward installation authority already given.
4. Choose silence, exact-range, protected-range, optional marker and audio settings that match the request. Protect demonstrations, reading holds, music and deliberate pauses.
5. Run `--dry-run` and inspect the report and generated plan. Check words around proposed joins and unusually long removals. Adjust the plan if needed.
6. In careful mode, show the meaningful checkpoint the person requested. In balanced or handle-it-for-me mode, proceed within the agreed cut rules after internal review. Ask when a material ambiguity or new action falls outside that scope.
7. Render with `--from-plan` so the reviewed options carry forward. Keep source-hash, protected-range, output-path and full-restart confirmation checks intact.
8. Verify the new MP4's picture, sound, duration and cuts, then save its report. Continue the requested editor finishing or deliver the pre-edit for feedback according to the brief.

If the tool needs a technical check, the assistant generates the neutral fixture
in `tests/make_fixture.py`. A customer recording is not required just to prove
that FFmpeg works. Record the actual outcome rather than promising a setup time.

## Restart rules

The user may choose other phrases. The recommended phrases are:

- `cut cut`: remove the spoken mistake and marker, then keep the corrected restart;
- `full stop restart`: discard earlier material and begin after the last marker.

Marker detection is off by default. It requires `--detect-restarts` plus either local Whisper or `--words-json`. The phrase match is exact. If the transcript looks corrupt, the tool disables transcript-driven cuts and reports the fallback.

The full-restart rule is also off by default. It requires both `--detect-full-stop-restart` and `--confirm-full-restart`. It can remove a large opening and refuses to cross a protected range.

## Silence and media rules

- Silence cutting is on by default at a conservative `-40 dB`, `0.8` second minimum, with `150 ms` kept on each side. Use `--keep-silence` to disable it.
- Adjust one setting at a time after reviewing a dry run.
- Preserve deliberate pauses when the user wants a slower pace.
- Add each clip, music section, generated sound, or deliberate pause as a repeatable `--protect START-END` range using original-source timestamps.
- Review the picture before accepting silence cuts into the plan. Add silent demonstrations, reading time, and other intentional visual-only sections as protected ranges; low audio level does not mean nothing useful is happening.
- Do not use this tool directly on HDR, multicamera, multitrack audio, subtitle-bearing, or edit-master media. Make a flattened SDR working copy.

## Audio rules

Audio cleanup is off by default. `--enhance-audio` applies local high-pass and low-pass filters, light EQ, compression, measured fixed gain toward `-16 LUFS`, and a `-1.5 dBFS` limiter ceiling. Fixed gain avoids the opening volume ramp that dynamic normalization can create.

This is a practical speech starting point, not certified true-peak delivery compliance. Meter again in the final editor when a platform or client has a delivery specification.

The tool does not call paid audio services.

Color is handled in the chosen editor. Inspect the actual footage, correct exposure and white balance, match shots and check skin tones before applying a look. This tool has no color-grading feature; do not add a generic color filter to every input.

Before replacing an established audio workflow, use `templates/AUDIO COMPARISON.md`
with a suitable editor. Compare matched source, complete processing bypass and
level-matched listening, then encoded loudness/peak/sync and a separate full
recording. Provider-specific parameter values are not portable presets. This
optional operator procedure does not expand the included tool's capabilities
or change its audio-off default.

### Carrying an approved main into later work

If the user has approved the finished main and explicitly authorizes downstream work using that approval plus audio-presence evidence, carry that acceptance forward without making a new listening pass mandatory. Record the approved file's hash, the instruction and its scope, and the actual audio-stream or visible-waveform evidence in the editor handoff. A waveform shows audio activity; it does not establish how the audio sounds. Record whether anyone listened, and never turn technical evidence into a claim of listening.

Before accepting a newly processed output, retain full audio/video decode, audio presence, planned duration and frame count, measured alignment, and complete spoken-word boundaries. Preserve the approved audio in a picture-only revision and compare it with an independent same-length reference; verify copied audio payloads when applicable. These checks need separate evidence beyond this tool's stream and duration probe. A failed or missing technical check still needs resolution. This downstream policy does not approve new cuts, waive technical or editorial checks, authorize paid processing or publication, or require changes to existing passed review records.

## Output rules

- The source is never an allowed output.
- Existing outputs and reports are refused unless the user explicitly supplies `--overwrite`.
- Rendering happens in a temporary folder, then the tool verifies the video stream, audio stream, and planned duration before moving it to the approved output.
- The output is a standard 8-bit H.264/AAC MP4. Video is re-encoded. Source metadata is stripped, and the encoder may add new technical tags. Subtitle streams, chapters, extra audio or video tracks, HDR, and high-bit-depth inputs are rejected before rendering.
- Reports use basenames, not full local paths, and do not include transcript text.

## Report rules

Record:

- each removed time range;
- the reason for each cut;
- each protected range;
- source and output duration;
- total time removed;
- audio processing applied;
- transcript warnings;
- any single long cut;
- any choice that still needs human review.

Flag a total reduction above 45 percent and every cut longer than 15 seconds. Every spoken-marker cut is marked for review.

## Success check

The output exists as a new file, contains one video and one audio stream, has the planned duration, preserves protected content, matches the approved rules, and has a report that lets a human review every important change. The report distinguishes AI checks from any human review actually performed.

## Test and evidence

Run `tools/setup_doctor.py`, then the unit tests and synthetic FFmpeg test in `tests`. Save the dry-run plan, rendered-copy hash, source hash, media probe, and edit report. A passing fixture does not approve cuts in a real recording.

## Ten-run measurement

Use `TEN-RUN EDIT TRACKER.md`. Record source length, dry-run time, render time, review and rework, proposed and rejected cuts, protected-range failures, and whether the handoff was usable.

## Maintenance loop

Save a known-good edit profile only after repeated reviewed runs. Re-run setup and fixture tests after Python, FFmpeg, operating-system, or optional-model changes. Keep the prior profile until the new one passes.

## Safety and human review

Keep the source immutable and use a new output name. The tool prepares a first pass for the requested editor workflow. Inspect every flagged cut and deliver the result for user feedback; only pause before handoff when the person requested that checkpoint or a material uncertainty remains.

## Optional staged review and clean companion

For projects that need an editorial review before motion finishing, use
`templates/MANUAL REVIEW AND CLEAN MASTER.md` with a suitable editor. It records
which native revision was approved, distinguishes source edits from ripple-only
layer shifts, and defines a clean companion that preserves the approved cuts,
dialogue, grade and recorded demonstrations. Keep added overlays and their sound
effects separable. This operator procedure does not expand the included utility's
capabilities or change its conservative pre-edit defaults.
