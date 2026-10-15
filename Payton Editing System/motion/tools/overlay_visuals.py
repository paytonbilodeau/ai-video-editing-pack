#!/usr/bin/env python3
"""
Overlay Visual Images onto Video

Reads the visual_manifest.json from generate_script_visuals.py and overlays
each image onto the video at its timestamp with a smooth zoom-out effect
(starts at 105% scale, zooms out to 100%).

Each image is pre-rendered as a short video clip with the zoom animation
baked in frame-by-frame using PIL, then overlaid onto the video. This
avoids FFmpeg's zoompan filter which causes jitter at small zoom ranges.

Usage:
    python3 execution/overlay_visuals.py Drop/video.mp4 Drop/visuals/ Drop/video_with_visuals.mp4
    python3 execution/overlay_visuals.py Drop/video.mp4 Drop/visuals/ Drop/output.mp4 --max-duration 8
    python3 execution/overlay_visuals.py Drop/video.mp4 Drop/visuals/ Drop/output.mp4 --dry-run
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image


def get_video_info(video_path: str) -> dict:
    """Get video resolution and duration via ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe error: {result.stderr}")

    data = json.loads(result.stdout)

    video_stream = None
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            video_stream = stream
            break

    if not video_stream:
        raise RuntimeError("No video stream found")

    width = int(video_stream["width"])
    height = int(video_stream["height"])
    duration = float(data.get("format", {}).get("duration", 0))

    return {"width": width, "height": height, "duration": duration}


def load_manifest(visuals_dir: str) -> list[dict]:
    """Load visual manifest and return successful moments sorted by timestamp."""
    manifest_path = os.path.join(visuals_dir, "visual_manifest.json")
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with open(manifest_path) as f:
        manifest = json.load(f)

    moments = [
        m for m in manifest.get("moments", [])
        if m.get("status") == "success"
    ]
    moments.sort(key=lambda m: m["timestamp_seconds"])

    return moments


def compute_durations(moments: list[dict], video_duration: float, max_duration: float) -> list[dict]:
    """Compute display duration for each image.

    If a moment has 'end_timestamp' set, use that for precise duration.
    Otherwise fall back to gap-based calculation.
    """
    for i, moment in enumerate(moments):
        start = moment["timestamp_seconds"]

        if "end_timestamp" in moment and moment["end_timestamp"]:
            duration = moment["end_timestamp"] - start
            duration = max(duration, 2.0)
        elif i + 1 < len(moments):
            gap = moments[i + 1]["timestamp_seconds"] - start
            duration = min(gap, max_duration)
            duration = max(duration, 2.0)
        else:
            remaining = video_duration - start
            duration = min(remaining, max_duration)
            duration = max(duration, 2.0)

        moment["display_duration"] = round(duration, 3)
        moment["start"] = round(start, 3)
        moment["end"] = round(start + duration, 3)

    return moments


