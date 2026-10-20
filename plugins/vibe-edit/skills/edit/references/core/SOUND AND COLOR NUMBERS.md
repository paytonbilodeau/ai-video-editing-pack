# Sound and Color Numbers

Starting values for dialogue audio and color on a talking-head video, with the
reasons and the tool names in each editor. Labels: **sourced** (standard,
vendor manual or a named practitioner's published guidance), **common
practice**, **opinion**. Every value is a starting point to check against meters
and ears, never a preset to apply blind. The [audio guide](AUDIO%20GUIDE.md)
explains how to choose treatment by microphone and defect; this file supplies
the numbers. The current brief and the audio guide take precedence. Do not add
a processor merely because it appears below. Respect a no-processing request
and preserve a clean source for derivatives. Compiled October 3, 2026.

## Part A: Sound

### A1. Loudness targets and why they differ

- ITU-R BS.1770 defines the LUFS measurement and true peak; EBU R128 sets
  broadcast at -23 LUFS integrated with a -1 dBTP maximum (sourced). Apple
  Podcasts asks for -16 LUFS with a 1 dB tolerance and -1 dBTP (sourced). AES
  streaming guidance puts speech around -18 and music around -16 (sourced via a
  summary).
- YouTube playback normalization and optional [Stable Volume](https://support.google.com/youtube/answer/14106294)
  can change the listening result. Do not rely on playback processing to fix
  an uneven or quiet mix, or treat an observed playback level as a guaranteed
  upload requirement.
- Recommendation for talking heads (opinion from the above): -14 to -16 LUFS
  integrated with true peak no higher than -1 dBTP is a useful web starting
  range. Do not raise the level merely to compete with playback normalization.
  Pick a target suited to
  the destination and keep comparisons consistent across
  the channel. Measure the encoded export, not the timeline meter, because
  lossy encoding adds peak overshoot.

### A2. Choose only the treatment the recording needs

These are possible treatments, not a mandatory chain. Their order can change
the sound, so inspect the actual signal path and compare the result. If Auphonic
or another final service is the chosen route, finish cuts and visuals first,
then use that finish once on each delivered export. Do not automatically stack
this full chain before it. Derivatives start from the pre-finish master.

0. **Edit first, listen raw.** Note what is wrong before processing. Only treat
   what you heard.
1. **Clip gain.** Match gross differences between takes before any dynamics.
   Raw dialogue peaks around -12 to -6 dBFS, body around -20 to -18 dBFS
   (common practice). A leveler first (Resolve Dialogue Leveler, Optimize
   Moderate Levels, Lift Soft Dialogue off on noisy sources) means the
   compressor later has less work to do; check whether compression is still
   needed (practitioner guidance).
2. **Repair.** De-clip if tops are squared; de-hum at 50 or 60 Hz with
   harmonics; mouth de-click at light sensitivity; de-plosive, or a dynamic cut
   of 3 to 5 dB near 150 Hz on the burst, or a clip-gain dip of 6 to 9 dB on the
   plosive alone (sourced).
3. **Noise.** Steady hiss and room tone: spectral noise reduction in light
   amounts, starting low and increasing only while the result improves. For
   changing background noise, compare voice isolation with the original;
   a clean shotgun recording may need none. Listen for watery
   or robotic voice, chirps in pauses, lost room tone that makes edits jump,
   dulled consonants. Some background noise beats artifacts.
4. **High-pass.** If low rumble is audible, try roughly 70 to 100 Hz at 12 to
   18 dB per octave, then adjust for this voice and recording (starting values).
   Stop before the voice loses useful body. Put it before dynamics when rumble
   is driving the compressor; a clean recording may need no filter.
5. **Subtractive EQ.** Sweep with a narrow boost to find the resonance, then
   cut with Q 1.5 to 3: mud 200 to 300 Hz (2 to 3 dB; thin voices may want a
   boost instead), boxiness 300 to 800 Hz (2 to 4 dB; chest lavs resonate near
   730 Hz), nasal honk 1 to 2 kHz (2 dB), harsh resonance 2 to 5 kHz (narrow
   only, since it is also presence). Do not static-cut sibilance; use a
   de-esser (sourced).
6. **Presence and air.** If a voice remains dull, try a small wide boost around
   3 to 5 kHz; an optional 1 to 2 dB shelf around 10 to 12 kHz also raises hiss.
   Check harshness and sibilance. EQ before compression changes what triggers
   it; EQ after compression changes the finished tone. Choose the placement
   that solves the audible problem rather than applying a fixed boost rule.
7. **De-esser.** Band 5 to 8 kHz, 7 kHz center (4 to 5 kHz for deep voices, 8
   to 10 kHz for bright ones), 3 to 6 dB of reduction only on esses, release 50
   to 100 ms; stop before the voice lisps (sourced controls, common practice
   values).
8. **Compression.** Ratio 2.5:1 to 3:1 (Blackmagic's own dialogue guidance,
   sourced), attack 10 to 25 ms and release 100 to 200 ms are possible starting
   points. Set the threshold for the actual input. Compare intelligibility and
   expression with and without treatment at matched loudness. More than 6 dB
   of reduction is a reason to listen, not proof that clip gain was skipped.
9. **Peak control.** After the mix and loudness gain are settled, measure true
   peak. If peaks exceed the chosen delivery ceiling, use gain adjustment or
   suitable limiting and compare the result. A -1.0 dBTP ceiling is a common
   web starting point; the actual destination requirement takes precedence.
   A file already within target needs no additional limiter simply to pass QC.
10. **Final loudness.** Measure the whole mix, including music. If a gain change
    is needed, re-check true peak afterwards and adjust peak control if needed.
    Verify the encoded file; processing or encoding can change the peaks.
11. **Room tone and breaths.** Fill gaps with room tone, not digital silence
    when the gap would otherwise sound abruptly gated. Retain natural breaths;
    reduce only distracting ones and compare in the assembled sentence.
12. **Music under speech.** 18 to 24 LU below dialogue while speaking (roughly
    -34 to -40 LUFS short-term on the music when speech sits at -14 to -16),
    rising to -22 to -26 LUFS short-term in gaps, intros and B-roll (opinion
    reasoned from the standards). Duck 6 to 12 dB with attack 30 to 80 ms and
    release 250 to 700 ms; Fairlight Ducker 3:1 to 5:1 with the dialogue track as
    the trigger (sourced). If the music still masks consonants, compare a 2 to
    4 dB reduction around 1 to 4 kHz with a simple level change (common practice).
13. **Compare at matched loudness.** A louder version can bias the comparison.
    Match listening level with gain or a loudness meter, then judge clarity,
    artifacts and expression. Louder is not automatically better.

### A3. Per-microphone starting points (mix of sourced and common practice)

| Source | Possible issues to listen for | Conditional starting points |
|---|---|---|
| Shotgun indoors | boxiness, hollow early reflections | compare gentle de-reverb if the tail is distracting; filter rumble or de-ess only if audible |
| Lav or wireless | proximity buildup, muffling under clothing, rustle | locate the actual resonance before EQ; repair rustle without removing speech; do not assume a fixed resonance frequency |
| Dynamic broadcast mic | preamp hiss, strong proximity effect | try a small low-mid cut if boomy; add presence only if dull, not simply because of the mic type |
| USB condenser | room, keyboard and desk noise, brightness | compare noise treatment where needed; retain useful demonstration clicks and avoid boosting already harsh highs |
| Phone or camera built-in | room, automatic gain or processing already applied | compare a light repair with the original; avoid adding another leveler or compressor if it worsens existing gain changes |

### A4. Where the tools live

- **Resolve (Fairlight).** Inspector > Audio on a clip: Voice Isolation
  (Studio, Amount 0 to 100), Dialogue Leveler (free and Studio; presets Allow
  wider dynamics, More lift for low levels, Lift soft whispery sources, Optimize
  moderate levels; switches Reduce Loud, Lift Soft, Background Reduction; Output
  Gain 0 to 6 dB). Mixer channel strip: 6-band EQ, Dynamics (expander, gate,
  compressor, limiter), six FX slots. FairlightFX: De-Esser, De-Hummer, Noise
  Reduction with learn, Ducker, Limiter. Studio adds Dialogue Separator,
  Dialogue Matcher and Audio Assistant (an automatic mix whose effects you can
  open and adjust). Loudness meter in the Mixer; target in Project Settings >
  Fairlight (default -23, set -14 or -16). Normalize Audio Levels on clips with
  Sample Peak or BS.1770 modes. No "Dialogue Processor" by that name exists.
- **Premiere (Essential Sound, Dialogue).** Loudness > Auto-Match (targets -23
  LUFS, changeable only through Audition's master template, reported); Repair
  sliders 0 to 10: Reduce Noise, Reduce Rumble, DeHum 50 or 60 Hz, DeEss, Reduce
  Reverb; Clarity: Dynamics (Natural to Focused), EQ presets with Amount, Vocal
  Enhancer High or Low tone; Enhance Speech with a Mix Amount; Loudness Radar on
  the master via Audio Track Mixer > Special (set -16 or -14 for web).
- **Final Cut (Audio inspector > Audio Enhancements).** Equalization presets or
  manual; Voice Isolation Amount (per component; several at once can garble);
  Loudness (Amount and Uniformity, a compressor-style control, not a
  normalizer); Background Noise Removal Amount; Hum Removal 50 or 60 Hz;
  Modify > Enhance Audio runs the analysis. No LUFS meter: measure the export or
  use an Audio Unit meter.
- **CapCut (Audio tab).** Normalize loudness (target undocumented), Enhance
  voice with an intensity slider, Reduce noise, Isolate voice (paid where
  gated). Measure the export.

### A5. Reading the waveform and spectrogram (sourced, iZotope and SoundGirls)

Squared tops: clipping, de-clip first. Horizontal lines at 50 or 60 Hz with
fainter lines above: hum, de-hum with harmonics. Buzz: hum whose harmonics reach
above 400 Hz. Speckle across the spectrum: hiss, light noise reduction passes.
Bright low-frequency bumps under p, b, t, k: plosives. Thin vertical lines: mouth
clicks. Bright bursts at 5 to 9 kHz on s and sh: sibilance. Smear after each
word: room reverb, de-reverb before EQ. Harmonic stacks sliding in pitch under
the voice: music bleed, isolation can only reduce it.

### A6. Mastering and QC

Measure the encoded file: integrated LUFS, true peak, loudness range (4 to 8 LU
is typical for a leveled talking head, opinion). A single microphone is mono:
map it to a mono track or center it; never duplicate it onto left and right
with an offset, never leave one channel silent; music stays stereo. Check lip
sync at the start, middle and last minute; a file processed outside the editor
must return at the same duration to the frame. Listen on headphones (clicks,
hiss, edits), a phone speaker (intelligibility, whether the high-pass removed
body) and a laptop or TV speaker (sibilance, harshness). Spot-check three places
where music runs under speech with eyes closed on the phone speaker. Confirm no
truncated first syllable and room tone, not silence, under the opening frames.

## Part B: Color

### B1. Order of operations (sourced: Juan Melara, Cullen Kelly, Jarle Leirpoll)

1. Identify the source encoding, working space and intended output. For a
   simple Resolve route, use Color Management with correct input tags, or use
   explicit CST input/output nodes in an unmanaged project. Do not apply the
   same normalization twice. A CST can also serve a deliberate conversion
   inside a managed project; its presence alone does not prove a double
   transform. Check Premiere's color-management settings or Final Cut's camera
   interpretation before adding a technical LUT.
2. Exposure on the waveform: black point, white point, then midtones.
3. White balance against something neutral and the vectorscope skin line.
4. Contrast with a pivot, then saturation.
5. Match shots to the hero (Resolve stills and wipe, Premiere Comparison View
   and Color Match, Final Cut Match Color).
6. Put the creative look or LUT on its own adjustable node or effect. Match its
   expected input space and check for clipping or unwanted color shifts.
7. Secondaries for skin, background, eyes and teeth.
8. Confirm the output transform matches delivery. For SDR Rec.709, let the
   chosen managed output or explicit output transform perform that conversion
   once. Check levels; add a legalizer only if the destination requires it and
   the signal needs correction.

### B2. Exposure and balance targets (sourced ranges, opinion placements)

The figures below are comparison points for an SDR example, not values every
face or scene must hit. Lighting intent, skin reflectance and the chosen view
transform matter. Preserve the intended scene and confirm by looking as well
as reading scopes; do not force every complexion onto one target.

On a 0 to 100 waveform of a Rec.709 image: skin falls roughly between 45 and 70
(light skin 65 to 75 in one guide), middle gray near 45, midtones 33 to 66,
highlights 66 to 100 (sourced). Place the brightest diffuse part of the face at
60 to 70, the average lit face at 50 to 65 for light skin, 40 to 55 for medium,
30 to 45 for dark, with a specular skin highlight at 70 to 85 so the face does
not read flat; blacks at 2 to 5, not 0, so shadows keep detail on phones
(opinion). In log before the transform, 18 percent gray sits near 34 to 41
depending on the curve (sourced), so read scopes after the input transform.

White balance: use a known neutral reference when one is available, then check
skin and the rest of the scene. The vectorscope skin-tone line is a reference,
not a rule that every face must sit exactly on it. If skin differs from a
neutral reference, inspect lighting, makeup, source interpretation and the
creative look before choosing a global or selective correction.

Contrast: Resolve contrast 1.05 to 1.15 with the pivot near the face's mid
level (default pivot 0.435; one colorist uses 0.391 for 18 percent gray in his
working space). Saturation after contrast: Resolve 55 to 60, Lumetri 105 to
115 with Vibrance before Saturation to protect skin (opinion). Skin that reaches
the vectorscope's red and yellow targets is oversaturated.

### B3. Node and panel order per editor

- **Resolve:** one example uses camera input to DaVinci Wide Gamut/Intermediate,
  then balance, contrast, saturation and any needed secondaries or look, then
  the delivery output. In RCM, verify the managed input/output transforms;
  in a manual CST route, use explicit nodes for them. Do not add a second
  output conversion because a generic node recipe lists one. A film-print LUT
  needs its specified gamut/gamma at the input and a known output; do not
  assume every such LUT expects the same Cineon conversion. Save a reusable
  empty tree only after documenting its source, working and output spaces.
- **Premiere (Lumetri, top to bottom):** Basic Correction (Input LUT for
  technical transforms, white balance, exposure, contrast, highlights, shadows,
  whites, blacks, saturation; Whites and Blacks apply before the other sliders
  despite their position) > Creative (Look for creative LUTs, vibrance,
  saturation, split tone) > Curves > Color Wheels and Match > HSL Secondary >
  Vignette (sourced). Separate Lumetri effects per job, renamed; shared look on
  an adjustment layer. Choose viewer gamma for the actual monitoring setup
  and delivery, then keep that setup consistent; 2.2 is not a universal web rule.
- **Final Cut:** Apple states no required order (sourced). Practical: Balance
  Color or Color Adjustments (Enhance Light and Color as a start) > Color Wheels
  > Color Curves > Hue/Saturation Curves for secondaries > Custom LUT effect
  last; Auto Mask inside a corrector for skin (common practice).
- **CapCut:** one adjustment layer across the timeline; Adjust > Basic for
  temperature, tint, exposure, contrast, highlights, shadows; verify a supported
  input transform for log rather than treating contrast curves as a defined
  color-space conversion; HSL for one color; optional creative LUT or vignette
  (reported from the color course).

### B4. Sources that need different handling

Log: identify the exact camera gamut/gamma and use the appropriate input
interpretation or transform. Higher contrast after conversion does not by
itself prove the transform is correct. Rec.709 sources do not need a log-to-709
LUT, but still need correct tagging and any conversion into the chosen working
space. Phones may record ordinary SDR, HLG, another HDR format or Apple Log;
inspect the actual file and verify automatic detection before relying on it.
Match saturation by comparison, not a mandatory percentage reduction.

Keep screen recordings and authentic UI evidence out of creative looks that
alter their meaning or appearance. Identify their actual encoding rather than
assuming every screen capture is sRGB. For mixed sources, map each correctly
into the working space, balance and match shots, then test a shared creative
look only on the material it is intended to affect.

### B5. Skin, eyes, background, vignette (common practice, opinion amounts)

Qualify skin mainly to protect it: slight desaturation of over-red skin, a hue
nudge toward the skin line, a 2 to 5 percent midtone lift; apply the look after
skin is right or key skin out of the look. Eyes: a small window with 3 to 5
percent gain and slight sharpening; teeth: narrow yellow qualifier, 10 to 20
percent less saturation, no brightness lift. Background: 10 to 25 percent
darker than the face and 10 to 20 percent less saturated, with an inverted
person mask or a soft window; add 2 to 4 pixels of edge blur so hair chatter
stays invisible. Vignette: a soft oval centered above the face darkening 5 to
15 percent; if you can see its edge it is too strong.

### B6. LUT practice (sourced principles)

Technical LUTs convert defined encodings; place them where that conversion is
needed. Creative LUTs supply looks. The node before a LUT must produce what it expects
(feed a LogC LUT LogC). Test on a gray ramp and a chart: the ramp must stay
smooth unless the intended look deliberately changes it. A 33-point LUT is a
useful starting size; grid size, interpolation, the transform and footage all
affect accuracy. A 17-point LUT does not necessarily show banding, and a larger
grid does not guarantee a good look. Check skin and gradients on representative
footage and a different held-out clip. Wrong input/output assumptions can cause
crushed contrast, clipping or hue shifts; identify the mismatch rather than
diagnosing it from one appearance alone. A LUT cannot adapt to exposure or white balance between
shots, hold masks or tracking, or do spatial work; never bake the input
normalization into a creative LUT or it becomes camera-specific. An
AI-generated .cube deserves the same ramp and chart test before use; prefer an
editable node tree or PowerGrade when the look must stay adjustable.

### B7. The talking-head starting look (opinion; adjust to the footage)

Contrast plus 5 to 15 percent with a gentle S-curve rather than crushed blacks;
highlight roll-off so the brightest skin and background land at 85 to 95 instead
of clipping; saturation 55 to 60 (Resolve) or 105 to 115 (Lumetri); a small warm
push in the midtones (Resolve offset or midtone wheel 1 to 3 units, Lumetri
Temperature plus 3 to 8) with the background allowed slightly cooler for
separation, then recheck skin on the line; skin desaturated 5 to 10 percent if
it reads red; background 10 to 25 percent darker; no sharpening beyond the
camera's; spatial noise reduction 5 to 10 on the background only if the darkened
areas show noise.

### B8. Monitoring: why YouTube looks different

The editor viewer, export transform, file tags, player and display can each
affect appearance. Record the chosen SDR/HDR output and monitoring setup. Tags
should describe the actual encoded signal; do not relabel a file or change the
grade merely to compensate for one player's appearance. Check the exact export
in a color-managed player on the same display, then inspect the intended
destination and another representative screen. An unlisted upload is an
external action and needs authorization. A gray ramp and representative skin
frame can help separate a pipeline mismatch from a creative grading choice.

### B9. Compact rules

| Trigger | Action | Default | Not when | Label |
|---|---|---|---|---|
| Takes differ in level | clip gain before dynamics | peaks -12 to -6 dBFS | within 2 dB already | common practice |
| Distracting level changes | compare clip gain or a leveler, then assess remaining dynamics | start gently and compare at matched loudness | existing camera processing or extra compression worsens the voice | conditional treatment |
| Hum lines at 50 or 60 Hz | de-hum with harmonics | 3 to 5 harmonics | high-pass already removed it | sourced |
| Distracting changing background noise | compare gentle isolation with the original | start low; increase only while useful | clean source, lost articulation or watery voice | conditional starting point |
| Audible low rumble | try a high-pass before dynamics | roughly 70 to 100 Hz; adjust by listening | no rumble or voice loses body | conditional starting point |
| Boomy | cut 200 to 300 Hz | 2 to 3 dB, Q 1.5 | thin voice: boost instead | sourced |
| Boxy | cut 300 to 800 Hz | 2 to 4 dB, Q 2 to 3 | de-reverb solved it | sourced |
| Buried | presence | plus 2 to 3 dB at 3 to 5 kHz, wide | already harsh | sourced |
| Piercing esses | de-esser | 5 to 8 kHz, 3 to 6 dB, release 50 to 100 ms | esses fine after reducing presence | common practice |
| Uneven peaks | compressor | 2.5:1 to 3:1, attack 10 to 25 ms, release 100 to 200 ms, 2 to 6 dB | leveled within 3 dB already | sourced |
| Delivery check | measure integrated loudness and true peak | use the destination target; -1.0 dBTP is a common web ceiling | measurement does not require another processing pass | measurement plus starting point |
| Final mix outside the chosen target | adjust gain or suitable peak control, then remeasure the encode | -14 to -16 LUFS is one web speech starting range | already within target, no-processing brief or selected external finish | opinion |
| Distracting breaths | compare gentle attenuation with the original | retain natural breathing and complete words | the breath carries expression or treatment harms the join | conditional treatment |
| Music under speech | duck or ride | 18 to 24 LU under dialogue; duck 6 to 12 dB | speech-free passages: -22 to -26 LUFS short-term | opinion |
| Mono mic | map mono, center | one channel | stereo music | common practice |
| Known source encoding | map source to the chosen working space | managed interpretation or explicit transform, with output defined | the same conversion is already applied | color-management requirement |
| Exposure | inspect the scene, output transform and scopes before adjusting | SDR ranges above are examples, not targets for every face | intentional lighting, different skin tone or a different output | conditional judgment |
| Suspected color cast | inspect known neutrals and source interpretation, then compare skin | vectorscope line is a reference | intentional colored light or no reliable neutral reference | conditional judgment |
| Creative LUT | late node, ramp and chart test | 33 point | input mismatch, banding, skin twist | sourced |
| Screen capture | preserve authentic UI and exclude it from creative looks | identify actual encoding and map it correctly | do not guess sRGB or Rec.709 from the content alone | color-management check |
| Export differs from the editor | compare output transform, actual tags, player and display | keep the chosen monitoring setup consistent | do not retag or regrade solely to match one player | pipeline check |
