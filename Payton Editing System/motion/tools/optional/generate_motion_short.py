# Portable adaptation. Optional paid route, off by default. Historical model IDs/prices
# require current provider verification before --allow-paid. No account/key is included.
#!/usr/bin/env python3
"""
Motion Graphics Short Generator v2 (Kie.ai pipeline).

Turns a user-approved storyboard.json into one or more finished, silent,
vertical animation videos ready to overlay on a talking-head short.

Pipeline per beat:
  1. KEYFRAME  - Explicitly approved Kie Images 2.5 Flare renders a hand-drawn animatic frame (9:16).
  2. ANIMATE   - Kie image-to-video (Grok Imagine default) animates that frame.
  3. ASSEMBLE  - ffmpeg trims each clip to its exact beat duration, normalizes,
                 and concatenates per segment.

v2 additions:
  - Segments: several separate animation files placed at different points in
    the talking-head video, or one continuous file (legacy format still works).
  - Grok Imagine default tier (#1 on the I2V arena, flexible 1-15s durations,
    per-clip pricing) with automatic lanczos upscale to the delivery
    resolution when the model caps below it (line art upscales cleanly).
  - --force slug[,slug] to regenerate specific beats only.
  - Multi-segment --overlay-on: every segment lands at its start_at, base
    narration audio untouched.

Design principles:
  - Keyframe-first: style, logos, symbols are locked in a cheap image before
    any video money is spent. Bad frame = cents. Bad clip = dollars.
  - Over-generate slightly, trim precisely.
  - Paid result URLs persist to manifest.json BEFORE download, so a network
    hiccup never costs a regeneration (rerun with --resume, redownload free).
  - Pure stdlib + ffmpeg. Runs on the Mac (Cowork) or any Linux container.

Usage:
    python3 generate_motion_short.py storyboard.json --out-dir ./out --dry-run
    python3 generate_motion_short.py storyboard.json --out-dir ./out --keyframes-only
    python3 generate_motion_short.py storyboard.json --out-dir ./out --animate-only --resume
    python3 generate_motion_short.py storyboard.json --out-dir ./out --assemble-only
    python3 generate_motion_short.py storyboard.json --out-dir ./out --force 02_context-folder
    python3 generate_motion_short.py storyboard.json --out-dir ./out \
        --overlay-on talking_head.mp4

Environment:
    KIE_API_KEY must be set in your own environment.
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# ---------------------------------------------------------------- config ---

KIE_API_BASE = "https://api.kie.ai/api/v1/jobs"
KIE_CREATE_TASK_URL = f"{KIE_API_BASE}/createTask"
KIE_TASK_STATUS_URL = f"{KIE_API_BASE}/recordInfo"

IMAGE_MODEL = "gpt-image-2-5-flare-text-to-image"  # explicit paid backup after native generation
IMAGE_MODEL_RESTYLE = "gpt-image-2-5-flare-image-to-image"  # hosted input_urls

POLL_INITIAL = 4
POLL_MAX = 10
POLL_TIMEOUT_IMAGE = 600
POLL_TIMEOUT_VIDEO = 1200
STALE_TASK_SECONDS = 1800  # abandon queued tasks older than this and recreate
                           # (30 min: congested queues are slow but alive;
                           # abandoning a live paid task = paying twice)

DOWNLOAD_UA = "Mozilla/5.0 (MotionGraphicsSkill)"  # Kie CDN rejects blank UA

SCRIPT_DIR = Path(__file__).resolve().parent

# Video tiers. Candidate model IDs are tried in order so a renamed model
# degrades gracefully. Schemas differ per model family on Kie.
#
# Pricing notes (July 2026):
#   grok:    per-clip pricing, roughly $0.10-0.15 per clip; #1 on the
#            Image-to-Video Arena leaderboard (beat Seedance 2.0 blind);
#            durations 1-15s (we clamp 2-15); caps at 720p.
#   quality: Seedance 1.5 Pro ~ $0.025/s, native 1080p, durations 4-12s.
#   budget:  Seedance 1.0 Lite (live-verified 2026-07-07): 480p $0.010/s,
#            720p $0.0225/s, 1080p $0.050/s; durations 5 or 10.
#   premium: Seedance 2.0 Fast; verify price at kie.ai/pricing.
TIERS = {
    "default": {
        "label": "Grok Imagine (image-to-video, I2V arena #1)",
        "models": ["grok-imagine/image-to-video"],
        "schema": "grok",
        "duration_mode": "range",
        "duration_range": (6, 30),
        "max_resolution": "720p",
        "cost_model": ("per_clip", 0.15),
    },
    "quality": {
        "label": "Seedance 1.5 Pro (native 1080p)",
        "models": ["bytedance/seedance-1.5-pro"],
        "schema": "v15",
        "duration_mode": "range",
        "duration_range": (4, 12),
        "max_resolution": "1080p",
        "cost_model": ("per_second", {"480p": 0.020, "720p": 0.025, "1080p": 0.050}),
    },
    "budget": {
        "label": "Seedance 1.0 Lite (cheapest per-second)",
        "models": ["bytedance/v1-lite-image-to-video",
                   "bytedance/seedance-v1-lite-i2v"],
        "schema": "v1",
        "duration_mode": "discrete",
        "durations": [5, 10],
        "max_resolution": "1080p",
        "cost_model": ("per_second", {"480p": 0.010, "720p": 0.0225, "1080p": 0.050}),
    },
    "premium": {
        "label": "Seedance 2.0 Fast (hero posts)",
        "models": ["bytedance/seedance-2-fast"],
        "schema": "v2",
        "duration_mode": "discrete",
        "durations": [5, 10],
        "max_resolution": "1080p",
        "cost_model": ("per_second", {"480p": 0.04, "720p": 0.06, "1080p": 0.10}),
    },
}

VALID_RESOLUTIONS = ["480p", "720p", "1080p"]
RES_DIMS = {"480p": (480, 854), "720p": (720, 1280), "1080p": (1080, 1920)}
RES_ORDER = {"480p": 0, "720p": 1, "1080p": 2}

# --------------------------------------------------------------- helpers ---

def log(msg):
    print(msg, flush=True)


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_api_key():
    """Use only the customer-provided environment; never scan private files."""
    return os.environ.get("KIE_API_KEY")


def kie_request(url, api_key, data=None):
    headers = {"Authorization": f"Bearer {api_key}",
               "Content-Type": "application/json"}
    is_get = data is None
    attempts = 3 if is_get else 1  # never auto-retry POSTs (could double-charge)
    last = None
    for attempt in range(attempts):
        if data is not None:
            req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                         headers=headers, method="POST")
        else:
            req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:500]
            return {"code": e.code, "msg": f"HTTP {e.code}: {body}"}
        except Exception as e:  # noqa: BLE001  (URLError, TimeoutError, ssl, json)
            last = {"code": -1, "msg": f"network error: {e}"}
            if attempt < attempts - 1:
                time.sleep(5)
    return last


def create_task(api_key, model, payload_input):
    result = kie_request(KIE_CREATE_TASK_URL, api_key,
                         {"model": model, "input": payload_input})
    if result.get("code") != 200:
        return None, result.get("msg", "unknown error")
    task_id = (result.get("data") or {}).get("taskId") \
        or (result.get("data") or {}).get("task_id")
    if not task_id:
        return None, f"no taskId in response: {json.dumps(result)[:300]}"
    return task_id, None


def poll_task(api_key, task_id, timeout):
    interval, elapsed = POLL_INITIAL, 0
    while elapsed < timeout:
        time.sleep(interval)
        elapsed += interval
        result = kie_request(f"{KIE_TASK_STATUS_URL}?taskId={task_id}", api_key)
        if not result:
            log(f"    ...poll blip, retrying [{elapsed}s]")
            continue
        data = result.get("data") or {}
        state = data.get("state", "unknown")
        if state == "success":
            rj = data.get("resultJson", "{}")
            try:
                rj = json.loads(rj) if isinstance(rj, str) else rj
            except json.JSONDecodeError:
                rj = {}
            urls = rj.get("resultUrls") or rj.get("result_urls") or []
            if urls:
                return urls, None
            return None, "task succeeded but returned no result URLs"
        if state == "fail":
            return None, f"{data.get('failMsg', 'task failed')} (code {data.get('failCode', '?')})"
        prog = data.get("progress", "")
        log(f"    ...{state}{f' {prog}%' if prog else ''} [{elapsed}s]")
        interval = min(interval + 2, POLL_MAX)
    return None, f"timed out after {timeout}s"


def download(url, dest, retries=6):
    """Patient download: CDN files can 503 briefly right after generation."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    last_err = None
    wait = 4
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": DOWNLOAD_UA})
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = resp.read()
            if not data:
                raise ValueError("empty response body")
            dest.write_bytes(data)
            return True, None
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
            if attempt < retries - 1:
                log(f"    download retry in {wait}s ({last_err})")
                time.sleep(wait)
                wait = min(wait * 2, 40)
    return False, last_err


