#!/usr/bin/env python3
"""
RSVP Captions — Rapid Serial Visual Presentation word-by-word captions.

Takes verified word JSON or Auphonic word-timed HTML and overlays one-word-at-a-time
captions onto a video. Check actual wording and timing against the recording. Each word has a red "focal letter"
(the Optimal Recognition Point) while the word itself is centered on screen.

The strict route retains the supplied word intervals. Their accuracy depends on
the transcript; this renderer cannot verify speech. Segment interpolation is
available only as an explicitly approximate preview.

The optional red focal letter uses this fixed presentation table; no reading-
speed or comprehension benefit is claimed:
    Word len:  1  2  3  4  5  6  7  8  9 10 11 12 13 14+
    ORP idx:   0  0  1  1  1  1  2  2  2  2  3  3  3  4

Usage:
    python3 tools/rsvp_captions.py project/video.mp4 project/transcript.html project/video_rsvp.mp4
    python3 tools/rsvp_captions.py project/video.mp4 project/transcript.html project/out.mp4 --dry-run
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ============================================================
# ORP Lookup Table
# ============================================================

ORP_TABLE = [0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4]


def compute_orp(word: str) -> int:
    """Return the 0-based index of the Optimal Recognition Point letter."""
    clean = re.sub(r"[^\w']", "", word)
    length = len(clean)
    if length == 0:
        return 0
    if length <= len(ORP_TABLE):
        orp_in_clean = ORP_TABLE[length - 1]
    else:
        orp_in_clean = 4

    orp_in_clean = min(orp_in_clean, length - 1)

    clean_idx = 0
    for i, ch in enumerate(word):
        if re.match(r"[\w']", ch):
            if clean_idx == orp_in_clean:
                return i
            clean_idx += 1
    return 0


# ============================================================
# Transcript Parsing — Word-Level Timing
# ============================================================

def _split_hyphenated_words(words: list[dict]) -> list[dict]:
    """
    Split hyphenated compound words (e.g. 'Notre-Dame-des-Péries') into
    separate display words, distributing the original timing evenly.

    Each part gets its own ORP and timing slice.
    """
    result = []
    for w in words:
        text = w["word"]
        # Only split on hyphens if the word has multiple parts
        # (not for single hyphens used as dashes)
        parts = text.split("-")
        if len(parts) > 1 and all(len(p) > 0 for p in parts):
            duration = w["end"] - w["start"]
            part_duration = duration / len(parts)
            for j, part in enumerate(parts):
                part_start = w["start"] + j * part_duration
                part_end = part_start + part_duration
                result.append({
                    "word": part,
                    "start": round(part_start, 4),
                    "end": round(part_end, 4),
                    "orp_index": compute_orp(part),
                })
        else:
            result.append(w)
    return result


def parse_html_words(path: str, allow_estimated=False) -> list[dict]:
    """
    Parse Auphonic HTML transcript and extract per-word timestamps.

    The Auphonic transcript embeds a JSON structure with word-level timing:
    timestamps: [[word, start, end, confidence], ...]

    Returns a list of {word, start, end, orp_index} dicts.
    """
    if not allow_estimated:
        from video_word_timing import load_word_timing
        return [dict(w, orp_index=compute_orp(w["word"])) for w in load_word_timing(path)["words"]]
    from bs4 import BeautifulSoup

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Strategy 0: Auphonic embedded JSON with word-level timestamps
    json_script = soup.find("script", {"type": "application/json"})
    if json_script and json_script.string:
        try:
            data = json.loads(json_script.string)
            versions = data.get("transcript_versions", [])
            if versions:
                transcript = versions[0].get("transcript", {})
                results = transcript.get("results", {})
                if results:
                    words = []
                    sorted_keys = sorted(results.keys(), key=lambda k: int(k))
                    for k in sorted_keys:
                        seg = results[k]
                        timestamps = seg.get("timestamps", [])
                        if timestamps:
                            for ts in timestamps:
                                w_text = ts[0]
                                w_start = float(ts[1])
                                w_end = float(ts[2])
                                if w_text.strip():
                                    words.append({
                                        "word": w_text,
                                        "start": round(w_start, 4),
                                        "end": round(w_end, 4),
                                        "orp_index": compute_orp(w_text),
                                    })
                    if words:
                        # Split hyphenated compound words into parts
                        words = _split_hyphenated_words(words) if allow_estimated else words
                        # Make each word stay visible until the next word starts
                        for i in range(len(words) - 1):
                            words[i]["end"] = words[i + 1]["start"]
                        print(f"   Parsed {len(words)} words with per-word timestamps")
                        return words
        except (json.JSONDecodeError, KeyError, ValueError, IndexError):
            pass

    # Fallback: segment-level parsing with even distribution
    if not allow_estimated:
        raise ValueError("No real word timings found. Supply word JSON/HTML, or explicitly allow a visibly approximate preview.")
    return _parse_html_segments_to_words(path, soup)


def _parse_html_segments_to_words(path: str, soup) -> list[dict]:
    """Fallback: parse segment-level timestamps and distribute evenly."""
    segments = []

    # Try embedded JSON segment-level
    json_script = soup.find("script", {"type": "application/json"})
    if json_script and json_script.string:
        try:
            data = json.loads(json_script.string)
            versions = data.get("transcript_versions", [])
            if versions:
                transcript = versions[0].get("transcript", {})
                rate = transcript.get("rate", 44100)
                results = transcript.get("results", {})
                if results:
                    sorted_keys = sorted(results.keys(), key=lambda k: int(k))
                    for k in sorted_keys:
                        seg = results[k]
                        start = int(k) / rate
                        text = seg.get("text", "").strip()
                        if text:
                            segments.append({"start": start, "end": start + 5.0, "text": text})
                    if segments:
                        for i in range(len(segments) - 1):
                            segments[i]["end"] = segments[i + 1]["start"]
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

    if not segments:
        # Try span data-start
        spans = soup.find_all("span", attrs={"data-start": True})
        for span in spans:
            try:
                start = float(span["data-start"])
                end = float(span.get("data-end", start + 5.0))
                text = span.get_text(strip=True)
                if text:
                    segments.append({"start": start, "end": end, "text": text})
            except (ValueError, KeyError):
                continue

    if not segments:
        print("Could not parse transcript.")
        sys.exit(1)

    # Distribute words evenly within each segment
    words = []
    for seg in segments:
        text = seg["text"].strip()
        if not text:
            continue
        word_list = text.split()
        n = len(word_list)
        if n == 0:
            continue
        seg_duration = seg["end"] - seg["start"]
        word_duration = seg_duration / n
        for i, w in enumerate(word_list):
            word_start = seg["start"] + i * word_duration
            word_end = word_start + word_duration
            words.append({
                "word": w,
                "start": round(word_start, 4),
                "end": round(word_end, 4),
                "orp_index": compute_orp(w),
            })

    print(f"   Parsed {len(words)} words (segment-level fallback, evenly distributed)")
    return words


def parse_vtt_words(path: str) -> list[dict]:
    """Parse VTT and distribute words evenly within each caption."""
    try:
        import webvtt
    except ImportError:
        print("webvtt-py not installed. Run: pip install webvtt-py")
        sys.exit(1)

    words = []
    for caption in webvtt.read(path):
        text = re.sub(r"<[^>]+>", "", caption.text).strip()
        if not text:
            continue
        parts = caption.start.split(":")
        if len(parts) == 3:
            start_sec = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            start_sec = int(parts[0]) * 60 + float(parts[1])
        else:
            start_sec = float(parts[0])

        parts_end = caption.end.split(":")
        if len(parts_end) == 3:
            end_sec = int(parts_end[0]) * 3600 + int(parts_end[1]) * 60 + float(parts_end[2])
        elif len(parts_end) == 2:
            end_sec = int(parts_end[0]) * 60 + float(parts_end[1])
        else:
            end_sec = float(parts_end[0])

        word_list = text.split()
        n = len(word_list)
        if n == 0:
            continue
        dur = (end_sec - start_sec) / n
        for i, w in enumerate(word_list):
            ws = start_sec + i * dur
            we = ws + dur
            words.append({
                "word": w,
                "start": round(ws, 4),
                "end": round(we, 4),
                "orp_index": compute_orp(w),
            })

    return words


def parse_transcript_words(path: str, allow_estimated=False) -> list[dict]:
    """Auto-detect format and parse transcript into per-word timing."""
    ext = Path(path).suffix.lower()
    if not allow_estimated and ext in (".json", ".html", ".htm"):
        from video_word_timing import load_word_timing
        return [dict(w, orp_index=compute_orp(w["word"])) for w in load_word_timing(path)["words"]]
    if ext == ".json":
        data = json.loads(Path(path).read_text())
        words = data if isinstance(data, list) else data.get("words", [])
        if not words:
            raise ValueError("Word JSON contains no words")
        import math
        previous = -1.0
        result = []
        for row in words:
            text = str(row.get("word", row.get("text", ""))).strip()
            start, end = float(row["start"]), float(row["end"])
            if not text or not all(math.isfinite(v) for v in (start,end)) or start < 0 or end <= start or start < previous:
                raise ValueError("Invalid or unordered word interval")
            previous = start
            result.append({"word":text,"start":start,"end":end,"orp_index":compute_orp(text)})
        return result
    if ext == ".vtt":
        if not allow_estimated:
            raise ValueError("VTT segment timing is not word timing; use word JSON or explicitly allow an approximate preview")
        return parse_vtt_words(path)
    elif ext in (".html", ".htm"):
        return parse_html_words(path, allow_estimated=allow_estimated)
    else:
        print(f"Unsupported transcript format: {ext}")
        sys.exit(1)


# ============================================================
# Video Info
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

    r_frame_rate = video_stream.get("r_frame_rate", "30/1")
    num, den = r_frame_rate.split("/")
    fps = round(int(num) / int(den))

    return {"width": width, "height": height, "duration": duration, "fps": fps}


# ============================================================
# Rendering — PIL-based word image generation
# ============================================================

FONT_PATHS = [
    "/Library/Fonts/Palatino.ttc",
    "/System/Library/Fonts/Times.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
]

RED_COLOR = (210, 96, 96, 255)      # #D46060 — pastel red, slightly more saturated
WHITE_COLOR = (255, 255, 255, 255)
STROKE_COLOR = (0, 0, 0, 255)
SHADOW_COLOR = (0, 0, 0, 180)       # Shadow base color (blurred)


def find_font(font_size: int) -> ImageFont.FreeTypeFont:
    """Find and load a serif font."""
    for fp in FONT_PATHS:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, font_size)
            except Exception:
                continue
    return ImageFont.load_default()


def render_word_image(
    word: str,
    orp_index: int,
    frame_width: int,
    frame_height: int,
    font: ImageFont.FreeTypeFont,
    y_center: int,
    stroke_width: int = 5,
    shadow_offset: int = 10,
    shadow_blur: int = 6,
    background: bool = False,
) -> Image.Image:
    """
    Render a single word as a transparent PNG at full frame size.

    The word is horizontally centered on the frame. The ORP letter is
    colored red. Strong black stroke + blurred drop shadow for legibility.
    Optionally draws a semi-transparent rounded rectangle background.
    """
    if not word:
        return Image.new("RGBA", (frame_width, frame_height), (0, 0, 0, 0))

    orp_index = min(orp_index, len(word) - 1)

    # Measure each character's width
    char_widths = []
    for ch in word:
        bbox = font.getbbox(ch)
        char_widths.append(bbox[2] - bbox[0])

    # Pin the ORP letter's center to a fixed X position (slightly left of
    # frame center). This is the RSVP technique: your eye stays locked on
    # one fixed point, and words shuffle around it. The anchor is at ~45%
    # of frame width — left enough that the ORP (which is ~25-35% into the
    # word) makes the overall word feel roughly centered.
    anchor_x = frame_width * 0.45
    orp_left = sum(char_widths[:orp_index])
    orp_center_from_start = orp_left + char_widths[orp_index] / 2
    x_offset = anchor_x - orp_center_from_start

    # Vertical centering
    ascent, descent = font.getmetrics()
    text_y = y_center - ascent // 2

    total_text_width = sum(char_widths)

    # --- Shadow layer (rendered separately, then blurred) ---
    shadow_layer = Image.new("RGBA", (frame_width, frame_height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    sx = x_offset + shadow_offset
    for i, ch in enumerate(word):
        shadow_draw.text(
            (sx, text_y + shadow_offset),
            ch, font=font, fill=SHADOW_COLOR,
        )
        sx += char_widths[i]
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=shadow_blur))

    # --- Main layer (stroke + text) ---
    main_layer = Image.new("RGBA", (frame_width, frame_height), (0, 0, 0, 0))
    main_draw = ImageDraw.Draw(main_layer)
    current_x = x_offset
    for i, ch in enumerate(word):
        color = RED_COLOR if i == orp_index else WHITE_COLOR
        main_draw.text(
            (current_x, text_y), ch, font=font, fill=color,
            stroke_width=stroke_width, stroke_fill=STROKE_COLOR,
        )
        current_x += char_widths[i]

    # --- Compose: optional background → shadow → text ---
    img = Image.new("RGBA", (frame_width, frame_height), (0, 0, 0, 0))

    if background:
        bg_draw = ImageDraw.Draw(img)
        pad_h = int(ascent * 0.35)
        pad_w = int(ascent * 0.5)
        corner_radius = max(8, int(ascent * 0.15))
        bg_x0 = int(x_offset - pad_w)
        bg_y0 = int(text_y - pad_h)
        bg_x1 = int(x_offset + total_text_width + pad_w)
        bg_y1 = int(text_y + ascent + descent + pad_h * 0.4)
        bg_draw.rounded_rectangle(
            [bg_x0, bg_y0, bg_x1, bg_y1],
            radius=corner_radius,
            fill=(0, 0, 0, 200),  # ~78% opacity
        )

    img = Image.alpha_composite(img, shadow_layer)
    img = Image.alpha_composite(img, main_layer)

    return img


# ============================================================
# Main Pipeline
# ============================================================

def render_caption_frames(
    words: list[dict],
    frame_width: int,
    frame_height: int,
    font_size: int,
    y_percent: float,
    stroke_width: int,
    shadow_offset: int,
    shadow_blur: int,
    background: bool,
    output_dir: str,
) -> int:
    """Render all RSVP caption words as transparent PNG images (deduplicated)."""
    font = find_font(font_size)
    y_center = int(frame_height * y_percent)

    print(f"   Rendering word images...")

    word_cache = {}
    unique_count = 0

    for w in words:
        key = (w["word"], w["orp_index"])
        if key not in word_cache:
            img = render_word_image(
                w["word"], w["orp_index"],
                frame_width, frame_height,
                font, y_center,
                stroke_width, shadow_offset,
                shadow_blur, background,
            )
            fname = f"word_{unique_count:05d}.png"
            img.save(os.path.join(output_dir, fname), "PNG")
            word_cache[key] = fname
            unique_count += 1

    print(f"   {unique_count} unique word images ({len(words)} total words)")

    for w in words:
        key = (w["word"], w["orp_index"])
        w["image_file"] = word_cache[key]

    return unique_count


def overlay_rsvp_on_video(
    video_path: str,
    words: list[dict],
    output_path: str,
    images_dir: str,
    chunk_size: int = 50,
    allow_estimated_timing: bool = False,
) -> None:
    """Overlay RSVP word images onto video using FFmpeg filter_complex."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if Path(output_path).exists() or Path(output_path).is_symlink() or Path(output_path).resolve() == Path(video_path).resolve():
        raise FileExistsError("Use a fresh caption output filename")
    total_words = len(words)
    if total_words == 0:
        print("   No words to overlay.")
        return

    chunks = []
    for i in range(0, total_words, chunk_size):
        chunks.append(words[i:i + chunk_size])

    current_input = video_path
    total_passes = len(chunks)
    pass_files = []

    try:
        for pi, chunk in enumerate(chunks):
            is_last = pi == len(chunks) - 1
            if is_last:
                chunk_output = output_path
            else:
                stem = Path(output_path).stem
                ext = Path(output_path).suffix
                chunk_output = str(Path(images_dir) / f"{stem}_rsvp_pass{pi}{ext}")
                pass_files.append(chunk_output)

            pass_label = f"pass {pi+1}/{total_passes}" if total_passes > 1 else "encoding"
            print(f"\n   Running {pass_label} ({len(chunk)} words)...")

            unique_images = {}
            for w in chunk:
                img_file = w["image_file"]
                if img_file not in unique_images:
                    unique_images[img_file] = len(unique_images)

            cmd = ["ffmpeg", "-y", "-i", current_input]

            img_index_map = {}
            input_idx = 1
            for img_file, _ in sorted(unique_images.items(), key=lambda x: x[1]):
                cmd.extend(["-i", os.path.join(images_dir, img_file)])
                img_index_map[img_file] = input_idx
                input_idx += 1

            filter_parts = []
            current_base = "[0:v]"

            for i, w in enumerate(chunk):
                inp = img_index_map[w["image_file"]]
                start = w["start"]
                end = w["end"]
                out_label = f"[v{i}]" if i < len(chunk) - 1 else "[vout]"

                filter_parts.append(
                    f"{current_base}[{inp}:v]"
                    f"overlay=0:0:enable='between(t,{start:.9g},{end:.9g})'"
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

            print(f"   {pass_label} complete")

            if not is_last:
                current_input = chunk_output
    finally:
        for pf in pass_files:
            if os.path.exists(pf) and pf != output_path:
                os.remove(pf)


# ============================================================
# Main
# ============================================================

def rsvp_captions(
    video_path: str,
    transcript_path: str,
    output_path: str,
    font_size: int = 0,
    y_percent: float = 0.58,
    stroke_width: int = 0,
    shadow_offset: int = 0,
    shadow_blur: int = 0,
    background: bool = False,
    dry_run: bool = False,
    chunk_size: int = 50,
    allow_estimated_timing: bool = False,
) -> None:
    """Main pipeline: parse transcript, render words, overlay onto video."""
    if Path(output_path).resolve() == Path(video_path).resolve() or Path(output_path).exists():
        raise FileExistsError("Use a new output file; originals and prior exports are preserved")
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    if not os.path.exists(transcript_path):
        raise FileNotFoundError(f"Transcript not found: {transcript_path}")

    print(f"\n   RSVP Captions")
    print(f"   Video: {video_path}")
    print(f"   Transcript: {transcript_path}")
    print(f"   Output: {output_path}")

    info = get_video_info(video_path)
    width, height = info["width"], info["height"]
    fps = info["fps"]
    print(f"   Resolution: {width}x{height} @ {fps}fps")
    print(f"   Duration: {info['duration']:.1f}s")

    # Auto-scale: ~5% of height (smaller than before)
    if font_size == 0:
        font_size = max(48, int(height * 0.05))
    if stroke_width == 0:
        stroke_width = max(3, font_size // 40)
    if shadow_offset == 0:
        shadow_offset = max(5, font_size // 20)
    if shadow_blur == 0:
        shadow_blur = max(4, font_size // 30)

    print(f"   Font size: {font_size}px")
    print(f"   Stroke: {stroke_width}px, Shadow offset: {shadow_offset}px, Shadow blur: {shadow_blur}px")
    print(f"   Y position: {y_percent*100:.0f}% from top")
    if background:
        print(f"   Background: enabled (rounded pill, ~78% opacity)")

    # Parse transcript with word-level timing
    print(f"\n   Parsing transcript...")
    words = parse_transcript_words(transcript_path, allow_estimated=allow_estimated_timing)
    print(f"   {len(words)} words total")

    if not words:
        print("   No words found in transcript.")
        return

    # Show sample
    print(f"\n   Sample (first 15 words):")
    print(f"   {'Word':<20} {'Start':>7} {'End':>7} {'Dur':>6} {'ORP':>3} {'Letter':>6}")
    print(f"   {'─'*20} {'─'*7} {'─'*7} {'─'*6} {'─'*3} {'─'*6}")
    for w in words[:15]:
        dur_ms = (w["end"] - w["start"]) * 1000
        orp_ch = w["word"][w["orp_index"]] if w["orp_index"] < len(w["word"]) else "?"
        print(f"   {w['word']:<20} {w['start']:>7.2f} {w['end']:>7.2f} {dur_ms:>5.0f}ms {w['orp_index']:>3} {orp_ch:>6}")

    durations = [w["end"] - w["start"] for w in words]
    avg_dur = sum(durations) / len(durations) if durations else 0
    avg_wpm = 60.0 / avg_dur if avg_dur > 0 else 0
    print(f"\n   Avg word duration: {avg_dur*1000:.0f}ms ({avg_wpm:.0f} WPM effective)")

    if dry_run:
        print(f"\n   DRY RUN — no encoding performed.")
        return

    tmpdir = tempfile.mkdtemp(prefix="rsvp_")
    try:
        render_caption_frames(
            words, width, height,
            font_size, y_percent,
            stroke_width, shadow_offset,
            shadow_blur, background,
            tmpdir,
        )

        print(f"\n   Overlaying {len(words)} words onto video...")
        overlay_rsvp_on_video(
            video_path, words, output_path,
            tmpdir, chunk_size,
        )

        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n   Output saved: {output_path} ({file_size:.1f} MB)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        description="RSVP word-by-word captions with ORP focal letter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 tools/rsvp_captions.py project/video.mp4 project/transcript.html project/video_rsvp.mp4
    python3 tools/rsvp_captions.py project/video.mp4 project/transcript.html project/out.mp4 --dry-run
"""
    )

    parser.add_argument("video", help="Input video file")
    parser.add_argument("transcript", help="Transcript file (HTML or VTT)")
    parser.add_argument("output", help="Output video file")
    parser.add_argument("--font-size", type=int, default=0,
                        help="Font size in pixels (default: auto ~5%% of height)")
    parser.add_argument("--y-percent", type=float, default=0.58,
                        help="Vertical position as fraction from top (default: 0.58)")
    parser.add_argument("--stroke-width", type=int, default=0,
                        help="Outline stroke width (default: auto-scale)")
    parser.add_argument("--shadow-offset", type=int, default=0,
                        help="Drop shadow offset pixels (default: auto-scale)")
    parser.add_argument("--shadow-blur", type=int, default=0,
                        help="Gaussian blur radius for drop shadow (default: auto-scale)")
    parser.add_argument("--background", action="store_true",
                        help="Add semi-transparent rounded rectangle behind each word")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show word list without encoding")
    parser.add_argument("--chunk-size", type=int, default=50,
                        help="Words per FFmpeg overlay pass (default: 50)")

    parser.add_argument("--allow-estimated-timing", action="store_true", help="Approximate preview only: distribute subtitle words evenly; this is not actual word alignment")
    args = parser.parse_args()

    rsvp_captions(
        video_path=args.video,
        transcript_path=args.transcript,
        output_path=args.output,
        font_size=args.font_size,
        y_percent=args.y_percent,
        stroke_width=args.stroke_width,
        shadow_offset=args.shadow_offset,
        shadow_blur=args.shadow_blur,
        background=args.background,
        dry_run=args.dry_run,
        chunk_size=args.chunk_size,
        allow_estimated_timing=args.allow_estimated_timing,
    )


if __name__ == "__main__":
    main()
