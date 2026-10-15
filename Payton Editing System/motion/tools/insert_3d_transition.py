#!/usr/bin/env python3
"""
Insert Swivel Teaser into Video

Inserts a "swivel teaser" at a specified point in a video - a fast-forward
preview of video content starting at 1 minute with 3D rotation effects.
Original audio continues playing throughout.

See: directives/pan_3d_transition.md for effect parameters.

Usage:
    # Insert 5-second swivel teaser at 3 seconds (previews from 1:00 to end)
    python execution/insert_3d_transition.py input.mp4 output.mp4

    # Custom teaser content start point
    python execution/insert_3d_transition.py input.mp4 output.mp4 \
        --teaser-start 90  # Preview starts at 1:30

    # With background image
    python execution/insert_3d_transition.py input.mp4 output.mp4 \
        --bg-image Drop/background.png

Timeline Result:
    Video: [0-3s original] [3-8s swivel teaser showing content from 1:00 onwards] [8s+ original]
    Audio: [original audio plays continuously throughout]
"""

import subprocess
import tempfile
import os
import argparse
import json
import sys
from pathlib import Path

# Add execution directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the transition creator
from pan_3d_transition import create_transition, get_video_info
# Import hardware encoding functions
# Use a portable software encoder; no ASR/model import for a visual effect.
def get_cached_encoder_args(): return ['-c:v','libx264','-crf','18','-preset','medium']

DEFAULT_INSERT_AT = 3.0    # Insert transition at 3 seconds
DEFAULT_DURATION = 5.0     # 5-second transition
DEFAULT_TEASER_START = 60.0  # Teaser content starts at 1 minute
MAX_PLAYBACK_RATE = 100.0  # Cap teaser speed at 100x for readability


