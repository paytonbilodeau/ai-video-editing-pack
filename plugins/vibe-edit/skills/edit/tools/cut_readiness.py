#!/usr/bin/env python3
"""Fail-closed structural readiness checks for a staged video cut.

This helper never listens to media and cannot grant perceptual acceptance. It
checks only the claims and evidence declared in a JSON manifest.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
AUDITORY_METHODS = {"human_listening", "continuous_av_review"}


def issue(code: str, message: str, path: str, scope: str = "structural", severity: str = "blocker") -> dict:
    return {"code": code, "severity": severity, "scope": scope, "path": path, "message": message}


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def speed_factor(clip: dict) -> Fraction:
    return Fraction(str(clip["speed_percentage"])) / 100


def exact_source_span(clip: dict) -> tuple[int, int]:
    """Derive half-open source occupancy from offsets and speed, never reported ends."""
    factor = speed_factor(clip)
    source_start = round(Fraction(str(clip["left_offset"])) * factor)
    source_duration = round(Fraction(str(clip["duration_frames"])) * factor)
    return source_start, source_start + source_duration


def intersects(first: tuple[int, int], second: tuple[int, int]) -> bool:
    return max(first[0], second[0]) < min(first[1], second[1])


def fully_covered(span: tuple[int, int], occupied: list[tuple[int, int]]) -> bool:
    pieces = sorted((max(span[0], a), min(span[1], b)) for a, b in occupied if intersects(span, (a, b)))
    cursor = span[0]
    for start, end in pieces:
        if start > cursor:
            return False
        cursor = max(cursor, end)
        if cursor >= span[1]:
            return True
    return cursor >= span[1]


def timeline_position_for_source(clip: dict, source_frame: int) -> Fraction:
    source_start, _ = exact_source_span(clip)
    return Fraction(clip["timeline_start_frame"]) + Fraction(source_frame - source_start, 1) / speed_factor(clip)


def ordered_hook_fragments(source_span: tuple[int, int], clips: list[dict]) -> list[dict]:
    fragments = []
    for clip in clips:
        clip_start, clip_end = exact_source_span(clip)
        if not intersects(source_span, (clip_start, clip_end)):
            continue
        start = max(source_span[0], clip_start)
        end = min(source_span[1], clip_end)
        fragments.append(
            {
                "clip_id": clip["id"],
                "source_span": (start, end),
                "timeline_start": timeline_position_for_source(clip, start),
                "timeline_end": timeline_position_for_source(clip, end),
            }
        )
    return sorted(fragments, key=lambda fragment: (fragment["timeline_start"], fragment["timeline_end"]))


def validate_manifest(manifest: dict) -> dict:
    issues: list[dict] = []
    diagnostics: dict[str, Any] = {}

    if manifest.get("schema_version") != SCHEMA_VERSION:
        issues.append(issue("UNSUPPORTED_SCHEMA", f"Expected schema_version {SCHEMA_VERSION}.", "schema_version"))

    claim = manifest.get("release_claim")
    if not isinstance(claim, dict) or not isinstance(claim.get("ready"), bool):
        issues.append(issue("INVALID_RELEASE_CLAIM", "release_claim.ready must be a boolean.", "release_claim.ready"))
        ready_claimed = False
    else:
        ready_claimed = claim["ready"]

    manifest_source_id = manifest.get("source_id")
    if not isinstance(manifest_source_id, str) or not manifest_source_id.strip():
        issues.append(issue("NO_SOURCE_ID", "Schema v1 requires one explicit nonempty source_id.", "source_id"))
        manifest_source_id = None

    timeline = manifest.get("timeline")
    clips = timeline.get("clips") if isinstance(timeline, dict) else None
    if not isinstance(clips, list) or not clips:
        issues.append(issue("NO_TIMELINE_CLIPS", "timeline.clips must contain at least one clip.", "timeline.clips"))
        clips = []

    valid_clips: list[dict] = []
    clip_spans: list[dict] = []
    for index, clip in enumerate(clips):
        path = f"timeline.clips[{index}]"
        if not isinstance(clip, dict):
            issues.append(issue("INVALID_CLIP", "Clip must be an object.", path))
            continue
        required = ("id", "source_id", "timeline_start_frame", "duration_frames", "left_offset", "speed_percentage")
        missing = [key for key in required if key not in clip]
        if missing:
            issues.append(issue("INVALID_CLIP", f"Missing clip fields: {', '.join(missing)}.", path))
            continue
        numeric = ("timeline_start_frame", "duration_frames", "left_offset", "speed_percentage")
        if any(not is_number(clip[key]) for key in numeric) or clip["duration_frames"] <= 0 or clip["speed_percentage"] <= 0:
            issues.append(issue("INVALID_CLIP", "Frame values must be numeric; duration and speed must be positive.", path))
            continue
        if manifest_source_id is not None and clip["source_id"] != manifest_source_id:
            issues.append(
                issue(
                    "MULTIPLE_SOURCES_UNSUPPORTED",
                    f"Schema v1 accepts only source_id {manifest_source_id!r}; clip declares {clip['source_id']!r}.",
                    path,
                )
            )
            continue
        source_start, source_end = exact_source_span(clip)
        if source_end <= source_start:
            issues.append(issue("EMPTY_SOURCE_OCCUPANCY", "Derived source span is empty.", path))
            continue
        valid_clips.append(clip)
        clip_spans.append(
            {
                "id": clip["id"],
                "source_id": clip["source_id"],
                "timeline_span": [clip["timeline_start_frame"], clip["timeline_start_frame"] + clip["duration_frames"]],
                "exact_source_span": [source_start, source_end],
                "reported_source_span": [clip.get("reported_source_start"), clip.get("reported_source_end")],
            }
        )
        reported_start = clip.get("reported_source_start")
        reported_end = clip.get("reported_source_end")
        if reported_start is not None and reported_end is not None and (reported_start, reported_end) != (source_start, source_end):
            issues.append(
                issue(
                    "ROUNDED_REPORTED_SOURCE_SPAN_IGNORED",
                    f"Reported [{reported_start}, {reported_end}) differs from exact [{source_start}, {source_end}); exact occupancy was used.",
                    path,
                    severity="warning",
                )
            )
    diagnostics["clip_source_spans"] = clip_spans

    ordered = sorted(valid_clips, key=lambda clip: clip["timeline_start_frame"])
    for previous, current in zip(ordered, ordered[1:]):
        previous_end = previous["timeline_start_frame"] + previous["duration_frames"]
        if current["timeline_start_frame"] < previous_end:
            issues.append(issue("OVERLAPPING_TIMELINE_CLIPS", "Timeline clip ranges overlap.", f"timeline.clips[{current['id']}]"))

    hook = manifest.get("required_hook")
    blocks = hook.get("ordered_blocks") if isinstance(hook, dict) else None
    expected_hook_start = hook.get("expected_start_frame") if isinstance(hook, dict) else None
    if not is_number(expected_hook_start):
        issues.append(
            issue(
                "NO_EXPECTED_HOOK_START",
                "required_hook.expected_start_frame must declare the exact expected timeline start.",
                "required_hook.expected_start_frame",
            )
        )
    if not isinstance(blocks, list) or not blocks:
        issues.append(issue("NO_REQUIRED_HOOK", "required_hook.ordered_blocks must declare the protected hook.", "required_hook.ordered_blocks"))
        blocks = []
    occupied = [exact_source_span(clip) for clip in valid_clips]
    hook_positions: list[tuple[str, Fraction, Fraction]] = []
    for index, block in enumerate(blocks):
        path = f"required_hook.ordered_blocks[{index}]"
        if not isinstance(block, dict) or not isinstance(block.get("source_span"), list) or len(block["source_span"]) != 2:
            issues.append(issue("INVALID_HOOK_BLOCK", "Hook block needs id and half-open source_span.", path))
            continue
        start, end = block["source_span"]
        if not all(is_number(value) for value in (start, end)) or start >= end:
            issues.append(issue("INVALID_HOOK_BLOCK", "Hook source_span must be increasing numeric frames.", path))
            continue
        source_span = (int(start), int(end))
        if not fully_covered(source_span, occupied):
            issues.append(issue("MISSING_REQUIRED_HOOK", f"Required hook block {block.get('id', index)} is not fully retained.", path))
            continue
        fragments = ordered_hook_fragments(source_span, valid_clips)
        if not fragments:
            issues.append(issue("MISSING_REQUIRED_HOOK", f"Required hook block {block.get('id', index)} has no retained fragments.", path))
            continue
        cursor = source_span[0]
        internal_order_ok = True
        for fragment in fragments:
            fragment_start, fragment_end = fragment["source_span"]
            if fragment_start != cursor:
                internal_order_ok = False
                break
            cursor = fragment_end
        if cursor != source_span[1]:
            internal_order_ok = False
        if not internal_order_ok:
            issues.append(
                issue(
                    "REORDERED_HOOK_INTERNAL",
                    f"Required hook block {block.get('id', index)} is covered, but its split source fragments are duplicated or out of source order.",
                    path,
                )
            )
        hook_positions.append(
            (str(block.get("id", index)), fragments[0]["timeline_start"], fragments[-1]["timeline_end"])
        )
    for (previous_id, _, previous_end), (current_id, current_start, _) in zip(hook_positions, hook_positions[1:]):
        if current_start < previous_end:
            issues.append(
                issue(
                    "REORDERED_REQUIRED_HOOK",
                    f"Hook block {current_id} begins before {previous_id} finishes in the current timeline.",
                    "required_hook.ordered_blocks",
                )
            )
    if hook_positions and is_number(expected_hook_start):
        actual_hook_start = hook_positions[0][1]
        expected_start = Fraction(str(expected_hook_start))
        if actual_hook_start != expected_start:
            issues.append(
                issue(
                    "HOOK_START_DISPLACED",
                    f"Required hook begins at timeline frame {actual_hook_start}, expected {expected_start}.",
                    "required_hook.expected_start_frame",
                )
            )
    diagnostics["required_hook_timeline_positions"] = [
        {"id": block_id, "timeline_start_frame_exact": str(start), "timeline_end_frame_exact": str(end)}
        for block_id, start, end in hook_positions
    ]

    defects = manifest.get("known_speech_defects")
    if not isinstance(defects, list):
        issues.append(issue("NO_SPEECH_DEFECT_REGISTER", "known_speech_defects must be a list, including an empty reviewed list.", "known_speech_defects"))
        defects = []
    unresolved_ids: list[str] = []
    for index, defect in enumerate(defects):
        path = f"known_speech_defects[{index}]"
        if not isinstance(defect, dict) or defect.get("status") not in {"resolved", "unresolved"}:
            issues.append(issue("INVALID_SPEECH_DEFECT", "Speech defect status must be resolved or unresolved.", path))
            continue
        defect_id = str(defect.get("id", index))
        if defect["status"] == "unresolved":
            unresolved_ids.append(defect_id)
            if ready_claimed:
                issues.append(issue("UNRESOLVED_SPEECH_DEFECT_REPORTED_READY", f"{defect_id} is unresolved while release_claim.ready is true.", path))
            continue
        resolution = defect.get("resolution")
        if not isinstance(resolution, dict) or not resolution.get("evidence_refs"):
            issues.append(issue("UNSUPPORTED_SPEECH_RESOLUTION", f"{defect_id} lacks resolution evidence.", path))
            continue
        if resolution.get("method") == "source_removed":
            core = resolution.get("source_span")
            if not isinstance(core, list) or len(core) != 2 or not all(is_number(value) for value in core):
                issues.append(issue("INVALID_SPEECH_RESOLUTION", f"{defect_id} needs a valid removed source_span.", path))
            elif any(intersects((int(core[0]), int(core[1])), span) for span in occupied):
                issues.append(issue("RESOLVED_SPEECH_CORE_STILL_RETAINED", f"{defect_id} is labeled resolved, but its source core remains occupied.", path))
    diagnostics["unresolved_speech_defect_ids"] = unresolved_ids

    markers = manifest.get("diagnostic_markers", [])
    if not isinstance(markers, list):
        issues.append(issue("INVALID_DIAGNOSTIC_MARKERS", "diagnostic_markers must be a list.", "diagnostic_markers"))
        markers = []
    diagnostics["stale_marker_objects_observed"] = sum(
        1 for marker in markers if isinstance(marker, dict) and marker.get("object_remains") is True
    )

    dead_air = manifest.get("dead_air_review")
    if not isinstance(dead_air, dict):
        issues.append(issue("NO_DEAD_AIR_REVIEW", "dead_air_review is required.", "dead_air_review"))
        dead_air = {}
    if not isinstance(dead_air.get("thresholds"), dict) or not dead_air.get("thresholds"):
        issues.append(issue("NO_DEAD_AIR_THRESHOLDS", "Declare the detector thresholds used; the helper supplies no duration quota.", "dead_air_review.thresholds"))
    if not isinstance(dead_air.get("context_evidence_refs"), list) or not dead_air.get("context_evidence_refs"):
        issues.append(issue("NO_DEAD_AIR_CONTEXT", "Dead-air review needs source-context evidence references.", "dead_air_review.context_evidence_refs"))
    candidates = dead_air.get("candidates")
    if not isinstance(candidates, list):
        issues.append(issue("NO_DEAD_AIR_CANDIDATES", "dead_air_review.candidates must be a reviewed list.", "dead_air_review.candidates"))
        candidates = []
    for index, candidate in enumerate(candidates):
        path = f"dead_air_review.candidates[{index}]"
        if not isinstance(candidate, dict):
            issues.append(issue("INVALID_DEAD_AIR_CANDIDATE", "Candidate must be an object.", path))
            continue
        location = candidate.get("location")
        if not isinstance(location, dict) or location.get("scope") not in {"between_clips", "intra_clip"}:
            issues.append(issue("INVALID_DEAD_AIR_LOCATION", "Candidate scope must be between_clips or intra_clip.", path))
        elif location["scope"] == "intra_clip":
            span = location.get("source_span")
            if not location.get("clip_id") or not isinstance(span, list) or len(span) != 2 or not all(is_number(value) for value in span) or span[0] >= span[1]:
                issues.append(issue("INVALID_DEAD_AIR_LOCATION", "Intra-clip dead air needs clip_id and an increasing source_span.", path))
        else:
            span = location.get("timeline_span")
            if not isinstance(span, list) or len(span) != 2 or not all(is_number(value) for value in span) or span[0] >= span[1]:
                issues.append(issue("INVALID_DEAD_AIR_LOCATION", "Between-clip dead air needs an increasing timeline_span.", path))
        disposition = candidate.get("disposition")
        if disposition not in {"retain", "repair"}:
            issues.append(issue("UNEXPLAINED_DEAD_AIR", "Candidate needs an explicit retain or repair disposition.", path))
        if not isinstance(candidate.get("reason_code"), str) or not candidate.get("reason_code") or not isinstance(candidate.get("reason"), str) or not candidate.get("reason").strip():
            issues.append(issue("UNSPECIFIC_DEAD_AIR_REASON", "Candidate needs a reason_code and concrete reason.", path))
        if not isinstance(candidate.get("evidence_refs"), list) or not candidate.get("evidence_refs"):
            issues.append(issue("NO_DEAD_AIR_EVIDENCE", "Candidate needs context evidence references.", path))
        if disposition == "repair":
            status = candidate.get("repair_status")
            if status not in {"planned", "applied"}:
                issues.append(issue("INVALID_DEAD_AIR_REPAIR", "Repair needs planned or applied status.", path))
            elif ready_claimed and status != "applied":
                issues.append(issue("UNAPPLIED_DEAD_AIR_REPAIR_REPORTED_READY", "A planned repair cannot support a ready claim.", path))

    audio = manifest.get("review_audio")
    audio_stage = audio.get("measurement_stage") if isinstance(audio, dict) else None
    audio_valid = isinstance(audio, dict) and all(
        is_number(audio.get(key)) for key in ("gain_db", "measured_true_peak_dbtp", "peak_ceiling_dbtp")
    )
    if not audio_valid or audio_stage not in {"source_prediction", "encoded_render"} or not audio.get("evidence_refs"):
        issues.append(
            issue(
                "INVALID_REVIEW_AUDIO",
                "review_audio needs finite gain_db, measured_true_peak_dbtp, peak_ceiling_dbtp, evidence_refs, and a valid measurement_stage.",
                "review_audio",
            )
        )
        audio_safe = False
    else:
        ceiling_valid = audio["peak_ceiling_dbtp"] <= 0
        if not ceiling_valid:
            issues.append(
                issue(
                    "POSITIVE_TRUE_PEAK_CEILING",
                    "peak_ceiling_dbtp must be at or below 0 dBTP.",
                    "review_audio.peak_ceiling_dbtp",
                )
            )
        within_ceiling = audio["measured_true_peak_dbtp"] <= audio["peak_ceiling_dbtp"]
        audio_safe = ceiling_valid and within_ceiling
        if not within_ceiling:
            issues.append(
                issue(
                    "TRUE_PEAK_EXCEEDS_CEILING",
                    f"Measured {audio['measured_true_peak_dbtp']} dBTP exceeds ceiling {audio['peak_ceiling_dbtp']} dBTP.",
                    "review_audio.measured_true_peak_dbtp",
                )
            )
        if ready_claimed and audio_stage != "encoded_render":
            issues.append(
                issue(
                    "SOURCE_PREDICTION_NOT_FINAL",
                    "A source prediction can record pending audio work, but only an encoded-render measurement supports final readiness.",
                    "review_audio.measurement_stage",
                )
            )
    audio_gate_satisfied = audio_valid and audio_safe and audio_stage == "encoded_render"
    audio_headroom_db = (
        round(audio["peak_ceiling_dbtp"] - audio["measured_true_peak_dbtp"], 12) if audio_valid else None
    )

    listening = manifest.get("perceptual_review")
    listening_status = listening.get("status") if isinstance(listening, dict) else None
    listening_method = listening.get("method") if isinstance(listening, dict) else None
    listening_reviewer = listening.get("reviewer") if isinstance(listening, dict) else None
    reviewer_present = isinstance(listening_reviewer, str) and bool(listening_reviewer.strip())
    listening_satisfied = (
        listening_status == "passed"
        and listening_method in AUDITORY_METHODS
        and reviewer_present
        and bool(listening.get("evidence_refs"))
    )
    if listening_status == "passed" and listening_method not in AUDITORY_METHODS:
        issues.append(
            issue(
                "NONAUDITORY_PERCEPTUAL_ACCEPTANCE",
                "Waveform, ASR, stills, and structural checks cannot establish perceptual acceptance.",
                "perceptual_review.method",
                scope="perceptual",
            )
        )
    if listening_status == "passed" and not reviewer_present:
        issues.append(
            issue(
                "MISSING_PERCEPTUAL_REVIEWER",
                "A passed perceptual review needs the nonempty name or identifier of the person who actually heard and saw it.",
                "perceptual_review.reviewer",
                scope="perceptual",
            )
        )
    if ready_claimed and not listening_satisfied:
        issues.append(issue("LISTENING_GATE_NOT_PASSED", "A ready claim requires an evidenced, named human listening or continuous audiovisual review.", "perceptual_review", scope="perceptual"))

    structural_blockers = [item for item in issues if item["severity"] == "blocker" and item["scope"] == "structural"]
    perceptual_blockers = [item for item in issues if item["severity"] == "blocker" and item["scope"] == "perceptual"]
    return {
        "schema_version": SCHEMA_VERSION,
        "structural_checks": {"passed": not structural_blockers, "blocker_count": len(structural_blockers)},
        "perceptual_review": {
            "reported_status": listening_status,
            "reported_method": listening_method,
            "reported_reviewer": listening_reviewer,
            "gate_satisfied": listening_satisfied,
            "note": "This helper does not listen; it validates only the declared human-review record.",
        },
        "audio_review": {
            "measurement_stage": audio_stage,
            "headroom_db": audio_headroom_db,
            "gate_satisfied": audio_gate_satisfied,
            "note": "Gain has no fixed target. Final readiness requires an encoded-render true-peak measurement at or below the declared ceiling.",
        },
        "release_claim": {
            "ready_reported": ready_claimed,
            "supported": ready_claimed and not structural_blockers and not perceptual_blockers and listening_satisfied and audio_gate_satisfied,
        },
        "issues": issues,
        "diagnostics": diagnostics,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text())
        if not isinstance(manifest, dict):
            raise ValueError("manifest root must be an object")
        result = validate_manifest(manifest)
    except (OSError, json.JSONDecodeError, ValueError, KeyError, ZeroDivisionError) as error:
        result = {
            "schema_version": SCHEMA_VERSION,
            "structural_checks": {"passed": False, "blocker_count": 1},
            "perceptual_review": {"gate_satisfied": False, "note": "No perceptual inference was made."},
            "audio_review": {"gate_satisfied": False, "note": "No audio inference was made."},
            "release_claim": {"ready_reported": False, "supported": False},
            "issues": [issue("MANIFEST_LOAD_FAILED", str(error), str(args.manifest))],
            "diagnostics": {},
        }
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        sys.stdout.write(rendered)
    return 0 if result["release_claim"]["supported"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
