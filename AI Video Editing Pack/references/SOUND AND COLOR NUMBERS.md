# Sound and Color Numbers

Starting values for dialogue audio and color on a talking-head video, with the
reasons and the tool names in each editor. Labels: **sourced** (standard,
vendor manual or a named practitioner's published guidance), **common
practice**, **opinion**. Every value is a starting point to check against meters
and ears, never a preset to apply blind. The [audio guide](AUDIO%20GUIDE.md)
explains how to choose treatment by microphone and defect; this file supplies
the numbers. Compiled October 3, 2026.

## Part A: Sound

### A1. Loudness targets and why they differ

- ITU-R BS.1770 defines the LUFS measurement and true peak; EBU R128 sets
  broadcast at -23 LUFS integrated with a -1 dBTP maximum (sourced). Apple
  Podcasts asks for -16 LUFS with a 1 dB tolerance and -1 dBTP (sourced). AES
  streaming guidance puts speech around -18 and music around -16 (sourced via a
  summary).
- YouTube publishes no number. Measurement shows it turns louder uploads down
  to about -14 LUFS and never raises quiet ones; "Stable Volume" may add dynamic
  processing on top (sourced for behavior).
- Recommendation for talking heads (opinion from the above): deliver -14 to
  -16 LUFS integrated, true peak no higher than -1 dBTP, and nothing louder than
  -14 because the extra limiting buys nothing. Pick one target and keep it across
  the channel. Measure the encoded export, not the timeline meter, because
  lossy encoding adds peak overshoot.

### A2. The dialogue chain in order

Each stage changes what the next one sees, so the order matters (consensus of
the sourced guides).

0. **Edit first, listen raw.** Note what is wrong before processing. Only treat
   what you heard.
1. **Clip gain.** Match gross differences between takes before any dynamics.
   Raw dialogue peaks around -12 to -6 dBFS, body around -20 to -18 dBFS
   (common practice). A leveler first (Resolve Dialogue Leveler, Optimize
   Moderate Levels, Lift Soft Dialogue off on noisy sources) means the
   compressor later only touches transients (sourced, Curtis Judd).
2. **Repair.** De-clip if tops are squared; de-hum at 50 or 60 Hz with
   harmonics; mouth de-click at light sensitivity; de-plosive, or a dynamic cut
   of 3 to 5 dB near 150 Hz on the burst, or a clip-gain dip of 6 to 9 dB on the
   plosive alone (sourced).
3. **Noise.** Steady hiss and room tone: spectral noise reduction in light
   passes of 6 to 12 dB, never one heavy pass. Changing background (traffic,
   HVAC): voice isolation, Resolve 70 to 80 for a noisy room, lower (35 to 50)
   for a clean shotgun recording (sourced range plus opinion). Listen for watery
   or robotic voice, chirps in pauses, lost room tone that makes edits jump,
   dulled consonants. Some background noise beats artifacts.
4. **High-pass.** 80 Hz for male voices, 100 Hz for female, 12 to 18 dB per
   octave, before the compressor so rumble does not drive it (sourced). Above
   120 Hz a male voice thins.
5. **Subtractive EQ.** Sweep with a narrow boost to find the resonance, then
   cut with Q 1.5 to 3: mud 200 to 300 Hz (2 to 3 dB; thin voices may want a
   boost instead), boxiness 300 to 800 Hz (2 to 4 dB; chest lavs resonate near
   730 Hz), nasal honk 1 to 2 kHz (2 dB), harsh resonance 2 to 5 kHz (narrow
   only, since it is also presence). Do not static-cut sibilance; use a
   de-esser (sourced).
6. **Presence and air.** 2 to 3 dB wide boost between 3 and 5 kHz for
   intelligibility; a 1 to 2 dB high shelf from 10 to 12 kHz only on clean
   recordings, since it raises hiss as much as voice (sourced for presence,
   common practice for air). Boosts after compression, cuts before.
7. **De-esser.** Band 5 to 8 kHz, 7 kHz center (4 to 5 kHz for deep voices, 8
   to 10 kHz for bright ones), 3 to 6 dB of reduction only on esses, release 50
   to 100 ms; stop before the voice lisps (sourced controls, common practice
   values).
8. **Compression.** Ratio 2.5:1 to 3:1 (Blackmagic's own dialogue guidance,
   sourced; 6:1 and above flattens expression), threshold -18 to -22 dBFS just
   under normal speech, attack 10 to 25 ms to keep consonants, release 100 to
   200 ms, 2 to 6 dB of reduction on loud words, makeup gain equal to the
   average reduction (sourced). More than 6 dB means leveling or clip gain was
   skipped; split into two stages (2:1 slow, then 3:1 to 4:1 fast) instead.
9. **Limiter.** True-peak limiter on the master, ceiling -1.0 dBTP, barely
   lighting (sourced ceiling; opinion on behavior). Keep 1.5 dB of headroom if
   the file goes through another encoder.
10. **Normalize.** Measure integrated loudness over the whole program and set
    the master to the target; re-check true peak after the gain change.
11. **Room tone and breaths.** Fill gaps with room tone, not digital silence
    (sourced). Reduce breaths 6 to 12 dB rather than muting; muting switches the
    room off and on (sourced).
12. **Music under speech.** 18 to 24 LU below dialogue while speaking (roughly
    -34 to -40 LUFS short-term on the music when speech sits at -14 to -16),
    rising to -22 to -26 LUFS short-term in gaps, intros and B-roll (opinion
    reasoned from the standards). Duck 6 to 12 dB with attack 30 to 80 ms and
    release 250 to 700 ms; Fairlight Ducker 3:1 to 5:1 with the dialogue track as
    the trigger (sourced). Carve 2 to 4 dB from the music around 1 to 4 kHz where
    consonants live (common practice).
13. **Compare at matched loudness.** Louder always sounds better. Equalize with
    makeup gain or short-term LUFS before judging (sourced).

### A3. Per-microphone starting points (mix of sourced and common practice)

| Source | Expect | First moves |
|---|---|---|
| Shotgun indoors | boxiness 300 to 800 Hz, hollow early reflections | de-reverb before EQ if the tail is audible; high-pass 80 to 100 Hz; moderate de-ess; otherwise the least EQ |
| Lav or wireless | exaggerated lows, lost highs under clothing, a resonance near 730 Hz, rustle | high-pass 100 Hz; 2 to 4 dB cut at 400 to 700 Hz; 2 to 6 dB high shelf above 6 kHz if muffled; repair rustle as clip edits |
| Dynamic broadcast mic | low output, preamp hiss, strong proximity effect | high-pass 80 to 100 Hz; 2 to 3 dB cut at 200 to 300 Hz if boomy; presence 2 to 3 dB at 3 to 5 kHz if the mic's own bump does not cover it |
| USB condenser | room, keyboard and desk, often bright | noise reduction or isolation first; high-pass 100 Hz; cut 300 to 600 Hz; de-ess harder; skip the air shelf |
| Phone or camera built-in | wide pattern, heavy room, automatic gain already applied | voice isolation 70 to 80 or Enhance Speech; high-pass 120 Hz; de-reverb; a leveler rather than a compressor |

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

1. Decide color management once: Resolve Color Management or explicit Color
   Space Transform nodes (they produce identical images; never both, which
   double-normalizes), Premiere's Lumetri Settings color management (Direct 709
   default), Final Cut's camera LUT on import.
