# Manual Review and Clean Master

Use this optional procedure with an editor that can preserve source timing and
separate layers. The included pre-edit utility does not inspect native timelines,
manage graphics tracks, or produce this comparison automatically. Keep the tool's
existing source restrictions and approval rules.

## Agree on the review sequence

When the project calls for editorial approval before visual finishing, deliver a
polished cut with the agreed sound and color, an editable project, and no added
graphics or captions. Preserve complete speech, useful breathing, demonstrated
actions and reading time. Inspect fine pacing and partial takes in context; a
fixed silence threshold is not an editorial decision. Check outgoing and incoming
handles together at each join, as well as pauses inside a clip. Distinguish idle
waiting during screen sharing from useful playback, actions and reading time.

Record the review sequence and authorized next stage. If the user already
approved the exact edit and requested its export or next stage, carry that
approval forward within its scope. Export approval does not authorize publication.

- **Review delivery:** [relative media and project labels, hashes, version]
- **Source map:** [relative label; exact frame rate and end convention]
- **Saved native state:** [project/timeline identity and snapshot reference]
- **Reviewer and approval:** [person, instruction reference, exact version, scope]
- **Playback review reported:** [speed and coverage if supplied, or unknown]
- **Agent checks actually performed:** [methods and limits]

## Compare a returned manual edit

Leave the editor under the user's control while they work. When they return it,
locate the project and timeline actually edited, even if renamed or imported, and
save its state before making changes. Preserve the approved revision.

Compare source ranges, their order, audio, grade, framing, speed and dependent
layers with the handoff. Use exact source/output timing instead of treating every
shifted output timestamp as a new decision. Preserve fractional timing where the
editor exposes it. Intersect retained source ranges: an old exclusion between
two endpoints is not a new deletion.

| Change | Source/output evidence | Classification | Supported lesson | Uncertainty |
|---|---|---|---|---|
| [range or layer] | [before/after offsets, lengths and properties] | [ripple only, trim, restored words, take/order change, layer change, or unresolved] | [narrow inference, or none] | [unverified listening, ASR ambiguity, or none] |

For each graphic and its sound cue, compare asset identity, source offset,
duration, position and properties. Splits or ripple shifts can preserve the same
design. A removal's duration alone does not explain why it was removed. Check
speech and visuals in context before generalizing a preference, and keep an
uncertain interpretation separate from an observed edit.

## Make a clean companion

Define what “clean” means for this delivery. A handoff awaiting captions may
retain graphics; a source intended for new crops may need all added overlays
removed. Name the excluded layers explicitly.

For a decorated approved edit, preserve the full timeline and duplicate it.
Disable only the agreed added graphics, captions, overlays and their dedicated
sound effects. Keep the exact approved picture sequence, dialogue, grade,
transforms, crop, speed and other native properties. Keep original recorded
visuals and demonstration audio, including examples of effects being taught.
Use the underlying editable assembly when added overlays are baked into a render.
Reuse approved audio processing instead of enhancing the same dialogue again.

| Layer or source | Role | Full master | Clean companion | Verification |
|---|---|---|---|---|
| [relative label] | [original picture/dialogue, added graphic, added SFX, or other] | [enabled state] | [enabled state] | [source offsets/properties retained or exclusion checked] |

- **Approved full timeline snapshot:** [relative label and hash]
- **Clean timeline snapshot:** [relative label and hash]
- **Exact expected frame count and rate:** [values]
- **Shared picture/dialogue source map:** [relative label and comparison result]
- **Allowed differences:** [exact added layers and dedicated sound effects]
- **Source demonstrations preserved:** [ranges and evidence]
- **Dialogue reference:** [same-length approved reference and hash]

## Verify both exports

Run exports sequentially and wait for each job to complete and close its file
before inspection. Check actual encoded duration, frame count, audio/video decode
and dialogue alignment. Compare native snapshots to confirm that only the
intended layer states differ and that media remain available in the saved project.

Sample each retained graphic at a visible state in the full master and at the
same frame in the clean companion. Include entrances, exits and difficult mask
movement where relevant. Check clean regions against the underlying approved
picture and sample original demonstrations in both exports. Account for codec
noise when comparing decoded pixels.

The clean mix intentionally excludes added effects. Compare its dialogue with
the approved dialogue reference; equal mixed-audio hashes are not the right test.
Payload equality is useful only when the same encoded audio is copied unchanged.
Keep listening, visual sampling, transcript checks and full decode as separate
evidence. A user's review does not mean the agent watched or listened.

- **Full and clean output labels/hashes:** [values]
- **Native layer/source comparison:** [result and receipt]
- **Encoded picture checks:** [exact frames, observations and limits]
- **Dialogue/effects checks:** [reference, method, result and limits]
- **Actual playback review:** [reviewer and coverage, or not performed]
- **Editable project and media readback:** [result]
- **Next authorized use:** [review, motion finishing, clip selection, or other]

Keep both masters when they serve distinct uses. A request for a clean source
export alone does not authorize making clips, imposing a clip quota or publishing.


## Isolated-noise review before approval

Check short retained islands and peaks between dialogue cuts against source
context. Classify speech, useful breaths, demonstration sounds and incidental
input-device noise separately. Record the boundary decision and inspect the
rebuilt phrase. Recognition timestamps that extend through quiet space do not
establish spoken content across that entire interval. Keep meaningful short
speech and complete articulation; avoid a universal minimum clip length or
silence threshold. System 14's cut-review template provides a detailed ledger.
