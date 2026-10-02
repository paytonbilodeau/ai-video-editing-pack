# Start Here: Video Pre-Edit System

Part of Payton's AI Systems, created and maintained by Payton Bilodeau.

Use this system to make a conservative first pass on a talking-head recording. It can shorten quiet pauses, remove exact ranges you approve, detect an exact spoken restart marker, and apply light local speech cleanup. It creates a new MP4 and a cut report. It never edits the source file.

This is a pre-edit, not a final creative edit. You still review pacing, cuts, captions, color, music, and story.

## Minimum AI capability

**Run named tools** is required to inspect media and render a pre-edit with the included local utility. The AI must have local file access and permission to run Python 3.11+, FFmpeg, and ffprobe in the approved folder. Codex, Claude Code, or another coding agent can usually do this. A chat-only AI can prepare the brief, help choose settings, and write a command, but it must say that it did not inspect, render, or verify the video.

Exact spoken-marker detection also needs local timed-word JSON or the optional local Whisper install. Read `INSTALL.md` before the first run.

## Quick start

1. Put one copied test recording in an approved working folder. Start with a flattened SDR file containing one video track and one audio track.
2. Complete `templates/PRE-EDIT BRIEF.md`.
3. Open Terminal, PowerShell, or your coding agent in this system folder.
4. Run a dry plan first:

   ```text
   python3 tools/video_pre_edit.py "/path/to/raw-video.mp4" "/path/to/raw-video_preedit.mp4" --dry-run
   ```

   On Windows, use `py -3.11` in place of `python3`.
5. Read the generated `_dry_run_report.md`. Add `--protect START-END` for anything the tool must keep. Use `--keep-silence` if you only want approved range or marker cuts. Rerun the dry plan after changing an option so the generated `_plan.json` records the exact approved settings. If you reuse the same filenames, add `--overwrite` only after reviewing the prior dry-run report and plan; a dry run still does not write the MP4 or touch the source.
6. Render from that plan. Do not retype the edit options:

   ```text
   python3 tools/video_pre_edit.py "/path/to/raw-video.mp4" "/path/to/raw-video_preedit.mp4" --from-plan "/path/to/raw-video_preedit_plan.json"
   ```

7. Review the new MP4 with `templates/REVIEW CHECKLIST.md`. Keep the source.

Plan for 60 to 90 minutes on the first pass (environment checks, a dry run, a review, and the first render); later runs are much faster than the bundle's usual 30 to 60 minute estimate.

## Give your AI this message

```text
1. Read START HERE.md, INSTALL.md, SYSTEM.md, TOOL ADAPTER.md, THIRD-PARTY.md, tools/video_pre_edit.py, and every file in templates before acting.
2. First state whether you can run named local tools.
3. Check whether Python 3.11+, ffmpeg, and ffprobe are already available without installing anything.
4. Ask me to complete the pre-edit brief, especially protected ranges, silence preference, exact approved cuts, spoken marker choice, and audio cleanup.
5. Start with --dry-run. Show me the dry-run report and the generated plan before rendering.
6. Render with --from-plan so every approved option carries forward.
7. Keep the source unchanged, use a new MP4 filename, and verify the output has video, audio, and the planned duration.
8. Do not install software, download a model, use paid processing, or guess at unmarked retakes without my approval.
9. Save my brief and review notes under _MY WORK/Video Pre-Edit.
```

## Have these ready

- a short copied SDR test recording with one video and one audio track;
- at least one section that must not be cut;
- your exact restart phrase, if you intentionally use one;
- the final editor where you will review the new MP4.

## A good first result

The first pass removes only agreed material, preserves protected ranges, sounds natural at every join, and lists every cut for review. Do not start with an irreplaceable file, HDR media, multicamera media, or a recording with several audio tracks. Export a flattened SDR working copy first.

For a complete editor setup and finishing workflow, use [System 14](../14%20AI%20Video%20Editing%20System/START%20HERE.md). This pre-edit remains a standalone option with the same tool and defaults.

## Continuing in a final editor

If the project needs a polished cut review before graphics, a comparison of a
returned manual edit, or a clean source for later reframing, use
`templates/MANUAL REVIEW AND CLEAN MASTER.md`. It is an optional editor procedure;
the included command-line utility still produces only the pre-edit described above.
