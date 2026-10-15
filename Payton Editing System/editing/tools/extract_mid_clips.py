#!/usr/bin/env python3
"""Waterfall renderer: extract 16:9 mid-form clips (5-20 min) from a long recording.

Companion to extract_short_clips.py (which does face-tracked 9:16 shorts).
Mids keep the native 16:9 frame: no crop, no tracking, just requested timestamp trims, subject to actual export verification
at source resolution. Clips are processed SEQUENTIALLY (VideoToolbox silently
fails under concurrent load).

Usage:
    python3 tools/extract_mid_clips.py SOURCE.mp4 OUTPUT_DIR \
        --manifest project/waterfall/<proj>/map/content-map.json

Reads the "mids" array of a content map (or a bare JSON list of clips with
start/end/id/title). Writes mid_<id>_<slug>.mp4 plus mids_manifest.json.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HW_ENCODER = "h264_videotoolbox"
SW_CRF = "18"


def hw_available() -> bool:
    try:
        result = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"],
                                capture_output=True, text=True, timeout=15)
        return HW_ENCODER in result.stdout
    except Exception:
        return False


def encoder_args(use_hw: bool):
    if use_hw:
        # Optional hardware quality setting; verify the actual rendered picture
        return ["-c:v", HW_ENCODER, "-q:v", "65", "-allow_sw", "1"]
    return ["-c:v", "libx264", "-preset", "fast", "-crf", SW_CRF]


def slugify(text: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len].rstrip("-") or "clip"


def load_clips(manifest_path: Path):
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        clips = data.get("mids", [])
    else:
        clips = data
    if not clips:
        sys.exit("No mids found in manifest.")
    return clips


def extract(source: Path, out_dir: Path, clips, use_hw: bool):
    import math
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError("Use an empty output directory")
    seen = set()
    for i, clip in enumerate(clips, 1):
        start, end = float(clip["start"]), float(clip["end"])
        cid = str(clip.get("id", f"mid_{i:02d}"))
        if not all(math.isfinite(x) for x in (start,end)) or not 0 <= start < end:
            raise ValueError("Invalid clip interval")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", cid) or cid in seen:
            raise ValueError("Clip IDs must be unique plain names")
        seen.add(cid)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for i, clip in enumerate(clips, 1):
        start, end = float(clip["start"]), float(clip["end"])
        title = clip.get("title", f"mid {i}")
        cid = clip.get("id", f"mid_{i:02d}")
        out_path = out_dir / f"{cid}_{slugify(title)}.mp4"
        duration = end - start
        print(f"[{i}/{len(clips)}] {out_path.name}  ({start:.1f}s -> {end:.1f}s, {duration/60:.1f} min)")
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-n",
            "-ss", f"{start:.3f}", "-i", str(source), "-t", f"{duration:.3f}",
            *encoder_args(use_hw),
            "-c:a", "aac", "-b:a", "320k",
            "-movflags", "+faststart",
            str(out_path),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print(proc.stderr[-800:], file=sys.stderr)
            sys.exit(f"ffmpeg failed on {out_path.name}")
        size_mb = out_path.stat().st_size / 1e6
        if size_mb < 0.05:
            sys.exit(f"Suspiciously small output ({size_mb:.2f} MB): {out_path.name}")
        results.append({
            "id": cid, "file": str(out_path), "title": title,
            "start": start, "end": end, "duration": round(duration, 2),
        })
    manifest_out = out_dir / "mids_manifest.json"
    manifest_out.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"Done: {len(results)} mid clip(s), manifest at {manifest_out}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", help="Source video file")
    p.add_argument("output_dir", help="Output directory for mid clips")
    p.add_argument("--manifest", required=True, help="content-map.json (uses its 'mids' array) or bare clip list")
    p.add_argument("--software", action="store_true", help="Force libx264 instead of VideoToolbox")
    args = p.parse_args()

    source = Path(args.source).expanduser()
    if not source.exists():
        sys.exit(f"Not found: {source}")
    clips = load_clips(Path(args.manifest).expanduser())
    use_hw = (not args.software) and hw_available()
    print(f"Encoder: {'VideoToolbox (hw)' if use_hw else 'libx264 (sw)'}")
    extract(source, Path(args.output_dir).expanduser(), clips, use_hw)


if __name__ == "__main__":
    main()