def slugify(text, maxlen=40):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:maxlen] or "beat"


def validate_beat_slug(value):
    """A storyboard slug is a filename component, never a filesystem path."""
    if (not isinstance(value, str) or not value or value in {".", ".."}
            or any(char in value for char in ("/", "\\", ":"))
            or any(ord(char) < 32 or 127 <= ord(char) < 160 for char in value)):
        die("beat slug must be a filename without path separators, drive prefixes or control characters")
    return value


def run_ffmpeg(args):
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        die(f"ffmpeg failed:\n  {' '.join(cmd)}\n{proc.stderr[-1200:]}")


def ffprobe_duration(path):
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return 0.0


def fmt_ts(seconds):
    m, s = divmod(seconds, 60)
    return f"{int(m):02d}:{s:04.1f}"

# ------------------------------------------------------------ storyboard ---

def load_storyboard(path):
    try:
        sb = json.loads(Path(path).read_text())
    except Exception as e:  # noqa: BLE001
        die(f"could not read storyboard {path}: {e}")

    sb.setdefault("title", "motion-short")
    sb.setdefault("intro_seconds", 0.0)
    sb.setdefault("outro_seconds", 0.0)

    # Normalize: legacy top-level beats become one segment.
    if "segments" in sb and sb["segments"]:
        segments = sb["segments"]
    elif "beats" in sb and sb["beats"]:
        segments = [{"name": "main",
                     "start_at": float(sb.get("intro_seconds", 0.0)),
                     "beats": sb["beats"]}]
    else:
        die("storyboard has no beats or segments")

    multi = len(segments) > 1
    seen_slugs = set()
    for si, seg in enumerate(segments):
        seg.setdefault("name", f"seg{si + 1}")
        if "start_at" not in seg:
            die(f"segment '{seg['name']}' missing start_at (seconds in the final video)")
        beats = seg.get("beats") or []
        if not beats:
            die(f"segment '{seg['name']}' has no beats")
        for i, b in enumerate(beats):
            for field in ("line", "seconds", "keyframe_prompt", "motion_prompt"):
                if field not in b:
                    die(f"segment '{seg['name']}' beat {i + 1} missing '{field}'")
            supplied_slug = b.get("slug")
            if supplied_slug is not None and supplied_slug != "":
                validate_beat_slug(supplied_slug)
            base = supplied_slug or f"{i + 1:02d}_{slugify(b['line'])}"
            if not re.match(r"^\d\d_", base):
                base = f"{i + 1:02d}_{slugify(base)}"
            slug = f"s{si + 1}_{base}" if multi else base
            if slug in seen_slugs:
                slug = f"{slug}-{i + 1}"
            seen_slugs.add(slug)
            b["slug"] = validate_beat_slug(slug)
            b.setdefault("source_image", None)
            b["_segment"] = si

    sb["segments"] = segments
    return sb


