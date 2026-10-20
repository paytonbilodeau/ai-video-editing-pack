#!/usr/bin/env python3
"""
Extract Short-Form Clips from Long-Form Video

Takes a manifest JSON with clip timestamps and extracts each clip from the source
video with a dynamic face-centered 9:16 crop at full resolution. Face position is
tracked throughout the clip using MediaPipe FaceMesh, producing a subtle auto-pan
that keeps the speaker centered.

The editing assistant handles clip selection and hook/caption generation.
This script handles only the deterministic extraction + face-tracked crop.

Usage:
    # Extract clips from manifest
    python3 tools/extract_short_clips.py project/video.mp4 project/shorts/ --manifest project/shorts/clips_manifest.json

    # Force static center crop (skip face tracking)
    python3 tools/extract_short_clips.py project/video.mp4 project/shorts/ --manifest manifest.json --static-crop
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

try:
    import mediapipe as mp
    from mediapipe.tasks.python import BaseOptions, vision
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False

# Singleton FaceLandmarker instance (reuse across frames)
_face_landmarker = None

def _get_face_landmarker():
    """Get or create a singleton FaceLandmarker using the Tasks API."""
    global _face_landmarker
    if _face_landmarker is not None:
        return _face_landmarker

    # The user supplies a properly licensed model if face tracking is wanted.
    model_candidates = [os.environ.get("VIBE_FACE_MODEL", ""),
                        os.path.join(os.path.dirname(__file__), "face_landmarker.task")]
    model_path = None
    for p in model_candidates:
        if os.path.exists(p):
            model_path = p
            break

    if model_path is None:
        print("   WARNING: face_landmarker.task model not found, falling back to static crop")
        return None

    options = vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        num_faces=1,
        min_face_detection_confidence=0.5,
    )
    _face_landmarker = vision.FaceLandmarker.create_from_options(options)
    return _face_landmarker

# ============================================================
# Constants
# ============================================================

HARDWARE_ENCODER = "h264_videotoolbox"
SOFTWARE_ENCODER = "libx264"
HARDWARE_BITRATE = "20M"
SOFTWARE_CRF = "18"
FPS = 30


# ============================================================
# Video info utilities
# ============================================================

def get_video_info(video_path: str) -> dict:
    """Get video resolution, duration, and fps via ffprobe."""
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

    # Parse fps from r_frame_rate (e.g. "30/1" or "30000/1001")
    fps_str = video_stream.get("r_frame_rate", "30/1")
    try:
        num, den = fps_str.split("/")
        fps = round(int(num) / int(den))
    except (ValueError, ZeroDivisionError):
        fps = FPS

    return {"width": width, "height": height, "duration": duration, "fps": fps}


def check_hardware_encoder() -> bool:
    """Check if h264_videotoolbox hardware encoder is available."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True, text=True, timeout=5
        )
        return "h264_videotoolbox" in result.stdout
    except Exception:
        return False


_hw_available = None

def get_encoder_args() -> list[str]:
    """Get FFmpeg encoder args with cached hardware check."""
    global _hw_available
    if _hw_available is None:
        _hw_available = check_hardware_encoder()
        enc_name = "h264_videotoolbox" if _hw_available else "libx264"
        print(f"   Encoder: {enc_name}")
    if _hw_available:
        return ["-c:v", HARDWARE_ENCODER, "-b:v", HARDWARE_BITRATE]
    else:
        return ["-c:v", SOFTWARE_ENCODER, "-preset", "fast", "-crf", SOFTWARE_CRF]


# ============================================================
# Face detection
# ============================================================

def detect_face_center_x(frame_rgb: np.ndarray) -> float | None:
    """
    Detect face bounding box center X in a video frame using MediaPipe FaceLandmarker (Tasks API).

    Args:
        frame_rgb: RGB numpy array (H, W, 3)

    Returns:
        Face center X coordinate in pixels, or None if no face detected.
    """
    if not HAS_MEDIAPIPE:
        return None

    landmarker = _get_face_landmarker()
    if landmarker is None:
        return None

    h, w = frame_rgb.shape[:2]
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    result = landmarker.detect(mp_image)

    if not result.face_landmarks:
        return None

    landmarks = result.face_landmarks[0]
    xs = [lm.x * w for lm in landmarks]
    center_x = (min(xs) + max(xs)) / 2.0
    return center_x


