# Native audio: Shotgun

Use this only for the confirmed microphone and chosen native route. Read [AUDIO.md](AUDIO.md) first. These are real audition starting points, not universal settings or Auphonic parity.

## Route only matching sources

Trigger on **Shotgun Mic**, **shotgun**, **boom mic**, or a production record that
confirms shotgun capture. Do not infer the mic solely from a filename or an earlier project default. Refresh the source identity for each recording.

Listen for off-axis dullness, reflected room tails, hollow low mids, background
ambience, quiet phrase endings, and changes caused by speaker movement. Preserve
natural room continuity and complete word tails.

## Native starting point

Start conservatively, then tune to the actual difficult passage:

- Voice Isolation: **35** as an audition starting point. Lower it when room tone
  pumps, consonant tails vanish, or the voice sounds watery.
- Dialogue Leveler mode: `DIALOGUE_LEVELER_MODE_OPTIMIZE_MODERATE_LEVELS`.
  Start with Reduce Loud and Lift Soft enabled, background reduction off, and
  output gain at 0. Reduce or disable Lift Soft after listening if it raises room
  tone; use clip gain for remaining off-axis or quiet phrase endings.
- Route the healthy dialogue channel to one centered dialogue path. Confirm a
  stereo container is not two independent signals before mapping to mono.
- Preserve source handles and use automation for individual room tails or joins
  instead of gating phrase endings.
- For many fragmented cuts, audition native processing on the complete source
  and render source-aligned 48 kHz/24-bit PCM with all original handles before
  assembly. Retain the untouched source and recovery timeline. Validate the
  full PCM and edited exports under the shared procedure; do not stack the
  same real-time cleanup on the processed clips. Previous local production supports this workflow, not a confirmed cause of an earlier playback fault.

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

- Add a high-pass around 60 to 80 Hz only when real rumble is present. Keep the
  speaker's natural body.
- If reflections create boxiness, try a broad 1 to 3 dB cut around 200 to 500 Hz.
  Sweep to find the source-specific area.
- If off-axis speech is dull, audition a small broad presence lift around 2 to
  4 kHz. Avoid a wide high-frequency boost that exaggerates room hiss.
- Start compression around 1.5:1 to 2:1 with roughly 15 to 25 ms attack and 120
  to 200 ms release, aiming for about 2 to 3 dB gain reduction on ordinary speech.
- Use Dialogue Separator ambience control or Voice Isolation only as strongly as
  the room defect requires. Dialogue Separator is mono-only. Check consonant and
  phrase tails after every ambience change.

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

Compare a matched-loudness passage containing an off-axis turn, reflected room
tail, quiet phrase ending, and normal speech. Check intelligibility, natural tone,
consonant tails, ambience continuity, pumping, and fatigue. Verify one active
dialogue path, start, middle, and ending sync, full decode, complete ending,
Global Track Presets UI state, and applied processor readback. A technical pass
is not a listening pass. The Shotgun Mic workflow is not audio-qualified until
it passes a matched-loudness challenge passage and a separate complete recording from the same mic family.

For requested chapters, use the final exported file and the local transcript companion. Chapter creation does not require Auphonic.