def all_beats(sb):
    return [b for seg in sb["segments"] for b in seg["beats"]]


def plan_duration(seconds, tier_cfg):
    """Requested generation duration for a beat under this tier."""
    if tier_cfg["duration_mode"] == "range":
        lo, hi = tier_cfg["duration_range"]
        d = max(lo, min(hi, math.ceil(seconds)))
        if seconds > hi:
            die(f"a beat is {seconds:.1f}s but this tier caps clips at {hi}s; "
                f"split the beat in the storyboard")
        return d
    for d in sorted(tier_cfg["durations"]):
        if d >= seconds - 0.01:
            return d
    die(f"a beat is {seconds:.1f}s but this tier caps clips at "
        f"{max(tier_cfg['durations'])}s; split the beat in the storyboard")


def estimate_cost(beats, tier_cfg, gen_resolution):
    kind, val = tier_cfg["cost_model"]
    if kind == "per_clip":
        return len(beats) * val
    rate = val[gen_resolution]
    return sum(b["_gen_duration"] for b in beats) * rate

# ------------------------------------------------------------- payloads ---

def image_payload(prompt, aspect_ratio, resolution, image_data_uri=None):
    """Verified Images 2.5 input schema; videos keep their own model schemas."""
    ratios = {"auto", "1:1", "3:2", "2:3", "4:3", "3:4", "16:9", "9:16", "21:9", "27:16", "16:27", "9:8", "8:9"}
    if not prompt.strip() or len(prompt) > 20000 or aspect_ratio not in ratios or resolution not in ("1K", "2K", "4K"):
        raise ValueError("Invalid Images 2.5 prompt, ratio or resolution.")
    if aspect_ratio in {"27:16", "16:27", "9:8", "8:9"} and resolution != "1K":
        raise ValueError("This Images 2.5 ratio supports 1K only.")
    refs = [image_data_uri] if isinstance(image_data_uri, str) else list(image_data_uri or [])
    if len(refs) > 16 or any(not str(ref).startswith("https://") for ref in refs):
        raise ValueError("Supply at most 16 hosted HTTPS reference URLs; upload local files first.")
    result = {"prompt": prompt, "aspect_ratio": aspect_ratio, "resolution": resolution, "background": "auto"}
    if refs:
        result["input_urls"] = refs
    return result


