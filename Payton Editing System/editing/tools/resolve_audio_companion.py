#!/usr/bin/env python3
"""Build local transcript and reviewed chapter files from Resolve timing data.

The input may be a final-timeline subtitle export or saved native Resolve
GetTranscription JSON with explicit FPS and source timecode origin. Chapter
titles and boundaries are accepted only from JSON reviewed by Codex or a user.
This tool does not transcribe audio or invent semantic chapters.

Example:
    python3 tools/resolve_audio_companion.py final-timeline.srt output/ \
        --duration 3725.4 --chapters reviewed-chapters.json
"""

import argparse
from html import escape, unescape
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
from fractions import Fraction


TIMING_RE = re.compile(
    r"^(?P<start>(?:\d+:)?\d{1,2}:\d{2}[,.]\d{3})\s*-->\s*"
    r"(?P<end>(?:\d+:)?\d{1,2}:\d{2}[,.]\d{3})(?:\s+.*)?$"
)


class _CueTextParser(HTMLParser):
    """Remove subtitle markup while retaining its displayed text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def clean_cue_text(value):
    parser = _CueTextParser()
    parser.feed(value)
    parser.close()
    return " ".join(unescape("".join(parser.parts)).split())


def parse_timestamp(value):
    """Return subtitle timestamp seconds, supporting hours longer than 99."""
    value = value.replace(",", ".")
    parts = value.split(":")
    if len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    elif len(parts) == 3:
        hours, minutes, seconds = parts
    else:
        raise ValueError(f"Invalid subtitle timestamp: {value}")
    hours, minutes, seconds = int(hours), int(minutes), float(seconds)
    if minutes >= 60 or seconds >= 60:
        raise ValueError(f"Invalid subtitle timestamp: {value}")
    return hours * 3600 + minutes * 60 + seconds


def format_vtt_timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"


def format_youtube_timestamp(seconds):
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, whole_seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{whole_seconds:02d}"
    return f"{minutes}:{whole_seconds:02d}"


def parse_fps(value):
    try:
        fps = Fraction(str(value))
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError("FPS must be a positive number or fraction such as 30000/1001.") from error
    if fps <= 0:
        raise ValueError("FPS must be a positive number or fraction such as 30000/1001.")
    nominal = round(float(fps))
    if nominal < 1:
        raise ValueError("FPS is too low for timecode conversion.")
    return fps, nominal


def timecode_to_frames(value, nominal_fps):
    """Convert a non-drop HH:MM:SS:FF label to its integer frame count."""
    if not isinstance(value, str) or len(value) > 32 or ";" in value:
        raise ValueError("Drop-frame or malformed timecode is unsupported; use non-drop HH:MM:SS:FF.")
    match = re.fullmatch(r"(\d+):(\d{2}):(\d{2}):(\d{2})", value)
    if not match:
        raise ValueError(f"Invalid non-drop timecode: {value!r}")
    hours, minutes, seconds, frames = map(int, match.groups())
    if minutes >= 60 or seconds >= 60 or frames >= nominal_fps:
        raise ValueError(f"Invalid non-drop timecode: {value!r}")
    return ((hours * 60 + minutes) * 60 + seconds) * nominal_fps + frames


def parse_native_transcription(path, duration, fps_value, timecode_origin):
    """Convert saved Resolve GetTranscription data to timeline-relative timing."""
    if fps_value is None or timecode_origin is None:
        raise ValueError("Native Resolve JSON requires both --fps and --timecode-origin.")
    fps, nominal_fps = parse_fps(fps_value)
    origin_frames = timecode_to_frames(timecode_origin, nominal_fps)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("segments"), list):
        raise ValueError("Native Resolve JSON must contain a segments list.")

    def relative_seconds(value):
        frames = timecode_to_frames(value, nominal_fps) - origin_frames
        if frames < 0:
            raise ValueError(f"Timecode {value!r} is before --timecode-origin.")
        return float(Fraction(frames, 1) / fps)

    segments = []
    previous_start = -1.0
    found_words = False
    for index, raw_segment in enumerate(raw["segments"]):
        if not isinstance(raw_segment, dict):
            raise ValueError(f"Native transcription segment {index} must be an object.")
        if not isinstance(raw_segment.get("text"), str):
            raise ValueError(f"Native transcription segment {index} text must be a string.")
        try:
            start = relative_seconds(raw_segment["start"])
            end = relative_seconds(raw_segment["end"])
            text = clean_cue_text(str(raw_segment["text"]))
        except KeyError as error:
            raise ValueError(f"Native transcription segment {index} is missing {error.args[0]}.") from error
        if not text or end <= start or end > duration or start < previous_start:
            raise ValueError(f"Invalid native transcription segment interval at index {index}.")
        previous_start = start

        raw_words = raw_segment.get("words", [])
        if not isinstance(raw_words, list):
            raise ValueError(f"Native transcription words at segment {index} must be a list.")
        words = []
        previous_word_start = -1.0
        for word_index, raw_word in enumerate(raw_words):
            if not isinstance(raw_word, dict):
                raise ValueError(f"Native word {word_index} in segment {index} must be an object.")
            if not isinstance(raw_word.get("text"), str):
                raise ValueError(
                    f"Native word {word_index} in segment {index} text must be a string."
                )
            try:
                word_start = relative_seconds(raw_word["start"])
                word_end = relative_seconds(raw_word["end"])
                word_text = raw_word["text"]
            except KeyError as error:
                raise ValueError(
                    f"Native word {word_index} in segment {index} is missing {error.args[0]}."
                ) from error
            if (not word_text.strip() or word_end <= word_start or word_start < start
                    or word_end > end or word_start < previous_word_start):
                raise ValueError(f"Invalid native word interval at segment {index}, word {word_index}.")
            previous_word_start = word_start
            words.append({
                "start_seconds": word_start,
                "end_seconds": word_end,
                "text": word_text,
            })
        found_words = found_words or bool(words)
        segment = {
            "start_seconds": start,
            "end_seconds": end,
            "text": text,
            "index": index + 1,
            "words": words,
        }
        if "speaker" in raw_segment:
            segment["speaker"] = raw_segment["speaker"]
        segments.append(segment)
    if not segments:
        raise ValueError("Native Resolve JSON contains no transcription segments.")
    metadata = {
        "source": "resolve_native_transcription",
        "language": raw.get("language"),
        "fps": str(fps),
        "timecode_origin": timecode_origin,
        "word_timestamps": found_words,
    }
    return segments, metadata


def readable_native_cues(segments, max_seconds=6, max_words=12, pause_seconds=.65):
    """Split long native segments only at their preserved word boundaries."""
    cues = []
    for segment in segments:
        words = segment.get("words") or []
        if not words:
            cues.append({
                "start_seconds": segment["start_seconds"],
                "end_seconds": segment["end_seconds"],
                "text": segment["text"],
            })
            continue
        cue_start = 0
        for index, word in enumerate(words):
            count = index - cue_start + 1
            duration = word["end_seconds"] - words[cue_start]["start_seconds"]
            final_word = index == len(words) - 1
            punctuation = bool(re.search(r"[.!?][\"')\]]*$", word["text"].strip()))
            pause = (not final_word and
                     words[index + 1]["start_seconds"] - word["end_seconds"] >= pause_seconds)
            if (final_word or count >= max_words or duration >= max_seconds
                    or (count >= 3 and punctuation) or (count >= 2 and pause)):
                cue_words = words[cue_start:index + 1]
                cues.append({
                    "start_seconds": cue_words[0]["start_seconds"],
                    "end_seconds": cue_words[-1]["end_seconds"],
                    "text": "".join(item["text"] for item in cue_words).strip(),
                })
                cue_start = index + 1
    for index, cue in enumerate(cues):
        cue["index"] = index + 1
    return cues


def _subtitle_blocks(raw_text):
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    lines = normalized.splitlines()
    if lines and lines[0].strip().upper().startswith("WEBVTT"):
        lines = lines[1:]
    return [block for block in re.split(r"\n\s*\n", "\n".join(lines)) if block.strip()]


def parse_subtitles(path, duration):
    """Parse SRT or VTT into final-timeline subtitle segments."""
    segments = []
    for block in _subtitle_blocks(path.read_text(encoding="utf-8-sig")):
        lines = [line.strip() for line in block.splitlines()]
        if not lines or lines[0].upper().startswith(("NOTE", "STYLE", "REGION")):
            continue
        timing_index = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing_index is None:
            continue
        match = TIMING_RE.match(lines[timing_index])
        if not match:
            raise ValueError(f"Invalid subtitle timing line: {lines[timing_index]}")
        start = parse_timestamp(match.group("start"))
        end = parse_timestamp(match.group("end"))
        text = clean_cue_text(" ".join(lines[timing_index + 1:]))
        if not text:
            continue
        segments.append({"start_seconds": start, "end_seconds": end, "text": text})

    if not segments:
        raise ValueError("The subtitle file contains no usable cues.")
    previous_start = -1.0
    for index, segment in enumerate(segments):
        start, end = segment["start_seconds"], segment["end_seconds"]
        if start < 0 or end <= start or end > duration or start < previous_start:
            raise ValueError(f"Invalid final-timeline subtitle interval at index {index}.")
        previous_start = start
        segment["index"] = index + 1
    return segments


def validate_duration(duration):
    duration = float(duration)
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Duration must be a positive, finite number of seconds.")
    return duration


def load_chapters(path, duration):
    """Load reviewed chapters and enforce YouTube's manual chapter rules."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or len(raw) < 3:
        raise ValueError("Reviewed chapters must be a JSON list with at least three entries.")
    chapters = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict) or not {"start", "title"}.issubset(item):
            raise ValueError(f"Chapter {index} must contain start and title.")
        start = item["start"]
        title = item["title"]
        if isinstance(start, bool) or not isinstance(start, (int, float)):
            raise ValueError(f"Chapter {index} start must be seconds as a number.")
        start = float(start)
        if not math.isfinite(start) or start < 0 or start > duration:
            raise ValueError(f"Chapter {index} start is outside the final timeline.")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"Chapter {index} title must be non-empty text.")
        chapters.append({"start": start, "title": " ".join(title.split())})

    if chapters[0]["start"] != 0:
        raise ValueError("The first reviewed chapter must start at 0:00.")
    boundaries = [chapter["start"] for chapter in chapters] + [duration]
    for index, (start, end) in enumerate(zip(boundaries, boundaries[1:])):
        if end <= start:
            raise ValueError("Reviewed chapter starts must be strictly ascending.")
        if end - start < 10:
            suffix = "final chapter" if index == len(chapters) - 1 else f"chapter {index}"
            raise ValueError(f"The {suffix} is shorter than 10 seconds.")
    return chapters


