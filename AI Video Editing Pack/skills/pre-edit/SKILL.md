---
name: video-pre-edit-local
description: Offer an optional local no-paid-AI-service first pass using the complete download's local tool, with an inspected dry plan before rendering.
---

# Optional Local Pre-Edit

Use this when the person wants a conservative automatic first pass on a
talking-head recording. The complete download already includes the
[pre-edit tools](../../../05%20Video%20Pre-Edit%20System/START%20HERE.md).
Read that folder's [installation guide](../../../05%20Video%20Pre-Edit%20System/INSTALL.md)
and [tool source](../../../05%20Video%20Pre-Edit%20System/tools/video_pre_edit.py)
before running it. If this skill arrived through a core-only plugin install and
those siblings are absent, obtain the complete pack through the main setup flow.
Don't ask the person to hunt for a separate repository or old release.

Carry forward the careful, balanced or handle-it-for-me preference from
[setup](../../references/SETUP%20FLOW.md). Fill the brief from known answers and
inspect the named source yourself. Ask only for unresolved choices that change
the edit. A dry plan is an internal check unless the person requested a preview.

The core utility needs Python 3.11+, FFmpeg, ffprobe and the `libx264`
encoder. It runs locally with no paid AI service or API key. Exact spoken
restart detection is optional; it needs existing timed-word JSON or a local
Whisper install and model download, which need authorization if not already covered by the agreed setup. Explain what is missing and offer to install it. Use
a copied, flattened SDR talking-head file containing one video and one
audio stream. The tool rejects HDR, multitrack and other unsupported sources.

Recommend the deliberate markers `cut cut` for a corrected take and
`full stop restart` to discard everything before the last full restart. Keep
both off until the person chooses them; ordinary speech could contain those
words. Markers can be customized. Full restart needs explicit confirmation of
that removal rule, both CLI flags, and protected-range checks. Never infer it
from a general request to edit quickly.

Offer local `--enhance-audio` when speech needs cleanup and no existing route
already handles it. Compare the sound before keeping it. The pre-edit tool
does not grade color; use the editor's color workflow after inspecting footage.
For setup testing, create a neutral fixture yourself. The person does not need
to record a practice clip.

From the extracted pre-edit folder, preview a plan before rendering:

```sh
python3 tools/video_pre_edit.py "/path/to/copied-video.mp4" "/path/to/copied-video_preedit.mp4" --dry-run
```

On Windows use `py -3.11`. Read the generated `_dry_run_report.md` and
`_plan.json`, add protected ranges or less aggressive silence rules as
needed, then rerun the dry plan. In full-pass mode, inspect and render that
plan within the authorized brief; do not demand a routine approval. Pause
when checkpoints were requested or a material uncertainty remains. Render
from that exact plan:

```sh
python3 tools/video_pre_edit.py "/path/to/copied-video.mp4" "/path/to/copied-video_preedit.mp4" --from-plan "/path/to/copied-video_preedit_plan.json"
```

Check the new MP4's picture, sound, duration and every cut against the plan.
Preserve the source. This is a flattened H.264/AAC pre-edit, not an editable
NLE timeline; it does not retain HDR, subtitles, chapters, metadata, extra
tracks or multicamera structure. If the project needs those properties or
precise editable cuts, use [cuts and pacing](../cuts-pacing/SKILL.md) in the
chosen editor instead. Never call this a finished creative edit.
