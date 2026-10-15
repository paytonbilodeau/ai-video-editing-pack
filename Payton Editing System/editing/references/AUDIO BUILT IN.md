# Native audio: Built In

Use this only for the confirmed microphone and chosen native route. Read [AUDIO.md](AUDIO.md) first. These are real audition starting points, not universal settings or Auphonic parity.

## Route only matching sources

Trigger on **No Mic**, **built-in mic**, **phone mic**, **laptop mic**, **tablet
mic**, or dialogue explicitly recorded without an external microphone. Confirm
the actual recording device or ask when the choice changes the processing. A file
recorded on a phone may still use a wireless mic, and an interface name does not
identify the microphone.

Expect some combination of distance loss, room reflections, device AGC, narrow or
thin tone, handling noise, fan noise, and soft word endings. Preserve intentional
speaker movement and wanted device or demonstration audio.

## Native starting point

Start conservatively, then tune to the actual difficult passage:

- Voice Isolation: **55** as an audition starting point. Lower it immediately if
  consonants become watery, attacks disappear, or room tone pumps.
- Dialogue Leveler mode: `DIALOGUE_LEVELER_MODE_MORE_LIFT_FOR_LOW_LEVELS`.
  Start with Reduce Loud and Lift Soft enabled, background reduction off, and
  output gain at 0. Reduce or disable Lift Soft after listening if it raises room
  noise or AGC breathing.
- Route the healthy dialogue channel to one centered dialogue path. Do not sum
  duplicate mono channels or leave original and replacement dialogue audible.
- Use clip gain or volume automation before heavier compression when individual
  words remain too soft.

Treat these as starting values, not a saved preset, qualified match, or promise of
Auphonic parity. Do not use `GetFairlightPresets()` as proof that a Global Track
audio preset exists; its list can describe Fairlight configuration or layout
presets. Inspect **Fairlight > Presets Library > Global Track Presets** in the UI.
Use only an exact entry verified there, then apply it to a disposable track and
read back the actual Voice Isolation, Dialogue Leveler, EQ, dynamics, and plugin
state before judging a render. If the entry is absent, follow the shared procedure
to configure and save it through the UI. Do not invent XML, alter Resolve's
database, or claim a preset was saved from configuration enumeration alone.

## Source-aware EQ and dynamics

Inspect and listen before adding a band:

- Add a high-pass around 70 to 90 Hz only when handling or mechanical rumble is
  present. Keep enough low voice body.
- If the voice is boxy, try a broad 1 to 3 dB cut in roughly 200 to 500 Hz. Sweep
  to identify the actual problem instead of applying a fixed curve.
- If distance made speech dull, audition a broad 1 to 2 dB presence lift around
  2.5 to 4.5 kHz. Do not boost the top end when the source already has hiss.
- Start compression around 1.5:1 to 2:1 with roughly 15 to 25 ms attack and
  120 to 200 ms release, aiming for about 2 to 4 dB gain reduction on ordinary speech. Back off
  when device AGC already compresses the recording.
- Use Noise Reduction, Dialogue Separator ambience control, De-Hummer, De-Esser,
  or Dialogue Processor only for a defect heard in this source. Dialogue
  Separator is mono-only, so verify channel routing first.

Native scriptable clip controls cover Voice Isolation and Dialogue Leveler.
Local source evidence verified Dialogue Leveler mode, Reduce Loud, Lift Soft,
and AudioVolume readback; use the installed API and actual readback for Voice
Isolation get/set evidence. EQ, dynamics, de-essing, dereverberation, and selective
breath work remain UI-authored until a current receipt proves otherwise. Do not
claim those controls were scripted or tested merely because the skill describes
them.

## Finish and prove the result

Keep music, effects, and demonstration playback on separate paths from aggressive
voice cleanup. Do not run blanket breath, silence, filler, or cough removal.
Preserve timing and lower only genuinely intrusive breaths or joins with selective
automation and short verified fades.

Finish the actual encoded delivery at **-16 LUFS integrated, tolerance ±0.5 LU**,
with encoded true peak **no higher than -1 dBTP**. Normally limit the pre-AAC
master near **-2 dBTP** for codec headroom, then measure the encoded file rather
than trusting a limiter setting.

Compare a matched-loudness difficult passage for intelligibility, consonants,
room continuity, pumping, and fatigue. Verify one active dialogue path, start,
middle, and ending sync, full decode, complete ending, Global Track Presets UI
state, and applied processor readback. A technical pass is not a listening pass.
The No Mic workflow is not audio-qualified until it passes the shared
two-recording qualification process.

For requested chapters, use the final exported file and the local transcript companion. Chapter creation does not require Auphonic.