def video_payload(schema, prompt, image_url, resolution, duration):
    if schema == "grok":
        return {
            "prompt": prompt,
            "image_urls": [image_url],
            "aspect_ratio": "9:16",
            "resolution": resolution,
            "duration": int(duration),
        }
    if schema == "v15":
        return {
            "prompt": prompt,
            "input_urls": [image_url],
            "aspect_ratio": "9:16",
            "resolution": resolution,
            "duration": int(duration),
            "fixed_lens": True,
            "generate_audio": False,
        }
    if schema == "v2":
        return {
            "prompt": prompt,
            "first_frame_url": image_url,
            "resolution": resolution,
            "duration": str(int(duration)),
            "generate_audio": False,
        }
    # v1 (Seedance 1.0 Lite/Pro image-to-video)
    return {
        "prompt": prompt,
        "image_url": image_url,
        "resolution": resolution,
        "duration": str(int(duration)),
        "camera_fixed": True,
        "seed": -1,
    }

# ------------------------------------------------------------ API phases ---

def request_keyframe_url(api_key, beat, aspect_ratio, img_resolution,
                         m=None, on_task_created=None):
    """Run the image task and return the hosted result URL (no download).
    If m has a saved image_task_id (interrupted run), resume polling it."""
    if m is not None and m.get("image_task_id") and not m.get("image_url"):
        age = time.time() - m.get("image_task_created", time.time())
        if age > STALE_TASK_SECONDS:
            log(f"    in-flight image task stale ({age/60:.0f} min); recreating")
            m.pop("image_task_id", None)
        else:
            log(f"    resuming in-flight image task {m['image_task_id']}")
            urls, err = poll_task(api_key, m["image_task_id"], POLL_TIMEOUT_IMAGE)
            if not err:
                return urls[0], None
            log(f"    in-flight task unusable ({err}); starting a new one")
            m.pop("image_task_id", None)

    prompt = beat["keyframe_prompt"]
    model = IMAGE_MODEL
    references = list(beat.get("reference_images") or [])
    src = beat.get("source_image")
    if src:
        references.insert(0, str(src))
    if references:
        model = IMAGE_MODEL_RESTYLE
    try:
        fields = image_payload(prompt, aspect_ratio, img_resolution, references)
    except ValueError as error:
        return None, str(error)

    task_id, err = create_task(api_key, model, fields)
    if err:
        return None, f"image task creation failed: {err}"
    if m is not None:
        m["image_task_id"] = task_id
        m["image_task_created"] = time.time()
        if on_task_created:
            on_task_created()
    urls, err = poll_task(api_key, task_id, POLL_TIMEOUT_IMAGE)
    if err:
        return None, f"image generation failed: {err}"
    return urls[0], None