def composite_with_transition(
    input_path: str,
    output_path: str,
    insert_at: float = DEFAULT_INSERT_AT,
    duration: float = DEFAULT_DURATION,
    teaser_start: float = DEFAULT_TEASER_START,
    bg_color: str = "#2d3436",
    bg_image: str = None,
) -> None:
    """
    Insert a swivel teaser into video while preserving original audio.

    The swivel teaser shows video content from teaser_start to end,
    compressed into the specified duration with 3D rotation effects.

    Args:
        input_path: Source video file
        output_path: Output video file
        insert_at: Where to insert teaser in timeline (seconds)
        duration: Teaser duration (seconds)
        teaser_start: Where to start sourcing teaser content (seconds, default 60)
        bg_color: Background color for teaser
        bg_image: Optional background image for teaser
    """
    if Path(output_path).exists(): raise FileExistsError(output_path)
    # Get video info
    info = get_video_info(input_path)
    total_duration = info["duration"]

    # Validate teaser_start
    if teaser_start >= total_duration:
        raise ValueError(f"Teaser start ({teaser_start}s) must be less than video duration ({total_duration}s)")

    # Calculate content to preview (from teaser_start to end)
    # Cap playback rate at MAX_PLAYBACK_RATE for readability
    available_content = total_duration - teaser_start
    uncapped_rate = available_content / duration

    if uncapped_rate > MAX_PLAYBACK_RATE:
        # Cap at max speed, take only as much content as fits
        playback_rate = MAX_PLAYBACK_RATE
        teaser_content = duration * MAX_PLAYBACK_RATE  # e.g., 5s × 100x = 500s of content
        print(f"   ⚠️  Capping speed at {MAX_PLAYBACK_RATE}x (would have been {uncapped_rate:.1f}x)")
    else:
        playback_rate = uncapped_rate
        teaser_content = available_content

    print(f"🎬 Insert Swivel Teaser")
    print(f"   Input: {input_path}")
    print(f"   Insert at: {insert_at}s")
    print(f"   Teaser duration: {duration}s")
    print(f"   Teaser content: {teaser_start}s → {total_duration:.1f}s ({teaser_content:.1f}s at {playback_rate:.1f}x speed)")
    print()

    if insert_at + duration > total_duration:
        raise ValueError(f"Insert point + duration ({insert_at + duration}s) exceeds video duration ({total_duration}s)")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Generate the swivel teaser (content from teaser_start to end)
        transition_path = os.path.join(tmpdir, "transition.mp4")
        print(f"📐 Generating swivel teaser...")

        create_transition(
            input_path=input_path,
            output_path=transition_path,
            start=teaser_start,  # Start sourcing from teaser_start (default 60s)
            source_duration=teaser_content,  # Content from teaser_start to end
            output_duration=duration,
            playback_rate=playback_rate,  # Calculated to fit all content
            bg_color=bg_color,
            bg_image=bg_image,
        )

        # NEW APPROACH: Keep audio attached to video segments to prevent drift
        # Each segment has its own paired audio, eliminating sync issues
        print(f"\n✂️  Extracting segments (keeping audio paired with video)...")

        # Get encoder args (hardware if available) - only for transition
        encoder_args = get_cached_encoder_args()

        # Segment 1: 0 to insert_at WITH AUDIO (stream copy both)
        seg1_path = os.path.join(tmpdir, "seg1.mp4")
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-t", str(insert_at),
            "-c:v", "copy",  # Stream copy video
            "-c:a", "copy",  # Stream copy audio
            "-loglevel", "error",
            seg1_path
        ]
        subprocess.run(cmd, check=True)
        print(f"   Segment 1: 0s - {insert_at}s (stream copy, with audio)")

        # Segment 2: Transition video + matching audio from original
        # First, extract the audio for the transition period
        seg2_audio_path = os.path.join(tmpdir, "seg2_audio.aac")
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-ss", str(insert_at),
            "-t", str(duration),
            "-vn", "-c:a", "copy",  # Stream copy audio
            "-loglevel", "error",
            seg2_audio_path
        ]
        subprocess.run(cmd, check=True)

        # Now merge transition video with the extracted audio
        seg2_path = os.path.join(tmpdir, "seg2.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-i", transition_path,
            "-i", seg2_audio_path,
            "-map", "0:v",  # Video from transition
            "-map", "1:a",  # Audio from original
        ] + encoder_args + [
            "-c:a", "copy",  # Stream copy audio
            "-shortest",
            "-loglevel", "error",
            seg2_path
        ]
        subprocess.run(cmd, check=True)
        print(f"   Segment 2: transition ({duration}s) (re-encoded video, original audio)")

        # Segment 3: insert_at + duration to end WITH AUDIO (stream copy both)
        seg3_path = os.path.join(tmpdir, "seg3.mp4")
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-ss", str(insert_at + duration),
            "-c:v", "copy",  # Stream copy video
            "-c:a", "copy",  # Stream copy audio
            "-avoid_negative_ts", "make_zero",
            "-loglevel", "error",
            seg3_path
        ]
        subprocess.run(cmd, check=True)
        remaining = total_duration - (insert_at + duration)
        print(f"   Segment 3: {insert_at + duration}s - end ({remaining:.1f}s) (stream copy, with audio)")

        # Step 3: Concatenate all segments (each has paired audio+video)
        print(f"\n🔗 Concatenating segments...")

        concat_list = os.path.join(tmpdir, "concat.txt")
        with open(concat_list, "w") as f:
            f.write(f"file '{seg1_path}'\n")
            f.write(f"file '{seg2_path}'\n")
            f.write(f"file '{seg3_path}'\n")

        concat_raw = os.path.join(tmpdir, "concat_raw.mp4")
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            "-loglevel", "error",
            concat_raw
        ]
        subprocess.run(cmd, check=True)

        # Fix A/V sync: measure video encoder priming delay and delay audio to match
        vid_start = 0.0
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "stream=start_time", "-of", "csv=p=0", concat_raw],
                capture_output=True, text=True
            )
            vid_start = float(result.stdout.strip())
        except (ValueError, AttributeError):
            pass

        delay_ms = max(0, round(vid_start * 1000))
        if delay_ms > 0:
            print(f"🔧 Fixing A/V sync (adelay={delay_ms}ms)...")
            cmd = [
                "ffmpeg", "-y", "-i", concat_raw,
                "-c:v", "copy",
                "-af", f"adelay={delay_ms}|{delay_ms}",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-loglevel", "error",
                output_path
            ]
            subprocess.run(cmd, check=True)
        else:
            import shutil
            shutil.copy2(concat_raw, output_path)

    print(f"\n✅ Output saved to {output_path}")
    print(f"   Timeline: [0-{insert_at}s] [swivel teaser {duration}s] [{insert_at+duration}s-end]")
    print(f"   Teaser shows: {teaser_start}s → {total_duration:.1f}s ({teaser_content:.1f}s at {playback_rate:.1f}x speed)")
    print(f"   Audio: Original audio preserved throughout")


def main():
    parser = argparse.ArgumentParser(
        description="Insert 3D transition into video while preserving audio"
    )
    parser.add_argument("input", help="Input video file")
    parser.add_argument("output", help="Output video file")
    parser.add_argument("--insert-at", type=float, default=DEFAULT_INSERT_AT,
                        help=f"Insert point in seconds (default: {DEFAULT_INSERT_AT})")
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION,
                        help=f"Transition duration in seconds (default: {DEFAULT_DURATION})")
    parser.add_argument("--teaser-start", type=float, default=DEFAULT_TEASER_START,
                        help=f"Where to start sourcing teaser content (default: {DEFAULT_TEASER_START}s = 1 minute)")
    parser.add_argument("--bg-color", type=str, default="#2d3436",
                        help="Background color (hex, default: #2d3436)")
    parser.add_argument("--bg-image", type=str, default=None,
                        help="Background image path (overrides --bg-color)")

    args = parser.parse_args()

    composite_with_transition(
        input_path=args.input,
        output_path=args.output,
        insert_at=args.insert_at,
        duration=args.duration,
        teaser_start=args.teaser_start,
        bg_color=args.bg_color,
        bg_image=args.bg_image,
    )


if __name__ == "__main__":
    main()
