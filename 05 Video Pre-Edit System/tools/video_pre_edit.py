#!/usr/bin/env python3
"""Conservative local pre-edit for talking-head videos.

The tool removes detected quiet pauses, can remove explicitly spoken restart
markers with a local Whisper model, optionally applies local speech cleanup,
and writes a review report. It never edits the source file.

Core requirements:
    Python 3.11+
    ffmpeg and ffprobe on PATH

Optional spoken-marker requirement:
    openai-whisper and torch installed locally
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


TOOL_VERSION = "1.0.0"
PLAN_SCHEMA = "ai-mentorship-video-pre-edit-plan-v1"
DEFAULT_MIN_SILENCE = 0.8
DEFAULT_SILENCE_THRESHOLD_DB = -40.0
DEFAULT_PADDING_MS = 150
DEFAULT_RESTART_PHRASE = "cut cut"
DEFAULT_FULL_RESTART_PHRASE = "full stop restart"
DEFAULT_RESTART_LOOKBACK = 10.0
DEFAULT_MARKER_WORD_GAP = 0.8
MICRO_FADE_SECONDS = 0.015
LONG_CUT_WARNING_SECONDS = 15.0
REMOVAL_WARNING_RATIO = 0.45
TARGET_LUFS = -16.0
LIMITER_CEILING_DBFS = -1.5
LIMITER_CEILING_LINEAR = 10 ** (LIMITER_CEILING_DBFS / 20)
MAX_AUDIO_GAIN_DB = 18.0


class PreEditError(RuntimeError):
    """A user-facing error that should stop without touching the source."""


@dataclass(frozen=True)
class EditRange:
    start: float
    end: float
    reasons: tuple[str, ...] = ()

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass(frozen=True)
class MediaInfo:
    duration: float
    has_video: bool
    has_audio: bool
    video_streams: int
    audio_streams: int
    video_pixel_format: str
    video_transfer: str
    subtitle_streams: int = 0
    chapter_count: int = 0


PLAN_OPTION_NAMES = (
    "silence_threshold",
    "min_silence",
    "padding_ms",
    "keep_silence",
    "cut",
    "protect",
    "detect_restarts",
    "restart_phrase",
    "detect_full_stop_restart",
    "confirm_full_restart",
    "full_restart_phrase",
    "whisper_model",
    "language",
    "enhance_audio",
)

PLAN_CONTROL_FLAGS = {
    "--silence-threshold",
    "--min-silence",
    "--padding-ms",
    "--keep-silence",
    "--cut",
    "--protect",
    "--detect-restarts",
    "--restart-phrase",
    "--detect-full-stop-restart",
    "--confirm-full-restart",
    "--full-restart-phrase",
    "--words-json",
    "--whisper-model",
    "--language",
    "--enhance-audio",
}


def run_command(
    command: Sequence[str],
    *,
    allow_failure: bool = False,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(command),
        capture_output=True,
        text=True,
        shell=False,
    )
    if result.returncode != 0 and not allow_failure:
        details = (result.stderr or result.stdout or "").strip().splitlines()
        short_details = "\n".join(details[-12:])
        raise PreEditError(
            "A local media command failed."
            + (f"\n{short_details}" if short_details else "")
        )
    return result


def require_local_tools() -> None:
    missing = [name for name in ("ffmpeg", "ffprobe") if not shutil.which(name)]
    if missing:
        raise PreEditError(
            "Missing local requirement: "
            + ", ".join(missing)
            + ". Install FFmpeg, then confirm both ffmpeg and ffprobe are on PATH."
        )


def require_libx264_encoder() -> None:
    result = run_command(
        ["ffmpeg", "-hide_banner", "-encoders"],
        allow_failure=True,
    )
    if result.returncode != 0 or not re.search(
        r"(?m)^\s*V\S*\s+libx264(?:\s|$)",
        result.stdout or "",
    ):
        raise PreEditError(
            "This render needs an FFmpeg build with the libx264 encoder. "
            "Review INSTALL.md and THIRD-PARTY.md before changing FFmpeg."
        )


def parse_timestamp(value: str) -> float:
    text = value.strip()
    if not text:
        raise ValueError("Timestamp cannot be empty.")

    parts = text.split(":")
    if len(parts) > 3:
        raise ValueError(f"Invalid timestamp: {value}")
    try:
        numbers = [float(part) for part in parts]
    except ValueError as error:
        raise ValueError(f"Invalid timestamp: {value}") from error
    if any(not math.isfinite(number) or number < 0 for number in numbers):
        raise ValueError(f"Invalid timestamp: {value}")

    if len(numbers) == 1:
        return numbers[0]
    if numbers[-1] >= 60:
        raise ValueError(f"Seconds must be below 60: {value}")
    if len(numbers) == 2:
        return numbers[0] * 60 + numbers[1]
    if numbers[1] >= 60:
        raise ValueError(f"Minutes must be below 60 in HH:MM:SS: {value}")
    return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]


def parse_time_range(value: str) -> tuple[float, float]:
    if "-" not in value:
        raise ValueError(
            f"Range must use START-END, for example 00:30-00:45: {value}"
        )
    start_text, end_text = value.split("-", 1)
    start = parse_timestamp(start_text)
    end = parse_timestamp(end_text)
    if end <= start:
        raise ValueError(f"Range end must be after its start: {value}")
    return start, end


def format_timestamp(seconds: float) -> str:
    milliseconds = round(max(0.0, seconds) * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    if hours:
        return f"{hours}:{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"
    return f"{minutes}:{whole_seconds:02d}.{milliseconds:03d}"


def single_line_text(value: object) -> str:
    """Keep untrusted report values on one visible line."""
    text = "".join(
        " " if character in "\r\n\t" or ord(character) < 32 or ord(character) == 127
        else character
        for character in str(value)
    )
    return " ".join(text.split())


def markdown_inline_code(value: object) -> str:
    """Render an untrusted value as one safe Markdown code span."""
    text = single_line_text(value)
    longest_run = max(
        (len(match.group(0)) for match in re.finditer(r"`+", text)),
        default=0,
    )
    fence = "`" * max(1, longest_run + 1)
    if not text or text.startswith("`") or text.endswith("`"):
        text = f" {text} "
    return f"{fence}{text}{fence}"


def markdown_table_cell(value: object) -> str:
    """Keep an untrusted value inside one Markdown table cell."""
    text = single_line_text(value)
    unsafe = set("&\\`*_{[<>|]}")
    return "".join(
        f"&#{ord(character)};" if character in unsafe else character
        for character in text
    )


def markdown_plain_text(value: object) -> str:
    """Keep an untrusted value from creating Markdown links, HTML, or emphasis."""
    text = single_line_text(value)
    unsafe = set("&\\`*_{[<>]}")
    return "".join(
        f"&#{ord(character)};" if character in unsafe else character
        for character in text
    )


def clamp_range(
    start: float,
    end: float,
    duration: float,
    reasons: Iterable[str] = (),
) -> EditRange | None:
    clamped_start = max(0.0, min(duration, float(start)))
    clamped_end = max(0.0, min(duration, float(end)))
    if clamped_end - clamped_start <= 0.001:
        return None
    return EditRange(
        clamped_start,
        clamped_end,
        tuple(sorted(set(reasons))),
    )


def merge_plain_ranges(
    ranges: Iterable[tuple[float, float]],
    duration: float,
) -> list[tuple[float, float]]:
    normalized = []
    for start, end in ranges:
        item = clamp_range(start, end, duration)
        if item:
            normalized.append((item.start, item.end))
    normalized.sort()

    merged: list[tuple[float, float]] = []
    for start, end in normalized:
        if merged and start <= merged[-1][1] + 0.001:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def subtract_protected(
    edit_range: EditRange,
    protected: Sequence[tuple[float, float]],
) -> list[EditRange]:
    pieces = [edit_range]
    for protected_start, protected_end in protected:
        next_pieces: list[EditRange] = []
        for piece in pieces:
            if protected_end <= piece.start or protected_start >= piece.end:
                next_pieces.append(piece)
                continue
            if piece.start < protected_start:
                next_pieces.append(
                    EditRange(piece.start, protected_start, piece.reasons)
                )
            if piece.end > protected_end:
                next_pieces.append(
                    EditRange(protected_end, piece.end, piece.reasons)
                )
        pieces = next_pieces
    return [piece for piece in pieces if piece.duration > 0.001]


def normalize_cuts(
    cuts: Iterable[EditRange],
    duration: float,
    protected: Sequence[tuple[float, float]] = (),
) -> list[EditRange]:
    protected_ranges = merge_plain_ranges(protected, duration)
    pieces: list[EditRange] = []
    for cut in cuts:
        clamped = clamp_range(cut.start, cut.end, duration, cut.reasons)
        if not clamped:
            continue
        pieces.extend(subtract_protected(clamped, protected_ranges))
    pieces.sort(key=lambda item: (item.start, item.end))

    merged: list[EditRange] = []
    for cut in pieces:
        if merged and cut.start <= merged[-1].end + 0.001:
            previous = merged[-1]
            merged[-1] = EditRange(
                previous.start,
                max(previous.end, cut.end),
                tuple(sorted(set(previous.reasons + cut.reasons))),
            )
        else:
            merged.append(cut)
    return merged


def invert_cuts(
    cuts: Sequence[EditRange],
    duration: float,
) -> list[tuple[float, float]]:
    kept: list[tuple[float, float]] = []
    cursor = 0.0
    for cut in cuts:
        if cut.start > cursor + 0.001:
            kept.append((cursor, cut.start))
        cursor = max(cursor, cut.end)
    if cursor < duration - 0.001:
        kept.append((cursor, duration))
    return [(start, end) for start, end in kept if end - start > 0.05]


def probe_media(path: Path) -> MediaInfo:
    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-show_entries",
            "stream=codec_type,pix_fmt,color_transfer",
            "-show_entries",
            "chapter=id",
            "-of",
            "json",
            str(path),
        ]
    )
    try:
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        streams = data.get("streams", [])
        video_streams = [
            stream for stream in streams if stream.get("codec_type") == "video"
        ]
        audio_streams = [
            stream for stream in streams if stream.get("codec_type") == "audio"
        ]
        subtitle_streams = [
            stream for stream in streams if stream.get("codec_type") == "subtitle"
        ]
        chapters = data.get("chapters", [])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise PreEditError("Could not read the video's duration and streams.") from error
    if not math.isfinite(duration) or duration <= 0:
        raise PreEditError("The source video has no usable duration.")
    return MediaInfo(
        duration=duration,
        has_video=bool(video_streams),
        has_audio=bool(audio_streams),
        video_streams=len(video_streams),
        audio_streams=len(audio_streams),
        subtitle_streams=len(subtitle_streams),
        chapter_count=len(chapters) if isinstance(chapters, list) else 0,
        video_pixel_format=str(
            video_streams[0].get("pix_fmt", "") if video_streams else ""
        ),
        video_transfer=str(
            video_streams[0].get("color_transfer", "") if video_streams else ""
        ),
    )


def reject_unsafe_source_layout(info: MediaInfo) -> None:
    if not info.has_video or not info.has_audio:
        raise PreEditError(
            "Source must contain both a video stream and one readable audio stream."
        )
    if info.video_streams != 1 or info.audio_streams != 1:
        raise PreEditError(
            "This release supports one video stream and one audio stream. "
            "Export a flattened working copy first; keep the original unchanged."
        )
    if info.subtitle_streams:
        raise PreEditError(
            "This source contains a subtitle stream. Export a flattened working "
            "copy without subtitles, or preserve them in a proper editing workflow."
        )
    if info.chapter_count:
        raise PreEditError(
            "This source contains chapters. Export a flattened working copy without "
            "chapters, or preserve them in a proper editing workflow."
        )
    pixel_format = info.video_pixel_format.lower()
    transfer = info.video_transfer.lower()
    if (
        re.search(r"p(?:9|10|12|14|16)(?:le|be)?$", pixel_format)
        or transfer in {"smpte2084", "arib-std-b67"}
    ):
        raise PreEditError(
            "HDR or high-bit-depth input needs a deliberate color-managed workflow. "
            "Export an SDR working copy before using this tool."
        )


def detect_silence(
    input_path: Path,
    duration: float,
    threshold_db: float,
    minimum_duration: float,
) -> list[tuple[float, float]]:
    result = run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(input_path),
            "-map",
            "0:a:0",
            "-af",
            f"silencedetect=noise={threshold_db:g}dB:d={minimum_duration:g}",
            "-f",
            "null",
            "-",
        ],
        allow_failure=True,
    )
    if result.returncode != 0:
        raise PreEditError(
            "FFmpeg could not analyze the source audio. Confirm the file has one readable audio track."
        )

    start_pattern = re.compile(r"silence_start:\s*(-?\d+(?:\.\d+)?)")
    end_pattern = re.compile(r"silence_end:\s*(-?\d+(?:\.\d+)?)")
    pending_start: float | None = None
    silences: list[tuple[float, float]] = []

    for line in (result.stderr or "").splitlines():
        start_match = start_pattern.search(line)
        if start_match:
            pending_start = max(0.0, float(start_match.group(1)))
        end_match = end_pattern.search(line)
        if end_match:
            end = min(duration, float(end_match.group(1)))
            start = pending_start if pending_start is not None else 0.0
            if end > start:
                silences.append((start, end))
            pending_start = None
    if pending_start is not None and duration > pending_start:
        silences.append((pending_start, duration))
    return merge_plain_ranges(silences, duration)


def silence_ranges_to_cuts(
    silences: Sequence[tuple[float, float]],
    duration: float,
    padding_seconds: float,
) -> list[EditRange]:
    cuts = []
    for start, end in silences:
        cut = clamp_range(
            start + padding_seconds,
            end - padding_seconds,
            duration,
            ("detected silence",),
        )
        if cut:
            cuts.append(cut)
    return cuts


def normalize_word(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def validate_words(words: object) -> list[dict[str, float | str]]:
    if isinstance(words, dict):
        words = words.get("words")
    if not isinstance(words, list):
        raise PreEditError("Timed-word JSON must contain a list named words.")

    validated = []
    for index, item in enumerate(words):
        if not isinstance(item, dict):
            raise PreEditError(f"Timed word {index + 1} is not an object.")
        try:
            word = str(item["word"]).strip()
            start = float(item["start"])
            end = float(item["end"])
        except (KeyError, TypeError, ValueError) as error:
            raise PreEditError(
                f"Timed word {index + 1} needs word, start, and end."
            ) from error
        if (
            not word
            or not math.isfinite(start)
            or not math.isfinite(end)
            or start < 0
            or end <= start
        ):
            raise PreEditError(f"Timed word {index + 1} is invalid.")
        validated.append({"word": word, "start": start, "end": end})
    return validated


def load_timed_words(path: Path) -> list[dict[str, float | str]]:
    try:
        return validate_words(json.loads(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError as error:
        raise PreEditError("Timed-word JSON is not valid JSON.") from error


def transcribe_with_local_whisper(
    input_path: Path,
    model_name: str,
    language: str,
    restart_phrase: str,
    full_restart_phrase: str,
) -> list[dict[str, float | str]]:
    try:
        import whisper  # type: ignore
    except ImportError as error:
        raise PreEditError(
            "Spoken marker detection needs the optional local Whisper install. "
            "Install requirements-markers.txt or provide --words-json."
        ) from error

    print(f"Transcribing locally with Whisper model {model_name!r}...")
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(
            str(input_path),
            word_timestamps=True,
            initial_prompt=f"{restart_phrase}. {full_restart_phrase}.",
            language=language,
            condition_on_previous_text=False,
            verbose=False,
        )
    except Exception as error:
        raise PreEditError(
            "Local Whisper could not transcribe this file. "
            "Check the optional install and model download, or use --words-json."
        ) from error
    words = []
    for segment in result.get("segments", []):
        for item in segment.get("words", []):
            word = str(item.get("word", "")).strip()
            start = float(item.get("start", 0.0))
            end = float(item.get("end", 0.0))
            # Local Whisper can emit an empty or zero-duration boundary token.
            # Ignore that artifact; user-supplied JSON remains strictly validated.
            if (
                not word
                or not math.isfinite(start)
                or not math.isfinite(end)
                or start < 0
                or end <= start
            ):
                continue
            words.append(
                {
                    "word": word,
                    "start": start,
                    "end": end,
                }
            )
    return validate_words(words)


def transcript_problem(
    words: Sequence[dict[str, float | str]],
    language: str = "en",
) -> str | None:
    if not words:
        return "the local transcript contains no timed words"
    tokens = [normalize_word(str(item["word"])) for item in words]
    tokens = [token for token in tokens if token]
    if not tokens:
        return "the local transcript contains no usable words"

    if language.lower().startswith("en"):
        non_ascii = sum(
            1
            for token in tokens
            if not any(character.isascii() and character.isalpha() for character in token)
        )
        if non_ascii / len(tokens) > 0.20:
            return "too many English transcript tokens contain no ASCII letters"

    counts: dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    most_common = max(counts.values())
    if len(tokens) >= 50 and most_common / len(tokens) > 0.25:
        return "one token dominates the transcript"

    longest_run = 1
    current_run = 1
    for previous, current in zip(tokens, tokens[1:]):
        current_run = current_run + 1 if previous == current else 1
        longest_run = max(longest_run, current_run)
    if longest_run >= 25:
        return "the transcript contains a repeated-token loop"
    return None


def find_exact_marker_spans(
    words: Sequence[dict[str, float | str]],
    phrase: str,
    *,
    maximum_word_gap: float = DEFAULT_MARKER_WORD_GAP,
) -> list[tuple[float, float]]:
    phrase_tokens = [normalize_word(token) for token in phrase.split()]
    phrase_tokens = [token for token in phrase_tokens if token]
    if not phrase_tokens:
        raise PreEditError("Restart phrase must contain at least one word.")

    spans: list[tuple[float, float]] = []
    for index in range(len(words) - len(phrase_tokens) + 1):
        window = words[index : index + len(phrase_tokens)]
        if [normalize_word(str(item["word"])) for item in window] != phrase_tokens:
            continue
        gaps = [
            float(current["start"]) - float(previous["end"])
            for previous, current in zip(window, window[1:])
        ]
        if any(gap < -0.05 or gap > maximum_word_gap for gap in gaps):
            continue

        start = float(window[0]["start"])
        end = float(window[-1]["end"])
        if end - start > max(3.0, len(phrase_tokens) * 1.2):
            continue

        # Repeated two-word markers should be deliberate: either tightly spoken
        # or separated from the prior sentence by a short pause.
        if len(phrase_tokens) == 2 and phrase_tokens[0] == phrase_tokens[1]:
            prior_gap = (
                start - float(words[index - 1]["end"])
                if index > 0
                else float("inf")
            )
            marker_gap = gaps[0] if gaps else 0.0
            if marker_gap >= 0.30 and prior_gap < 0.15:
                continue

        if spans and start <= spans[-1][1] + 0.05:
            continue
        spans.append((start, end))
    return spans


def marker_overlaps_protected(
    span: tuple[float, float],
    protected: Sequence[tuple[float, float]],
) -> bool:
    start, end = span
    return any(start < protected_end and end > protected_start for protected_start, protected_end in protected)


def restart_marker_cuts(
    kept_segments: Sequence[tuple[float, float]],
    marker_spans: Sequence[tuple[float, float]],
    *,
    lookback: float = DEFAULT_RESTART_LOOKBACK,
) -> list[EditRange]:
    if not marker_spans:
        return []

    windows: list[EditRange] = []
    segments = sorted(kept_segments)
    for marker_start, marker_end in sorted(marker_spans):
        containing_segment = next(
            (
                (segment_start, segment_end)
                for segment_start, segment_end in segments
                if segment_start <= marker_start < segment_end
            ),
            None,
        )
        if containing_segment is None:
            continue
        segment_start, _ = containing_segment
        cut_start = max(segment_start, marker_end - lookback)
        windows.append(
            EditRange(
                cut_start,
                marker_end,
                (f"spoken restart marker: {DEFAULT_RESTART_PHRASE}",),
            )
        )
    return windows


def render_cut_video(
    input_path: Path,
    output_path: Path,
    kept_segments: Sequence[tuple[float, float]],
) -> None:
    if not kept_segments:
        raise PreEditError("The cut plan leaves no video to render.")

    filter_lines = []
    labels = []
    for index, (start, end) in enumerate(kept_segments):
        segment_duration = end - start
        video_label = f"v{index}"
        audio_label = f"a{index}"
        filter_lines.append(
            f"[0:v:0]trim=start={start:.6f}:end={end:.6f},"
            f"setpts=PTS-STARTPTS[{video_label}]"
        )

        audio_filters = [
            f"atrim=start={start:.6f}:end={end:.6f}",
            "asetpts=PTS-STARTPTS",
        ]
        fade_duration = min(MICRO_FADE_SECONDS, segment_duration / 4)
        if index > 0 and fade_duration > 0:
            audio_filters.append(
                f"afade=t=in:st=0:d={fade_duration:.6f}"
            )
        if index < len(kept_segments) - 1 and fade_duration > 0:
            fade_start = max(0.0, segment_duration - fade_duration)
            audio_filters.append(
                f"afade=t=out:st={fade_start:.6f}:d={fade_duration:.6f}"
            )
        filter_lines.append(
            f"[0:a:0]{','.join(audio_filters)}[{audio_label}]"
        )
        labels.append(f"[{video_label}][{audio_label}]")

    if len(kept_segments) == 1:
        video_map = "[v0]"
        audio_map = "[a0]"
    else:
        filter_lines.append(
            "".join(labels)
            + f"concat=n={len(kept_segments)}:v=1:a=1[vout][aout]"
        )
        video_map = "[vout]"
        audio_map = "[aout]"

    filter_graph = ";\n".join(filter_lines)
    run_command(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-nostats",
            "-i",
            str(input_path),
            "-filter_complex",
            filter_graph,
            "-map",
            video_map,
            "-map",
            audio_map,
            "-map_metadata",
            "-1",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    )


def audio_pre_filter() -> str:
    return ",".join(
        [
            "highpass=f=80",
            "lowpass=f=12000",
            "equalizer=f=200:t=q:w=1:g=-1",
            "equalizer=f=3000:t=q:w=1.5:g=2",
            "acompressor=threshold=-20dB:ratio=3:attack=5:release=50",
        ]
    )


def measure_loudness(input_path: Path, pre_filter: str) -> dict[str, str] | None:
    chain = (
        f"{pre_filter},"
        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json"
    )
    result = run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(input_path),
            "-vn",
            "-af",
            chain,
            "-f",
            "null",
            "-",
        ],
        allow_failure=True,
    )
    stderr = result.stderr or ""
    marker = stderr.rfind("[Parsed_loudnorm")
    start = stderr.find("{", marker if marker != -1 else 0)
    if start == -1:
        return None
    try:
        stats, _ = json.JSONDecoder().raw_decode(stderr[start:])
    except json.JSONDecodeError:
        return None
    return stats if "input_i" in stats else None


def measure_integrated_loudness(input_path: Path) -> float | None:
    result = run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(input_path),
            "-vn",
            "-af",
            "ebur128",
            "-f",
            "null",
            "-",
        ],
        allow_failure=True,
    )
    matches = re.findall(
        r"I:\s*(-?\d+(?:\.\d+)?)\s*LUFS",
        result.stderr or "",
    )
    return float(matches[-1]) if matches else None


def apply_local_audio_enhancement(
    input_path: Path,
    output_path: Path,
) -> dict[str, float | str | bool | None]:
    pre_filter = audio_pre_filter()
    stats = measure_loudness(input_path, pre_filter)
    if not stats:
        raise PreEditError("Could not measure source loudness for local enhancement.")
    try:
        measured_lufs = float(stats["input_i"])
    except (TypeError, ValueError) as error:
        raise PreEditError("The measured loudness result is invalid.") from error
    if not math.isfinite(measured_lufs):
        raise PreEditError("The source audio is too quiet to enhance safely.")

    requested_gain = TARGET_LUFS - measured_lufs
    applied_gain = max(-MAX_AUDIO_GAIN_DB, min(MAX_AUDIO_GAIN_DB, requested_gain))
    gain_was_limited = abs(requested_gain - applied_gain) > 0.01
    chain = (
        f"{pre_filter},volume={applied_gain:.2f}dB,"
        f"alimiter=limit={LIMITER_CEILING_LINEAR:.4f}:attack=5:release=50:"
        "level=disabled:latency=true"
    )
    run_command(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-nostats",
            "-i",
            str(input_path),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-map_metadata",
            "-1",
            "-c:v",
            "copy",
            "-af",
            chain,
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    )
    final_lufs = measure_integrated_loudness(output_path)
    return {
        "applied": True,
        "target_lufs": TARGET_LUFS,
        "limiter_ceiling_dbfs": LIMITER_CEILING_DBFS,
        "true_peak_compliance": "not certified; review or meter for delivery",
        "measured_before_lufs": round(measured_lufs, 2),
        "requested_gain_db": round(requested_gain, 2),
        "applied_gain_db": round(applied_gain, 2),
        "gain_was_limited": gain_was_limited,
        "measured_after_lufs": (
            round(final_lufs, 2) if final_lufs is not None else None
        ),
    }


def verification_for(
    path: Path,
    expected_duration: float,
) -> dict[str, object]:
    info = probe_media(path)
    tolerance = max(0.50, expected_duration * 0.02)
    duration_matches = abs(info.duration - expected_duration) <= tolerance
    if not info.has_video or not info.has_audio:
        raise PreEditError("Rendered output does not contain both video and audio.")
    if info.subtitle_streams or info.chapter_count:
        raise PreEditError(
            "Rendered output unexpectedly contains subtitles or chapters."
        )
    if not duration_matches:
        raise PreEditError(
            "Rendered output duration does not match the approved cut plan."
        )
    return {
        "scope": "video stream, audio stream, and duration",
        "has_video": info.has_video,
        "has_audio": info.has_audio,
        "subtitle_streams": info.subtitle_streams,
        "chapters": info.chapter_count,
        "duration_seconds": round(info.duration, 3),
        "expected_duration_seconds": round(expected_duration, 3),
        "duration_matches": duration_matches,
    }


def report_markdown(
    *,
    source_name: str,
    output_name: str,
    rendered: bool,
    source_duration: float,
    expected_duration: float,
    cuts: Sequence[EditRange],
    protected: Sequence[tuple[float, float]],
    settings: dict[str, object],
    marker_summary: dict[str, object],
    audio_summary: dict[str, object],
    verification: dict[str, object] | None,
    warnings: Sequence[str],
    plan_name: str | None = None,
) -> str:
    removed = max(0.0, source_duration - expected_duration)
    removed_ratio = removed / source_duration if source_duration else 0.0
    lines = [
        "# Video Pre-Edit Report",
        "",
        f"- Tool version: {TOOL_VERSION}",
        f"- Reported: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"- Source file: {markdown_inline_code(source_name)}",
        f"- Planned output file: {markdown_inline_code(output_name)}",
        (
            "- Render state: rendered; video stream, audio stream, and duration verified"
            if rendered
            else "- Render state: dry-run plan only"
        ),
        "",
        "## Duration",
        "",
        f"- Source: {format_timestamp(source_duration)}",
        f"- Planned output: {format_timestamp(expected_duration)}",
        f"- Removed: {format_timestamp(removed)} ({removed_ratio * 100:.1f}%)",
        "",
        "## Settings",
        "",
    ]
    if plan_name:
        lines.insert(6, f"- Approved plan file: {markdown_inline_code(plan_name)}")
    for key, value in settings.items():
        lines.append(
            f"- {markdown_plain_text(key)}: {markdown_inline_code(value)}"
        )

    lines += ["", "## Cuts", ""]
    if cuts:
        lines += [
            "| Start | End | Duration | Reason | Review |",
            "|---:|---:|---:|---|---|",
        ]
        for cut in cuts:
            review = (
                "check"
                if cut.duration > LONG_CUT_WARNING_SECONDS
                or any("restart" in reason for reason in cut.reasons)
                else "standard"
            )
            lines.append(
                "| "
                + " | ".join(
                    [
                        format_timestamp(cut.start),
                        format_timestamp(cut.end),
                        format_timestamp(cut.duration),
                        markdown_table_cell(", ".join(cut.reasons)),
                        review,
                    ]
                )
                + " |"
            )
    else:
        lines.append("No cuts were proposed.")

    lines += ["", "## Protected ranges", ""]
    if protected:
        lines += [
            "| Start | End | Reason |",
            "|---:|---:|---|",
        ]
        for start, end in protected:
            lines.append(
                f"| {format_timestamp(start)} | {format_timestamp(end)} | user-protected; no cuts allowed |"
            )
    else:
        lines.append("No protected ranges were supplied.")

    lines += ["", "## Spoken marker analysis", ""]
    for key, value in marker_summary.items():
        lines.append(
            f"- {markdown_plain_text(key)}: {markdown_inline_code(value)}"
        )

    lines += ["", "## Local audio", ""]
    for key, value in audio_summary.items():
        lines.append(
            f"- {markdown_plain_text(key)}: {markdown_inline_code(value)}"
        )

    lines += ["", "## Verification", ""]
    if verification:
        for key, value in verification.items():
            lines.append(
                f"- {markdown_plain_text(key)}: {markdown_inline_code(value)}"
            )
    else:
        lines.append("- Not run because this was a dry run.")

    lines += ["", "## Warnings and review", ""]
    if warnings:
        for warning in warnings:
            lines.append(f"- {markdown_plain_text(warning)}")
    else:
        lines.append("- No automatic warning threshold was crossed.")
    lines += [
        "- All timestamps refer to the original source.",
        "- Review every spoken-marker cut and every long cut before replacing a manual edit.",
        "- Keep the source file until the new output passes the review checklist.",
        "",
    ]
    return "\n".join(lines)


def write_text_safely(
    destination: Path,
    content: str,
    *,
    overwrite: bool,
    label: str = "Report",
) -> None:
    if destination.exists() and not overwrite:
        raise PreEditError(
            f"{label} already exists: {destination.name}. "
            "Use --overwrite only after reviewing it."
        )
    destination.parent.mkdir(parents=False, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".tmp",
        prefix=f".video-pre-edit-{label.lower()}-",
        dir=destination.parent,
        delete=False,
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    try:
        install_new_file(
            temporary_path,
            destination,
            overwrite=overwrite,
            label=label,
        )
    finally:
        temporary_path.unlink(missing_ok=True)


def install_new_file(
    temporary_path: Path,
    destination: Path,
    *,
    overwrite: bool,
    label: str,
) -> None:
    if overwrite:
        os.replace(temporary_path, destination)
        return

    try:
        os.link(temporary_path, destination)
    except FileExistsError as error:
        raise PreEditError(
            f"{label} appeared during the run: {destination.name}. Nothing was overwritten."
        ) from error
    except OSError:
        # Some removable and network filesystems do not support hard links.
        # Exclusive creation keeps the no-overwrite rule on those filesystems.
        pass
    else:
        try:
            temporary_path.unlink()
        except OSError as error:
            destination.unlink(missing_ok=True)
            raise PreEditError(
                f"{label} could not be finalized safely: {destination.name}."
            ) from error
        return

    descriptor: int | None = None
    created_destination = False
    try:
        descriptor = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o666,
        )
        created_destination = True
        with os.fdopen(descriptor, "wb") as output_handle:
            descriptor = None
            with temporary_path.open("rb") as input_handle:
                shutil.copyfileobj(input_handle, output_handle)
            output_handle.flush()
            os.fsync(output_handle.fileno())
        temporary_path.unlink()
    except FileExistsError as error:
        raise PreEditError(
            f"{label} appeared during the run: {destination.name}. Nothing was overwritten."
        ) from error
    except OSError as error:
        if created_destination:
            destination.unlink(missing_ok=True)
        raise PreEditError(
            f"{label} could not be installed safely: {destination.name}."
        ) from error
    except BaseException:
        if created_destination:
            destination.unlink(missing_ok=True)
        raise
    finally:
        if descriptor is not None:
            os.close(descriptor)


def install_output_safely(
    temporary_output: Path,
    destination: Path,
    source: Path,
    *,
    overwrite: bool,
) -> None:
    if source.resolve() == destination.resolve():
        raise PreEditError("Output must not be the source file.")
    if destination.exists() and not overwrite:
        raise PreEditError(
            f"Output already exists: {destination.name}. Nothing was overwritten."
        )
    install_new_file(
        temporary_output,
        destination,
        overwrite=overwrite,
        label="Output",
    )


def plan_payload(
    args: argparse.Namespace,
    *,
    source: Path,
    output: Path,
    source_info: MediaInfo,
    plan_path: Path,
) -> dict[str, object]:
    options = {
        name: list(value) if isinstance(value := getattr(args, name), list) else value
        for name in PLAN_OPTION_NAMES
    }
    words_json_relative = None
    if args.words_json:
        words_path = Path(args.words_json).expanduser().resolve()
        words_json_relative = os.path.relpath(words_path, plan_path.parent)
    return {
        "schema": PLAN_SCHEMA,
        "toolVersion": TOOL_VERSION,
        "source": {
            "name": source.name,
            "sizeBytes": source.stat().st_size,
            "durationSeconds": round(source_info.duration, 6),
        },
        "outputName": output.name,
        "options": options,
        "wordsJsonRelativeToPlan": words_json_relative,
    }


def load_approved_plan(
    plan_path: Path,
    *,
    source: Path,
    output: Path,
    source_info: MediaInfo,
    args: argparse.Namespace,
) -> None:
    if not plan_path.exists() or not plan_path.is_file():
        raise PreEditError("Approved plan file does not exist.")
    if plan_path.stat().st_size > 128 * 1024:
        raise PreEditError("Approved plan file is unexpectedly large.")
    try:
        data = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PreEditError("Approved plan file is not readable JSON.") from error
    if not isinstance(data, dict) or data.get("schema") != PLAN_SCHEMA:
        raise PreEditError("Approved plan file has an unsupported schema.")
    if data.get("toolVersion") != TOOL_VERSION:
        raise PreEditError(
            "Approved plan was created by a different tool version. Run a new dry plan."
        )

    source_record = data.get("source")
    if not isinstance(source_record, dict):
        raise PreEditError("Approved plan is missing its source record.")
    if source_record.get("name") != source.name:
        raise PreEditError("Approved plan was created for a different source filename.")
    if source_record.get("sizeBytes") != source.stat().st_size:
        raise PreEditError("Source size changed after the dry plan. Run a new dry plan.")
    try:
        planned_duration = float(source_record["durationSeconds"])
    except (KeyError, TypeError, ValueError) as error:
        raise PreEditError("Approved plan has an invalid source duration.") from error
    duration_tolerance = max(0.05, source_info.duration * 0.001)
    if (
        not math.isfinite(planned_duration)
        or abs(planned_duration - source_info.duration) > duration_tolerance
    ):
        raise PreEditError("Source duration changed after the dry plan. Run a new dry plan.")
    if data.get("outputName") != output.name:
        raise PreEditError("Approved plan was created for a different output filename.")

    options = data.get("options")
    if not isinstance(options, dict) or set(options) != set(PLAN_OPTION_NAMES):
        raise PreEditError("Approved plan has missing or unexpected edit settings.")

    bool_names = {
        "keep_silence",
        "detect_restarts",
        "detect_full_stop_restart",
        "confirm_full_restart",
        "enhance_audio",
    }
    list_names = {"cut", "protect"}
    number_names = {"silence_threshold", "min_silence"}
    string_names = {
        "restart_phrase",
        "full_restart_phrase",
        "whisper_model",
        "language",
    }
    for name in PLAN_OPTION_NAMES:
        value = options[name]
        if name in bool_names and not isinstance(value, bool):
            raise PreEditError(f"Approved plan setting {name} must be true or false.")
        if name in list_names and (
            not isinstance(value, list)
            or any(not isinstance(item, str) for item in value)
        ):
            raise PreEditError(f"Approved plan setting {name} must be a text list.")
        if name in number_names and (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):
            raise PreEditError(f"Approved plan setting {name} must be finite and numeric.")
        if name == "padding_ms" and (
            isinstance(value, bool) or not isinstance(value, int)
        ):
            raise PreEditError("Approved plan setting padding_ms must be an integer.")
        if name in string_names and not isinstance(value, str):
            raise PreEditError(f"Approved plan setting {name} must be text.")
        setattr(args, name, list(value) if isinstance(value, list) else value)

    words_relative = data.get("wordsJsonRelativeToPlan")
    if words_relative is not None and not isinstance(words_relative, str):
        raise PreEditError("Approved plan has an invalid timed-word path.")
    args.words_json = (
        str((plan_path.parent / words_relative).resolve())
        if words_relative
        else None
    )


def parser() -> argparse.ArgumentParser:
    value_parser = argparse.ArgumentParser(
        description=(
            "Create a conservative local first-pass edit without changing the source."
        )
    )
    value_parser.add_argument("input", help="Source video")
    value_parser.add_argument(
        "output",
        nargs="?",
        help="New MP4 output. Default: SOURCE_preedit.mp4",
    )
    value_parser.add_argument(
        "--silence-threshold",
        type=float,
        default=DEFAULT_SILENCE_THRESHOLD_DB,
        help=f"Quiet-audio threshold in dB (default: {DEFAULT_SILENCE_THRESHOLD_DB:g})",
    )
    value_parser.add_argument(
        "--min-silence",
        type=float,
        default=DEFAULT_MIN_SILENCE,
        help=f"Minimum quiet pause to consider in seconds (default: {DEFAULT_MIN_SILENCE:g})",
    )
    value_parser.add_argument(
        "--padding-ms",
        type=int,
        default=DEFAULT_PADDING_MS,
        help=f"Audio kept on each side of a quiet pause (default: {DEFAULT_PADDING_MS})",
    )
    value_parser.add_argument(
        "--keep-silence",
        action="store_true",
        help="Do not propose silence cuts. Useful for marker-only runs.",
    )
    value_parser.add_argument(
        "--cut",
        action="append",
        default=[],
        metavar="START-END",
        help="Exact original-source range approved for removal. Repeat as needed.",
    )
    value_parser.add_argument(
        "--protect",
        action="append",
        default=[],
        metavar="START-END",
        help="Original-source range where no cuts are allowed. Repeat as needed.",
    )
    value_parser.add_argument(
        "--detect-restarts",
        action="store_true",
        help="Use local timed words to remove exact spoken restart markers.",
    )
    value_parser.add_argument(
        "--restart-phrase",
        default=DEFAULT_RESTART_PHRASE,
        help=f"Exact spoken marker (default: {DEFAULT_RESTART_PHRASE!r})",
    )
    value_parser.add_argument(
        "--detect-full-stop-restart",
        action="store_true",
        help="Find the exact full-stop marker and discard everything before the last one.",
    )
    value_parser.add_argument(
        "--confirm-full-restart",
        action="store_true",
        help="Required with --detect-full-stop-restart because it can remove a large opening.",
    )
    value_parser.add_argument(
        "--full-restart-phrase",
        default=DEFAULT_FULL_RESTART_PHRASE,
        help=f"Exact full restart marker (default: {DEFAULT_FULL_RESTART_PHRASE!r})",
    )
    value_parser.add_argument(
        "--words-json",
        help="Optional local timed-word JSON instead of running Whisper.",
    )
    value_parser.add_argument(
        "--whisper-model",
        default="base",
        help="Local Whisper model used only for marker detection (default: base)",
    )
    value_parser.add_argument(
        "--language",
        default="en",
        help="Spoken language code for local Whisper (default: en)",
    )
    value_parser.add_argument(
        "--enhance-audio",
        action="store_true",
        help="Apply local speech EQ, compression, fixed gain, and a limiter.",
    )
    value_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write the cut report without rendering a video.",
    )
    value_parser.add_argument(
        "--plan-output",
        help=(
            "Dry-run plan path. Default: OUTPUT_STEM_plan.json. "
            "Use the plan with --from-plan to preserve every chosen option."
        ),
    )
    value_parser.add_argument(
        "--from-plan",
        help=(
            "Render with the exact options saved by a prior dry run. "
            "Do not combine with edit-setting flags."
        ),
    )
    value_parser.add_argument(
        "--report",
        help="Report path. Default: OUTPUT_STEM_report.md",
    )
    value_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing an existing output/report/plan, never the source.",
    )
    return value_parser


def validate_arguments(args: argparse.Namespace) -> None:
    if args.dry_run and args.from_plan:
        raise PreEditError("--dry-run cannot be combined with --from-plan.")
    if args.plan_output and not args.dry_run:
        raise PreEditError("--plan-output is used only with --dry-run.")
    if args.from_plan:
        raw_arguments = getattr(args, "_raw_argv", [])
        conflicting = sorted(
            {
                flag
                for token in raw_arguments
                for flag in PLAN_CONTROL_FLAGS
                if token == flag or token.startswith(f"{flag}=")
            }
        )
        if conflicting:
            raise PreEditError(
                "--from-plan already supplies the edit settings. Remove: "
                + ", ".join(conflicting)
            )
    if (
        not math.isfinite(args.min_silence)
        or args.min_silence < 0.3
        or args.min_silence > 30
    ):
        raise PreEditError("--min-silence must be from 0.3 to 30 seconds.")
    if args.padding_ms < 0 or args.padding_ms > 2000:
        raise PreEditError("--padding-ms must be from 0 to 2000.")
    if not math.isfinite(args.silence_threshold) or not (
        -90 <= args.silence_threshold <= -10
    ):
        raise PreEditError("--silence-threshold must be from -90 to -10 dB.")
    if args.detect_full_stop_restart and not args.confirm_full_restart:
        raise PreEditError(
            "--detect-full-stop-restart also requires --confirm-full-restart."
        )
    if args.words_json and not (
        args.detect_restarts or args.detect_full_stop_restart
    ):
        raise PreEditError(
            "--words-json is only used with spoken-marker detection."
        )


def execute(args: argparse.Namespace) -> tuple[Path | None, Path]:
    validate_arguments(args)
    require_local_tools()

    source = Path(args.input).expanduser()
    if not source.exists() or not source.is_file():
        raise PreEditError("Source video does not exist.")
    source = source.resolve()

    output = (
        Path(args.output).expanduser()
        if args.output
        else source.with_name(f"{source.stem}_preedit.mp4")
    )
    if output.suffix.lower() != ".mp4":
        raise PreEditError("This release currently supports MP4 output only.")
    if not output.is_absolute():
        output = (Path.cwd() / output).resolve()
    else:
        output = output.resolve()
    if not output.parent.exists():
        raise PreEditError("Output folder does not exist.")
    if output.resolve() == source.resolve():
        raise PreEditError("Output must use a different filename from the source.")
    if output.exists() and not args.overwrite and not args.dry_run:
        raise PreEditError(
            f"Output already exists: {output.name}. Nothing was overwritten."
        )

    report_path = (
        Path(args.report).expanduser()
        if args.report
        else output.with_name(
            f"{output.stem}_{'dry_run_' if args.dry_run else ''}report.md"
        )
    )
    if not report_path.is_absolute():
        report_path = (Path.cwd() / report_path).resolve()
    else:
        report_path = report_path.resolve()
    if not report_path.parent.exists():
        raise PreEditError("Report folder does not exist.")
    if report_path.resolve() in {source.resolve(), output.resolve()}:
        raise PreEditError("Report must use a separate filename.")
    if report_path.exists() and not args.overwrite:
        raise PreEditError(
            f"Report already exists: {report_path.name}. Nothing was overwritten."
        )

    from_plan_path: Path | None = None
    if args.from_plan:
        from_plan_path = Path(args.from_plan).expanduser()
        if not from_plan_path.is_absolute():
            from_plan_path = (Path.cwd() / from_plan_path).resolve()
        else:
            from_plan_path = from_plan_path.resolve()

    plan_path: Path | None = None
    if args.dry_run:
        plan_path = (
            Path(args.plan_output).expanduser()
            if args.plan_output
            else output.with_name(f"{output.stem}_plan.json")
        )
        if not plan_path.is_absolute():
            plan_path = (Path.cwd() / plan_path).resolve()
        else:
            plan_path = plan_path.resolve()
        if not plan_path.parent.exists():
            raise PreEditError("Plan folder does not exist.")
        if plan_path.resolve() in {
            source.resolve(),
            output.resolve(),
            report_path.resolve(),
        }:
            raise PreEditError("Plan must use a separate filename.")
        if plan_path.exists() and not args.overwrite:
            raise PreEditError(
                f"Plan already exists: {plan_path.name}. Nothing was overwritten."
            )

    source_info = probe_media(source)
    reject_unsafe_source_layout(source_info)
    if from_plan_path:
        load_approved_plan(
            from_plan_path,
            source=source,
            output=output,
            source_info=source_info,
            args=args,
        )
        validate_arguments(args)
    duration = source_info.duration

    try:
        protected = merge_plain_ranges(
            [parse_time_range(value) for value in args.protect],
            duration,
        )
    except ValueError as error:
        raise PreEditError(str(error)) from error

    try:
        approved_cuts = [
            parse_time_range(value)
            for value in args.cut
        ]
    except ValueError as error:
        raise PreEditError(str(error)) from error

    print(f"Analyzing {source.name} locally...")
    cuts: list[EditRange] = [
        EditRange(start, end, ("user-approved range",))
        for start, end in approved_cuts
    ]
    if not args.keep_silence:
        silences = detect_silence(
            source,
            duration,
            args.silence_threshold,
            args.min_silence,
        )
        cuts.extend(
            silence_ranges_to_cuts(
                silences,
                duration,
                args.padding_ms / 1000,
            )
        )
    preliminary_cuts = normalize_cuts(cuts, duration, protected)
    preliminary_kept = invert_cuts(preliminary_cuts, duration)

    marker_summary: dict[str, object] = {
        "enabled": bool(
            args.detect_restarts or args.detect_full_stop_restart
        ),
        "restart phrase": args.restart_phrase,
        "restart markers found": 0,
        "restart markers skipped for protected conflict": 0,
        "full restart markers found": 0,
        "transcript fallback": "none",
    }
    transcript_warning: str | None = None

    if args.detect_restarts or args.detect_full_stop_restart:
        if args.words_json:
            words_path = Path(args.words_json).expanduser().resolve()
            if not words_path.exists():
                raise PreEditError("Timed-word JSON does not exist.")
            words = load_timed_words(words_path)
        else:
            words = transcribe_with_local_whisper(
                source,
                args.whisper_model,
                args.language,
                args.restart_phrase,
                args.full_restart_phrase,
            )

        transcript_warning = transcript_problem(words, args.language)
        if transcript_warning:
            marker_summary["transcript fallback"] = (
                f"silence-only; {transcript_warning}"
            )
        else:
            if args.detect_restarts:
                restart_spans = find_exact_marker_spans(
                    words,
                    args.restart_phrase,
                )
                restart_spans = [
                    span
                    for span in restart_spans
                    if not marker_overlaps_protected(span, protected)
                ]
                marker_summary["restart markers found"] = len(restart_spans)
                restart_cuts = restart_marker_cuts(
                    preliminary_kept,
                    restart_spans,
                )
                safe_restart_cuts = [
                    cut
                    for cut in restart_cuts
                    if not marker_overlaps_protected(
                        (cut.start, cut.end),
                        protected,
                    )
                ]
                marker_summary[
                    "restart markers skipped for protected conflict"
                ] = len(restart_cuts) - len(safe_restart_cuts)
                restart_reason = f"spoken restart marker: {args.restart_phrase}"
                cuts.extend(
                    EditRange(cut.start, cut.end, (restart_reason,))
                    for cut in safe_restart_cuts
                )

            if args.detect_full_stop_restart:
                full_spans = find_exact_marker_spans(
                    words,
                    args.full_restart_phrase,
                )
                full_spans = [
                    span
                    for span in full_spans
                    if not marker_overlaps_protected(span, protected)
                ]
                marker_summary["full restart markers found"] = len(full_spans)
                if full_spans:
                    _, last_end = full_spans[-1]
                    if any(
                        protected_start < last_end and protected_end > 0
                        for protected_start, protected_end in protected
                    ):
                        raise PreEditError(
                            "The confirmed full-restart cut crosses a protected range. "
                            "Remove the conflict or use ordinary restart markers."
                        )
                    cuts.append(
                        EditRange(
                            0.0,
                            last_end,
                            (
                                "confirmed full restart marker: "
                                + args.full_restart_phrase,
                            ),
                        )
                    )

    final_cuts = normalize_cuts(cuts, duration, protected)
    kept_segments = invert_cuts(final_cuts, duration)
    expected_duration = sum(end - start for start, end in kept_segments)
    if expected_duration < 0.50:
        raise PreEditError(
            "The proposed cut plan leaves less than half a second. No output was written."
        )

    removed_ratio = (duration - expected_duration) / duration
    warnings = [
        "Container and stream metadata are not preserved; the encoder may add new technical tags."
    ]
    if removed_ratio > REMOVAL_WARNING_RATIO:
        warnings.append(
            f"Planned removal is {removed_ratio * 100:.1f}%, above the 45% review threshold."
        )
    for cut in final_cuts:
        if cut.duration > LONG_CUT_WARNING_SECONDS:
            warnings.append(
                "Long cut needs review: "
                f"{format_timestamp(cut.start)} to {format_timestamp(cut.end)} "
                f"({format_timestamp(cut.duration)})."
            )
    if transcript_warning:
        warnings.append(
            f"Transcript-driven cuts were disabled: {transcript_warning}."
        )
    skipped_markers = int(
        marker_summary["restart markers skipped for protected conflict"]
    )
    if skipped_markers:
        noun_and_verb = (
            "restart marker cut was"
            if skipped_markers == 1
            else "restart marker cuts were"
        )
        warnings.append(
            f"{skipped_markers} {noun_and_verb} skipped because it crossed a protected range."
        )

    settings: dict[str, object] = {
        "silence threshold": f"{args.silence_threshold:g} dB",
        "minimum silence": f"{args.min_silence:g} seconds",
        "speech padding": f"{args.padding_ms} ms per side",
        "silence cuts enabled": not bool(args.keep_silence),
        "user-approved exact ranges": len(approved_cuts),
        "local audio enhancement": bool(args.enhance_audio),
        "spoken-marker language": args.language,
        "dry run": bool(args.dry_run),
    }
    audio_summary: dict[str, object] = {
        "applied": False,
        "method": (
            "none"
            if not args.enhance_audio
            else "pending local render"
        ),
    }
    verification: dict[str, object] | None = None
    rendered = False

    if not args.dry_run:
        require_libx264_encoder()
        with tempfile.TemporaryDirectory(
            prefix=".video-pre-edit-",
            dir=output.parent,
        ) as temporary_directory:
            temporary_root = Path(temporary_directory)
            cut_output = temporary_root / "cut.mp4"
            final_output = temporary_root / "final.mp4"
            render_cut_video(source, cut_output, kept_segments)

            if args.enhance_audio:
                audio_summary = apply_local_audio_enhancement(
                    cut_output,
                    final_output,
                )
                audio_summary["method"] = (
                    "high-pass, light EQ, compression, fixed measured gain, ceiling limiter"
                )
            else:
                shutil.copy2(cut_output, final_output)

            verification = verification_for(
                final_output,
                expected_duration,
            )
            install_output_safely(
                final_output,
                output,
                source,
                overwrite=args.overwrite,
            )
            rendered = True

    report = report_markdown(
        source_name=source.name,
        output_name=output.name,
        rendered=rendered,
        source_duration=duration,
        expected_duration=expected_duration,
        cuts=final_cuts,
        protected=protected,
        settings=settings,
        marker_summary=marker_summary,
        audio_summary=audio_summary,
        verification=verification,
        warnings=warnings,
        plan_name=(plan_path or from_plan_path).name
        if (plan_path or from_plan_path)
        else None,
    )
    write_text_safely(
        report_path,
        report,
        overwrite=args.overwrite,
    )
    if plan_path:
        plan = plan_payload(
            args,
            source=source,
            output=output,
            source_info=source_info,
            plan_path=plan_path,
        )
        write_text_safely(
            plan_path,
            f"{json.dumps(plan, indent=2, sort_keys=True)}\n",
            overwrite=args.overwrite,
            label="Plan",
        )

    if rendered:
        print(f"Created {output.name}")
    else:
        print("Dry run complete; no video was rendered.")
    print(f"Report: {report_path.name}")
    if plan_path:
        print(f"Approved plan: {plan_path.name}")
        print(
            "Next: render with the same source and output plus "
            f"--from-plan {plan_path.name!r}."
        )
    return (output if rendered else None), report_path


def main(argv: Sequence[str] | None = None) -> int:
    try:
        raw_arguments = list(argv) if argv is not None else sys.argv[1:]
        args = parser().parse_args(raw_arguments)
        args._raw_argv = raw_arguments
        execute(args)
        return 0
    except (PreEditError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Stopped. The source file was not changed.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
