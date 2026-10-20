# Editing Craft Numbers

Measurable defaults for cutting a talking-head or tutorial video, written so an
assistant can apply them in DaVinci Resolve, Premiere Pro, Final Cut Pro or
CapCut. Every number carries a label: **sourced** (a document listed in
[SOURCES](../../../../docs/SOURCES.md) or named inline), **common practice** (consistent
across working editors and tool vendors, no controlled study) or **opinion** (a
default proposed because an agent needs a number). Opinion defaults are starting
points to tune against the person's taste and their retention data. The
[editing judgment guide](EDITING%20JUDGMENT.md) explains the reasoning; this
file supplies the numbers. The current brief, the actual recording and that
judgment guide take precedence over these ranges. A duration, similarity score
or detected sound identifies something to review; it does not authorize a cut.
Compiled October 3, 2026.

## 1. Two frameworks behind every rule

- Walter Murch's Rule of Six (sourced, *In the Blink of an Eye*): an ideal cut
  serves emotion (51 percent), story (23), rhythm (10), eye-trace (7), screen
  plane (5) and spatial continuity (4). When a cut cannot satisfy all six,
  sacrifice from the bottom up, never the top. For one speaker, criteria five
  and six are nearly free, so the working order is: emotional truth, argument,
  thought boundary, eye position.
- Karen Pearlman's rhythm (sourced, *Cutting Rhythms*): editing is cycles of
  tension and release. A constant pace, even a fast one, is not rhythm. Pace
  should rise toward a payoff and relax after it.
- The viewer-job test (opinion): before each cut, name what the viewer is doing
  (following an argument, reading, watching a demonstration, laughing). Hold
  until that job is done; then judge whether a cut helps the next thought.

## 2. Takes and restarts

Choosing between repeated attempts (common practice, ordered by weight):
completeness, clarity (no stumble or mid-word fix), energy that matches the
neighbors, grammatical and visual continuity with the surrounding sentences.
Check distracting blinks or gestures at a join without sacrificing useful speech
merely to obtain an eyes-open or hands-still frame.

Compare the complete takes rather than choosing the last automatically. A later
attempt may improve the wording or become flat, rushed or off-topic. A change
of roughly 20 percent in speaking pace is a review cue, not a rejection rule
(opinion). For a corrected clause, check meaning, pitch and mic distance before
splicing it into the earlier sentence.

False start versus deliberate repeat (common practice, opinion thresholds): a
false start is short (1 to 6 words), stops without sentence-final intonation,
and the retry begins within about 0.3 to 2.0 s sharing its first two or three
words. A 70 percent match within 2 s can flag a possible retake; listen to both
versions before choosing. Repetition can add emphasis, explain a difficult idea
or support a demonstration even when the wording is identical.

Use restart markers only when the creator has explicitly identified them for
this recording. Words such as "again" or a clap can be meaningful content or a
sync cue. For an agreed marker, locate the actual failed attempt and corrected
take by listening; a pause length alone does not identify the boundary. Remove
only the confirmed failed material within the brief. A full restart can replace
more than one sentence only when that intent is clear. If the marker or retake
is ambiguous, retain it and ask a focused question. Log removed source ranges
and review the rebuilt join with complete words on both sides.

## 3. Pauses, breaths and word edges

Natural speech (sourced): pauses cluster under 200 ms, 200 to 1000 ms and over
1000 ms; listeners rate about 0.6 s as most natural at commas and 0.6 or 1.2 s at
sentence ends; speakers inhale about every 5.3 s; an audible inhale lasts 200 to
500 ms, sits 16 to 29 dB below speech with its energy below 2 kHz, and is
bracketed by about 50 ms of silence each side.

Fast YouTube pacing compresses pauses without removing them (opinion defaults
calibrated to the sourced numbers):

| Context | Leave | Do not apply when |
|---|---|---|
| Between sentences in one thought | 0.20 to 0.40 s | the pause sets up a reveal or number |
| Between thoughts or sections | 0.40 to 0.70 s | an emotional moment is visible on the face |
| Before a reveal, answer or punchline | 0.50 to 1.00 s (keep it) | the pause holds a throat clear or click: clean, do not shorten |
| After a joke or strong line | 0.60 to 1.20 s | the delivery needs a different hold; shorts may also need this pause |
| Mid-sentence hesitation with no content | remove, leave 0.10 to 0.20 s | the join would land inside a breath or a fricative |
| Viewer must read or watch the screen | hold for the reading time; silence is fine | never shorten below the reading time |