def render_zoom_clip(
    img_path: str,
    output_clip: str,
    video_width: int,
    video_height: int,
    duration: float,
    zoom_start: float = 1.05,
    fps: int = 30,
) -> bool:
    """
    Pre-render a zoom-out animation as a short video clip.

    Opens the source image, and for each frame scales it to the current
    zoom level and center-crops to video dimensions. This produces a
    smooth 105% -> 100% zoom-out with no jitter.

    Returns True on success.
    """
    img = Image.open(img_path)
    total_frames = int(duration * fps)
    tmpdir = tempfile.mkdtemp()

    try:
        for n in range(total_frames):
            progress = n / max(total_frames - 1, 1)
            zoom = zoom_start - (zoom_start - 1.0) * progress

            scaled_w = int(video_width * zoom)
            scaled_h = int(video_height * zoom)
            # Ensure at least video dimensions
            scaled_w = max(scaled_w, video_width)
            scaled_h = max(scaled_h, video_height)

            factor=max(scaled_w/img.width,scaled_h/img.height)
            resized = img.resize((round(img.width*factor),round(img.height*factor)), Image.LANCZOS)
            scaled_w,scaled_h=resized.size

            # Center crop to video dimensions
            left = (scaled_w - video_width) // 2
            top = (scaled_h - video_height) // 2
            cropped = resized.crop((left, top, left + video_width, top + video_height))

            frame_path = os.path.join(tmpdir, f"frame_{n:04d}.png")
            cropped.save(frame_path, "PNG")

        # Encode frames to video clip
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", os.path.join(tmpdir, "frame_%04d.png"),
            "-c:v", "h264_videotoolbox", "-b:v", "20M",
            "-pix_fmt", "yuv420p",
            output_clip
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Try software fallback
            cmd_sw = [c.replace("h264_videotoolbox", "libx264") for c in cmd]
            try:
                bv_idx = cmd_sw.index("-b:v")
                cmd_sw[bv_idx] = "-crf"
                cmd_sw[bv_idx + 1] = "18"
            except ValueError:
                pass
            result = subprocess.run(cmd_sw, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"      FFmpeg error: {result.stderr[-200:]}")
                return False

        return True
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def overlay_clips_onto_video(
    video_path: str,
    clip_paths: list[str],
    moments: list[dict],
    output_path: str,
    chunk_size: int = 10,
) -> None:
    """Overlay pre-rendered zoom clips onto the video in chunked passes."""
    if len(clip_paths) <= chunk_size:
        chunks = [(clip_paths, moments)]
    else:
        chunks = []
        for i in range(0, len(clip_paths), chunk_size):
            chunks.append((clip_paths[i:i + chunk_size], moments[i:i + chunk_size]))

    current_input = video_path
    total_passes = len(chunks)

    for pi, (clips, moms) in enumerate(chunks):
        is_last = pi == len(chunks) - 1
        if is_last:
            chunk_output = output_path
        else:
            stem = Path(output_path).stem
            ext = Path(output_path).suffix
            chunk_output = str(Path(output_path).parent / f"{stem}_pass{pi}{ext}")

        pass_label = f"pass {pi+1}/{total_passes}" if total_passes > 1 else "encoding"
        print(f"\n   Running {pass_label}...")

        cmd = ["ffmpeg", "-y", "-i", current_input]
        for clip in clips:
            cmd.extend(["-i", clip])

        # Build filter: offset each clip's PTS to its start time, then overlay
        filter_parts = []
        current_base = "[0:v]"
        for i, (clip, mom) in enumerate(zip(clips, moms)):
            input_idx = i + 1
            start = mom["start"]
            end = mom["end"]

            # Shift clip PTS to the right timestamp
            filter_parts.append(
                f"[{input_idx}:v]setpts=PTS+{start}/TB[clip{i}]"
            )

            out_label = f"[v{i}]" if i < len(clips) - 1 else "[vout]"
            filter_parts.append(
                f"{current_base}[clip{i}]"
                f"overlay=0:0:enable='between(t,{start},{end})'"
                f"{out_label}"
            )
            current_base = out_label

        filter_complex = ";".join(filter_parts)

        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "0:a?",
            "-c:v", "h264_videotoolbox",
            "-b:v", "20M",
            "-c:a", "copy",
            "-shortest",
            chunk_output
        ])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   Hardware encoding failed, trying software fallback...")
            cmd_sw = [c.replace("h264_videotoolbox", "libx264") for c in cmd]
            try:
                bv_idx = cmd_sw.index("-b:v")
                cmd_sw[bv_idx] = "-crf"
                cmd_sw[bv_idx + 1] = "18"
            except ValueError:
                pass
            result = subprocess.run(cmd_sw, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"   FFmpeg error:\n{result.stderr[-500:]}")
                raise RuntimeError(f"FFmpeg failed on {pass_label}")

        print(f"   ✓ {pass_label} complete")

        if not is_last:
            current_input = chunk_output

    # Clean up intermediate pass files
    if total_passes > 1:
        for pi in range(total_passes - 1):
            stem = Path(output_path).stem
            ext = Path(output_path).suffix
            pass_file = str(Path(output_path).parent / f"{stem}_pass{pi}{ext}")
            if os.path.exists(pass_file) and pass_file != output_path:
                os.remove(pass_file)