2. Exposure on the waveform: black point, white point, then midtones.
3. White balance against something neutral and the vectorscope skin line.
4. Contrast with a pivot, then saturation.
5. Match shots to the hero (Resolve stills and wipe, Premiere Comparison View
   and Color Match, Final Cut Match Color).
6. Creative look or LUT on its own node or adjustment layer, late, because LUTs
   clip destructively.
7. Secondaries for skin, background, eyes and teeth.
8. Output transform to Rec.709 and a limiter for legal levels.

### B2. Exposure and balance targets (sourced ranges, opinion placements)

On a 0 to 100 waveform of a Rec.709 image: skin falls roughly between 45 and 70
(light skin 65 to 75 in one guide), middle gray near 45, midtones 33 to 66,
highlights 66 to 100 (sourced). Place the brightest diffuse part of the face at
60 to 70, the average lit face at 50 to 65 for light skin, 40 to 55 for medium,
30 to 45 for dark, with a specular skin highlight at 70 to 85 so the face does
not read flat; blacks at 2 to 5, not 0, so shadows keep detail on phones
(opinion). In log before the transform, 18 percent gray sits near 34 to 41
depending on the curve (sourced), so read scopes after the input transform.

White balance: neutralize a gray or white so its trace sits at the vectorscope
center, then confirm skin lies on or just clockwise of the skin-tone line (the
I-line at 123 degrees, sourced). Skin off the line while gray is centered means
colored lighting on the face: fix with a secondary, not the global balance.