def render_transcript_html(segments, duration, timing_note):
    rows = []
    for segment in segments:
        start = format_vtt_timestamp(segment["start_seconds"])
        end = format_vtt_timestamp(segment["end_seconds"])
        rows.append(
            f'<section class="cue"><div class="time">{start} to {end}</div>'
            f'<p>{escape(segment["text"])}</p></section>'
        )
    body = "\n".join(rows)
    return f"""<!doctype html>
<html lang="en" class="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.className=localStorage.getItem('transcript-theme')||'dark';</script>
<title>Final timeline transcript</title>
<style>
:root {{ color-scheme: light; --bg:#f5f7fb; --panel:#fff; --text:#18202b; --muted:#526174; --line:#dbe2ea; }}
:root.dark {{ color-scheme: dark; --bg:#10151d; --panel:#171f2b; --text:#f2f5f8; --muted:#aeb9c7; --line:#2d3948; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:var(--bg); color:var(--text); font:17.5px/1.6 system-ui,sans-serif; }}
main {{ width:min(860px,calc(100% - 32px)); margin:0 auto; padding:24px 0 64px; }}
button {{ float:right; padding:9px 13px; border:1px solid var(--line); border-radius:8px; background:var(--panel); color:var(--text); cursor:pointer; }}
h1 {{ font-size:clamp(28px,5vw,44px); line-height:1.1; margin:44px 0 8px; }} .note {{ color:var(--muted); margin:0 0 30px; }}
.cue {{ padding:18px 20px; margin:12px 0; border:1px solid var(--line); border-radius:12px; background:var(--panel); }}
.time {{ color:var(--muted); font-size:14px; font-variant-numeric:tabular-nums; }} p {{ margin:6px 0 0; }}
</style>
</head>
<body><main>
<button type="button" onclick="toggleTheme()">Light or dark</button>
<h1>Final timeline transcript</h1>
<p class="note">Duration: {escape(format_vtt_timestamp(duration))}. {escape(timing_note)}</p>
{body}
</main><script>
function toggleTheme() {{ const root=document.documentElement; root.className=root.className==='dark'?'light':'dark'; localStorage.setItem('transcript-theme',root.className); }}
</script></body></html>
"""


