#!/usr/bin/env python3
"""Validate, caption, and extract an approved source-grounded content map."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


MAP_SCHEMA = "ai-mentorship-content-map-v1"
TRANSCRIPT_SCHEMA = "ai-mentorship-transcript-v1"
OUTPUT_RANGES = {
    "long_cutdown": (120.0, 1800.0),
    "mid": (300.0, 1200.0),
    "short": (20.0, 90.0),
    "email": (0.001, math.inf),
    "text_post": (0.001, math.inf),
    "caption": (0.001, math.inf),
}
VIDEO_TYPES = {"long_cutdown", "mid", "short"}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")


class WaterfallError(RuntimeError):
    """A safe user-facing Waterfall error."""


def finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def safe_label(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.replace("\\", "/")
    return "/" not in normalized and normalized not in {".", ".."}


def validate_content_map(payload: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Content map must be one JSON object."]
    if payload.get("schema") != MAP_SCHEMA:
        errors.append(f"schema must be {MAP_SCHEMA}")
    source = payload.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
        source = {}
    if not safe_label(source.get("label")):
        errors.append("source.label must be one basename without a path")
    if not isinstance(source.get("sha256"), str) or not SHA256_PATTERN.fullmatch(source["sha256"]):
        errors.append("source.sha256 must be one lowercase SHA-256 value")
    duration = source.get("durationSeconds")
    if not finite_number(duration) or duration <= 0:
        errors.append("source.durationSeconds must be a positive finite number")
        duration = 0.0

    claims = payload.get("claimLedger")
    if not isinstance(claims, list) or not claims:
        errors.append("claimLedger must contain at least one claim")
        claims = []
    claim_by_id: dict[str, dict[str, Any]] = {}
    for index, claim in enumerate(claims):
        label = f"claimLedger[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{label} must be an object")
            continue
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not ID_PATTERN.fullmatch(claim_id):
            errors.append(f"{label}.id is invalid")
        elif claim_id in claim_by_id:
            errors.append(f"{label}.id must be unique")
        else:
            claim_by_id[claim_id] = claim
        if not isinstance(claim.get("text"), str) or not claim["text"].strip():
            errors.append(f"{label}.text is required")
        start = claim.get("sourceStart")
        end = claim.get("sourceEnd")
        if not finite_number(start) or not finite_number(end) or not (0 <= start < end <= duration):
            errors.append(f"{label} has an invalid source range")

    outputs = payload.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        errors.append("outputs must contain at least one planned output")
        outputs = []
    output_ids = set()
    for index, output in enumerate(outputs):
        label = f"outputs[{index}]"
        if not isinstance(output, dict):
            errors.append(f"{label} must be an object")
            continue
        output_id = output.get("id")
        if not isinstance(output_id, str) or not ID_PATTERN.fullmatch(output_id):
            errors.append(f"{label}.id is invalid")
        elif output_id in output_ids:
            errors.append(f"{label}.id must be unique")
        else:
            output_ids.add(output_id)
        output_type = output.get("type")
        if output_type not in OUTPUT_RANGES:
            errors.append(f"{label}.type is invalid")
        if not isinstance(output.get("title"), str) or not output["title"].strip():
            errors.append(f"{label}.title is required")
        start = output.get("sourceStart")
        end = output.get("sourceEnd")
        valid_range = finite_number(start) and finite_number(end) and 0 <= start < end <= duration
        if not valid_range:
            errors.append(f"{label} has an invalid source range")
        elif output_type in OUTPUT_RANGES:
            clip_duration = end - start
            minimum, maximum = OUTPUT_RANGES[output_type]
            if not minimum <= clip_duration <= maximum:
                errors.append(
                    f"{label} duration must be between {minimum:g} and {maximum:g} seconds"
                )
        claim_ids = output.get("claimIds")
        if not isinstance(claim_ids, list) or not claim_ids or any(
            not isinstance(item, str) for item in claim_ids
        ):
            errors.append(f"{label}.claimIds must contain at least one claim ID")
            claim_ids = []
        for claim_id in claim_ids:
            claim = claim_by_id.get(claim_id)
            if claim is None:
                errors.append(f"{label} references unknown claim {claim_id}")
            elif valid_range:
                claim_start = claim.get("sourceStart")
                claim_end = claim.get("sourceEnd")
                if finite_number(claim_start) and finite_number(claim_end) and not (
                    start <= claim_start and claim_end <= end
                ):
                    errors.append(f"{label} does not include the full range for claim {claim_id}")
        if not isinstance(output.get("approved"), bool):
            errors.append(f"{label}.approved must be true or false")
    return errors


def load_validated_map(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise WaterfallError(f"Could not read content map: {error}") from error
    errors = validate_content_map(payload)
    if errors:
        raise WaterfallError("Content map failed validation:\n- " + "\n- ".join(errors))
    return payload


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True, shell=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "local media command failed").strip()
        raise WaterfallError("Local media command failed:\n" + "\n".join(detail.splitlines()[-8:]))
    return result


def probe_duration(path: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    try:
        duration = float(result.stdout.strip())
    except ValueError as error:
        raise WaterfallError("ffprobe returned an invalid duration.") from error
    if not math.isfinite(duration) or duration <= 0:
        raise WaterfallError("The media file has no usable duration.")
    return duration


def require_media_tools() -> None:
    missing = [name for name in ("ffmpeg", "ffprobe") if shutil.which(name) is None]
    if missing:
        raise WaterfallError("Missing local requirement: " + ", ".join(missing))


def extract_clips(source: Path, content_map: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    require_media_tools()
    if not source.is_file() or source.is_symlink():
        raise WaterfallError("Source must be one regular local media file.")
    if output_dir.exists():
        raise WaterfallError("Output directory already exists. Choose a new directory.")
    if source.name != content_map["source"]["label"]:
        raise WaterfallError("Source basename does not match the approved content map.")
    expected_hash = content_map["source"]["sha256"]
    before_hash = sha256(source)
    if before_hash != expected_hash:
        raise WaterfallError("Source hash does not match the approved content map.")
    source_duration = probe_duration(source)
    expected_duration = float(content_map["source"]["durationSeconds"])
    if abs(source_duration - expected_duration) > 1.0:
        raise WaterfallError("Source duration does not match the approved content map.")
    approved = [
        item
        for item in content_map["outputs"]
        if item["approved"] and item["type"] in VIDEO_TYPES
    ]
    if not approved:
        raise WaterfallError("The approved map has no video outputs to extract.")

    output_dir.mkdir(parents=True)
    receipts = []
    for item in approved:
        output = output_dir / f"{item['id']}.mp4"
        duration = float(item["sourceEnd"] - item["sourceStart"])
        run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-n",
                "-ss",
                f"{item['sourceStart']:.3f}",
                "-i",
                str(source),
                "-t",
                f"{duration:.3f}",
                "-map",
                "0:v:0",
                "-map",
                "0:a?",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                str(output),
            ]
        )
        actual_duration = probe_duration(output)
        if abs(actual_duration - duration) > 0.75:
            raise WaterfallError(f"Extracted duration verification failed for {item['id']}.")
        receipts.append(
            {
                "id": item["id"],
                "type": item["type"],
                "outputLabel": output.name,
                "sourceStart": item["sourceStart"],
                "sourceEnd": item["sourceEnd"],
                "durationSeconds": actual_duration,
                "sha256": sha256(output),
            }
        )
    after_hash = sha256(source)
    if before_hash != after_hash:
        raise WaterfallError("Source hash changed during extraction.")
    receipt = {
        "schema": "ai-mentorship-waterfall-extraction-receipt-v1",
        "sourceLabel": source.name,
        "sourceSha256": before_hash,
        "sourceUnchanged": True,
        "outputs": receipts,
    }
    (output_dir / "extraction-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    return receipt


def transcript_words(transcript: object) -> tuple[float, list[dict[str, Any]]]:
    if not isinstance(transcript, dict) or transcript.get("schema") != TRANSCRIPT_SCHEMA:
        raise WaterfallError(f"Transcript schema must be {TRANSCRIPT_SCHEMA}.")
    duration = transcript.get("durationSeconds")
    if not finite_number(duration) or duration <= 0:
        raise WaterfallError("Transcript durationSeconds is invalid.")
    segments = transcript.get("segments")
    if not isinstance(segments, list) or not segments:
        raise WaterfallError("Transcript needs segments with exact word timings.")
    words = []
    prior_end = 0.0
    for segment in segments:
        if not isinstance(segment, dict) or not isinstance(segment.get("words"), list):
            raise WaterfallError("Every transcript segment needs exact word timings.")
        for word in segment["words"]:
            if not isinstance(word, dict):
                raise WaterfallError("Each word timing must be an object.")
            token = word.get("word")
            start = word.get("start")
            end = word.get("end")
            if (
                not isinstance(token, str)
                or not token.strip()
                or not finite_number(start)
                or not finite_number(end)
                or not (0 <= start < end <= duration)
                or start < prior_end
            ):
                raise WaterfallError("Transcript contains an invalid exact word timing.")
            words.append({"word": token.strip(), "start": float(start), "end": float(end)})
            prior_end = float(end)
    if not words:
        raise WaterfallError("Transcript contains no timed words.")
    return float(duration), words


def clip_word_cues(words: list[dict[str, Any]], start: float, end: float) -> list[dict[str, Any]]:
    cues = []
    for word in words:
        if word["end"] <= start or word["start"] >= end:
            continue
        cue_start = round(max(start, word["start"]) - start, 6)
        cue_end = round(min(end, word["end"]) - start, 6)
        if cue_end > cue_start:
            cues.append({"text": word["word"], "start": cue_start, "end": cue_end})
    if not cues:
        raise WaterfallError("No exact word timings fall inside the selected clip.")
    return cues


def vtt_time(seconds: float) -> str:
    milliseconds = round(max(0.0, seconds) * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"


def write_vtt(path: Path, cues: list[dict[str, Any]]) -> None:
    if path.exists():
        raise WaterfallError("Caption output exists. Choose a new output directory.")
    lines = ["WEBVTT", ""]
    for index, cue in enumerate(cues, start=1):
        safe_text = " ".join(cue["text"].replace("-->", "→").split())
        lines.extend(
            [
                str(index),
                f"{vtt_time(cue['start'])} --> {vtt_time(cue['end'])}",
                safe_text,
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def create_captions(
    transcript: dict[str, Any], content_map: dict[str, Any], output_dir: Path
) -> dict[str, Any]:
    if output_dir.exists():
        raise WaterfallError("Caption output directory already exists. Choose a new directory.")
    transcript_duration, words = transcript_words(transcript)
    map_duration = float(content_map["source"]["durationSeconds"])
    if abs(transcript_duration - map_duration) > 0.001:
        raise WaterfallError("Transcript duration does not match the content map.")
    selected = [
        item
        for item in content_map["outputs"]
        if item["approved"] and item["type"] in VIDEO_TYPES
    ]
    if not selected:
        raise WaterfallError("The approved map has no video outputs for captions.")
    output_dir.mkdir(parents=True)
    outputs = []
    for item in selected:
        cues = clip_word_cues(words, item["sourceStart"], item["sourceEnd"])
        output = output_dir / f"{item['id']}.vtt"
        write_vtt(output, cues)
        outputs.append({"id": item["id"], "outputLabel": output.name, "cueCount": len(cues)})
    receipt = {
        "schema": "ai-mentorship-waterfall-caption-receipt-v1",
        "timingMethod": "exact_supplied_word_times_rebased",
        "outputs": outputs,
    }
    (output_dir / "caption-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("map_path", type=Path)
    extract_parser = subparsers.add_parser("extract")
    extract_parser.add_argument("--source", type=Path, required=True)
    extract_parser.add_argument("--map", dest="map_path", type=Path, required=True)
    extract_parser.add_argument("--output-dir", type=Path, required=True)
    extract_parser.add_argument("--confirm", required=True)
    caption_parser = subparsers.add_parser("captions")
    caption_parser.add_argument("--transcript", type=Path, required=True)
    caption_parser.add_argument("--map", dest="map_path", type=Path, required=True)
    caption_parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        content_map = load_validated_map(args.map_path)
        if args.command == "validate":
            result = {"ok": True, "claims": len(content_map["claimLedger"]), "outputs": len(content_map["outputs"])}
        elif args.command == "extract":
            if args.confirm != "EXTRACT":
                raise WaterfallError("Extraction requires --confirm EXTRACT.")
            result = extract_clips(args.source, content_map, args.output_dir)
        else:
            transcript = json.loads(args.transcript.read_text(encoding="utf-8"))
            result = create_captions(transcript, content_map, args.output_dir)
    except (OSError, json.JSONDecodeError, WaterfallError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
