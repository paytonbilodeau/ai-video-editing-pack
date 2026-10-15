# Optional tighter teaching reference

Payton's returned edits repeatedly tighten fine gaps inside phrases and at existing joins. The starting preference is crisp speech with no accidental leading/trailing fragments, no automatic pause merely because a layout changed, and breaths retained when they carry emphasis or keep the delivery natural. A sentence about a screen action still needs the action and reading time.

The following measurements are included so the actual working reference is available. They describe specific recordings, not safe defaults for arbitrary voices or input levels:

| Historical reference | Observed / proposed | Scope |
|---|---|---|
| Around 36 ms after audible tails and 27 ms before attacks; many joins with no measured silence | Observed returned-pass measurements | One microphone/recording and its chosen envelope threshold |
| Roughly 20 ms tail and 15 ms attack detector margins, with source-relative level checks | Applied candidate on a later part | Needed source calibration and actual listening; it still required correction |
| A voiced-attack search above -40 dBFS, 15 ms margin and median residue under three frames | Proposed follow-up to distinguish breath/lip noise from the actual word | An unqualified hypothesis, not a proven universal detector or target |
| First/last four seconds of finished shorts checked for lost words or stray conjunctions | Practical boundary review | Full relevant review remains necessary |

Use these as a comparison reference only after matching the source level, microphone and intended pace. Do not cut at these numbers without hearing the actual word. Low source level changes what a fixed dB threshold detects. ASR spans locate a region but do not determine phoneme boundaries. If the edit gets choppy or loses articulation, widen the relevant handle and replay it.

The assistant's job is to finish useful fine work before handoff, not to achieve a statistic. Preserve the creator's returned map and inspect whether a proposed detector actually reduces repeated corrections on the next authorized edit. A new rule file is not evidence that it does.