def sample_face_positions(
    video_path: str,
    start: float,
    end: float,
    sample_interval: float,
    video_width: int,
    video_height: int,
) -> list[tuple[float, float | None]]:
    """
    Sample face center X positions throughout a clip by extracting frames
    and running face detection on each.

    Returns list of (timestamp_offset, face_center_x_or_None) tuples.
    Timestamps are relative to clip start (0-based).
    """
    duration = end - start
    num_samples = max(1, int(duration / sample_interval) + 1)
    results = []

    # Downscale threshold: run face detection at 1080p max for speed
    scale_factor = 1.0
    if video_width > 2000:
        scale_factor = 1920 / video_width

    for i in range(num_samples):
        t_offset = min(i * sample_interval, duration - 0.1)
        t_abs = start + t_offset

        # Extract one frame via FFmpeg pipe (raw RGB)
        cmd = [
            "ffmpeg", "-v", "quiet",
            "-ss", str(t_abs),
            "-i", video_path,
            "-frames:v", "1",
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "pipe:1"
        ]
        proc = subprocess.run(cmd, capture_output=True, timeout=10)
        if proc.returncode != 0 or len(proc.stdout) == 0:
            results.append((t_offset, None))
            continue

        frame = np.frombuffer(proc.stdout, dtype=np.uint8)
        try:
            frame = frame.reshape((video_height, video_width, 3))
        except ValueError:
            results.append((t_offset, None))
            continue

        # Downscale for face detection speed
        if scale_factor < 1.0:
            import cv2
            small_h = int(video_height * scale_factor)
            small_w = int(video_width * scale_factor)
            small_frame = cv2.resize(frame, (small_w, small_h))
            center_x = detect_face_center_x(small_frame)
            if center_x is not None:
                # Scale back to full resolution
                center_x = center_x / scale_factor
        else:
            center_x = detect_face_center_x(frame)

        results.append((t_offset, center_x))

    return results


