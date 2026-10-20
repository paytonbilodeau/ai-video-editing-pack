# Keep the click

**Synthetic practice media.** Original illustrations and a generated sound effect, with no recorded speech or filmed lamp. This is a small cutting exercise, not a demonstration of voice cleanup or color correction.

1. Watch [the source](source.mp4). There is waiting before and after the useful part.
2. Watch [the intentional mistake](too-short.mp4). The lamp comes on, but the click has been cut out.
3. Watch [the corrected edit](corrected.mp4). The wait is shorter. The click and time to see the result remain.

Give your AI the source and this instruction:

```text
Trim the unused wait at the beginning and end. Keep the switch click and enough time to see the lamp turn on. Preserve the original file. Give me an editable timeline and a video I can review.
```

The example keeps source time 2.000–9.000 seconds. The source is 10 seconds; the corrected edit is 7 seconds. The click moves from source 4.000 seconds to output 2.000 seconds. [The cut sheet](lamp-practice-corrected.cut-sheet.md) shows the exact edit. These times belong to this example, not to every recording.

## Try the editable version

Keep the files together. Run `python3 relink.py` from this folder, then import the appropriate file from `local-timelines`: `.fcpxml` or `.premiere.xml`. The script writes new copies with the source's current location and preserves the originals. Alternatively, import the supplied XML and relink its `source.mp4` placeholder in the editor. The EDL and cut sheet are other ways to recreate the same single cut.

The interchange describes picture/audio timing. It does not add the video's diagnostic header or the separate [caption file](corrected.srt). Import the SRT after the cut and check its click caption at 2 seconds. Native editor behavior must be checked in the actual app; generating valid XML does not prove that import succeeded.

## Hear one sound-processing mechanism

Play [A: tone with hum](../../ASSETS.md#audio-a-hum-wav), then [B: the same signal with two notch filters](../../ASSETS.md#audio-b-notched-wav). Their measured integrated levels are matched near -23 LUFS. A clean [reference tone](../../ASSETS.md#audio-reference-tone-wav) is included.

The artificial hum is exactly 60Hz and 120Hz; the useful tone is 660Hz. This deliberately simple signal makes the filter's effect easy to hear. It is not a microphone recording, a human voice comparison, an Auphonic example or a claim that these settings suit speech. Match playback volume and listen for the hum difference. This audio exercise is separate from the lamp edit, whose click needs no cleanup.

## Rebuild or move it

The accompanying `build.py` and prepared scene cards rebuild the media with Python 3.11+, FFmpeg and ffprobe already installed. Pass the current Vibe Editors `tools/cut_list_to_timeline.py` as `--exporter` and choose a new `--out` folder. No model, API, speech voice or browser is used. See [rights and limits](RIGHTS%20AND%20LIMITS.md). Existing output folders are refused so previous work remains intact.
