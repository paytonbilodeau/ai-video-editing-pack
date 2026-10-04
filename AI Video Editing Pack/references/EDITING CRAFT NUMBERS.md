# Editing Craft Numbers

Measurable defaults for cutting a talking-head or tutorial video, written so an
assistant can apply them in DaVinci Resolve, Premiere Pro, Final Cut Pro or
CapCut. Every number carries a label: **sourced** (a document listed in
[SOURCES](../SOURCES.md) or named inline), **common practice** (consistent
across working editors and tool vendors, no controlled study) or **opinion** (a
default proposed because an agent needs a number). Opinion defaults are starting
points to tune against the person's taste and their retention data. The
[editing judgment guide](EDITING%20JUDGMENT.md) explains the reasoning; this
file supplies the numbers. Compiled October 3, 2026.

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
  until that job is done; cut the instant it is.

## 2. Takes and restarts

Choosing between repeated attempts (common practice, ordered by weight):
completeness, clarity (no stumble or mid-word fix), energy that matches the
neighbors, grammatical and visual continuity with the surrounding sentences,
eyes open and hands still at the in-point.

The last take is the default winner because each attempt rehearses the next,
but not when it is flat from fatigue, rushed (more than about 20 percent faster
than its neighbors, opinion), drifted off the point, or fixed one word inside a
long sentence (then splice only the corrected clause if mic distance and pitch
match).

False start versus deliberate repeat (common practice, opinion thresholds): a
false start is short (1 to 6 words), stops without sentence-final intonation,
and the retry begins within about 0.3 to 2.0 s sharing its first two or three
words. If the repeated span is at least 70 percent identical, the first copy is
shorter, and the gap is under 2 s, keep the later copy. Two complete sentences
with falling pitch where the second adds no words is probably emphasis; keep
both only when the beat earns it.

Spoken restart markers ("cut cut", "again", "take two", a clap under 20 ms):
walk back to the start of the attempted sentence or the last pause over 0.6 s,
forward past the breath or filler to the retake's first word, remove the whole
span, then confirm the retake's opening words match what was removed. If they do
not, the marker may have ended a section; flag it instead of deleting silently.
Log every removed span with its transcript text.

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
| After a joke or strong line | 0.60 to 1.20 s | shorts |
| Mid-sentence hesitation with no content | remove, leave 0.10 to 0.20 s | the join would land inside a breath or a fricative |
| Viewer must read or watch the screen | hold for the reading time; silence is fine | never shorten below the reading time |

Below about 0.15 s between sentences the join reads as a stutter; a silent
stretch over about 0.8 s with no picture change reads as dead air (common
practice). If the new pace makes you tense while listening, you overcut.

Breaths: keep the breath before a long sentence or a new idea. Dip rather than
delete, 4 to 8 dB (opinion), or use a tool that only reduces breaths above a
ceiling. Delete a breath when it is a sharp gasp near the mic or when two breaths
land within one second after tightening. Never leave half a breath; include it
whole or remove it whole (sourced).

Word edges (sourced acoustics, opinion defaults): stop consonants (p, t, k)
release in under 60 ms; word-final s and sh run 100 to 150 ms. Protect the tail
with 80 to 150 ms after the detected end of speech, default 120 ms, 80 ms when
the word ends on a vowel or nasal. Protect the head with 50 to 100 ms before the
first word. Automatic speech recognition timestamps are commonly 20 to 80 ms
late at onsets and early at offsets, so never cut on the raw timestamp. Fade 2
to 10 ms at every audio join to prevent clicks (common practice). Set a silence
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
| Clap or slate | under 20 ms | one very loud broadband spike | treat as a restart marker | common practice |

Decision logic (opinion): anything inside a word boundary is speech unless it
is a transient under 20 ms or a thump under 150 Hz, which are repaired, not cut.
A non-speech event in a pause that lasts 300 ms or more, weighted under 800 Hz,
with no speech within 1 s is most likely a throat clear or exhale: cut it. A
tiny retained clip that contains only a click is a failed cut, not a kept beat.

## 5. Pacing

The one platform fact (sourced): YouTube's Intro metric is the share of
viewers still watching at 30 seconds, and YouTube asks that the first 30 seconds
match the title and thumbnail. Everything else is practitioner practice:

