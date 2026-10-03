# Cut List Export

`tools/cut_list_to_timeline.py` turns one reviewed cut list into files every
editor can open. It is the route that makes the same edit decisions land in
DaVinci Resolve, Premiere Pro, Final Cut Pro or CapCut without a live
connection. Standard library Python 3.11 or later; nothing is rendered and the
source recording is never touched.

| Output | Opens in | Notes |
|---|---|---|
| `.fcpxml` (FCPXML 1.11 by default) | Final Cut Pro, DaVinci Resolve | Rational frame-accurate times, linked audio, markers inside clips, a library and event wrapper. Validated against Apple's shipped FCPXML DTD on October 3, 2026 (Final Cut Pro 12.4). |
| `.premiere.xml` (Final Cut Pro 7 XML, xmeml version 5) | Premiere Pro, DaVinci Resolve | Integer frames with the NTSC flag for 23.976, 29.97 and 59.94; one video track and one audio track per channel, linked; sequence markers. |
| `.edl` (CMX3600) | DaVinci Resolve, Premiere Pro, most editors | One video track, source and record timecode, `FROM CLIP NAME` comments for relinking, markers as `LOC` lines. 999 events maximum. |
| `.cut-sheet.md` and `.cut-sheet.csv` | CapCut and any editor, by hand or with computer use | Every kept clip and removed range in timecode and seconds, for split-and-delete work in an editor without timeline import. |
| `.summary.json` | the assistant | Counts, durations, warnings and SHA-256 of each written file. |

## The cut list

```json
{
  "name": "desk-tutorial clean cut v1",
  "source": "desk-tutorial-take-2.mp4",
  "fps": 30,
  "width": 3840,
  "height": 2160,
  "duration": 95.5,
  "keep": [
    {"start": 3.7, "end": 22.15, "note": "opening, take 2"},
    {"start": "0:27.900", "end": "0:41.300"},
    {"start": "00:00:46:12", "end": "00:01:08:03", "note": "demo"}
  ],
  "markers": [{"time": 30.2, "name": "check word tail"}]
}
```

- `source`: the recording, absolute or relative to the JSON file. A missing
  file only produces a warning; the editor will ask you to relink.
- `fps`: 30, 29.97, "24000/1001" and so on. Fractional rates become exact
  fractions; FCPXML gets `1001/30000s` frame durations and the Premiere XML gets
  `timebase 30` with `ntsc TRUE`.
- `keep` or `remove`, not both. `remove` needs `duration` so the kept ranges
  can be computed. Times accept seconds, `M:SS.sss`, `H:MM:SS.sss` or
  `HH:MM:SS:FF` timecode. Everything snaps to whole frames; overlapping ranges
  merge with a warning; adjacent ranges merge; slivers shorter than
  `min_clip_frames` (default 2) stay but are flagged for review.
- `markers`: source times; placed on the kept clip that contains them, dropped
  with a count if they fall in removed material.
- `--probe` reads fps, size, duration, audio channels and sample rate from the
  source with ffprobe when FFmpeg is installed.

The example above ships at `examples/example-cut-list.json`.

## Run it

```sh
python3 tools/cut_list_to_timeline.py "/path/to/cut-list.json" --out-dir "/path/to/private/project/exports"
```

Options: `--formats fcpxml,xmeml,edl,sheet` to choose outputs, `--probe` to
fill facts from the media, `--fcpxml-version 1.13` when the target Final Cut is
current, `--overwrite` after reviewing an earlier export, and
`--validate-dtd "<path to FCPXMLv1_11.dtd>"` on a Mac with Final Cut installed
(the DTDs live inside the app bundle under
`Contents/Frameworks/Interchange.framework/Versions/A/Resources/`; the tool
copies the DTD to a plain path because xmllint cannot read one from a path with
spaces). The output folder must be outside the pack. On Windows use `py -3.11`.

Print a plan first: the summary lists clip count, kept duration, markers that
fell outside the kept ranges and every warning. Read the cut sheet before
importing anything.

## Import by editor

- **DaVinci Resolve.** File > Import > Timeline > Import AAF, EDL, XML,
  FCPXML, OTIO and choose the `.fcpxml` (or the EDL as a fallback). Tick import
  source clips, or point the import at the folder that holds the recording. On
  Studio a script can call `MediaPool.ImportTimelineFromFile(path,
  {"timelineName": "...", "importSourceClips": True})`. Resolve timelines start
  at 01:00:00:00 by default; the imported record times start at zero, which is
  fine for a review timeline.
- **Premiere Pro.** File > Import and pick the `.premiere.xml`. If the Link
  Media dialog appears, the recording moved; point it at the file. Check
  Sequence Settings afterwards (frame size and rate come from the XML). The EDL
  is the fallback and arrives with offline clips to relink.
- **Final Cut Pro.** File > Import > XML, or double-click the `.fcpxml`, or
  `open -a "Final Cut Pro" cut.fcpxml`. Choose the library when asked; the
  project appears in an event named after the cut list. Final Cut 12 reads
  versions up to 1.14 and writes 1.14; 1.11 imports cleanly. Media that cannot
  be found imports offline (red) and relinks through File > Relink Files.
- **CapCut.** CapCut desktop imports none of these formats. Use the cut sheet:
  with the source on the timeline, type each removed range's start into the
  playhead, press Command-B (Ctrl-B on Windows), move to the range's end, split
  again, select the middle and delete with the gap closed; or use Q and W to
  ripple-delete left and right of the playhead. The Transcript tool and Auto Cut
  are the in-app alternatives. Writing a draft JSON directly is possible but
  unofficial; see the [CapCut playbook](EDITOR%20PLAYBOOK%20CAPCUT.md).

## Verify after import

1. Clip count matches the summary. In Resolve, read `GetItemListInTrack`; in
   Premiere, the Sequence Index panel; in Final Cut, the Timeline Index; in
   CapCut, count the segments.
2. The first and last kept clips start and end on the intended words. Play
   every join with sound. The exporter protects nothing by itself; word-edge
   handles belong in the cut list (see [EDITING CRAFT NUMBERS](EDITING%20CRAFT%20NUMBERS.md)).
3. Picture and sound are linked (select a clip and confirm both move).
4. The sequence frame rate equals the source frame rate. A mismatch shifts
   every cut.
5. Record the result in [EDIT PLAN AND REVIEW](../templates/EDIT%20PLAN%20AND%20REVIEW.md)
   with the summary's SHA-256 values so a later export can be compared.

## Limits

One source recording per cut list. No transitions, titles, effects, speed
changes or multiple camera angles; add those in the editor after the cut is
approved. Timecode in the EDL and cut sheet is non-drop-frame counted at the
integer timebase, so at 29.97 the timecode drifts from wall-clock time while
frame counts stay exact. A draft generated this way is still a first assembly:
the fine pass on joins, pauses and takes happens in the editor.