def request_clip_url(api_key, beat, tier_cfg, gen_resolution, gen_duration,
                     m=None, on_task_created=None):
    if m is not None and m.get("video_task_id") and not m.get("video_url"):
        age = time.time() - m.get("video_task_created", time.time())
        if age > STALE_TASK_SECONDS:
            log(f"    in-flight video task stale ({age/60:.0f} min); recreating")
            m.pop("video_task_id", None)
        else:
            log(f"    resuming in-flight video task {m['video_task_id']}")
            urls, err = poll_task(api_key, m["video_task_id"], POLL_TIMEOUT_VIDEO)
            if not err:
                return urls[0], None
            log(f"    in-flight task unusable ({err}); starting a new one")
            m.pop("video_task_id", None)

    hosted_url = beat.get("_hosted_image_url")
    if not hosted_url:
        return None, "no hosted keyframe URL (run keyframe phase first)"

    prompt = beat["motion_prompt"]
    last_err = None
    for model in tier_cfg["models"]:
        payload = video_payload(tier_cfg["schema"], prompt, hosted_url,
                                gen_resolution, gen_duration)
        task_id, err = create_task(api_key, model, payload)
        if err:
            last_err = f"[{model}] {err}"
            if any(t in err.lower() for t in ("model", "not found", "invalid", "404")):
                log(f"    model '{model}' rejected, trying next candidate...")
                continue
            return None, last_err
        if m is not None:
            m["video_task_id"] = task_id
            m["video_task_created"] = time.time()
            if on_task_created:
                on_task_created()
        log(f"    animating with {model} ({gen_duration}s @ {gen_resolution})")
        urls, err = poll_task(api_key, task_id, POLL_TIMEOUT_VIDEO)
        if err:
            return None, f"[{model}] {err}"
        return urls[0], None
    return None, last_err or "all candidate models failed"

# ------------------------------------------------------------- assembly ---

def normalize_segment_clip(src, dest, target_seconds, width, height, fps=30):
    """Trim to exact beat length, conform size/fps/pixfmt (lanczos when
    upscaling), strip audio."""
    vf = (f"scale={width}:{height}:force_original_aspect_ratio=increase:"
          f"flags=lanczos,crop={width}:{height},fps={fps},format=yuv420p")
    run_ffmpeg(["-i", str(src), "-t", f"{target_seconds:.3f}", "-vf", vf,
                "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                str(dest)])


def assemble_segment(beats, work_dir, out_path, width, height, xfade=0.0):
    seg_dir = work_dir / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    pieces = []
    for b in beats:
        src = b.get("_clip_path")
        if not src or not Path(src).exists():
            die(f"missing clip for beat {b['slug']} (run animate phase first)")
        piece = seg_dir / f"{b['slug']}_seg.mp4"
        normalize_segment_clip(src, piece, b["seconds"], width, height)
        pieces.append((piece, b["seconds"]))

    if xfade > 0 and len(pieces) > 1:
        inputs, filters = [], []
        for piece, _ in pieces:
            inputs += ["-i", str(piece)]
        prev = "0:v"
        offset = 0.0
        for i in range(1, len(pieces)):
            offset += pieces[i - 1][1] - xfade
            out_label = f"x{i}"
            filters.append(
                f"[{prev}][{i}:v]xfade=transition=fade:duration={xfade:.3f}:"
                f"offset={offset:.3f}[{out_label}]")
            prev = out_label
        run_ffmpeg(inputs + ["-filter_complex", ";".join(filters),
                             "-map", f"[{prev}]", "-an", "-c:v", "libx264",
                             "-preset", "medium", "-crf", "18",
                             "-pix_fmt", "yuv420p", str(out_path)])
    else:
        concat_file = out_path.with_suffix(".concat.txt")
        def concat_quote(path):
            # FFmpeg concat files use their own single-quote parser. Close the
            # quoted string, escape a literal apostrophe, then reopen it.
            return "'" + str(path).replace("'", "'\\''") + "'"
        concat_file.write_text(
            "".join(f"file {concat_quote(p.resolve())}\n" for p, _ in pieces))
        run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(concat_file),
                    "-c", "copy", str(out_path)])
        concat_file.unlink(missing_ok=True)
    return out_path


