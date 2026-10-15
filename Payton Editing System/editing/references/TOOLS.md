# Portable tools and exact limits

Run commands from this `editing` folder. Read `--help` before using an optional tool. Reuse installed tools; no script here is a request to install every dependency. The example paths refer to your own project.

| Tool | Does | Requires / limit |
|---|---|---|
| `resolve_control.py doctor` | Read-only native status | Installed Resolve Studio SDK/runtime; no media edit |
| `resolve_control.py smoke-test` | New scratch project, ≤60-second sample, export/DRP/receipt | Native route plus FFmpeg; fixed 4K test, not creative edit |
| `resolve_source_transcript.py` | Full source ASR draft + source hash/timing/review tables | FFmpeg and local Whisper route; English configuration; unverified words |
| `jump_cut_vad_parallel.py` | Optional VAD/marker pre-cut, FCPXML or video, reports | Torch/Silero, optional MLX/Whisper; model assets may download; candidates need review |
| `transcript_analyzer.py` | Word/take/filler/interval utilities used by the optional pre-cut | No independent authority to discard speech; heuristics are not the profile |
| `cut_readiness.py` | Validate declared hook/order/defect/review evidence | Standard Python; one-source schema; cannot listen or find unreported issues |
| `resolve_audio_profile.py` | Inspect or apply limited native clip isolation/leveling to a duplicate | Native SDK; no EQ/dynamics/full-mix automation |
| `resolve_audio_companion.py` | Convert native transcript or final subtitles; reviewed chapters/sidecars | Standard Python; explicit FPS/origin; distinguish words from subtitle timing |
| `video_word_timing.py` | Validate/load real word timing with an explicitly supplied constant offset | Standard Python; inspect actual speech separately |
| `video_render_check.py` | Decode/metadata/frame/audio checks against expectations | FFmpeg/ffprobe; no perceptual verdict |
| `protect_demo_audio.py` | Restore exact protected PCM spans with outside fades | NumPy + soundfile; aligned input WAVs; final lossy encode checked separately |
| `auphonic_enhance.py` | Authorized user-account processing, downloads and remux | requests + python-dotenv + user's own key/preset; cloud upload/cost; exact-name matching |
| `auphonic_chapter_timer.py` | Match reviewed chapter anchors to actual speech timings | Existing local speech JSON, or authorized read-only provider fetch; fuzzy matches need review |
| `rsvp_captions.py` | Optional word-by-word rendered captions | Pillow, BeautifulSoup, FFmpeg; real word JSON/HTML by default; approximate previews explicit |
| `extract_short_clips.py` | Reviewed-manifest crop/extraction | FFmpeg, NumPy; optional OpenCV/MediaPipe/model for tracking; static fallback is announced |
| `waterfall_transcribe.py` | Local long-form word transcript and strict clip sidecars | Optional MLX/Whisper; may download model if not present; no provider audio run |
| `waterfall_validate.py` | Check content-map times, frames, crops and schema | FFprobe for actual source; descriptive metadata check, no publication |
| `extract_mid_clips.py` | Sequential full-frame landscape excerpts | FFmpeg; fresh folder, real output verification; preserves source dimensions |

The original editing pack bundled alongside this system supplies timeline interchange; use its maintained exporter rather than duplicating it here.

## First useful commands

```sh
python3 tools/cut_readiness.py tools/fixtures/not-ready-unfamiliar.json --output project/readiness.json
python3 tools/resolve_source_transcript.py project/source.mp4 project/source-review --model medium
python3 tools/video_render_check.py --help
python3 tools/resolve_audio_companion.py --help
```

Create a fresh output directory first. The first example is intentionally **not ready**; exit code 1 is the expected result. It tests the checker, not your video. Do not feed a fictional “passed listening” fixture into a real project claim.

For native Resolve on a supported Mac, use the installed bundled ResolvePython, for example:

```sh
"/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/ResolvePython" tools/resolve_control.py doctor
```

Other operating systems/builds must use their documented installed SDK route. Do not point this command at an invented executable. The optional face model is supplied separately through `VIBE_FACE_MODEL`; no model weights are bundled. The provider cache is in the user's local cache, configurable through `VIBE_AUPHONIC_CACHE`, never inside the shared reference download. No key, preset mapping, token or personal account ID ships in the package.

## Checks before relying on a route

Run the included offline unit suite with your existing compatible Python environment:

```sh
python3 -m unittest discover -s tools/tests -v
```

Some tests need the media libraries listed above. Missing dependencies are reported; do not describe skipped tests as passes. Native controls are mostly tested here through fake APIs; a customer still needs the one relevant native save/reopen/render test. The scenario record in the release receipt states exactly what was executed during packaging.
