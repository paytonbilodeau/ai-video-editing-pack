# Make the Voice Clearer Without Making It Strange

First identify what was recorded, then choose the treatment. A phone recording
may use a good external microphone. A stereo file may hold two separate people,
or a normal track and a quieter safety copy. Ask if those facts are unknown.

## Choose a source profile

| Source | Listen for | Useful first move | What can make it worse |
|---|---|---|---|
| Close dynamic microphone | Boomy bass, plosives, desk bumps, harsh S sounds | Repair isolated bumps; compare gentle low-frequency EQ only where needed | Denoising a clean recording or removing its natural body |
| Shotgun microphone | Room reflections, hollow sound, dullness when the person turns away | Adjust quiet phrases locally; compare mild room/noise treatment | Cutting word tails or making the room sound pulse between words |
| Wireless or lavalier microphone | Clothing rub, chest resonance, breath blasts, level changes | Choose the healthy channel; repair individual rustles before broad processing | Boosting cloth noise, summing the safety copy with the main track |
| Built-in phone or laptop microphone | Distance, room echo, fan noise, automatic gain changes | Reduce steady defects gently; raise individual soft words only as needed | Strong cleanup that turns consonants watery or exposes room noise |
| Screen recording or music | App sounds, system audio, intentional silence | Keep the useful sound on its own track | Treating music or demonstration sounds as unwanted speech noise |

The profile identifies likely problems. It is not a preset to apply blindly.
The actual recording decides which problems exist.

## Use this order on a short difficult passage

1. **Choose one intended voice path.** Compare the available microphone tracks.
   Preserve the originals and unused safety track. Do not play duplicate dialogue
   under the replacement; that can cause an echo or hollow sound.
2. **Fix the isolated problem.** A click between sentences may need a small edit.
   A sudden loud word may need clip gain or volume automation. Do not process
   the whole recording harder to fix one bad second.
3. **Try cleanup only if needed.** Compare noise reduction or voice isolation
   with the untreated passage. Use the least processing that makes the actual
   defect acceptable. Do not assume a tool's slider value means the same thing
   in another product.
4. **Shape the tone.** EQ changes the balance of frequencies. Reduce a real
   rumble, boomy region, or harsh sound before adding brightness. A high-pass
   filter can reduce rumble, but moving it too high removes the body of a voice.
5. **Even the level.** Use gentle compression or a dialogue leveler if ordinary
   speech jumps too much. Keep intentional emphasis. Listen for background noise
   rising whenever the speaker pauses.
6. **Compare at similar volume.** Louder often sounds better at first. Turn the
   versions to a similar listening level before choosing. Check quiet phrases,
   hard consonants, breaths, laughter, and changes in microphone distance.
7. **Listen in context.** Put the voice back with music and effects. Lower or
   move competing sound when it hides a word. Keep useful breaths and room tone.

In Resolve, inspect the current Fairlight controls and edition before promising
Voice Isolation, Dialogue Leveler, or another processor. A feature appearing in
the UI does not prove the installed scripting connection can control it. Use
the documented UI route when the API lacks that operation.

## Local processing or an audio service

Local editor tools are a sensible first choice when they solve the problem.
An external service is optional. Explain which media leaves the computer, any
charge, and the output format before uploading. Obtain the user's permission.

For an external finishing pass, finish the cuts, color, captions and graphics
before uploading the final export. Select the agreed microphone preset and run
it once. Keep the pre-service version. Make each derivative from that untreated
master, finish its visual edit, and apply its agreed audio pass once. Revisions
return to the untreated source so an enhanced track is never processed twice. Disable any automatic cutting or filler removal that would change approved timing. When the result
returns, check duration, start/middle/end sync, complete words, and whether it
added an introduction, outro, or other unwanted material. Do not stack the same
cleanup again on an already processed track.

If native effects misbehave on many small clips, one possible repair is to
process a copy of the continuous source, retain exact timing and handles, and
relink a duplicate timeline to it. Prove alignment before replacing anything.

## Measure the file people will hear

Peak level measures loud moments. Integrated loudness describes the average
over a programme. Neither proves that a voice is pleasant or understandable.
Choose a target appropriate to the actual delivery specification and keep it
consistent across this creator's videos. Do not present one loudness number as
a requirement for every social platform.

Measure the encoded export, not just the editor's meter. Compression during
export can change peaks. Leave headroom, avoid clipping, and listen at normal
speed on headphones and a small speaker when available. Record any listening
check the assistant could not perform; ask the person to perform it.

## Ask the assistant

```text
Identify my actual microphone and dialogue tracks before processing. Choose a
difficult passage and make an untreated and a lightly improved comparison at
similar loudness. Explain the defect each change addresses. Preserve complete
word endings, useful breaths, and timing. Keep music and app sounds separate.
Show me the comparison before applying the treatment to the whole video. Save
the accepted settings with the microphone and room conditions they apply to.
```

Save the chosen profile in [project intake](../templates/PROJECT%20INTAKE.md)
and record the A/B comparison in [edit review](../templates/EDIT%20PLAN%20AND%20REVIEW.md).
Current control names and feature availability should be checked against the
[Blackmagic Design training and manuals](https://www.blackmagicdesign.com/products/davinciresolve/training)
or the chosen editor's own documentation.
