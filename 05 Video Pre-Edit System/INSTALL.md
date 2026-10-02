# Install and Run

The core pre-edit runs locally with:

- Python 3.11 or newer;
- FFmpeg and ffprobe, with the `libx264` encoder available;
- no Python packages;
- no account, API key, upload, or paid service.

Exact spoken-marker detection is optional and has a separate local dependency.

## 1. Check what is already installed

Open Terminal or PowerShell and run:

```text
python3 --version
ffmpeg -version
ffprobe -version
```

On Windows, use:

```text
py -3.11 --version
ffmpeg -version
ffprobe -version
```

If all three return versions, check the tool:

```text
python3 tools/video_pre_edit.py --help
```

Use `py -3.11 tools/video_pre_edit.py --help` on Windows.

Before rendering, confirm the FFmpeg encoder list includes `libx264`:

```text
ffmpeg -hide_banner -encoders
```

The included tool checks this again before it renders. Read `THIRD-PARTY.md`
for the GPL or commercial x264 licensing boundary. This library does not bundle
FFmpeg or x264.

## 2. Install the core requirements if needed

Ask before installing software. Use the normal package manager for the computer.

### macOS

Install Python from [python.org](https://www.python.org/downloads/) or Homebrew. With [Homebrew](https://brew.sh/) already installed:

```text
brew install python@3.11 ffmpeg
```

### Windows

Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/windows/) and select the installer option that adds Python to PATH.

Install an FFmpeg build from the download options linked by [ffmpeg.org](https://ffmpeg.org/download.html). Windows Package Manager commonly exposes the Gyan build:

```text
winget install --id Gyan.FFmpeg -e
```

Close and reopen PowerShell, then repeat the version checks. If `ffmpeg` or `ffprobe` is still not found, add that FFmpeg build's `bin` folder to PATH.

### Debian or Ubuntu Linux

```text
sudo apt update
sudo apt install python3 ffmpeg
```

Confirm `python3 --version` reports 3.11 or newer. Other Linux distributions should use their maintained Python and FFmpeg packages.

## 3. Run a dry plan

From this system folder:

```text
python3 tools/video_pre_edit.py "/path/to/raw-video.mp4" "/path/to/raw-video_preedit.mp4" --dry-run
```

Windows PowerShell:

```text
py -3.11 tools/video_pre_edit.py "C:\path\to\raw-video.mp4" "C:\path\to\raw-video_preedit.mp4" --dry-run
```

Read the new `_dry_run_report.md` and keep the generated `_plan.json` beside
the planned output. Render with `--from-plan` as shown in `START HERE.md`. This
keeps every approved dry-run option and writes a separate final `_report.md`.
The tool does not scan a media library. It reads only the named source,
approved plan, and optional timed-word JSON.

## 4. Optional local spoken-marker detection

You do not need this for silence cuts or exact `--cut` ranges.

Create a dedicated Python 3.11 environment for the optional packages. Do not
install them into the computer's main Python environment:

```text
python3.11 -m venv .venv-markers
source .venv-markers/bin/activate
python -m pip install -r requirements-markers.txt
```

Windows PowerShell:

```text
py -3.11 -m venv .venv-markers
.\.venv-markers\Scripts\Activate.ps1
python -m pip install -r requirements-markers.txt
```

`requirements-markers.txt` pins the two top-level packages used for this
release. Pip still resolves their platform-specific transitive dependencies,
so review the install summary before approving it. The first Whisper run
downloads the selected model. This needs internet access, disk space, and
explicit approval. Transcription then runs locally; the included tool does not
send the recording to an API.

Start with the `base` model:

```text
python3 tools/video_pre_edit.py "raw.mp4" "raw_preedit.mp4" --dry-run --detect-restarts --whisper-model base
```

You can avoid the Whisper install by providing local timed-word JSON with `--words-json`.

## Supported working input

Use a copied, flattened SDR talking-head file with:

- one video stream;
- one audio stream;
- ordinary 8-bit color;
- readable duration;
- a new `.mp4` output name.

The renderer writes H.264 video and AAC audio. It does not preserve HDR, subtitles, chapters, metadata, extra tracks, multicamera structure, or an editable timeline. Export a flattened SDR working copy for those sources.

The input gate rejects subtitle streams, chapters, extra audio or video tracks,
HDR, and high-bit-depth media. Source metadata is not copied to the output, and
the encoder may add new technical tags.

## Validation status

This release was run and smoke-tested on Apple Silicon macOS. The implementation uses standard Python and FFmpeg command interfaces, and setup guidance is included for Windows and Linux, but this release does not claim those systems were tested.

## Troubleshooting

- **Output already exists:** choose a new filename. Use `--overwrite` only after checking the target.
- **Source has several tracks or HDR:** export a flattened SDR working copy.
- **Words sound clipped:** increase `--padding-ms`, increase `--min-silence`, or add a protected range.
- **Too many pauses disappear:** use `--keep-silence` or a less sensitive threshold such as `--silence-threshold -45`.
- **Whisper fails:** confirm the optional environment, model download, and language. Or use timed-word JSON. Silence and exact-range cuts still work without Whisper.
- **A coding agent cannot render:** confirm it has local file and command access. A chat-only AI can plan the command but cannot run or verify it.
