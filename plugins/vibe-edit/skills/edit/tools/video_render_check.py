#!/usr/bin/env python3
"""Verify a local render's media properties, full decode and optional alpha samples.

This checks file integrity and specified technical properties. It does not judge
visual quality, speech/SFX alignment, sound quality or editor compatibility.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys


def _run(command):
    result = subprocess.run(command, capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode(errors="replace")[-2000:].strip() or "Media command failed")
    return result.stdout


def _probe(path, count=False):
    command = ["ffprobe", "-v", "error"]
    if count:
        command += ["-count_frames"]
    return json.loads(_run(command + ["-show_streams", "-show_format", "-of", "json", str(path)]))


def _rate(value):
    try:
        rate = Fraction(str(value))
    except (ValueError, ZeroDivisionError):
        return None
    return rate if rate > 0 else None


def _integer(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def _duration(video):
    try:
        value = float(video["duration"])
        if math.isfinite(value) and value >= 0:
            return value, "video_stream.duration"
    except (KeyError, TypeError, ValueError):
        pass
    try:
        value = float(int(video["duration_ts"]) * Fraction(video["time_base"]))
        if math.isfinite(value) and value >= 0:
            return value, "video_stream.duration_ts*time_base"
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        pass
    return None, "unavailable"


def _alpha_formats():
    data = json.loads(_run(["ffprobe", "-v", "error", "-show_pixel_formats", "-of", "json"]))
    return {item["name"] for item in data["pixel_formats"] if item.get("flags", {}).get("alpha")}


def _alpha_sample(path, frame, width, height):
    # Select by decoded frame index. RGBA conversion exposes full-range uint8
    # alpha, avoiding bit-depth/range assumptions about the original format.
    rgba = _run(["ffmpeg", "-v", "error", "-xerror", "-i", str(path),
                 "-map", "0:v:0", "-vf", f"select=eq(n\\,{frame}),format=rgba",
                 "-frames:v", "1", "-an", "-f", "rawvideo", "-pix_fmt", "rgba", "-"])
    expected = width * height * 4
    if len(rgba) != expected:
        raise ValueError(f"Alpha frame {frame} decoded {len(rgba)} bytes; expected {expected}")
    alpha = rgba[3::4]
    return {"frame_index": frame, "alpha_min_uint8": min(alpha), "alpha_max_uint8": max(alpha)}


def audio_packet_hash(path):
    """Hash the first audio stream's encoded payload without decoding/re-encoding."""
    return _run(["ffmpeg", "-v", "error", "-xerror", "-i", str(path),
                 "-map", "0:a:0", "-c", "copy", "-f", "hash", "-hash", "sha256", "-"]).decode().strip()