def smooth_face_trajectory(
    samples: list[tuple[float, float | None]],
    video_width: int,
    smooth_window: int,
) -> list[tuple[float, float]]:
    """
    Smooth and interpolate face center X positions.

    1. Fill gaps (None values) via linear interpolation from neighbors
    2. Apply moving average smoothing
    3. Return complete trajectory with no gaps

    Falls back to center of frame if too few detections.
    """
    center_fallback = video_width / 2.0

    # Separate detected vs missing
    detected = [(t, x) for t, x in samples if x is not None]
    total = len(samples)
    detected_count = len(detected)

    if detected_count == 0:
        # No faces detected at all — center crop
        return [(t, center_fallback) for t, _ in samples]

    if detected_count < total * 0.2:
        # Too few detections (<20%) — use median of detected positions
        median_x = sorted([x for _, x in detected])[detected_count // 2]
        return [(t, median_x) for t, _ in samples]

    # Fill gaps via linear interpolation
    filled = []
    for i, (t, x) in enumerate(samples):
        if x is not None:
            filled.append((t, x))
        else:
            # Find nearest detected before and after
            before = None
            for j in range(i - 1, -1, -1):
                if samples[j][1] is not None:
                    before = samples[j]
                    break
            after = None
            for j in range(i + 1, len(samples)):
                if samples[j][1] is not None:
                    after = samples[j]
                    break

            if before and after:
                # Linear interpolation
                frac = (t - before[0]) / (after[0] - before[0]) if after[0] != before[0] else 0.5
                interp_x = before[1] + frac * (after[1] - before[1])
                filled.append((t, interp_x))
            elif before:
                filled.append((t, before[1]))
            elif after:
                filled.append((t, after[1]))
            else:
                filled.append((t, center_fallback))

    # Moving average smoothing
    if smooth_window > 1 and len(filled) > smooth_window:
        xs = [x for _, x in filled]
        smoothed_xs = []
        half = smooth_window // 2
        for i in range(len(xs)):
            lo = max(0, i - half)
            hi = min(len(xs), i + half + 1)
            smoothed_xs.append(sum(xs[lo:hi]) / (hi - lo))
        filled = [(t, sx) for (t, _), sx in zip(filled, smoothed_xs)]

    return filled


def interpolate_to_frames(
    trajectory: list[tuple[float, float]],
    duration: float,
    fps: int,
) -> list[float]:
    """
    Interpolate smoothed keypoint trajectory to per-frame crop X values.

    Returns a list of face_center_x values, one per frame.
    """
    total_frames = int(duration * fps)
    if total_frames < 1:
        total_frames = 1

    if len(trajectory) < 2:
        return [trajectory[0][1]] * total_frames

    frame_xs = []
    for n in range(total_frames):
        t = n / fps

        # Find surrounding keypoints
        if t <= trajectory[0][0]:
            frame_xs.append(trajectory[0][1])
        elif t >= trajectory[-1][0]:
            frame_xs.append(trajectory[-1][1])
        else:
            # Binary-ish search for bracket
            for i in range(len(trajectory) - 1):
                if trajectory[i][0] <= t <= trajectory[i + 1][0]:
                    t0, x0 = trajectory[i]
                    t1, x1 = trajectory[i + 1]
                    frac = (t - t0) / (t1 - t0) if t1 != t0 else 0.0
                    frame_xs.append(x0 + frac * (x1 - x0))
                    break
            else:
                frame_xs.append(trajectory[-1][1])

    return frame_xs


# ============================================================
# Crop calculation
# ============================================================

def calculate_crop_params(
    video_width: int,
    video_height: int,
    face_center_x: float,
) -> tuple[int, int, int]:
    """
    Calculate 9:16 crop window centered on face.

    Returns (crop_w, crop_h, x_offset).
    """
    crop_w = int(video_height * 9 / 16)
    crop_h = video_height

    x_offset = int(face_center_x - crop_w / 2)
    # Clamp to valid range
    x_offset = max(0, min(x_offset, video_width - crop_w))

    return crop_w, crop_h, x_offset


# ============================================================
# Clip extraction
# ============================================================

def extract_clip_dynamic_crop(
    video_path: str,
    start: float,
    end: float,
    frame_crop_xs: list[float],
    video_width: int,
    video_height: int,
    fps: int,
    output_path: str,
    encoder_args: list[str],
) -> bool:
    """
    Extract a clip with per-frame dynamic crop using FFmpeg pipe I/O.

    1. Decode source segment to raw frames via FFmpeg stdout pipe
    2. Crop each frame using numpy slicing
    3. Pipe cropped frames to FFmpeg stdin for encoding

    Returns True on success.
    """
    duration = end - start
    crop_w = int(video_height * 9 / 16)
    crop_h = video_height

    # Decoder: extract raw frames from segment
    decode_cmd = [
        "ffmpeg", "-v", "quiet",
        "-ss", str(start),
        "-t", str(duration),
        "-i", video_path,
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "pipe:1"
    ]

    # Encoder: accept raw cropped frames, encode to output
    encode_cmd = [
        "ffmpeg", "-y", "-v", "quiet",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{crop_w}x{crop_h}",
        "-r", str(fps),
        "-i", "pipe:0",
    ]

    # Extract audio separately and add it
    encode_cmd.extend([
        "-ss", str(start),
        "-t", str(duration),
        "-i", video_path,
        "-map", "0:v",
        "-map", "1:a?",
    ])

    encode_cmd.extend(encoder_args)
    encode_cmd.extend([
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-avoid_negative_ts", "make_zero",
        "-loglevel", "error",
        output_path
    ])

    frame_size = video_width * video_height * 3  # RGB24
    cropped_frame_size = crop_w * crop_h * 3

    decoder = subprocess.Popen(decode_cmd, stdout=subprocess.PIPE)
    encoder = subprocess.Popen(encode_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    frame_idx = 0
    try:
        while True:
            raw = decoder.stdout.read(frame_size)
            if len(raw) < frame_size:
                break

            frame = np.frombuffer(raw, dtype=np.uint8).reshape((video_height, video_width, 3))

            # Get crop X for this frame (clamp index to trajectory length)
            if frame_idx < len(frame_crop_xs):
                face_x = frame_crop_xs[frame_idx]
            else:
                face_x = frame_crop_xs[-1]

            _, _, x_off = calculate_crop_params(video_width, video_height, face_x)

            # Numpy crop (fast, zero-copy view)
            cropped = frame[:, x_off:x_off + crop_w, :]

            # Write cropped frame to encoder
            encoder.stdin.write(cropped.tobytes())
            frame_idx += 1

    except BrokenPipeError:
        pass
    finally:
        decoder.stdout.close()
        decoder.wait()
        if encoder.stdin and not encoder.stdin.closed:
            try:
                encoder.stdin.close()
            except Exception:
                pass
        # Read remaining stderr and wait for encoder to finish
        stderr = encoder.stderr.read() if encoder.stderr else b""
        encoder.wait()

    if encoder.returncode != 0:
        err = stderr.decode() if stderr else "unknown error"
        print(f"      Encode error: {err[-200:]}")
        return False

    return True


def extract_clip_static_crop(
    video_path: str,
    start: float,
    end: float,
    crop_x: int,
    video_width: int,
    video_height: int,
    output_path: str,
    encoder_args: list[str],
) -> bool:
    """
    Extract a clip with static FFmpeg crop filter (faster, no Python frame processing).
    Used when --static-crop is set or face tracking fails.
    """
    duration = end - start
    crop_w = int(video_height * 9 / 16)

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-t", str(duration),
        "-i", video_path,
        "-vf", f"crop={crop_w}:{video_height}:{crop_x}:0",
    ]
    cmd.extend(encoder_args)
    cmd.extend([
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-avoid_negative_ts", "make_zero",
        "-loglevel", "error",
        output_path
    ])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"      FFmpeg error: {result.stderr[-200:]}")
        return False
    return True


