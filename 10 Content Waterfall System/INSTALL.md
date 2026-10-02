# Install and Test

## Planning only

Planning and text packages need Python 3.11 or a file-aware AI that can complete the templates manually.

From this system folder:

```bash
python3 -B -m unittest discover -s tests -p 'test_*.py'
python3 tools/content_waterfall.py validate examples/example-content-map.json
```

## Local clip extraction

Install FFmpeg from its official distribution for your operating system, then confirm both commands are on `PATH`:

```bash
ffmpeg -version
ffprobe -version
```

No speech model is required when you supply the canonical word-timed transcript JSON. `transcript_adapter.py` can normalize a compatible JSON export. Do not install a model or upload private media merely to complete setup.

Extraction requires a new output directory and explicit `--confirm EXTRACT`. The source hash in the content map must match the file. Review `python3 tools/content_waterfall.py --help` before use.

The portable mechanics have been tested with a synthetic fixture in the release environment. Operating-system support beyond the environment you personally test remains unverified.
