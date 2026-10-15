# Selected marker sound

The retained Payton starting sound is85% Feather squeak and15% Thin nib. Customers can change their own profile deliberately.

## Render the selected sound for a scene

For narrated personal shorts comparable to the approved iPhone Duo finish,
the retained baseline is this same blend **6 dB quieter** than the
standard production stem, about **−45 dBFS active RMS**. Render the new scene's
actual pen events first, then apply the reduction once. Do not lower an already
quiet stem a second time. Holds remain silent, and speech stays primary. The
standard −39 dBFS reference below remains useful for other formats and auditions;
final balance depends on the actual dialogue and perceptual review.

- Preset: `flow/src/components/gentlemen/sound-preset.json`.
- Renderer: `motion/tools/gentlemen_selected_sound.py`, using the maintained round-4 contact and squeak functions. The extracted helper reproduces selected round-4 layers exactly in int16 PCM.
- Supply JSON containing `fps`, `duration`, `motion` (one nonnegative visible distance per frame), and `strokes` (actual pen `start` and `end` times in seconds). Export these from the same `penLayout()` events and draw timings as the target composition. The existing `motion/flow/scripts/export-pen-events.cjs` exports this schema for the supplied configurable example. Adapt the export to the new composition and any visibility masks.
- Run `python3 motion/tools/gentlemen_selected_sound.py --events /absolute/path/events.json --output /absolute/path/marker.wav`. Add `--scene name` when the JSON maps several named scenes. This runs locally without a paid API.
- Supported frame rates are positive integers dividing 48000, including 24, 25, 30, 50 and 60. The duration must exactly match the motion frame count. Unsupported frame rates fail explicitly. A scene with no writing produces silence. Rebuild after text, timing or edit changes. Use the scene's visibility masks when hiding annotations during occlusion or early expiry.
- Add the resulting WAV to the new Remotion scene or as an independent editor track. Production active RMS is -39 dBFS; the demo's isolated review versions are 8 dB louder. Rebalance against actual speech when needed. Never loop the demo WAV beneath unrelated writing.

The current blend is built from the actual Round 4 D and A PCM waveforms. Read one channel of the dual-mono WAV for exact sample and level comparisons; the historical FFmpeg mono-reading helper adds about 3 dB when summing dual mono. Generic re-renders quantize the component layers to the audition representation before blending, and reproduce both delivered demo stems byte-for-byte. New timing at 60 fps, empty scenes and malformed input were also checked.

The clean CC0 recordings and bounded numeric tone guide are included. No source-show waveform, dialogue or score is supplied. Current portable verification is in the motion verification record.