def check_render(media, *, width, height, fps, frames, audio,
                 expect_alpha=False, alpha_times=(), audio_reference=None):
    """Return a JSON-safe receipt; failures appear in errors and set ok=False.

    Expected values describe one video stream. Alpha times select the frame at
    floor(time * actual_fps). Samples prove only their selected frames. When
    requested, alpha must show both nonzero opacity and some transparency.
    An audio reference is the approved clip before a picture-only revision, not
    the untrimmed master. It verifies encoded audio payload preservation only;
    matching payloads do not prove synchronization or perceptual quality.
    """
    expected_fps = _rate(fps)
    if any(isinstance(v, bool) or not isinstance(v, int) or v <= 0 for v in (width, height, frames)):
        raise ValueError("width, height and frames must be positive integers")
    if expected_fps is None or audio not in ("none", "present"):
        raise ValueError("fps must be positive and audio must be none or present")
    if audio_reference is not None and audio != "present":
        raise ValueError("An audio reference requires audio=present")
    times = [Fraction(str(value)) for value in alpha_times]
    if any(value < 0 for value in times):
        raise ValueError("Alpha sample times must be nonnegative")
    if expect_alpha and not times:
        raise ValueError("--expect-alpha requires at least one --alpha-time")
    if times and not expect_alpha:
        raise ValueError("Alpha sample times require --expect-alpha")
    path = Path(media).expanduser().resolve()
    report = {
        "schema_version": 1, "ok": False,
        "source": {"path": str(path), "sha256": None, "bytes": None},
        "expected": {"width": width, "height": height, "fps": str(expected_fps),
                     "frames": frames, "video_duration_seconds": float(frames / expected_fps),
                     "audio": audio, "alpha": expect_alpha},
        "actual": {}, "checks": {"nonempty": False, "full_decode": False},
        "alpha": {"requested": expect_alpha, "samples": [],
                  "scope": "Only listed frame samples; no whole-file alpha or visual-quality claim."},
        "errors": [],
    }
    errors = report["errors"]
    try:
        before = path.stat()
        if not path.is_file() or before.st_size == 0:
            raise ValueError("Media is not a nonempty regular file")
        report["source"]["bytes"] = before.st_size
        report["checks"]["nonempty"] = True
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
                digest.update(chunk)
        report["source"]["sha256"] = digest.hexdigest()
        data = _probe(path)
        streams = data.get("streams", [])
        videos = [stream for stream in streams if stream.get("codec_type") == "video"]
        counts = dict(Counter(stream.get("codec_type", "unknown") for stream in streams))
        report["actual"]["stream_counts"] = counts
        if len(videos) != 1:
            raise ValueError(f"Expected one video stream; found {len(videos)}")
        video = videos[0]
        actual_frames = _integer(video.get("nb_frames"))
        frame_basis = "nb_frames"
        if actual_frames is None:
            counted = _probe(path, count=True)
            counted_video = next(s for s in counted["streams"] if s.get("index") == video.get("index"))
            actual_frames = _integer(counted_video.get("nb_read_frames"))
            frame_basis = "ffprobe -count_frames:nb_read_frames"
        actual_fps = _rate(video.get("avg_frame_rate")) or _rate(video.get("r_frame_rate"))
        duration, duration_basis = _duration(video)
        if duration is None and actual_frames is not None and actual_fps:
            duration = float(actual_frames / actual_fps)
            duration_basis = "derived from actual frames/fps"
        report["actual"].update({
            "width": video.get("width"), "height": video.get("height"),
            "fps": str(actual_fps) if actual_fps else None,
            "avg_frame_rate": video.get("avg_frame_rate"), "r_frame_rate": video.get("r_frame_rate"),
            "frames": actual_frames, "frame_count_basis": frame_basis,
            "video_duration_seconds": duration, "duration_basis": duration_basis,
            "codec": video.get("codec_name"), "pixel_format": video.get("pix_fmt"),
        })
        checks = report["checks"]
        checks["canvas"] = (video.get("width"), video.get("height")) == (width, height)
        checks["fps"] = actual_fps == expected_fps
        checks["frames"] = actual_frames == frames
        checks["audio"] = (counts.get("audio", 0) > 0) == (audio == "present")
        # Container timestamps can be rounded. Half a frame bounds this check;
        # the independent exact frame count remains mandatory.
        checks["video_duration"] = duration is not None and abs(duration - float(frames / expected_fps)) <= float(1 / (2 * expected_fps))
        for name in ("canvas", "fps", "frames", "audio", "video_duration"):
            if not checks[name]:
                errors.append(f"Expected {name} does not match actual media; see expected/actual")
        try:
            _run(["ffmpeg", "-v", "error", "-xerror", "-i", str(path),
                  "-map", "0:v", "-map", "0:a?", "-f", "null", "-"])
            checks["full_decode"] = True
        except ValueError as error:
            errors.append(f"Full decode failed: {error}")
        if audio_reference is not None:
            reference = Path(audio_reference).expanduser().resolve()
            reference_before = reference.stat()
            if reference.samefile(path):
                raise ValueError("Audio reference must be a different file from the render")
            reference_audio = [s for s in _probe(reference).get("streams", [])
                               if s.get("codec_type") == "audio"]
            actual_audio = [s for s in streams if s.get("codec_type") == "audio"]
            if len(reference_audio) != 1 or len(actual_audio) != 1:
                raise ValueError("Audio preservation requires exactly one audio stream in each file")
            expected_hash = audio_packet_hash(reference)
            actual_hash = audio_packet_hash(path)
            checks["audio_payload_unchanged"] = (
                actual_audio[0].get("codec_name") == reference_audio[0].get("codec_name")
                and actual_hash == expected_hash
            )
            report["audio_preservation"] = {
                "reference": str(reference), "reference_payload_hash": expected_hash,
                "render_payload_hash": actual_hash,
                "scope": "Encoded audio payload only; synchronization and listening remain separate checks.",
            }
            if not checks["audio_payload_unchanged"]:
                errors.append("Audio payload differs from the approved reference; it may be truncated, changed or re-encoded")
            reference_after = reference.stat()
            checks["audio_reference_unchanged"] = (
                reference_before.st_size, reference_before.st_mtime_ns
            ) == (reference_after.st_size, reference_after.st_mtime_ns)
            if not checks["audio_reference_unchanged"]:
                errors.append("Audio reference changed during verification")
        if expect_alpha:
            alpha = report["alpha"]
            alpha["pixel_format_has_alpha"] = video.get("pix_fmt") in _alpha_formats()
            if not alpha["pixel_format_has_alpha"]:
                errors.append("Video pixel format has no alpha channel")
            elif actual_fps is None or actual_frames is None:
                errors.append("Cannot choose alpha frames without actual fps and frame count")
            else:
                for time in times:
                    frame = int(time * actual_fps)
                    if frame >= actual_frames:
                        errors.append(f"Alpha sample {float(time)}s falls outside the video")
                        continue
                    try:
                        sample = _alpha_sample(path, frame, video["width"], video["height"])
                        sample["requested_time_seconds"] = float(time)
                        alpha["samples"].append(sample)
                    except ValueError as error:
                        errors.append(f"Alpha sample failed: {error}")
                alpha["some_transparency"] = any(s["alpha_min_uint8"] < 255 for s in alpha["samples"])
                alpha["some_visible_opacity"] = any(s["alpha_max_uint8"] > 0 for s in alpha["samples"])
                if not alpha["some_transparency"] or not alpha["some_visible_opacity"]:
                    errors.append("Alpha samples must prove both some transparency and some visible opacity")
        after = path.stat()
        checks["source_unchanged"] = (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
        if not checks["source_unchanged"]:
            errors.append("Media changed during verification")
    except (OSError, ValueError, KeyError, StopIteration) as error:
        errors.append(f"Media check failed: {error}")
    report["ok"] = not errors
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media")
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--fps", required=True, help="Exact rational such as 30 or 30000/1001")
    parser.add_argument("--frames", type=int, required=True)
    parser.add_argument("--audio", choices=("none", "present"), required=True)
    parser.add_argument("--audio-reference", help="Approved same-length clip whose encoded audio must remain unchanged")
    parser.add_argument("--expect-alpha", action="store_true")
    parser.add_argument("--alpha-time", action="append", default=[], help="Seconds; repeat for each sample")
    parser.add_argument("--report", help="Save the receipt as JSON; stdout always receives JSON")
    args = parser.parse_args(argv)
    try:
        protected = [Path(args.media).expanduser().resolve()]
        if args.audio_reference:
            protected.append(Path(args.audio_reference).expanduser().resolve())
        if args.report:
            report_path = Path(args.report).expanduser().resolve()
            if any(report_path == path or
                   (report_path.exists() and path.exists() and report_path.samefile(path))
                   for path in protected):
                raise ValueError("Report must not overwrite the media or audio reference")
        result = check_render(args.media, width=args.width, height=args.height, fps=args.fps,
                              frames=args.frames, audio=args.audio, expect_alpha=args.expect_alpha,
                              alpha_times=args.alpha_time, audio_reference=args.audio_reference)
        output = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.report:
            Path(args.report).expanduser().write_text(output, encoding="utf-8")
        sys.stdout.write(output)
    except (OSError, ValueError, ZeroDivisionError) as error:
        parser.error(str(error))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