def upscale_file(src, factor_dims):
    w, h = factor_dims
    up = src.with_name(src.stem + "_4k.mp4")
    run_ffmpeg(["-i", str(src),
                "-vf", f"scale={w}:{h}:flags=lanczos,format=yuv420p",
                "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                "-an", str(up)])
    return up


def overlay_segments(base_video, seg_files, out_path):
    """Overlay every (file, start_at) onto the base video; keep base audio."""
    inputs = ["-i", str(base_video)]
    filters = []
    prev = "0:v"
    for i, (f, start_at) in enumerate(seg_files, start=1):
        inputs += ["-i", str(f)]
        dur = ffprobe_duration(f)
        filters.append(f"[{i}:v]setpts=PTS+{start_at:.3f}/TB[a{i}]")
        filters.append(
            f"[{prev}][a{i}]overlay=0:0:enable='between(t,{start_at:.3f},"
            f"{start_at + dur:.3f})':eof_action=pass[v{i}]")
        prev = f"v{i}"
    run_ffmpeg(inputs + ["-filter_complex", ";".join(filters),
                         "-map", f"[{prev}]", "-map", "0:a?",
                         "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                         "-c:a", "aac", "-b:a", "192k", str(out_path)])

# ------------------------------------------------------------- manifest ---

def manifest_path(out_dir):
    return Path(out_dir) / "manifest.json"


def load_manifest(out_dir):
    p = manifest_path(out_dir)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_manifest(out_dir, data):
    manifest_path(out_dir).write_text(json.dumps(data, indent=2))

# ----------------------------------------------------------------- main ---

def main():
    ap = argparse.ArgumentParser(
        description="Generate motion-graphics animation shorts via Kie.ai")
    ap.add_argument("storyboard", help="Path to storyboard.json written for your project")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--tier", choices=list(TIERS), default="default")
    ap.add_argument("--resolution", choices=VALID_RESOLUTIONS, default="1080p",
                    help="Delivery resolution. If the tier's model caps lower, "
                         "clips are generated at the cap and lanczos-upscaled.")
    ap.add_argument("--image-resolution", choices=["1K", "2K", "4K"], default="2K")
    ap.add_argument("--xfade", type=float, default=0.0)
    ap.add_argument("--upscale-4k", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-paid", action="store_true", help="Kie spend has been explicitly authorized for this request.")
    ap.add_argument("--image-cost-usd", type=float, help="Current verified per-keyframe quote; required for paid keyframe generation.")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--force", default="",
                    help="Comma-separated beat slugs to regenerate from scratch")
    ap.add_argument("--keyframes-only", action="store_true")
    ap.add_argument("--animate-only", action="store_true")
    ap.add_argument("--assemble-only", action="store_true")
    ap.add_argument("--parallel", type=int, default=4,
                    help="concurrent video generations (default 4; 1 = serial)")
    ap.add_argument("--overlay-on", default=None,
                    help="Talking-head MP4; every segment overlays at its start_at")
    args = ap.parse_args()
    if not (args.dry_run or args.assemble_only or args.allow_paid):
        ap.error("Native subscription generation is the default. Paid Kie work requires existing authorization and --allow-paid.")
    if args.image_cost_usd is not None and args.image_cost_usd < 0:
        ap.error("The image cost quote cannot be negative.")
    if args.allow_paid and not (args.animate_only or args.assemble_only or args.dry_run) and args.image_cost_usd is None:
        ap.error("Verify the current keyframe quote and pass --image-cost-usd before paid generation.")

    sb = load_storyboard(args.storyboard)
    beats = all_beats(sb)
    tier_cfg = TIERS[args.tier]
    out_dir = Path(args.out_dir)
    img_dir = out_dir / "keyframes"
    vid_dir = out_dir / "clips"
    work_dir = out_dir / "work"
    for d in (img_dir, vid_dir, work_dir):
        d.mkdir(parents=True, exist_ok=True)

    width, height = RES_DIMS[args.resolution]
    gen_resolution = args.resolution
    if RES_ORDER[gen_resolution] > RES_ORDER[tier_cfg["max_resolution"]]:
        gen_resolution = tier_cfg["max_resolution"]

    # ---- plan + cost ----
    for b in beats:
        b["_gen_duration"] = plan_duration(b["seconds"], tier_cfg)
    total_anim = sum(b["seconds"] for b in beats)
    gen_seconds = sum(b["_gen_duration"] for b in beats)
    vid_cost = estimate_cost(beats, tier_cfg, gen_resolution)
    img_cost = len(beats) * args.image_cost_usd if args.image_cost_usd is not None else None

    log(f"Storyboard: {sb['title']} | segments: {len(sb['segments'])} | "
        f"beats: {len(beats)} | animation: {total_anim:.1f}s")
    log(f"Tier: {args.tier} ({tier_cfg['label']}) | generate @ {gen_resolution}"
        + (f", deliver @ {args.resolution} (lanczos upscale)"
           if gen_resolution != args.resolution else ""))
    for seg in sb["segments"]:
        log(f"  [{seg['name']}] starts at {fmt_ts(seg['start_at'])}:")
        for b in seg["beats"]:
            log(f"    {b['slug']}: {b['seconds']:.1f}s -> generate "
                f"{b['_gen_duration']}s | \"{b['line'][:60]}\"")
    if img_cost is None:
        log(f"Video estimate ~${vid_cost:.2f}; Images 2.5 keyframe quote is unverified. Supply --image-cost-usd after checking current pricing.")
    else:
        log(f"Estimated cost: video ~${vid_cost:.2f} + quoted keyframes ~${img_cost:.2f} = ~${vid_cost + img_cost:.2f}")
    if args.dry_run:
        return

    manifest = load_manifest(out_dir)
    manifest.setdefault("beats", {})

    # --force: wipe state for named beats.
    forced = {s.strip() for s in args.force.split(",") if s.strip()}
    unknown = forced - {b["slug"] for b in beats}
    if unknown:
        die(f"--force names unknown slugs: {', '.join(sorted(unknown))}")
    for slug in forced:
        manifest["beats"].pop(slug, None)
        (img_dir / f"{slug}.png").unlink(missing_ok=True)
        (vid_dir / f"{slug}.mp4").unlink(missing_ok=True)
        log(f"  forced regeneration: {slug}")
    if forced:
        save_manifest(out_dir, manifest)

    do_keyframes = not (args.animate_only or args.assemble_only)
    do_animate = not (args.keyframes_only or args.assemble_only)
    do_assemble = not (args.keyframes_only or args.animate_only)

    api_key = None
    if do_keyframes or do_animate:
        api_key = load_api_key()
        if not api_key:
            die("KIE_API_KEY not found. Set it in your own environment.")

    # ---- phase 1: keyframes ----
    if do_keyframes:
        log("\n== Phase 1: keyframes (ChatGPT Images 2.5 Flare) ==")
        for b in beats:
            slug = b["slug"]
            m = manifest["beats"].setdefault(slug, {})
            png = img_dir / f"{slug}.png"
            if args.resume and png.exists() and m.get("image_url"):
                b["_hosted_image_url"] = m["image_url"]
                log(f"  {slug}: exists, skipping")
                continue
            if not (args.resume and m.get("image_url")):
                log(f"  {slug}: generating keyframe...")
                url, err = request_keyframe_url(
                    api_key, b, "9:16", args.image_resolution, m=m,
                    on_task_created=lambda: save_manifest(out_dir, manifest))
                if err:
                    die(f"beat {slug}: {err}")
                m["image_url"] = url
                save_manifest(out_dir, manifest)  # URL persisted BEFORE download
            else:
                log(f"  {slug}: reusing paid result URL, downloading...")
            ok, err = download(m["image_url"], png)
            if not ok:
                die(f"beat {slug}: image download failed ({err}). "
                    f"The result URL is saved in manifest.json; rerun with "
                    f"--resume to retry the download for free.")
            b["_hosted_image_url"] = m["image_url"]
            m["image_path"] = str(png)
            save_manifest(out_dir, manifest)
            log(f"  {slug}: saved {png}")
        log(f"Keyframes done -> {img_dir}")
        if args.keyframes_only:
            log("Stopped after keyframes (--keyframes-only). Review every "
                "frame, --force any weak ones, then rerun with "
                "--animate-only --resume.")
            return
    else:
        for b in beats:
            m = manifest["beats"].get(b["slug"], {})
            b["_hosted_image_url"] = m.get("image_url")

    # ---- phase 2: animate (parallel: tasks are queued server-side, so
    # posting all beats at once and polling concurrently turns N queue
    # waits into 1; manifest writes are locked) ----
    if do_animate:
        log("\n== Phase 2: animation (image-to-video) ==")
        manifest_lock = threading.Lock()

        def locked_save():
            with manifest_lock:
                save_manifest(out_dir, manifest)

        def animate_beat(b):
            slug = b["slug"]
            with manifest_lock:
                m = manifest["beats"].setdefault(slug, {})
            mp4 = vid_dir / f"{slug}.mp4"
            if args.resume and mp4.exists():
                b["_clip_path"] = str(mp4)
                log(f"  {slug}: clip exists, skipping")
                return None
            if not (args.resume and m.get("video_url")):
                log(f"  {slug}: animating...")
                url, err = request_clip_url(
                    api_key, b, tier_cfg, gen_resolution, b["_gen_duration"],
                    m=m, on_task_created=locked_save)
                if err:
                    return f"beat {slug}: {err}"
                m["video_url"] = url
                locked_save()  # URL persisted BEFORE download
            else:
                log(f"  {slug}: reusing paid clip URL, downloading...")
            ok, err = download(m["video_url"], mp4)
            if not ok:
                return (f"beat {slug}: video download failed ({err}). "
                        f"The result URL is saved in manifest.json; rerun with "
                        f"--resume to retry the download for free.")
            b["_clip_path"] = str(mp4)
            m["clip_path"] = str(mp4)
            locked_save()
            log(f"  {slug}: saved {mp4}")
            return None

        workers = max(1, min(args.parallel, len(beats)))
        if workers == 1:
            errors = [e for e in (animate_beat(b) for b in beats) if e]
        else:
            with ThreadPoolExecutor(max_workers=workers) as ex:
                errors = [e for e in ex.map(animate_beat, beats) if e]
        if errors:
            die("\n".join(errors))
    else:
        for b in beats:
            m = manifest["beats"].get(b["slug"], {})
            b["_clip_path"] = m.get("clip_path") or str(vid_dir / f"{b['slug']}.mp4")

    # ---- phase 3: assemble ----
    if do_assemble:
        log("\n== Phase 3: assembly (ffmpeg) ==")
        single = len(sb["segments"]) == 1
        seg_outputs = []
        for seg in sb["segments"]:
            name = (f"{slugify(sb['title'], 50)}_animation.mp4" if single
                    else f"{slugify(sb['title'], 40)}_{slugify(seg['name'], 20)}.mp4")
            out_path = out_dir / name
            out_path = assemble_segment(seg["beats"], work_dir, out_path,
                                        width, height, xfade=args.xfade)
            if args.upscale_4k:
                out_path = upscale_file(out_path, (2160, 3840))
            actual = ffprobe_duration(out_path)
            seg_outputs.append((out_path, float(seg["start_at"]), seg, actual))
            log(f"  [{seg['name']}] {out_path.name} ({actual:.1f}s, silent)")

        # timeline.md
        lines = [f"# Overlay timeline - {sb['title']}", ""]
        for out_path, start_at, seg, actual in seg_outputs:
            lines.append(f"## {seg['name']} -> `{out_path.name}` "
                         f"({actual:.1f}s), place at **{fmt_ts(start_at)}**")
            t = start_at
            for b in seg["beats"]:
                lines.append(f"- {fmt_ts(t)} -> {fmt_ts(t + b['seconds'])}  "
                             f"{b['slug']}: \"{b['line']}\"")
                t += b["seconds"]
            lines.append(f"- talking head back on screen at {fmt_ts(t)}")
            lines.append("")
        tl = out_dir / "timeline.md"
        tl.write_text("\n".join(lines))
        log(f"Timeline: {tl}")

        if args.overlay_on:
            base = Path(args.overlay_on)
            if not base.exists():
                die(f"--overlay-on video not found: {base}")
            merged = out_dir / f"{slugify(sb['title'], 50)}_final.mp4"
            log(f"Overlaying {len(seg_outputs)} segment(s) onto {base.name}...")
            overlay_segments(base, [(p, s) for p, s, _, _ in seg_outputs], merged)
            log(f"Final video: {merged} (original narration audio kept)")

    log("\nDone.")


if __name__ == "__main__":
    main()
