#!/usr/bin/env python3
"""
Auphonic Audio Enhancement

Send audio through Auphonic for professional audio processing, then
re-mux enhanced audio with the original video. Also downloads the HTML
transcript if speech recognition is included in the preset.
When Auphonic returns chapter marks, the script also saves machine-readable
JSON and a paste-ready YouTube chapter list.

Usage:
    # Using preset name (input must be a video file)
    python3 tools/auphonic_enhance.py project/video_final.mp4 project/video_auphonic.mp4 \
        --preset "voice cleaner"

    # Using preset UUID directly
    python3 tools/auphonic_enhance.py project/video_final.mp4 project/video_auphonic.mp4 \
        --preset-uuid YOUR_PRESET_UUID

    # List available presets
    python3 tools/auphonic_enhance.py --list-presets
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
AUPHONIC_API_KEY = os.getenv("AUPHONIC_API_KEY")
AUPHONIC_API_BASE = "https://auphonic.com/api"
DEFAULT_POLL_INTERVAL = 10  # seconds
DEFAULT_TIMEOUT = 1800  # 30 minutes max

# Preset name -> UUID mapping file
PRESETS_CONFIG_PATH = Path(os.environ.get("VIBE_AUPHONIC_CACHE", str(Path.home() / ".cache" / "vibe-editors" / "auphonic-presets.json")))


def load_presets() -> dict[str, str]:
    """Load preset name -> UUID mapping from config file."""
    if PRESETS_CONFIG_PATH.exists():
        with open(PRESETS_CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_presets(presets: dict[str, str]) -> None:
    """Save preset mapping to config file."""
    PRESETS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PRESETS_CONFIG_PATH, "w") as f:
        json.dump(presets, f, indent=2)


def fetch_presets_from_api() -> list[dict]:
    """Fetch all presets from Auphonic API."""
    headers = {"Authorization": f"Bearer {AUPHONIC_API_KEY}"}
    resp = requests.get(f"{AUPHONIC_API_BASE}/presets.json", headers=headers)
    resp.raise_for_status()
    return resp.json().get("data", [])


def resolve_preset_uuid(preset_name: str) -> str:
    """
    Resolve preset name to UUID.

    First checks local config, then fetches from API if not found.
    Updates local config with new mappings.
    """
    presets = load_presets()

    # Normalize name for matching
    normalized = preset_name.lower().strip()

    # Check local cache first (exact match)
    for name, uuid in presets.items():
        if name.lower() == normalized:
            return uuid

    # Fetch from API
    print(f"   Fetching presets from Auphonic API...")
    api_presets = fetch_presets_from_api()

    # Update local cache with all presets
    for preset in api_presets:
        name = preset.get("preset_name", "")
        uuid = preset.get("uuid", "")
        if name and uuid:
            presets[name] = uuid

    # Save updated cache
    save_presets(presets)

    # Check for exact match
    for preset in api_presets:
        name = preset.get("preset_name", "")
        uuid = preset.get("uuid", "")
        if name.lower() == normalized:
            return uuid

    raise ValueError(f"Preset not found: {preset_name}")


def extract_audio(video_path: str, audio_path: str) -> None:
    """Extract audio from video as WAV for Auphonic processing."""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn",  # No video
        "-acodec", "pcm_s16le",  # WAV format
        "-ar", "48000",  # 48kHz sample rate
        "-ac", "2",  # Stereo
        "-loglevel", "error",
        audio_path
    ]
    print(f"   Extracting audio from video...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr}")


def create_auphonic_production(preset_uuid: str, title: str = "Audio Enhancement") -> str:
    """Create Auphonic production and return production UUID."""
    headers = {"Authorization": f"Bearer {AUPHONIC_API_KEY}"}

    payload = {
        "preset": preset_uuid,
        "metadata": {"title": title},
        "output_files": [
            {"format": "wav"},
            {"format": "transcript", "ending": "html"},
        ],
    }

    resp = requests.post(
        f"{AUPHONIC_API_BASE}/productions.json",
        headers=headers,
        json=payload
    )
    resp.raise_for_status()
    return resp.json()["data"]["uuid"]


def upload_audio_to_production(production_uuid: str, audio_path: str) -> None:
    """Upload audio file to Auphonic production."""
    headers = {"Authorization": f"Bearer {AUPHONIC_API_KEY}"}

    print(f"   Uploading audio to Auphonic...")
    with open(audio_path, "rb") as f:
        resp = requests.post(
            f"{AUPHONIC_API_BASE}/production/{production_uuid}/upload.json",
            headers=headers,
            files={"input_file": f}
        )
    resp.raise_for_status()


def start_production(production_uuid: str) -> None:
    """Start Auphonic processing."""
    headers = {"Authorization": f"Bearer {AUPHONIC_API_KEY}"}

    print(f"   Starting Auphonic processing...")
    resp = requests.post(
        f"{AUPHONIC_API_BASE}/production/{production_uuid}/start.json",
        headers=headers
    )
    resp.raise_for_status()


def poll_for_completion(
    production_uuid: str,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    timeout: int = DEFAULT_TIMEOUT
) -> dict:
    """
    Poll Auphonic status until processing completes.

    Returns production data on success.
    Raises RuntimeError on failure or timeout.
    """
    headers = {"Authorization": f"Bearer {AUPHONIC_API_KEY}"}
    start_time = time.time()

    print(f"   Monitor at: https://auphonic.com/engine/status/{production_uuid}")

    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise RuntimeError(f"Auphonic processing timed out after {timeout}s")

        resp = requests.get(
            f"{AUPHONIC_API_BASE}/production/{production_uuid}.json",
            headers=headers
        )
        resp.raise_for_status()
        data = resp.json()["data"]

        status = data.get("status")
        status_string = data.get("status_string", "")

        # Current codes: 2=error, 3=done, 4=audio processing,
        # 5=audio encoding, 13=stopping, 14=speech recognition.
        if status == 3:  # Done
            print(f"   Processing complete! ({elapsed:.0f}s)")
            return data
        elif status == 2:
            error_msg = data.get("error_message") or "Unknown error"
            raise RuntimeError(f"Auphonic processing failed: {error_msg}")
        elif status == 13:
            raise RuntimeError("Auphonic production is stopping")
        else:
            print(f"   Status: {status_string} ({elapsed:.0f}s elapsed)")
            time.sleep(poll_interval)


def _find_output_file(production_data: dict, fmt: str, ending: str = None) -> "str | None":
    """Find a download URL in production output files by format and optional ending."""
    for output_file in production_data.get("output_files", []):
        file_fmt = output_file.get("format", "")
        file_ending = output_file.get("ending", "")
        if file_fmt == fmt:
            if ending is None or file_ending == ending:
                return output_file.get("download_url")
    return None


def _download_file(url: str, output_path: str, label: str = "file") -> bool:
    """Download a file from Auphonic. Returns True on success."""
    headers = {"Authorization": f"Bearer {AUPHONIC_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, stream=True, allow_redirects=True)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"   WARNING: Failed to download {label}: {e}")
        return False


def download_enhanced_audio(production_data: dict, output_path: str) -> None:
    """Download enhanced audio from Auphonic."""
    # Try WAV first, then MP3, then first available
    url = _find_output_file(production_data, "wav")
    if not url:
        url = _find_output_file(production_data, "mp3")
    if not url:
        output_files = production_data.get("output_files", [])
        for of in output_files:
            if of.get("format") not in ("transcript", "subtitle", "speech"):
                url = of.get("download_url")
                if url:
                    break

    if not url:
        raise RuntimeError("No audio download URL found in Auphonic production")

    print(f"   Downloading enhanced audio...")
    if not _download_file(url, output_path, "enhanced audio"):
        raise RuntimeError("Failed to download enhanced audio")


def download_transcript(production_data: dict, output_dir: str, stem: str) -> "str | None":
    """
    Download the HTML transcript from Auphonic if available.

    Returns the path to the downloaded transcript, or None if not available.
    """
    url = _find_output_file(production_data, "transcript", "html")
    if not url:
        url = _find_output_file(production_data, "transcript")
    if not url:
        print(f"   No transcript available (preset may not include speech recognition)")
        return None

    transcript_path = os.path.join(output_dir, f"{stem}.html")
    print(f"   Downloading transcript...")
    if _download_file(url, transcript_path, "transcript"):
        print(f"   Transcript saved: {transcript_path}")
        return transcript_path
    return None


def _format_youtube_timestamp(seconds: float) -> str:
    """Format seconds as a YouTube chapter timestamp."""
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds_part = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds_part:02d}"
    return f"{minutes:02d}:{seconds_part:02d}"


def save_chapters(production_data: dict, output_dir: str, stem: str) -> "dict | None":
    """Save Auphonic chapter marks for the social publishing workflow.

    Auphonic distinguishes input-relative and output-relative timestamps. The
    latter includes any intro or inserts, so it is the correct value for the
    finished video and for YouTube chapters.
    """
    raw_chapters = production_data.get("chapters") or []
    chapters = []
    for raw_chapter in raw_chapters:
        title = str(raw_chapter.get("title") or "").strip()
        seconds = raw_chapter.get("start_output_sec")
        if seconds is None:
            seconds = raw_chapter.get("start_sec")
        if not title or seconds is None:
            continue
        chapters.append(
            {
                "time": _format_youtube_timestamp(float(seconds)),
                "title": title,
                "start_output_seconds": float(seconds),
            }
        )
    if not chapters:
        print("   No chapter marks available (preset may not include Automatic Shownotes and Chapters)")
        return None
    if chapters[0]["start_output_seconds"] > 0:
        chapters[0]["original_start_output_seconds"] = chapters[0]["start_output_seconds"]
        chapters[0]["start_output_seconds"] = 0.0
        chapters[0]["time"] = "00:00"

    payload = {
        "schema_version": 1,
        "source": "auphonic",
        "production_uuid": production_data.get("uuid"),
        "chapters": chapters,
    }
    json_path = os.path.join(output_dir, f"{stem}_chapters.json")
    text_path = os.path.join(output_dir, f"{stem}_chapters.txt")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    with open(text_path, "w", encoding="utf-8") as handle:
        for chapter in chapters:
            handle.write(f"{chapter['time']} {chapter['title']}\n")
    print(f"   Chapters saved: {json_path}")
    print(f"   YouTube chapter list: {text_path}")
    return {"json": json_path, "text": text_path, "chapters": chapters}


def media_stream_duration(path: str, selector: str) -> float:
    """Read actual stream duration; never silently trim to conceal mismatch."""
    result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", selector,
        "-show_entries", "stream=duration", "-of", "json", path], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Cannot verify media duration before audio replacement")
    import math
    data = json.loads(result.stdout)
    duration = float(data["streams"][0]["duration"])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Invalid duration before audio replacement")
    return duration


def remux_video_with_audio(
    video_path: str,
    audio_path: str,
    output_path: str,
    timeout: int = 300,
    retries: int = 1,
) -> None:
    """Re-mux original video with enhanced audio.

    The ffmpeg stream-copy itself completes in seconds, but the mov->mp4 muxer
    has been observed (rarely, non-reproducibly) spinning at 100% CPU at
    end-of-file and never exiting -- a stalled process hung a batch for 8+ min
    on a 3.6-min clip after all media was already written. Guard against that
    with a ``timeout`` plus one automatic ``retries`` so a stall is killed and
    recovered in seconds instead of silently blocking the batch. ``-nostdin``
    keeps ffmpeg from waiting on inherited stdin under background execution.
    The portable route verifies durations and preserves the complete video stream.
    It does not use shortest-stream truncation to hide a mismatched audio result.
    """
    if Path(output_path).exists() or Path(output_path).is_symlink() or Path(output_path).resolve() in (Path(video_path).resolve(), Path(audio_path).resolve()):
        raise FileExistsError("Use a fresh remux output filename")
    video_seconds = media_stream_duration(video_path, "v:0")
    audio_seconds = media_stream_duration(audio_path, "a:0")
    if abs(video_seconds - audio_seconds) > 0.1:
        raise ValueError("Audio/video duration differs by more than 100 ms; investigate provider settings and alignment before remuxing")
    cmd = [
        "ffmpeg", "-n", "-nostdin",
        "-i", video_path,
        "-i", audio_path,
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "320k",
        "-loglevel", "error",
        output_path,
    ]
    print(f"   Re-muxing video with enhanced audio...")
    attempt = 0
    while True:
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            if os.path.exists(output_path):
                os.remove(output_path)
            if attempt < retries:
                attempt += 1
                print(
                    f"   Re-mux exceeded {timeout}s (muxer stall) -- killed, "
                    f"retrying ({attempt}/{retries})..."
                )
                continue
            raise RuntimeError(
                f"FFmpeg re-mux timed out after {timeout}s (muxer stall). "
                f"Input: {video_path}"
            )
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {result.stderr}")
        return


def enhance_video(
    input_path: str,
    output_path: str,
    preset_name: str = None,
    preset_uuid: str = None,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    timeout: int = DEFAULT_TIMEOUT,
) -> None:
    """
    Main function: Extract audio, enhance via Auphonic, re-mux with video,
    download transcript if available, and save Auphonic chapter marks.

    Either preset_name or preset_uuid must be provided.
    Input should be a video file.
    Output is the video with enhanced audio.
    Transcript and chapters (if available) are saved next to the output.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if Path(output_path).resolve() == Path(input_path).resolve() or Path(output_path).exists() or Path(output_path).is_symlink():
        raise FileExistsError("Use a fresh output filename before a provider call")
    output_parent = Path(output_path).parent
    output_stem = Path(output_path).stem
    for suffix in (".html", "_chapters.json", "_chapters.txt"):
        sidecar = output_parent / (output_stem + suffix)
        if sidecar.exists() or sidecar.is_symlink():
            raise FileExistsError(f"Use a fresh output stem; sidecar exists: {sidecar.name}")
    if not AUPHONIC_API_KEY:
        raise ValueError("AUPHONIC_API_KEY not set in .env")

    # Resolve preset
    if preset_uuid:
        final_uuid = preset_uuid
        print(f"   Using preset UUID: {final_uuid}")
    elif preset_name:
        final_uuid = resolve_preset_uuid(preset_name)
        print(f"   Resolved preset '{preset_name}' to UUID: {final_uuid}")
    else:
        raise ValueError("Either --preset or --preset-uuid must be provided")

    print(f"\n🎧 Auphonic Audio Enhancement")
    print(f"   Input: {input_path}")
    print(f"   Output: {output_path}")
    print()

    start_time = time.time()
    output_dir = str(Path(output_path).parent)
    stem = Path(output_path).stem
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Extract audio
        extracted_audio = os.path.join(tmpdir, "extracted.wav")
        extract_audio(input_path, extracted_audio)

        # Step 2: Create Auphonic production
        production_uuid = create_auphonic_production(final_uuid, title=f"Enhance: {stem}")
        print(f"   Created production: {production_uuid}")

        # Step 3: Upload audio
        upload_audio_to_production(production_uuid, extracted_audio)

        # Step 4: Start processing
        start_production(production_uuid)

        # Step 5: Poll for completion
        production_data = poll_for_completion(production_uuid, poll_interval, timeout)

        # Step 6: Download enhanced audio
        enhanced_audio = os.path.join(tmpdir, "enhanced.wav")
        download_enhanced_audio(production_data, enhanced_audio)

        # Step 7: Download transcript (if available)
        download_transcript(production_data, output_dir, stem)

        # Step 8: Save automatic chapter marks (if available)
        save_chapters(production_data, output_dir, stem)

        # Step 9: Re-mux video with enhanced audio
        remux_video_with_audio(input_path, enhanced_audio, output_path)

    elapsed = time.time() - start_time
    print()
    print(f"✅ Enhanced video saved to: {output_path}")
    print(f"   Total time: {elapsed:.0f}s")


