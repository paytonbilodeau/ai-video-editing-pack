# Local pre-edit

Use this optional tool to shorten quiet pauses, remove chosen ranges, recognize
deliberately spoken restart markers and, if useful, clean up speech. It creates
a new MP4 and a cut report while preserving the original recording. Finishing
continues in your editor.

Your AI can set up and run it for you. The tool is already included in the full
pack. It needs local file and command access, Python 3.11+, FFmpeg and ffprobe.
Those run the tool and read and write video. No paid API is required. A chat-only
assistant can explain the steps but cannot run a local edit.

## Give your AI this message

```text
Set up and run the included local pre-edit if it fits this recording. Read SYSTEM.md, INSTALL.md and TOOL ADAPTER.md. Reuse my editing profile, chosen working pace and permissions. Fill the brief yourself from my request and files, then ask only about missing choices that affect the result. Check existing dependencies and offer to install anything missing with a plain explanation. Use a neutral fixture for technical testing if needed. Inspect a dry plan before rendering from that exact plan. Treat it as internal review unless I asked for a checkpoint. Preserve original files and protected sections, verify the result and continue the edit I requested. Keep restart detection off unless I deliberately choose it. Ask specifically before enabling the full-restart removal rule. Save the brief, plan and report in my private project folder outside the downloaded pack.
```

## Choices worth making once

- **Quiet pauses:** The starting rule detects pauses of at least 0.8 seconds
  below -40 dB and keeps 150 milliseconds on each side. The AI should protect
  useful reading time, demonstrations, music and complete words. Keep all silence
  if that suits your style.
- **Spoken restarts:** `cut cut` can mark a mistake before a corrected take.
  `full stop restart` can mean discard everything before the last full restart.
  Both are optional, and you can choose other phrases. The second can remove a
  large opening, so it needs explicit confirmation. Timed-word data or an
  optional local Whisper install is needed to find the phrases.
- **Audio cleanup:** Offer the local cleanup if the recording needs it. Keep an
  existing audio workflow if it already works. Color is adjusted in the editor
  after the AI inspects the footage.

You can choose careful, balanced or handle-it-for-me during the main setup.
That sets the amount of explanation and review you want. It doesn't disable
checks that protect your source, agreed ranges or saved work.

## How the AI runs it

These commands are for the assistant or someone who wants manual control. You
do not have to type them yourself. Run them from this system folder, using a
working copy and a new output filename in your private project folder:

```sh
python3 tools/video_pre_edit.py "/path/to/raw-video.mp4" "/path/to/raw-video_preedit.mp4" --dry-run
```

Inspect the generated `_dry_run_report.md` and `_plan.json`. If settings change,
make a new plan. Render the exact reviewed plan:

```sh
python3 tools/video_pre_edit.py "/path/to/raw-video.mp4" "/path/to/raw-video_preedit.mp4" --from-plan "/path/to/raw-video_preedit_plan.json"
```

Use `py -3.11` instead of `python3` on Windows. See [INSTALL](INSTALL.md) and
[TOOL ADAPTER](TOOL%20ADAPTER.md) for dependencies, options and troubleshooting.

## What comes back

You get a new H.264/AAC MP4 and a report of the cuts. The AI checks picture,
sound, timing and protected sections. The original stays unchanged. This
utility requires a flattened SDR file with one video and one audio stream;
it does not preserve an editable timeline, HDR, extra tracks or multicamera
structure. Use the main [cuts and pacing workflow](../AI%20Video%20Editing%20Pack/skills/cuts-pacing/SKILL.md)
when those properties matter.

For the complete finishing workflow, use [the editing guide](../14%20AI%20Video%20Editing%20System/START%20HERE.md).
The [review and clean-master worksheet](templates/MANUAL%20REVIEW%20AND%20CLEAN%20MASTER.md)
is available when you request an editorial checkpoint or need a clean source
for later clips.