def output_payloads(segments, duration, chapters=None, metadata=None):
    metadata = metadata or {
        "source": "resolve_final_timeline_subtitles",
        "word_timestamps": False,
    }
    presentation = (
        readable_native_cues(segments)
        if metadata["source"] == "resolve_native_transcription" else segments
    )
    transcript_text = "\n\n".join(segment["text"] for segment in presentation) + "\n"
    vtt_cues = []
    for segment in presentation:
        vtt_cues.append(
            f'{format_vtt_timestamp(segment["start_seconds"])} --> '
            f'{format_vtt_timestamp(segment["end_seconds"])}\n{segment["text"]}'
        )
    speech = {
        "schema_version": 1,
        "source": metadata["source"],
        "timing_granularity": (
            "word_and_segment" if metadata["word_timestamps"] else "subtitle_segment"
        ),
        "timing_origin": "final timeline beginning, seconds",
        "word_timestamps": metadata["word_timestamps"],
        "word_timestamps_invented": False,
        "duration_seconds": duration,
        "segments": segments,
        "presentation_cue_count": len(presentation),
    }
    for key in ("language", "fps", "timecode_origin"):
        if metadata.get(key) is not None:
            speech[key] = metadata[key]
    if metadata["word_timestamps"]:
        speech["word_timestamp_source"] = "resolve_native_transcription"
    timing_note = (
        "Readable cues use Resolve native word boundaries. speech.json preserves the "
        "original native segments and word timestamps; no timing was inferred."
        if metadata["source"] == "resolve_native_transcription"
        else "Times are subtitle segment boundaries from the Resolve final timeline. "
             "No word-level timing is claimed."
    )
    payloads = {
        "transcript.html": render_transcript_html(presentation, duration, timing_note),
        "transcript.txt": transcript_text,
        "transcript.vtt": "WEBVTT\n\n" + "\n\n".join(vtt_cues) + "\n",
        "speech.json": json.dumps(speech, ensure_ascii=False, indent=2) + "\n",
    }
    if chapters is not None:
        payloads["chapters.json"] = json.dumps(chapters, ensure_ascii=False, indent=2) + "\n"
        payloads["YouTube chapters.txt"] = "".join(
            f'{format_youtube_timestamp(chapter["start"])} {chapter["title"]}\n'
            for chapter in chapters
        )
    return payloads