- New information or a new question every 10 to 15 s (sourced quote from a
  former MrBeast retention strategist, who warns that cutting speed alone does
  not hold attention).
- A visual change (punch-in, B-roll, text, graphic, angle) at each new idea and
  at least every 8 to 12 s in long form; every 3 to 6 s in the first 30 seconds
  and in passages with nothing demonstrated on screen (opinion; the "every 3 to
  8 seconds" rule in circulation has no study behind it).
- A real re-engagement (demo, result, story, surprising number) about every 2
  to 3 minutes of a 10 to 15 minute tutorial (opinion, scaled from the leaked
  MrBeast memo's 3 and 6 minute marks; memo origin unconfirmed).
- No fast passage longer than 60 to 90 s without a change of rhythm (opinion).
- Working ranges (opinion): educational talking head 12 to 30 cuts per minute,
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

A UHD frame delivered at 1080p has twice the pixels in each axis, so any scale up
to 200 percent is still downsampling (sourced arithmetic). Lens softness, noise
and compression show before the math does, so the practical ceiling is 160 to
170 percent (common practice).

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
punch-in per 8 to 10 s in long form is a tic (opinion), and never punch while
the viewer is reading on-screen text.

## 7. Text, captions and subtitles

Broadcast and streaming floors (sourced, Netflix and BBC guides): no faster
than 20 characters per second sustained (17 for children), 160 to 180 words per
minute, minimum about 0.8 s per phrase (20 frames at 24 fps), maximum 7 s, 42
characters per line, 2 lines, a 2 frame gap between consecutive subtitles,
in-time within 1 to 2 frames of the audio, snap to a shot change when speech
starts within 0.5 s of it.

YouTube and shorts break these on purpose (word-by-word, centered, larger) but
the floors still apply: never faster than the speaker, never shorter than about
150 ms per word on screen (opinion).

Size and weight (vendor measurements, common practice): shorts captions at
1080x1920, 60 to 75 px cap height (3.1 to 3.9 percent of frame height),
minimum 48 to 55 px, weight 700 or heavier; long-form 16:9 burned captions 40 to
55 px at 1080p; lower-third labels 28 to 36 px. White or near-white fill with a
2 to 4 px dark stroke or a soft shadow at 40 to 60 percent opacity; thin strokes
shimmer under compression. Heavy geometric sans faces: Montserrat Bold or
ExtraBold, Inter Bold, Instrument Sans ExtraBold or Black; thumbnail-style words
at weight 800 or heavier.

Safe areas (vendor measurements; platform UI changes, re-measure in the app):
shorts at 1080x1920 keep essentials out of the top 288 px, the bottom 288 px and
the right 140 px, roughly a 984x1500 band; captions above 300 px from the bottom.
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
payoff and the ending from the transcript. Then pass 1 removes retakes, markers,
long silences and off-topic spans; pass 2 tightens gaps and adds punch-ins and
B-roll; pass 3 adds text and graphics; pass 4 is QC (common practice; several
professional editors describe this order). Keyboard only: JKL transport, split
at the playhead, trim start and end to the playhead, ripple delete everything
so no black frames appear. Review at 1.5 to 2x for structure and repetition,
then at 1x with headphones for every join, because fast playback hides clicks,
clipped consonants and flash frames. Batch like work: all captions in one pass,
all punch-ins in one pass. Templates and presets for captions, titles, the two
or three punch-in scales, the audio chain per microphone, and export per
destination. Stop after the QC pass; iterating cosmetics without a review
trigger lowers quality (sourced from working editors' interviews).

## 10. Quality control before delivery

Structure: the first 5 s state or show the promise and the first 30 s match the
title and thumbnail; every section pays off; no idea survives twice; the ending
lands on the payoff without a wind-down.

Joins and words: every audio join played at 1x with headphones, no click, no
clipped consonant, no half or doubled breath; the output transcript reads as
complete sentences; gaps inside the section 3 ranges; no silence over 1.0 s
without a visual change; eyes open at every in-point.

Picture: no flash frames or black gap frames (scrub every cut frame by frame or
run a black-frame detector); punch-in scales only at the chosen fixed values
with a stable eye line; no upsampled frames; B-roll arrives within 0.5 s of its
word and leaves with the sentence; nothing essential in the bottom 10 percent,
the lower-right corner in the last 20 s, or outside the shorts safe band.

Audio: sync checked at start, middle and end against a hard consonant; dialogue
consistent within about 3 LU; integrated loudness and true peak at the delivery
target (see [SOUND AND COLOR NUMBERS](SOUND%20AND%20COLOR%20NUMBERS.md)); no
pops, hums, clicks or throat clears in kept pauses; music ducked so the voice
leads; if an external audio finish is used, it runs once on the final export and
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
run 25 to 40 s by default; YouTube caps Shorts at 3 minutes and 1080p (sourced).
Shorten pauses to 0.15 to 0.30 s between sentences, remove breaths that are not
needed for a long phrase, change the visual at least every 2 to 4 s (vendor
practice). Captions word-by-word or 1 to 3 words, 60 to 75 px, weight 700 or
heavier, centered, above 300 px from the bottom. Face in the upper middle with
eyes near the upper third line inside the safe band. End on a line or image that
connects to the first frame so the replay feels continuous; no goodbye.

## 12. The rules in one table

| Trigger | Action | Default | Not when | Label |
|---|---|---|---|---|
| Repeated span, 70 percent match, within 2 s | keep the later take | 70 percent, 2.0 s | both complete with falling pitch and no new words | opinion |
| Later take 20 percent faster or flat | prefer the earlier complete take | 20 percent | earlier take stumbles | common practice |
| Restart marker | remove from the failed sentence start through the marker and filler | clap under 20 ms | retake's first words do not match: flag | common practice |
| Sentence gap in one thought | shorten | 0.20 to 0.40 s | reveal, number, punchline follows | opinion |
| Gap between thoughts | shorten | 0.40 to 0.70 s | emotional moment on face | opinion |
| Gap before a reveal | keep | 0.50 to 1.00 s | contains a click or throat clear | common practice |
| Any cut point | protect word edges | head 50 to 100 ms, tail 80 to 150 ms (120 default) | never skip | sourced acoustics |
| Any audio join | fade both sides | 2 to 10 ms | never skip | common practice |
| Breath in a kept pause | dip, do not delete | 4 to 8 dB | sharp gasp near the mic: delete whole | sourced plus opinion |
| Non-speech event 300 ms or longer, under 800 Hz, weak onset | cut with the pause | throat clear 0.44 to 0.48 s | part of a laugh that is content | sourced |
| Transient under 20 ms inside speech | de-click, do not cut | one or two light passes | it is a plosive: de-plosive instead | sourced |
| New idea | visual change | at each idea; at least every 8 to 12 s | viewer is reading | opinion |
| First 30 s | faster cadence, promise stated | visual change every 3 to 6 s | the hook is one demonstration | sourced metric plus opinion |
| Jump cut with a head jump or mid-thought removal | hide with punch, B-roll or text | punch 110 to 130 percent of base | already one punch per 8 to 10 s | common practice |
| Animated zoom | ease out, land on the word | snap 2 to 4 frames; push 6 to 12 frames; slow 0.5 to 1.5 s | viewer is reading | common practice |
| Full-sentence captions | obey floors | 20 cps, 160 to 180 wpm, 0.8 s minimum, 7 s maximum, 42 chars, 2 lines | word-by-word shorts captions | sourced |
| Shorts captions | word-by-word, heavy sans, centered | 60 to 75 px, weight 700 plus, above 300 px from bottom | dense analytical content | vendor practice |
| Graphic named by a word | time the entrance to the word | visible within 100 to 200 ms after onset | the graphic is a deliberate reveal | opinion |
| Review | two speeds | 1.5 to 2x for structure, 1x with headphones for joins | never skip the 1x pass | common practice |
| Export | watch the file | first and last 10 s frame by frame | never skip | common practice |

Sourced items above: Murch's Rule of Six; Pearlman's rhythm; YouTube's Intro
metric, end-screen and Shorts rules; Netflix and BBC caption timing; Material
Design motion durations; breath and pause acoustics (Trouvain, Werner and
Möbius 2020; Zvonik and Cummins 2003; Frontiers in Psychology 2022); throat
clear and cough acoustics (PMC 2023); Jenny Hoyos's published structure. Not
verified for this file: Paddy Galloway, Film Booth, Colin and Samir, Peter
McKinnon and Film Riot; nothing here is attributed to them.