def list_presets() -> None:
    """List all available Auphonic presets."""
    if not AUPHONIC_API_KEY:
        print("Error: AUPHONIC_API_KEY not set in .env")
        sys.exit(1)

    print("Fetching presets from Auphonic...")
    presets = fetch_presets_from_api()

    print(f"\nAvailable Auphonic Presets ({len(presets)}):")
    print("-" * 60)
    for preset in sorted(presets, key=lambda p: p.get("preset_name", "").lower()):
        name = preset.get("preset_name", "Unnamed")
        uuid = preset.get("uuid", "")
        print(f"  {name}")
        print(f"    UUID: {uuid}")

    # Update local cache
    local_presets = {p["preset_name"]: p["uuid"] for p in presets if p.get("preset_name") and p.get("uuid")}
    save_presets(local_presets)
    print(f"\nPresets cached to: {PRESETS_CONFIG_PATH}")


def main():
    parser = argparse.ArgumentParser(
        description="Enhance video audio via Auphonic (extracts audio, processes, re-muxes)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Enhance audio and re-mux back onto video
    python3 tools/auphonic_enhance.py project/video.mp4 project/video_auphonic.mp4 --preset "voice cleaner"

    # Transcript (if available) is saved next to output as [stem].html

    # List all available presets
    python3 tools/auphonic_enhance.py --list-presets
"""
    )

    parser.add_argument("input", nargs="?", help="Input video file")
    parser.add_argument("output", nargs="?", help="Output video file (with enhanced audio)")
    parser.add_argument("--preset", "-p", type=str,
                        help="Preset name (e.g., 'voice cleaner', 'automatic chapters')")
    parser.add_argument("--preset-uuid", type=str,
                        help="Preset UUID (use instead of --preset)")
    parser.add_argument("--list-presets", action="store_true",
                        help="List all available Auphonic presets")
    parser.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL,
                        help=f"Polling interval in seconds (default: {DEFAULT_POLL_INTERVAL})")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Max wait time in seconds (default: {DEFAULT_TIMEOUT})")

    args = parser.parse_args()

    if args.list_presets:
        list_presets()
        return

    if not args.input or not args.output:
        parser.error("Input and output paths are required (unless using --list-presets)")

    if not args.preset and not args.preset_uuid:
        parser.error("Either --preset or --preset-uuid is required")

    enhance_video(
        input_path=args.input,
        output_path=args.output,
        preset_name=args.preset,
        preset_uuid=args.preset_uuid,
        poll_interval=args.poll_interval,
        timeout=args.timeout,
    )


if __name__ == "__main__":
    main()