def overlay_visuals(
    video_path: str,
    visuals_dir: str,
    output_path: str,
    max_duration: float = 6.0,
    zoom_start: float = 1.05,
    dry_run: bool = False,
    chunk_size: int = 10,
) -> None:
    """Main function: load manifest, compute timing, render zoom clips, overlay."""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    print(f"\n🖼️  Visual Overlay")
    print(f"   Video: {video_path}")
    print(f"   Visuals: {visuals_dir}")
    print(f"   Output: {output_path}")

    info = get_video_info(video_path)
    print(f"   Resolution: {info['width']}x{info['height']}")
    print(f"   Duration: {info['duration']:.1f}s")

    moments = load_manifest(visuals_dir)
    print(f"   Images found: {len(moments)}")

    if not moments:
        print("   No successful images to overlay. Exiting.")
        return

    # Verify image files exist
    missing = []
    for m in moments:
        img_path = os.path.join(visuals_dir, m["filename"])
        if not os.path.exists(img_path):
            missing.append(m["filename"])
    if missing:
        print(f"   WARNING: {len(missing)} image(s) missing:")
        for f in missing:
            print(f"     - {f}")
        moments = [m for m in moments if m["filename"] not in missing]

    moments = compute_durations(moments, info["duration"], max_duration)

    print(f"\n   Overlay plan:")
    print(f"   {'#':>3}  {'Start':>7}  {'End':>7}  {'Dur':>5}  Image")
    print(f"   {'─'*3}  {'─'*7}  {'─'*7}  {'─'*5}  {'─'*40}")
    for i, m in enumerate(moments):
        start_ts = f"{int(m['start']//60):02d}:{int(m['start']%60):02d}"
        end_ts = f"{int(m['end']//60):02d}:{int(m['end']%60):02d}"
        print(f"   {i+1:>3}  {start_ts:>7}  {end_ts:>7}  {m['display_duration']:>4.1f}s  {m['filename']}")

    print(f"\n   Zoom effect: {zoom_start*100:.0f}% → 100% (smooth zoom-out)")

    if dry_run:
        print(f"\n   DRY RUN — no encoding performed.")
        return

    # Step 1: Pre-render zoom clips for each image
    print(f"\n   Pre-rendering zoom clips...")
    clip_dir = tempfile.mkdtemp(prefix="overlay_clips_")
    clip_paths = []
    failed = 0

    for i, m in enumerate(moments):
        img_path = os.path.join(visuals_dir, m["filename"])
        clip_path = os.path.join(clip_dir, f"clip_{i:03d}.mp4")
        label = m["filename"].replace(".png", "")
        print(f"   [{i+1}/{len(moments)}] {label}...", end="", flush=True)

        ok = render_zoom_clip(
            img_path, clip_path,
            info["width"], info["height"],
            m["display_duration"],
            zoom_start=zoom_start,
        )

        if ok:
            clip_paths.append(clip_path)
            print(" ✓")
        else:
            clip_paths.append(None)
            failed += 1
            print(" ✗")

    # Filter out failed clips
    valid = [(cp, m) for cp, m in zip(clip_paths, moments) if cp is not None]
    if not valid:
        print("   All clips failed to render.")
        shutil.rmtree(clip_dir, ignore_errors=True)
        return

    valid_clips, valid_moments = zip(*valid)
    valid_clips = list(valid_clips)
    valid_moments = list(valid_moments)

    if failed:
        print(f"   {failed} clip(s) failed, proceeding with {len(valid_clips)}")

    # Step 2: Overlay all clips onto video
    overlay_clips_onto_video(
        video_path, valid_clips, valid_moments,
        output_path, chunk_size
    )

    # Cleanup
    shutil.rmtree(clip_dir, ignore_errors=True)

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ Output saved: {output_path} ({file_size:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(
        description="Overlay visual images onto video with smooth zoom-out effect",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 execution/overlay_visuals.py Drop/video.mp4 Drop/visuals/ Drop/video_with_visuals.mp4
    python3 execution/overlay_visuals.py Drop/video.mp4 Drop/visuals/ Drop/output.mp4 --max-duration 8
    python3 execution/overlay_visuals.py Drop/video.mp4 Drop/visuals/ Drop/output.mp4 --dry-run
"""
    )

    parser.add_argument("video", help="Input video file")
    parser.add_argument("visuals_dir", help="Directory containing images and visual_manifest.json")
    parser.add_argument("output", help="Output video file")
    parser.add_argument("--max-duration", type=float, default=6.0,
                        help="Max display duration per image in seconds (default: 6.0)")
    parser.add_argument("--zoom-start", type=float, default=1.05,
                        help="Starting zoom scale (default: 1.05 = 105%%)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show overlay plan without encoding")
    parser.add_argument("--chunk-size", type=int, default=10,
                        help="Images per FFmpeg overlay pass (default: 10)")

    args = parser.parse_args()
    if Path(args.output).exists(): parser.error("Output exists; choose a new path")

    overlay_visuals(
        video_path=args.video,
        visuals_dir=args.visuals_dir,
        output_path=args.output,
        max_duration=args.max_duration,
        zoom_start=args.zoom_start,
        dry_run=args.dry_run,
        chunk_size=args.chunk_size,
    )


if __name__ == "__main__":
    main()
