# Native audio: Wireless

Use this only for the confirmed microphone and chosen native route. Read [AUDIO.md](AUDIO.md) first. These are real audition starting points, not universal settings or Auphonic parity.

## Route only matching sources

Trigger on **Wireless Mic**, **wireless lav**, **lavalier**, **lav mic**, **Rode
Wireless Pro**, or confirmed body-worn transmitter audio. Confirm the microphone
from source notes, the user, or a reliable production receipt. A phone-recorded
video is not automatically No Mic, and a receiver or interface name alone does
not establish the capsule or placement.

Listen for clothing rub, chest resonance, breath bursts, RF or gain changes, head
turns, distance swings, and tone changes caused by mic placement. Repair isolated
rustle before adding broad processing.

## Native starting point

Start conservatively, then tune to the actual difficult passage:

- Voice Isolation: **25** as an audition starting point. Reduce or disable it when
  movement makes tone unstable or consonants become processed.
- Dialogue Leveler mode: `DIALOGUE_LEVELER_MODE_OPTIMIZE_MODERATE_LEVELS`.
  Start with Reduce Loud and Lift Soft enabled, background reduction off, and
  output gain at 0. Reduce or disable Lift Soft after listening if it raises
  clothing noise, room tone, or transmitter noise.
- Route the healthy lav channel to one centered dialogue path. Preserve a separate
  safety channel when useful, but do not leave both copies audible.
- Repair individual rustles, breath blasts, and transmitter bumps with source
  handles, clip gain, or automation before global compression.

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

- Add a high-pass around 70 to 90 Hz only when body movement or handling creates
  rumble. Avoid thinning a naturally light lav signal.
- If chest placement sounds heavy, try a broad 1 to 3 dB reduction around 150 to
  300 Hz. Find the actual resonance rather than applying a fixed notch.
- Add at most a small broad presence lift around 3 to 5 kHz when articulation is
  genuinely dull. Do not brighten cloth noise or hiss.
- Start compression around 1.5:1 to 2:1 with roughly 10 to 20 ms attack and
  100 to 150 ms release, aiming for about 2 to 4 dB gain reduction. Keep head turns natural and
  use automation for remaining local swings.
- Use De-Esser only when sibilance is demonstrated with Ess Only audition. Use
  Noise Reduction or De-Hummer only for identified steady noise or hum.

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

Compare a matched-loudness passage containing clothing contact, a breath, a head
turn, and a distance change. Check intelligibility, stable voice tone, consonants,
noise, pumping, and fatigue. Verify one active dialogue path, start, middle, and
ending sync, full decode, complete ending, Global Track Presets UI state, and
applied processor readback. A technical pass is not a listening pass. The
Wireless Mic workflow is not audio-qualified until it passes the shared
two-recording qualification process.

For requested chapters, use the final exported file and the local transcript companion. Chapter creation does not require Auphonic.