def build(input_path, output_dir, duration, chapter_path=None, overwrite=False,
          fps=None, timecode_origin=None):
    duration = validate_duration(duration)
    input_path = input_path.expanduser().resolve(strict=True)
    if not input_path.is_file():
        raise ValueError("Transcript input must be a file.")
    if input_path.suffix.lower() == ".json":
        segments, metadata = parse_native_transcription(
            input_path, duration, fps, timecode_origin
        )
    else:
        if fps is not None or timecode_origin is not None:
            raise ValueError("--fps and --timecode-origin apply only to native Resolve JSON.")
        segments = parse_subtitles(input_path, duration)
        metadata = None
    chapters = None
    if chapter_path is not None:
        chapter_path = chapter_path.expanduser().resolve(strict=True)
        chapters = load_chapters(chapter_path, duration)
    payloads = output_payloads(segments, duration, chapters, metadata)

    output_dir = output_dir.expanduser().resolve()
    conflicts = [output_dir / name for name in payloads if (output_dir / name).exists()]
    if conflicts and not overwrite:
        names = ", ".join(path.name for path in conflicts)
        raise FileExistsError(f"Existing output is preserved: {names}. Use --overwrite to replace it.")
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in payloads.items():
        (output_dir / name).write_text(content, encoding="utf-8")
    return [output_dir / name for name in payloads]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Resolve final-timeline SRT/VTT or native transcription JSON")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--duration", type=float, required=True, help="Final timeline duration in seconds")
    parser.add_argument("--chapters", type=Path, help="Reviewed JSON list of start/title objects")
    parser.add_argument("--fps", help="Exact native JSON frame rate, for example 30000/1001")
    parser.add_argument("--timecode-origin", help="Native source start as non-drop HH:MM:SS:FF")
    parser.add_argument("--overwrite", action="store_true", help="Replace this tool's existing output files")
    args = parser.parse_args()
    try:
        paths = build(
            args.input, args.output_dir, args.duration, args.chapters,
            args.overwrite, args.fps, args.timecode_origin
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(json.dumps({"state": "written", "files": [str(path) for path in paths]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