Very short sentence gaps can sound rushed. A longer silent stretch may be dead
air or essential reading, reaction or demonstration time. Listen in context;
do not fail either solely because it crosses a duration threshold.

Breaths: keep natural breathing, especially before a long sentence or a new idea.
If a breath distracts, compare a 4 to 8 dB dip (opinion) with the original, or use
a tool that reduces only the distracting breaths. Review a sharp gasp or doubled
breath after tightening; reduce or remove it only if the sentence still sounds
natural and its meaning is preserved. Never leave half a breath; include it
whole or remove it whole (sourced).

Word edges (sourced acoustics, opinion defaults): stop consonants (p, t, k)
release in under 60 ms; word-final s and sh run 100 to 150 ms. Protect the tail
with 80 to 150 ms after the detected end of speech, default 120 ms, 80 ms when
the word ends on a vowel or nasal. Protect the head with 50 to 100 ms before the
first word. Automatic speech recognition timestamps are commonly 20 to 80 ms
late at onsets and early at offsets, so never cut on the raw timestamp. If a join
clicks, try a 2 to 10 ms fade and verify that it preserves articulation; a clean
join needs no extra fade (common practice). Set a silence
threshold 10 to 14 dB above the measured room tone and a minimum trip of 250 to
400 ms, then review (opinion).

## 4. Classifying sounds that are not words

| Sound | Duration | Signature | Action | Label |
|---|---|---|---|---|
| Inhale | 200 to 500 ms | soft rise and fall, 16 to 29 dB under speech, energy under 2 kHz, 50 ms silent edges | keep whole or remove whole; usually dip 4 to 8 dB | sourced |
| Exhale or sigh | 300 to 1000 ms | slow decay, low-mid weighted | remove unless expressive | common practice |
| Throat clear | about 440 to 480 ms | weak onset, concave contour, energy mostly under 800 Hz | cut with its pause | sourced |
| Cough | about 320 to 370 ms | sharp onset burst then decay, broadband | cut; retake if mid-word | sourced |
| Mouth or tongue click | 1 to 15 ms | single narrow spike, peaks 6 to 9 kHz | de-click; cut only if inside a pause | sourced |
| Lip smack | 20 to 80 ms | spike plus short noisy tail | de-click with click widening; cut if in a pause | common practice |
| "um", "uh", hum | 150 to 600 ms | steady, harmonic at the speaker's pitch | remove with its pause; keep one if it carries meaning | common practice |
| Chair creak | 50 to 400 ms | irregular tonal bursts, not harmonic to the voice | cut in pauses; attenuate under speech | opinion |
| Keyboard or mouse click | 5 to 30 ms, trains at 100 to 300 ms | broadband 1 to 8 kHz, rhythmic | keep when typing is on screen; attenuate 6 to 12 dB over speech; cut in pauses | opinion |
| Plosive | 20 to 60 ms | thump under 150 Hz | high-pass or de-plosive; never cut, it is the word | common practice |
| Clap or slate | often a short transient | one loud broadband spike | retain unless confirmed as an agreed restart marker or expendable sync cue | context required |

Use these signatures to find possible problems, then listen. A short transient
can be part of a consonant; duration and frequency alone cannot identify an
unwanted event. Repair an actual click or plosive without removing speech.
Retain expressive breaths, meaningful sounds and sync cues unless their removal
is within the brief. Review isolated tiny clips for accidental remnants.

## 5. Pacing

The one platform fact (sourced): YouTube's Intro metric is the share of
viewers still watching at 30 seconds, and YouTube asks that the first 30 seconds
match the title and thumbnail. Everything else is practitioner practice:

- New information or a new question every 10 to 15 s (sourced quote from a
  former MrBeast retention strategist, who warns that cutting speed alone does
  not hold attention).
- Use a visual change (punch-in, B-roll, text, graphic or angle) when it makes
  an idea or detail easier to follow. Review long static sections, but preserve
  useful demonstrations and reading time. Timing ranges are practitioner
  heuristics, never movement quotas (opinion).
