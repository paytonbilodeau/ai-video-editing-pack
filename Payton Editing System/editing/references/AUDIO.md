# Preserve the voice; choose one finishing route

Identify microphone, placement, room, source channels, prior processing and the actual defect. Separate channel loss, low level, noise, room echo and sync. Raising volume can expose room sound; it does not remove reverb. Inspect throughout the recording and at setup transitions, not only the first sample.

Route wanted mono dialogue once to the center. Preserve intentional stereo and independent safety channels; do not sum duplicates or leave an original playing alongside its processed replacement. Missing sound that was never recorded cannot be recovered by routing.

## Payton's optional provider route

Payton prefers one mic-matched Auphonic finish after cuts, color, captions and graphics. In this portable system, first confirm that the user wants the external upload/cost and has their own account. No private preset IDs, credentials or account cache are supplied. Resolve a preset by its exact user-owned name; do not choose an ambiguous fuzzy match.

Keep the clean pre-provider master. Make derivatives from it, then process each finished derivative once. Review exports intended for the creator's own cut pass stay pre-provider. A caption/framing-only change can reuse accepted audio if timing and payload checks prove it is the same speech; do not run another production for a transcript or picture-only revision. The helper returns actual provider outputs when available; configured transcript outputs do not guarantee usable word timing.

The inherited microphone settings are a starting description for a user's own preset: AutoEQ, adaptive leveling, medium speech compression, -16 LUFS and no silence/filler/cough/music cutters. Historical provider denoise/reverb/breath amounts were wireless 12/6/12, shotgun 12/12/6, dynamic 18/15/6 and built-in dynamic-denoise 0/full with reverb12/breath6. These provider-specific semantics can change. Verify current labels and audition your own source; do not copy those numbers into Resolve percentage controls. No settings file here creates or modifies an online preset.

## Native Resolve alternative and source repairs

Use the appropriate [shotgun](AUDIO%20SHOTGUN.md), [dynamic](AUDIO%20DYNAMIC.md), [wireless](AUDIO%20WIRELESS.md) or [built-in](AUDIO%20BUILT%20IN.md) procedure. These carry Payton's real audition settings and defect-specific ranges. They are not qualified Auphonic clones.

Repair a local pop/rustle/breath before global treatment. About 3–6 dB selective breath attenuation is an audition start when the breath is intrusive, not a blanket reduction. Keep normal breaths and timing. Use modest isolation or a targeted noise tool only when a named defect improves. Audition removed material when possible. Reduce treatment when word attacks/tails disappear, room tone pumps, the voice becomes watery or sibilance becomes a lisp.

For fragmented shotgun edits, one proven local route processes the complete source to aligned 48 kHz/24-bit PCM before assembly, retaining all handles. Verify full duration, channel map, active speech and alignment, then avoid applying the same cleanup again to each processed clip. That experience does not prove every microphone, room or playback problem has the same cause.

The included native profile helper can inspect or apply clip Voice Isolation and Dialogue Leveler to a duplicate timeline. It does not configure EQ, compression, de-essing, dereverb, breaths or final loudness. Review track processing before applying clip effects. Use the actual UI for unsupported controls; never invent API methods or patch Resolve's database.

Save a complete channel strip through Fairlight > Presets Library > Global Track Presets when supported. A Fairlight Configuration/Layout preset is not proof of a complete audio chain. Apply a saved preset to a disposable track, read its actual state, save/reopen and audition the render.

## Measure and listen

Payton's speech-led comparison target is -16 LUFS integrated, ±0.5 LU, with encoded true peak ≤-1 dBTP; about -2 dBTP before AAC provides an initial margin. The destination brief can override these values. A sample-peak limiter setting is not a measured encoded true peak. Do not blindly stack levelers and compressors to hit a number.

Compare dry and treated passages at matched perceived loudness, including difficult words, quiet tails and mic movement. Preserve untouched masters for measurements. Check naturalness, intelligibility, consonants, breath/room continuity, pumping and fatigue. Record actual listener, file/version and reviewed range. ASR, waveforms, correlation and a successful command cannot replace listening. Qualification on one source does not qualify the other microphones or another room.

[Blackmagic Fairlight](https://www.blackmagicdesign.com/products/davinciresolve/fairlight) and [Auphonic algorithms](https://auphonic.com/help/algorithms/singletrack.html) describe different systems; matching labels does not establish matching sound.

The portable Auphonic wrapper refuses existing output/sidecar names before starting a production. Sidecars use the new output filename. It checks the returned audio against picture duration before remuxing; a difference above 100 ms stops the remux. Smaller differences can still reflect codec padding and require an ending/sync check. The wrapper preserves the full video stream without `-shortest`. If processing completed but remux fails, recover that existing production's output and investigate; do not automatically run another paid production.
