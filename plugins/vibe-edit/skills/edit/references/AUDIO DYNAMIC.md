# Native audio: Dynamic

Use this only for the confirmed microphone and chosen native route. Read [AUDIO.md](AUDIO.md) first. These are real audition starting points, not universal settings or Auphonic parity.

## Route only matching sources

Trigger on **Dynamic Mic**, **Shure MV7 Plus**, **MV7**, **podcast mic**, **close
studio mic**, or a production record that confirms a dynamic microphone. Confirm
the microphone rather than treating an interface name such as Shure MVX2U as mic
identity.

Listen for close plosives, proximity bass, desk or stand rumble, sibilance, mouth
noise, and quiet-to-loud changes. A clean dynamic recording may need no denoising
or isolation.

## Native starting point

Start conservatively, then tune to the actual difficult passage:

- Voice Isolation: **15** as an audition starting point, or off when the source is
  already clean. Retain the lower setting unless a real background defect improves
  without changing the voice.
- Dialogue Leveler mode: `DIALOGUE_LEVELER_MODE_OPTIMIZE_MODERATE_LEVELS`.
  Start with Reduce Loud and Lift Soft enabled, background reduction off, and
  output gain at 0. Reduce or disable Lift Soft after listening if it raises room
  or preamp noise; use automation for isolated low phrases.
- Route the healthy dialogue channel to one centered dialogue path. Check whether
  any second channel is a safety level before muting or mapping it.
- Repair individual plosives and stand bumps locally before global EQ or dynamics.

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

- Add a high-pass around 55 to 80 Hz only for real stand rumble or plosive energy.
  Do not thin a well-recorded voice.
- For proximity buildup, audition a broad low-shelf or 1 to 3 dB cut around 80 to
  180 Hz. Avoid a permanent cut when mic distance changes through the recording.
- Add a small presence lift around 2.5 to 4.5 kHz only when the mic sounds dark.
  Use De-Esser only for demonstrated sibilance and verify with Ess Only audition.
- Start compression around 2:1 to 2.5:1 with roughly 15 to 25 ms attack and
  100 to 160 ms release, aiming for about 3 to 4 dB gain reduction on louder speech while
  retaining natural emphasis.
- Try no denoising first. Use De-Hummer or Noise Reduction only for an identified
  tonal or steady noise defect.

Native scriptable clip controls cover Voice Isolation and Dialogue Leveler.
Local source evidence verified Dialogue Leveler mode, Reduce Loud, Lift Soft,
and AudioVolume readback; use the installed API and actual readback for Voice
Isolation get/set evidence. EQ, dynamics, de-essing, denoising, and selective breath
work remain UI-authored until a current receipt proves otherwise. Do not claim
those controls were scripted or tested merely because the skill describes them.

## Finish and prove the result

Keep music, effects, and demonstration playback on separate paths from aggressive
voice cleanup. Do not run blanket breath, silence, filler, or cough removal.
Preserve timing and lower only genuinely intrusive breaths or joins with selective
automation and short verified fades.

Finish the actual encoded delivery at **-16 LUFS integrated, tolerance ±0.5 LU**,
with encoded true peak **no higher than -1 dBTP**. Normally limit the pre-AAC
master near **-2 dBTP** for codec headroom, then measure the encoded file rather
than trusting a limiter setting.

Compare a matched-loudness passage containing a plosive, proximity bass, a
quiet-to-loud change, and normal speech. Check intelligibility, natural body,
plosive control, sibilance, pumping, and fatigue. Verify one active dialogue path,
start, middle, and ending sync, full decode, complete ending, Global Track
Presets UI state, and applied processor readback. A technical pass is not a
listening pass. The Dynamic Mic workflow is not audio-qualified until it passes
a matched-loudness challenge passage and a separate complete recording from the same mic family.

For requested chapters, use the final exported file and the local transcript companion. Chapter creation does not require Auphonic.