# ============================================================
# Slug generation
# ============================================================

def slugify(text: str) -> str:
    """Convert title to a filename-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug[:50].strip('-')


# ============================================================
# Main processing
# ============================================================

def process_clip(
    video_path: str,
    clip: dict,
    clip_index: int,
    output_dir: str,
    video_info: dict,
    encoder_args: list[str],
    sample_interval: float,
    smooth_window: int,
    static_crop: bool,
) -> dict:
    """Process a single clip: detect face trajectory, crop, and encode."""
    start = clip["start"]
    end = clip["end"]
    title = clip.get("title", f"clip_{clip_index}")
    duration = end - start
    slug = slugify(title)
    output_file = f"clip_{clip_index:02d}_{slug}.mp4"
    output_path = os.path.join(output_dir, output_file)

    w = video_info["width"]
    h = video_info["height"]
    fps = video_info["fps"]
    crop_w = int(h * 9 / 16)

    result = {
        "index": clip_index,
        "title": title,
        "start": start,
        "end": end,
        "duration": round(duration, 2),
        "output_file": output_file,
        "crop_w": crop_w,
        "output_resolution": f"{crop_w}x{h}",
        "face_tracked": False,
        "face_detection_rate": 0.0,
        "status": "pending",
    }

    start_ts = f"{int(start)//60}:{int(start)%60:02d}"
    end_ts = f"{int(end)//60}:{int(end)%60:02d}"
    print(f"\n   [{clip_index}] \"{title}\" ({start_ts} - {end_ts}, {duration:.1f}s)")

    if static_crop or not HAS_MEDIAPIPE:
        # Static center crop
        if not HAS_MEDIAPIPE and not static_crop:
            print(f"      MediaPipe not available, using center crop")
        else:
            print(f"      Static center crop")

        center_x = w / 2
        _, _, x_off = calculate_crop_params(w, h, center_x)
        result["crop_mode"] = "static_center"

        ok = extract_clip_static_crop(
            video_path, start, end, x_off, w, h, output_path, encoder_args
        )
    else:
        # Dynamic face tracking
        print(f"      Sampling face positions (every {sample_interval}s)...")
        samples = sample_face_positions(video_path, start, end, sample_interval, w, h)

        detected = sum(1 for _, x in samples if x is not None)
        total = len(samples)
        detection_rate = detected / total if total > 0 else 0
        result["face_detection_rate"] = round(detection_rate, 2)

        print(f"      Face detected in {detected}/{total} samples ({detection_rate:.0%})")

        if detection_rate < 0.2:
            # Too few detections — fall back to static center crop
            print(f"      Low detection rate, falling back to center crop")
            center_x = w / 2
            _, _, x_off = calculate_crop_params(w, h, center_x)
            result["crop_mode"] = "static_center_fallback"

            ok = extract_clip_static_crop(
                video_path, start, end, x_off, w, h, output_path, encoder_args
            )
        else:
            # Smooth trajectory and interpolate to per-frame
            trajectory = smooth_face_trajectory(samples, w, smooth_window)
            frame_crop_xs = interpolate_to_frames(trajectory, duration, fps)
            result["face_tracked"] = True
            result["crop_mode"] = "dynamic_face_tracked"

            # Log pan range
            all_xs = [calculate_crop_params(w, h, fx)[2] for fx in frame_crop_xs]
            min_x, max_x = min(all_xs), max(all_xs)
            pan_range_px = max_x - min_x
            print(f"      Pan range: {pan_range_px}px ({pan_range_px / w * 100:.1f}% of frame)")

            if pan_range_px < 5:
                # Negligible movement — use static crop for speed
                print(f"      Minimal movement, using static crop for speed")
                avg_x = sum(frame_crop_xs) / len(frame_crop_xs)
                _, _, x_off = calculate_crop_params(w, h, avg_x)
                result["crop_mode"] = "static_face_centered"

                ok = extract_clip_static_crop(
                    video_path, start, end, x_off, w, h, output_path, encoder_args
                )
            else:
                print(f"      Encoding with dynamic crop ({len(frame_crop_xs)} frames)...")
                ok = extract_clip_dynamic_crop(
                    video_path, start, end, frame_crop_xs,
                    w, h, fps, output_path, encoder_args
                )

    if ok and os.path.exists(output_path):
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        result["status"] = "success"
        result["file_size_mb"] = round(file_size, 1)
        print(f"      Done: {output_file} ({file_size:.1f} MB)")
    else:
        result["status"] = "failed"
        print(f"      FAILED")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Extract face-centered 9:16 short-form clips from a long-form video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 tools/extract_short_clips.py project/video.mp4 project/shorts/ --manifest clips.json
    python3 tools/extract_short_clips.py project/video.mp4 project/shorts/ --manifest clips.json --static-crop
"""
    )

    parser.add_argument("source_video", help="Source video file path")
    parser.add_argument("output_dir", help="Output directory for clips")
    parser.add_argument("--manifest", required=True, help="Path to JSON manifest with clip definitions")
    parser.add_argument("--sample-interval", type=float, default=1.0,
                        help="Seconds between face detection samples (default: 1.0)")
    parser.add_argument("--smooth-window", type=int, default=5,
                        help="Smoothing window size for face position (default: 5)")
    parser.add_argument("--static-crop", action="store_true",
                        help="Force static center crop (skip face tracking)")

    args = parser.parse_args()

    if not os.path.exists(args.source_video):
        print(f"Error: source video not found: {args.source_video}")
        sys.exit(1)

    if not os.path.exists(args.manifest):
        print(f"Error: manifest not found: {args.manifest}")
        sys.exit(1)

    with open(args.manifest) as f:
        clips = json.load(f)

    if not clips:
        print("Error: manifest is empty")
        sys.exit(1)

    if Path(args.output_dir).exists() and any(Path(args.output_dir).iterdir()):
        raise FileExistsError("Use an empty output directory; earlier clips are preserved")
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"\n   Short-Form Clip Extraction")
    print(f"   Source: {args.source_video}")
    print(f"   Output: {args.output_dir}")
    print(f"   Clips: {len(clips)}")

    video_info = get_video_info(args.source_video)
    crop_w = int(video_info["height"] * 9 / 16)
    print(f"   Source resolution: {video_info['width']}x{video_info['height']}")
    print(f"   Output resolution: {crop_w}x{video_info['height']} (9:16)")
    print(f"   FPS: {video_info['fps']}")

    if not HAS_MEDIAPIPE:
        print(f"   WARNING: MediaPipe not installed, all clips will use center crop")

    encoder_args = get_encoder_args()

    t0 = time.time()
    results = []

    for i, clip in enumerate(clips, 1):
        result = process_clip(
            video_path=args.source_video,
            clip=clip,
            clip_index=i,
            output_dir=args.output_dir,
            video_info=video_info,
            encoder_args=encoder_args,
            sample_interval=args.sample_interval,
            smooth_window=args.smooth_window,
            static_crop=args.static_crop,
        )
        results.append(result)

    elapsed = time.time() - t0
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "failed")

    # Write manifest
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "source_video": args.source_video,
        "source_resolution": f"{video_info['width']}x{video_info['height']}",
        "output_resolution": f"{crop_w}x{video_info['height']}",
        "total_clips": len(clips),
        "successful": success,
        "failed": failed,
        "processing_time_seconds": round(elapsed, 1),
        "clips": results,
    }

    manifest_path = os.path.join(args.output_dir, "shorts_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n   Summary: {success} succeeded, {failed} failed ({elapsed:.1f}s)")
    print(f"   Manifest: {manifest_path}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
