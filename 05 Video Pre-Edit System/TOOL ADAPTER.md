# Tool Adapter

This release includes `tools/video_pre_edit.py`, a local command-line reference tool for a conservative talking-head pre-edit. It uses Python's standard library plus FFmpeg and ffprobe. Read `INSTALL.md` before running it.

It was validated on macOS. Its core uses cross-platform Python and FFmpeg interfaces, and Windows/Linux setup notes are included, but those operating systems were not validated for this release.

## What the included tool does

- detects quiet pauses with FFmpeg `silencedetect`;
- accepts repeatable exact cuts with `--cut START-END`;
- protects repeatable ranges with `--protect START-END`;
- optionally finds exact spoken markers using local timed-word JSON or local Whisper;
- optionally applies a light local speech-audio chain;
- writes a new H.264/AAC MP4 and a Markdown report;
- verifies the output streams and duration.

Use original-source timestamps in `MM:SS`, `HH:MM:SS`, or seconds.

## Common modes

Plan quiet-pause cuts without rendering:

```text
python3 tools/video_pre_edit.py "raw.mp4" "raw_preedit.mp4" --dry-run
```

After reviewing the dry-run report, render with the generated plan so the
approved options carry forward:

```text
python3 tools/video_pre_edit.py "raw.mp4" "raw_preedit.mp4" --from-plan "raw_preedit_plan.json"
```

Keep silence and remove only exact approved ranges:

```text
python3 tools/video_pre_edit.py "raw.mp4" "raw_preedit.mp4" --keep-silence --cut 00:14-00:19 --cut 01:02-01:08
```

Protect a played clip while shortening quiet pauses:

```text
python3 tools/video_pre_edit.py "raw.mp4" "raw_preedit.mp4" --protect 02:10-02:42
```

Use an exact local restart marker and light speech cleanup:

```text
python3 tools/video_pre_edit.py "raw.mp4" "raw_preedit.mp4" --detect-restarts --restart-phrase "cut cut" --enhance-audio
```

Use precomputed local timed words instead of installing Whisper:

```text
python3 tools/video_pre_edit.py "raw.mp4" "raw_preedit.mp4" --detect-restarts --words-json "raw_words.json"
```

The JSON shape is:

```json
{
  "words": [
    {"word": "cut", "start": 12.10, "end": 12.32},
    {"word": "cut", "start": 12.36, "end": 12.58}
  ]
}
```

Run `python3 tools/video_pre_edit.py --help` for every option. On Windows, replace `python3` with `py -3.11`.

A dry run writes a separate `_dry_run_report.md` and `_plan.json`. The final
render writes `_report.md`, so the dry-run report cannot block it. If an option
changes, create and review a new dry plan instead of adding different edit
flags to `--from-plan`. To reuse the same dry-run filenames, add `--overwrite`
only after reviewing the old plan. In dry-run mode this replaces the report and
plan, not the MP4 or source.

## When to adapt

- If the user has a desktop editor but cannot run local commands, produce a cut list and say the plan was not rendered.
- If the source is HDR, multicamera, or multitrack, ask the user to export a flattened SDR working copy.
- If the destination needs ProRes, XML, captions, chapters, multiple audio tracks, or broadcast loudness compliance, hand the report to a proper editor. Do not pretend this MP4 tool preserves those features.
- If FFmpeg or Python is missing, give the relevant `INSTALL.md` section. Ask before installing.

## Permission boundary

Read the named source and write the output and report only in the approved working folder. Do not scan unrelated folders. Do not install software, download a Whisper model, use a paid service, or enable broad permissions without approval. Never add `--overwrite` merely to make an error disappear.

## Offline verification

Run:

```text
python3 -m unittest discover -s tests -p "test_*.py" -v
```

Most tests are pure and offline. If FFmpeg and ffprobe are installed, the integration test also generates a six-second synthetic video, renders it, verifies its streams and duration, and confirms the source hash did not change.