Contrast: Resolve contrast 1.05 to 1.15 with the pivot near the face's mid
level (default pivot 0.435; one colorist uses 0.391 for 18 percent gray in his
working space). Saturation after contrast: Resolve 55 to 60, Lumetri 105 to
115 with Vibrance before Saturation to protect skin (opinion). Skin that reaches
the vectorscope's red and yellow targets is oversaturated.

### B3. Node and panel order per editor

- **Resolve:** camera input to DaVinci Wide Gamut Intermediate (CST in, or
  RCM) > balance and exposure > contrast > saturation > parallel fine-tune
  nodes (temperature, highlights, warper, curves) > power windows > look or
  LUT (with a Rec.709-to-Cineon CST before a film-print LUT) > CST out to
  Rec.709 (sourced, Darren Mostyn and Cullen Kelly). Save the empty labelled
  tree as a PowerGrade. Group pre-clip nodes for per-camera input transforms.
- **Premiere (Lumetri, top to bottom):** Basic Correction (Input LUT for
  technical transforms, white balance, exposure, contrast, highlights, shadows,
  whites, blacks, saturation; Whites and Blacks apply before the other sliders
  despite their position) > Creative (Look for creative LUTs, vibrance,
  saturation, split tone) > Curves > Color Wheels and Match > HSL Secondary >
  Vignette (sourced). Separate Lumetri effects per job, renamed; shared look on
  an adjustment layer; viewer gamma 2.2 for a web audience (sourced).
- **Final Cut:** Apple states no required order (sourced). Practical: Balance
  Color or Color Adjustments (Enhance Light and Color as a start) > Color Wheels
  > Color Curves > Hue/Saturation Curves for secondaries > Custom LUT effect
  last; Auto Mask inside a corrector for skin (common practice).
- **CapCut:** one adjustment layer across the timeline; Adjust > Basic for
  temperature, tint, exposure, contrast, highlights, shadows; Curves for log
  decompression; HSL for one color; LUT at reduced intensity; light vignette
  (reported from the color course).

### B4. Sources that need different handling

