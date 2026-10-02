---
name: video-pre-edit-local
description: Offer an optional local no-paid-AI-service first pass using the separate public System 05 tool, with an approved dry plan before rendering.
---

# Optional Local Pre-Edit

Use this only if the person wants a conservative automatic first pass on a
talking-head recording. The tool belongs to the separate free
[System 05 release](https://github.com/paytonbilodeau/paytons-ai-systems/tree/v4.0.0/05%20Video%20Pre-Edit%20System);
it is not bundled in this plugin. Fetch the
[versioned repository source ZIP](https://github.com/paytonbilodeau/paytons-ai-systems/archive/refs/tags/v4.0.0.zip)
or use a clean local copy of that release. Read its
[START HERE](https://github.com/paytonbilodeau/paytons-ai-systems/blob/v4.0.0/05%20Video%20Pre-Edit%20System/START%20HERE.md),
[INSTALL](https://github.com/paytonbilodeau/paytons-ai-systems/blob/v4.0.0/05%20Video%20Pre-Edit%20System/INSTALL.md),
and [tool source](https://github.com/paytonbilodeau/paytons-ai-systems/blob/v4.0.0/05%20Video%20Pre-Edit%20System/tools/video_pre_edit.py)
before execution. Do not pipe a network download into a shell.

The core utility needs Python 3.11+, FFmpeg, ffprobe and the `libx264`
encoder. It runs locally with no paid AI service or API key. Exact spoken
restart detection is optional; it needs existing timed-word JSON or a local
Whisper install and model download, which require separate approval. Start
with a copied, flattened SDR talking-head file containing one video and one
audio stream. The tool rejects HDR, multitrack and other unsupported sources.

From the extracted System 05 folder, preview a plan before rendering:

```sh
python3 tools/video_pre_edit.py "/path/to/copied-video.mp4" "/path/to/copied-video_preedit.mp4" --dry-run
```

On Windows use `py -3.11`. Read the generated `_dry_run_report.md` and
`_plan.json`, add protected ranges or less aggressive silence rules as
needed, rerun the dry plan, and obtain approval. Render from that exact plan:

```sh
python3 tools/video_pre_edit.py "/path/to/copied-video.mp4" "/path/to/copied-video_preedit.mp4" --from-plan "/path/to/copied-video_preedit_plan.json"
```

Check the new MP4's picture, sound, duration and every cut against the plan.
Preserve the source. This is a flattened H.264/AAC pre-edit, not an editable
NLE timeline; it does not retain HDR, subtitles, chapters, metadata, extra
tracks or multicamera structure. If the project needs those properties or
precise editable cuts, use [cuts and pacing](../cuts-pacing/SKILL.md) in the
chosen editor instead. Never call this a finished creative edit.
