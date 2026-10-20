# Source, takes and fine pacing

## Preserve the meaning before tightening

Record the exact source hash, native rational frame rate, chosen hook, premise, tension, payoff and transition. Retain the causal order unless a deliberate reordering improves the explanation and preserves its promised content. A tutorial transition is not automatically a better opening than the creator's original argument.

Create a complete source-timed transcript, including failed takes, partial words and repeated syllables. Keep automatic output unchanged and corrections separate. Check the entire relevant recording, including voiced ranges missing from ASR. A cleaned script, summary or edited transcript cannot substitute for the original record. Two recognizers can agree and still omit the same restart.

Use `resolve_source_transcript.py` for an analysis-only draft. It records source hash, duration, FPS, word intervals and an explicitly unverified state. It does not edit media. Reuse a matching complete transcript only after checking source identity and time origin. The inherited recognizer is configured for English; do not apply it to another language and treat the result as reliable. A missing model can require a download, which setup must explain before proceeding.

For disputed speech, replay with context. A constant-gain analysis copy can expose quiet speech without changing duration. If transcribing an excerpt, add its original source offset to every word time. Keep uncertain words labeled rather than guessing. ASR times are not exact phoneme boundaries.

## Choose complete takes

Compare the claim, unique detail, qualifications, articulation, energy and continuity of the whole thought. Start with the latest clean complete take, but do not let a later incomplete or incorrect attempt win by date alone. Prefer one complete supported sentence over an abandoned beginning joined to a different ending. Intentional repetition, emphasis and “I think” may change the message.

Verified “full stop restart” recording commands discard material through the last actual command while retaining speech after it, even within the same VAD segment. “Cut cut” removes the abandoned thought and command while keeping its clean redo. Listen backward and forward to locate the thought; a bounded algorithmic lookback is a first-pass candidate. Do not act on quoted commands, a tutorial discussing them or played media. The automatic script cannot establish that context by itself.

Keep similarity-based retake and filler flags off by default. The included optional tool retains them for an explicitly chosen use, with every proposed deletion reviewed. Automated noise detection can mistake quiet speech or a useful click for disposable sound. Audio-based media protection does not find silent demonstrations.

## Finish the actual assembly

Review five things: complete take selection; both sides of every join; pauses inside retained phrases; word-free noises; and on-screen action/reading holds. A broad “screen share” exemption hides avoidable dead time. Each retained quiet span should have a specific reason.

Tighten towards the audible attack/tail, then replay at normal speed. Small one- or two-frame edge changes can help without creating tiny islands. Do not shave quiet syllables to make a waveform look neat. Remove throat clears or lip smacks only when they do not serve the demonstration; lower intrusive breaths selectively while retaining natural delivery. A short crossfade needs real handles and cannot reconstruct a missing consonant.

Hide incidental paste/menu/recording housekeeping when the viewer does not need it. Keep the completed prompt, meaningful click, demonstrated control, result and enough time to understand them. Preserve speech that overlaps a paste. A quiet interval is not proof that the picture is useless.

After an internal cut, review the joined gap again. Removing 0.4 seconds from a 0.985-second pause leaves 0.585 seconds, regardless of how the two retained tails are split. Inspect accidental tiny pieces and repeated connective words. Do not use a cut count, duration reduction or dB threshold as a quality target.

## Readiness and returned edits

The included `cut_readiness.py` checks declared hook order, exact occupancy, defect dispositions, audio measurement and listening evidence. It cannot discover unreported defects, authenticate a listening claim or judge pacing. Its schema currently supports one explicit source; use the full source map and manual review for multi-source work rather than mislabeling it a pass.

Compare returned edits using disjoint source intervals, not the bounding first/last range. Otherwise an apparent restoration can reintroduce rejected speech between approved pieces. Keep raw native fields; validate left-offset/duration/speed conventions on the current import before treating rounded source getters as exact. A stale marker does not prove a defect remains. Preserve the creator's original returned timeline and retire resolved markers only in a new review copy.

## A tighter dedicated-short option

For the tight dedicated-short starting style, keep the whole intended phrase,
including its quiet last consonant, then trim the following breath, noise or
empty tail at the actual waveform end. Listen to the rebuilt phrase at normal
speed. Do not add a fixed handle to every cut or trim every clip by the same
number of frames. Other formats can keep useful breathing and deliberate holds.
An existing customer preference or current brief takes priority.

Do a separate pass for complete repeated or abandoned lead-ins. A transcript
can merge an audible restart into one fluent sentence. Recheck the disputed
source interval instead of relying on similarity detection alone. Tightening
edges does not remove a repeated thought. If listening is unavailable, label
that remaining check rather than claiming complete cut review.