Log: always normalize first; it will look contrasty after the transform and
that is correct (sourced). Rec.709 camera profiles and webcams: no input
transform; use curves rather than big contrast moves. Phones: HDR HLG is
auto-detected by Premiere and handled by RCM; Apple Log is log; reduce phone
saturation 5 to 10 percent before matching to a camera (common practice).
Screen recordings and UI captures: do not grade them; they are display-referred
sRGB graphics, so exclude them from the look and tag them sRGB or Rec.709
(common practice, and the pack's rule never to alter authentic screenshots).
Mixed cameras: normalize each to the same working space, balance each to the
same gray and skin targets, match to the hero, then one shared look (sourced).

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

Technical LUTs convert encodings and belong at the input; creative LUTs are
looks and belong late. The node before a LUT must produce what the LUT expects
(feed a LogC LUT LogC). Test on a gray ramp and a chart: the ramp must stay
monotonic with no shelves at 0 or 100 and no steps (17-point LUTs band; use 33
for looks, 65 only for sharp knees); skin on the chart should stay near the
line. A LUT is wrong when inputs mismatch (log LUT on Rec.709 crushes and clips;
709 LUT on log looks milky), when exposure was not fixed first, when gradients
band or skin twists. A LUT cannot adapt to exposure or white balance between
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

Rec.709 mastering assumes a 2.4 gamma display in a dim room; laptops and phones
are closer to 2.2 or sRGB, which lifts shadows; macOS QuickTime historically
interprets Rec.709 at 1.96, so a grade judged in QuickTime looks washed out
elsewhere (sourced). Premiere offers Lumetri viewer gamma 2.4, 2.2 and 1.96; the
community advice is 2.2 for a YouTube audience. Resolve colorists split between
output Gamma 2.2 and 2.4; either works if kept constant, and the Deliver page
color and gamma tags should read Rec.709 (1-1-1) because YouTube assumes it
(sourced plus snippet). Check by uploading unlisted and comparing the player to
the viewer on the same display, then on a phone in daylight and in a dark room;
keep a reference frame with a gray ramp and a skin patch in the first project.

### B9. Compact rules

| Trigger | Action | Default | Not when | Label |
|---|---|---|---|---|
| Takes differ in level | clip gain before dynamics | peaks -12 to -6 dBFS | within 2 dB already | common practice |
| Wide dynamics | leveler first, light compression after | Optimize Moderate Levels, Lift Soft off | camera AGC audio: leveler only | sourced |
| Hum lines at 50 or 60 Hz | de-hum with harmonics | 3 to 5 harmonics | high-pass already removed it | sourced |
| Changing background noise | voice isolation | 70 to 80 (noisy room), 35 to 50 (clean shotgun) | voice goes watery | sourced plus opinion |
| All speech | high-pass before the compressor | 80 Hz male, 100 Hz female | deep voice loses body: 70 Hz | sourced |
| Boomy | cut 200 to 300 Hz | 2 to 3 dB, Q 1.5 | thin voice: boost instead | sourced |
| Boxy | cut 300 to 800 Hz | 2 to 4 dB, Q 2 to 3 | de-reverb solved it | sourced |
| Buried | presence | plus 2 to 3 dB at 3 to 5 kHz, wide | already harsh | sourced |
| Piercing esses | de-esser | 5 to 8 kHz, 3 to 6 dB, release 50 to 100 ms | esses fine after reducing presence | common practice |
| Uneven peaks | compressor | 2.5:1 to 3:1, attack 10 to 25 ms, release 100 to 200 ms, 2 to 6 dB | leveled within 3 dB already | sourced |
| Any delivery | true-peak limiter | ceiling -1.0 dBTP | never skip | sourced |
| YouTube delivery | normalize integrated | -14 to -16 LUFS | podcast-first: -16 to -18 | sourced |
| Loud breaths | attenuate | 6 to 12 dB | breath at an edit: cut and fill room tone | sourced |
| Music under speech | duck or ride | 18 to 24 LU under dialogue; duck 6 to 12 dB | speech-free passages: -22 to -26 LUFS short-term | opinion |
| Mono mic | map mono, center | one channel | stereo music | common practice |
| Log source | input transform first | CST or RCM, auto-detect, camera LUT | Rec.709 source | sourced |
| Exposure | black and white points, then mid | face 45 to 70, mid gray about 45, blacks 2 to 5 | log scopes before transform | sourced plus opinion |
| White balance | neutral to center, skin on the line | 123 degree line | skin off, gray centered: secondary | sourced |
| Creative LUT | late node, ramp and chart test | 33 point | input mismatch, banding, skin twist | sourced |
| Screen capture | no grade, exclude from look | tag sRGB or Rec.709 | never grade UI | common practice |
| Export looks flat on YouTube | check tags and viewer gamma | Rec.709 1-1-1; viewer 2.2 or 2.4 kept constant | broadcast: 2.4 | sourced |
