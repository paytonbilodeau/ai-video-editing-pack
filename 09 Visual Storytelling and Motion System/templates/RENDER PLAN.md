# Motion Render Plan

- **Composition:** [name]
- **Version:** [version]
- **Runtime and reason:** [existing renderer/editor, version, why it fits]
- **Finished base:** [relative file label, hash, duration, exact frame rate, or no recorded base]
- **Matching transcript:** [relative file label, hash, origin, timing method, or not applicable]
- **Timing status:** [matches finished base, remapped and checked, provisional, or standalone motion]
- **Story check:** [opening promise, explanation, recorded takeaway; gaps returned to the source-edit owner]
- **Input authority:** [which input governs facts/performance, appearance and requested output]
- **Source-to-output map:** [relative record of source/output intervals, frame rate, crop and speed, or unchanged base]
- **Alignment review:** [beginning, middle, end and splice times checked against playback]
- **Dimensions and fps:** [values]
- **Frame-rate conversion:** [none, or explicit source/output rates and reason]
- **Expected duration and frame count:** [values derived from the approved plan before rendering, with calculation or plan reference]
- **Deterministic inputs:** [fixed seed, timestep, stored transform source, or not applicable]
- **Background:** [opaque or transparent]
- **Blockout, when needed:** [viewer result, accepted geometry/camera/timing, what polish must preserve]
- **Layer order:** [base, insert, foreground and required visible background, or not applicable]
- **Mask source and alignment:** [method, matching source time/crop/speed, hardest full-interval review, or not applicable]
- **Initial state and join check:** [direct frame-zero seek and consecutive frames around changes]
- **Output:** [new relative path]
- **Audio:** [none for overlay, or separate final-edit plan]
- **Audio preservation:** [unchanged encoded audio, intentional re-encode/edit with reason, or not applicable]
- **Approved audio reference:** [same-length clip label, hash, codec and intended streams, or not applicable]
- **SFX cue source:** [rendered frame data, separate approved timeline, or none]
- **Emphasis cue check:** [exact frame and matching readable visual event, or none]
- **Directional fidelity:** [source-supported side and matching label placement, or not applicable]
- **Persistent footer check:** [none, or dedicated evidence beat with reason]
- **Test command:** [command]
- **Reproduction command:** [command using relative asset labels and fixed inputs]
- **Editor persistence:** [save/reload/re-render result, or not applicable]
- **Busy-frame review:** [frame labels]
- **Frame-indexed contact sheet:** [exact frame list and output]
- **Caption safe area:** [boundary]
- **Caption owner and delivery stage:** [renderer or receiving editor; captioned final or clean handoff]
- **Typography reference:** [authorized source; confirmed font or labeled approximation]
- **Rendered text check:** [actual glyph size, card padding, shadow legibility over bright/dark areas and small-display review]
- **Format review:** [each aspect ratio, destination overlay check, small-display result]
- **Movement and edge review:** [exact frames at greatest lean/turn, action near edges, return and final frame; face/action clearance from crop and text]
- **Alpha probe:** [exact transition and transparent-gap frames, or not required]
- **Editor import and base composite:** [receiving editor, tested file, result, or not required]
- **Final-file check:** [dimensions, exact fps, frames, duration, audio tracks, full decode]
- **Audio preservation check:** [audio duration and encoded payload comparison with the approved same-length reference, or separate re-encode/edit review]
- **Frame-timing check:** [constant-frame-rate requirement and measured timing evidence, or not required]
- **Playback review:** [reviewer, file, watched/listened ranges, joins and opening/ending results]
- **Delivery check:** [requested destination, verified file labels and hashes]
- **Pending checks:** [specific limits, or none]
- **Fallback:** [opaque export or editor handoff]
- **Human approval:** [pending or recorded]

## Section recovery, when needed

- **Representative sample:** [difficult transition, acceptance condition and observed result]
- **Attempt budget:** [limit and when to inspect new evidence or change the method]

| Part | Source and reference versions | Core frames / context handles | Expected frames | Output / owned job | State and checks | Attempts / dependencies to refresh |
|---|---|---|---|---|---|---|
| [ID] | [labels and hashes] | [exact ranges and end convention] | [count] | [relative file and ID] | [pending, failed, checked or accepted; evidence] | [count and affected parts/cues] |

Record assembly order, removal of context handles, and checks of every join.
Keep successful parts only while their inputs remain valid. Reconcile uncertain
job state before retries, then review the assembled result separately.

The included starter is configured at 30 fps; the JSON validator accepts integer frame rates only. Record rational source rates exactly and use a compatible route when needed. The template records checks; filling a field does not run them. Compare encoded audio payloads only when the revision preserves the same-length approved audio without re-encoding. That comparison does not replace sync review or listening.

## Approved editorial base and clean companion, when needed

- **Approved native edit:** [project/timeline identity, snapshot and approval scope]
- **Clean companion:** [relative master label and hash; exact excluded layers]
- **Separate added layers:** [graphics/captions and dedicated SFX tracks]
- **Returned manual-edit comparison:** [source-based evidence; ripple shifts versus design/timing changes]
- **Dependent timing after edits:** [continuous drawing/motion and matching sound events checked against the final map]
- **Full/clean parity:** [same picture sequence, dialogue, grade and native properties; permitted added-layer differences]
- **Encoded companion review:** [visible overlay states, mask movement, clean-frame absence and preserved source demonstrations]

Use System 05's `MANUAL REVIEW AND CLEAN MASTER.md` for the editor procedure.
Preserve an approved manual revision. Update motion and cue timing only for the
authorized next stage, and retain the clean companion for new aspect ratios.
Original recorded demonstrations remain part of the picture and sound.
