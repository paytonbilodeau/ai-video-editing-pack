#!/usr/bin/env python3
"""Normalize a supplied word-timed transcript without calling a provider."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


SCHEMA = "ai-mentorship-transcript-v1"


class TranscriptError(RuntimeError):
    """A safe user-facing transcript error."""


def finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def safe_label(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.replace("\\", "/")
    return "/" not in normalized and normalized not in {".", ".."}


def normalize(payload: object, source_label: str | None = None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TranscriptError("Transcript input must be one JSON object.")
    duration = payload.get("durationSeconds", payload.get("duration"))
    if not finite_number(duration) or duration <= 0:
        raise TranscriptError("durationSeconds must be a positive finite number.")
    segments = payload.get("segments")
    if not isinstance(segments, list) or not segments:
        raise TranscriptError("segments must contain at least one segment.")
    label = source_label or payload.get("sourceLabel") or "source-media"
    if not safe_label(label):
        raise TranscriptError("sourceLabel must be one basename without a path.")

    normalized_segments = []
    prior_segment_end = 0.0
    for segment_index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            raise TranscriptError(f"segments[{segment_index}] must be an object.")
        start = segment.get("start")
        end = segment.get("end")
        text = segment.get("text")
        words = segment.get("words")
        if not finite_number(start) or not finite_number(end) or not (0 <= start < end <= duration):
            raise TranscriptError(f"segments[{segment_index}] has an invalid time range.")
        if start < prior_segment_end:
            raise TranscriptError(f"segments[{segment_index}] overlaps the prior segment.")
        if not isinstance(text, str) or not text.strip():
            raise TranscriptError(f"segments[{segment_index}].text is required.")
        if not isinstance(words, list) or not words:
            raise TranscriptError(f"segments[{segment_index}] needs real word timings.")
        normalized_words = []
        prior_word_end = float(start)
        for word_index, word in enumerate(words):
            if not isinstance(word, dict):
                raise TranscriptError(
                    f"segments[{segment_index}].words[{word_index}] must be an object."
                )
            token = word.get("word")
            word_start = word.get("start")
            word_end = word.get("end")
            if not isinstance(token, str) or not token.strip():
                raise TranscriptError(
                    f"segments[{segment_index}].words[{word_index}].word is required."
                )
            if (
                not finite_number(word_start)
                or not finite_number(word_end)
                or not (start <= word_start < word_end <= end)
                or word_start < prior_word_end
            ):
                raise TranscriptError(
                    f"segments[{segment_index}].words[{word_index}] has invalid exact timing."
                )
            normalized_words.append(
                {"word": token.strip(), "start": float(word_start), "end": float(word_end)}
            )
            prior_word_end = float(word_end)
        normalized_segments.append(
            {
                "start": float(start),
                "end": float(end),
                "text": text.strip(),
                "words": normalized_words,
            }
        )
        prior_segment_end = float(end)
    return {
        "schema": SCHEMA,
        "sourceLabel": label,
        "durationSeconds": float(duration),
        "segments": normalized_segments,
    }


def write_new(path: Path, payload: dict[str, Any], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise TranscriptError("Output exists. Choose a new path or approve --overwrite.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-label")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.input.resolve() == args.output.resolve():
            raise TranscriptError("Output cannot replace the input transcript.")
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        normalized = normalize(payload, args.source_label)
        write_new(args.output, normalized, args.overwrite)
    except (OSError, json.JSONDecodeError, TranscriptError) as error:
        parser.error(str(error))
    print(json.dumps({"ok": True, "segments": len(normalized["segments"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
