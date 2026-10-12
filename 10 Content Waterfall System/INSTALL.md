# Install and Test

## Planning only

Planning and text packages need Python 3.11 or a file-aware AI that can complete the templates manually.

From this system folder:

```bash
python3 -B -m unittest discover -s tests -p 'test_*.py'
python3 tools/content_waterfall.py validate examples/example-content-map.json
```

## Local clip extraction

The assistant checks existing tools first. If FFmpeg is missing, explain that it reads and writes the local video, offer to install it from the official distribution for the operating system, and carry forward any setup permission already given. Then confirm both commands are on `PATH`:

```bash
ffmpeg -version
ffprobe -version
```

No speech model is required when the assistant can reuse the canonical word-timed transcript JSON. `transcript_adapter.py` can normalize a compatible JSON export. Do not install a model or upload private media merely to complete setup.

Extraction requires a new output directory and explicit `--confirm EXTRACT`. The assistant may supply that flag within the user's already recorded extraction request; it must not use the flag to invent permission. The source hash in the content map must match the file. Review `python3 tools/content_waterfall.py --help` before use.

The portable mechanics have been tested with a synthetic fixture in the release environment. Operating-system support beyond the environment you personally test remains unverified.