- A real re-engagement (demo, result, story, surprising number) about every 2
  to 3 minutes of a 10 to 15 minute tutorial (opinion, scaled from the leaked
  MrBeast memo's 3 and 6 minute marks; memo origin unconfirmed).
- A sustained fast passage is a reason to check comprehension and fatigue,
  not an instruction to add a pause or effect on a timer (opinion).
- Illustrative ranges, not targets (opinion): educational talking head 12 to 30 cuts per minute,
  average shot 2 to 5 s; tutorial with screen recording 6 to 15 cuts per minute,
  shots 4 to 10 s; shorts 20 to 40 cuts per minute, shots 1.5 to 3 s.

Jump cuts read as "edited for your time" and are accepted on YouTube. They read
badly when the head jumps more than a few percent of frame width, eyes are
closed at the in-point, the mouth is mid-word at the out-point, or the audio
join clicks. Hide a cut with a punch-in, B-roll, a text card or an angle when
light or posture changed across the removal or when a sentence continues across
it; do not hide every cut (common practice).

Split edits (sourced definitions): a J-cut starts the next audio before its
picture; an L-cut keeps the outgoing audio under the new picture. Default lead
or lag of 6 to 24 frames at 24 to 30 fps (opinion).

## 6. Punch-ins and zooms

A UHD frame has twice as many pixels per axis as 1080p. When 100 percent means
the full UHD frame fitted to 1080p, a 200 percent crop reaches roughly one source
pixel per output pixel. Editors expose different scale values depending on how
the clip was fitted, so inspect that setting first. Lens softness, focus, noise
and compression can limit useful enlargement before pixel count does.

| Move | 4K source in a 1080p timeline | Notes |
|---|---|---|
| Base framing | 100 to 110 percent | a 105 to 110 base leaves room for a later pull-back |
| Static punch to hide a cut or mark a new idea | 110 to 130 percent of the base | 110 or 115 for a jump-cut pop, 120 to 130 for a clear close-up |
| Emphasis close-up | 130 to 150 percent | rare; the face fills the frame |
| 1080p source in a 1080p timeline | 100 to 108 percent | above about 110 is visibly soft; prefer B-roll or text to hide cuts |
| 4K source in a 4K timeline | 105 to 125 percent | opinion; softness arrives early at full resolution |

Use two or three fixed values (for example 100, 115, 130) rather than a new
number each time; consistency reads as design (common practice). Push in when
energy rises; pull back on release or to reveal context. A hard cut to the new
scale hides an edit; an animated zoom draws attention. Durations and easing
(common practice, informed by Material Design's motion research): snap zoom 0
to 4 frames; quick push 6 to 12 frames with ease out, landing on the
emphasized word's onset; slow push 0.5 to 1.5 s or across the sentence with ease
in-out; pull back 0.4 to 1.0 s. Keep the eyes on the upper third line within
about 5 percent of frame height across all scales, anchor the transform between
the eyes, leave 5 to 10 percent headroom in a medium shot and never crop the
chin or eyes (sourced rule of thirds, common practice headroom). More than one
punch-in per 8 to 10 s can feel repetitive (opinion). Do not move text the
viewer is still trying to read. The brief and the purpose of the shot decide
whether any punch-in is useful.

## 7. Text, captions and subtitles

Examples from broadcast and streaming guides (Netflix and BBC; use the actual
destination's specification rather than combining these into one universal rule): no faster
than 20 characters per second sustained (17 for children), 160 to 180 words per
minute, minimum about 0.8 s per phrase (20 frames at 24 fps), maximum 7 s, 42
characters per line, 2 lines, a 2 frame gap between consecutive subtitles,
in-time within 1 to 2 frames of the audio, snap to a shot change when speech
starts within 0.5 s of it.

For social captions, choose a readable phrase or highlighted-word style that
fits the speech. If a word is too brief to read, group it into a phrase instead
of forcing a rapid word-by-word display. Check timing against the final edit.

Size and weight (vendor measurements, common practice): shorts captions at
1080x1920, 60 to 75 px cap height (3.1 to 3.9 percent of frame height),
minimum 48 to 55 px, weight 700 or heavier; long-form 16:9 burned captions 40 to
55 px at 1080p; lower-third labels 28 to 36 px. White or near-white fill with a
2 to 4 px dark stroke or a soft shadow at 40 to 60 percent opacity; thin strokes
shimmer under compression. Heavy geometric sans faces: Montserrat Bold or
ExtraBold, Inter Bold, Instrument Sans ExtraBold or Black; thumbnail-style words
at weight 800 or heavier.

Safe areas depend on the destination's current interface. For an arithmetic
example, a 1080x1920 frame with top and bottom margins of 288 px, a right margin
of 140 px and a left margin of 0 px leaves 940x1344 px. These are not universal
platform requirements. Inspect the intended upload preview and adjust all four
margins so captions, faces and demonstrations stay clear of interface overlays.
Long-form 16:9: inside a 90 percent title-safe box, the bottom 10 percent clear
for the progress bar, the lower-right corner clear in the last 20 s for end
screens (YouTube requires end screens in the last 5 to 20 s of a video at least
25 s long, sourced).

Word-by-word timing (vendor practice): light the word 50 to 100 ms before its
onset, hold its duration plus 50 to 100 ms, lead caption blocks by 100 to 200 ms,
gap blocks 150 to 250 ms. Phrase captions (5 to 8 words, 8 to 12 maximum on
mobile) for dense analytical content and long form over 10 minutes; word-by-word
or 1 to 3 words for shorts and muted viewing. One highlighted word per phrase,
at most two per sentence, highlighted by color and kept constant. Animated
captions distract when the viewer must read something else on screen or when the
pop exceeds about 10 percent per word; default pop-in 90 to 100 percent over 2
to 4 frames, no bounce (opinion). Burn in for shorts and emphasis; upload a
sidecar SRT or VTT for every long-form video; both is the usual professional
combination (common practice). Caption errors in the sidecar are QC failures.

Any text card that is not a caption: hold for reading time at 15 characters per
second plus 1 s (opinion).

## 8. Graphics beside or behind the speaker

Add a graphic when the words name something the viewer cannot picture
precisely: a number, a comparison, a sequence, a structure, a term to remember,
a location in a UI. Do not restate a sentence the viewer already understood.
One visual focus at a time: either the graphic is the focus (speaker shrinks or
moves) or the speaker is (graphic small, still, peripheral). Two moving things
at once fails Murch's eye-trace test.

Timing (motion research adapted, common practice): entrance 0.25 to 0.5 s with
ease out; hold for reading time plus 1 s, at least 1.5 s for a number or label;
exit 0.2 to 0.3 s with ease in, faster than the entrance; list items staggered
0.08 to 0.15 s and arriving as they are spoken. The graphic should be fully
visible within 100 to 200 ms after the word that names it; earlier spoils,
later than 0.5 s lags (opinion). Drive the entrance keyframe from the word onset
minus the entrance duration so the settle lands on the word. Place beside the
speaker on the side they face, vertically on the chest line, inside title-safe;
behind the speaker only when keyed or framed small; full frame for anything
needing more than two lines or a diagram.

## 9. Speed without losing quality

Decide the story before cutting: mark the hook, the promise, each section's
payoff and the ending from the transcript. Then pass 1 removes confirmed failed
takes and unwanted material within the brief; pass 2 refines actual joins and
uses punch-ins or B-roll where helpful; pass 3 adds requested or useful text and
graphics; pass 4 is QC (common practice; several
professional editors describe this order). Keyboard only: JKL transport, split
at the playhead, trim start and end to the playhead. Use ripple deletion only
when later timing should move; preserve intentionally timed gaps and overlays.
Review at 1.5 to 2x for structure and repetition if useful,
then at 1x with headphones for every join, because fast playback hides clicks,
clipped consonants and flash frames. Batch like work: all captions in one pass,
all punch-ins in one pass. Templates and presets for captions, titles, the two
or three punch-in scales, the audio chain per microphone, and export per
destination. Stop after the QC pass; iterating cosmetics without a review
trigger lowers quality (sourced from working editors' interviews).

## 10. Quality control before delivery

Structure: the first 5 s state or show the promise and the first 30 s match the
title and thumbnail; every section pays off; repeated ideas earn their place
through explanation, emphasis or demonstration. The ending serves the brief.

Joins and words: every audio join played at 1x with headphones, no click, no
clipped consonant, no half or doubled breath; the output transcript reads as
complete thoughts; pauses support the meaning and allow reading or watching.
Check distracting visual discontinuities without cutting useful speech to meet
a gap, blink or gesture rule.

Picture: no flash frames or black gap frames (scrub every cut frame by frame or
run a black-frame detector); punch-in scales only at the chosen fixed values
with a stable eye line where appropriate; enlarged footage remains acceptably
sharp at delivery size. B-roll supports the relevant idea and holds long enough
to understand. Check essential content against the actual destination overlays.

Audio: sync checked at start, middle and end against a hard consonant; dialogue
consistent within about 3 LU; integrated loudness and true peak at the delivery
target (see [SOUND AND COLOR NUMBERS](SOUND%20AND%20COLOR%20NUMBERS.md)); no
unwanted pops, hums or clicks; meaningful source sounds and expressive pauses
remain intact. Music stays below speech when intelligibility requires it.
If an external audio finish is used, it runs once on the final export and
derivatives come from the untreated master.

Text: every caption word matches the spoken word; timing within 1 to 2 frames
or a deliberate 100 to 200 ms lead; inside safe areas on every destination; one
highlight per phrase; sidecar regenerated after any re-edit.

Export: last 5 to 20 s leave room for end-screen elements; settings match the
destination; watch the exported file, not the timeline, at least once at 1x and
check the first and last 10 s frame by frame.

## 11. Shorts

Hook visually in the first 1 to 2 s; open on the action, result or question,
never a logo or greeting. One well-documented practitioner structure (sourced,
Jenny Hoyos): hook, a two-line foreshadow within 3 s, "but" and "therefore"
transitions rather than "and then", a payoff last line written before filming,
most popular videos around 34 s, a retention floor near 90 percent. Tutorials
may need a different length to preserve a complete useful idea. Check the
destination's current duration and format requirements before export.
For a fast style, try sentence gaps around 0.15 to 0.30 s, then listen; preserve
useful breaths, emphasis and demonstration holds. Add a visual change only when
it helps. Captions may be phrases or highlighted words; test their size, timing
and placement on a phone. A continuous loop is optional. Use the ending and
framing that serve this clip rather than forcing every short into one formula.

## 12. The rules in one table

| Trigger | Action | Default | Not when | Label |
|---|---|---|---|---|
| Repeated span, 70 percent match, within 2 s | compare complete takes in context | candidate review only | intentional repetition, emphasis or demonstration | opinion |
| Later take 20 percent faster or flat | compare clarity, expression and completeness | candidate review only | faster delivery serves the meaning | opinion |
| Explicitly agreed restart marker | identify failed material and corrected take, then review the rebuilt join | no automatic marker deletion | ambiguous intent, meaningful clap or sync cue | context required |
| Unused sentence gap in one thought | try shortening, then listen in context | 0.20 to 0.40 s | reveal, number, punchline or reading hold | opinion |
| Unused gap between thoughts | try shortening, then listen in context | 0.40 to 0.70 s | emotion, emphasis or demonstration needs the hold | opinion |
| Gap before a reveal | keep | 0.50 to 1.00 s | contains a click or throat clear | common practice |
| Any cut point | protect the actual audible word | head 50 to 100 ms, tail 80 to 150 ms as initial handles | source playback requires different handles or pause | acoustics plus opinion |
| Audible click at an audio join | try a short fade and listen again | 2 to 10 ms | already clean, or fade harms articulation | common practice |
| Distracting breath in a kept pause | compare a gentle dip with the original | 4 to 8 dB starting point | natural or expressive breath; treatment makes the join unnatural | opinion |
| Possible unwanted sound in a pause | listen and identify before treating | duration/frequency are review cues | meaningful sound, expressive breath or uncertain classification | context required |
| Confirmed unwanted click inside speech | compare light repair, preserve the word | duration is only a detection cue | meaningful sound, plosive or lost articulation | conditional repair |
| New idea | consider whether a visual helps | no fixed interval or effect quota | current shot already explains it, or viewer is reading | opinion |
| First 30 s | establish and progress the opening promise | meaningful progression, no fixed visual cadence | a clear demonstration needs uninterrupted viewing | sourced metric plus opinion |
| Distracting jump cut | compare a better cut with a useful punch, B-roll or text | punch 110 to 130 percent of fitted base is one option | added visual obscures the demonstration or draws more attention | common practice |
| Animated zoom | ease out, land on the word | snap 2 to 4 frames; push 6 to 12 frames; slow 0.5 to 1.5 s | viewer is reading | common practice |
| Full-sentence captions | meet the destination's caption rules and check readability | timing and line limits above are example guides | a different delivery specification applies | destination-dependent |
| Shorts captions | choose readable phrases or highlighted words | preview size, timing and placement on a phone | text covers the demonstration or competes with required reading | conditional judgment |
| Graphic named by a word | time the entrance to the word | visible within 100 to 200 ms after onset | the graphic is a deliberate reveal | opinion |
| Review | watch the full result at normal speed | optional faster structure pass, then 1x with headphones for joins | faster playback cannot replace normal-speed review | common practice |
| Export | watch the file | first and last 10 s frame by frame | never skip | common practice |

Sourced items above: Murch's Rule of Six; Pearlman's rhythm; YouTube's Intro
metric, end-screen and Shorts rules; Netflix and BBC caption timing; Material
Design motion durations; breath and pause acoustics (Trouvain, Werner and
Möbius 2020; Zvonik and Cummins 2003; Frontiers in Psychology 2022); throat
clear and cough acoustics (PMC 2023); Jenny Hoyos's published structure. Not
verified for this file: Paddy Galloway, Film Booth, Colin and Samir, Peter
McKinnon and Film Riot; nothing here is attributed to them.
