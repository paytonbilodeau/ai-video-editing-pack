from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cut_readiness import exact_source_span, validate_manifest  # noqa: E402


def fixture(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text())


def codes(result: dict) -> set[str]:
    return {item["code"] for item in result["issues"] if item["severity"] == "blocker"}


class CutReadinessTests(unittest.TestCase):
    def test_ready_fixture_uses_exact_retime_occupancy_and_ignores_stale_marker_as_state(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        result = validate_manifest(manifest)
        self.assertEqual(exact_source_span(manifest["timeline"]["clips"][2]), (140, 150))
        self.assertTrue(result["structural_checks"]["passed"])
        self.assertTrue(result["release_claim"]["supported"])
        self.assertEqual(result["diagnostics"]["stale_marker_objects_observed"], 1)
        self.assertIn("ROUNDED_REPORTED_SOURCE_SPAN_IGNORED", {item["code"] for item in result["issues"]})

    def test_missing_required_hook_fails_closed(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        manifest["timeline"]["clips"].pop(0)
        self.assertIn("MISSING_REQUIRED_HOOK", codes(validate_manifest(manifest)))

    def test_reordered_required_hook_fails_closed(self) -> None:
        result = validate_manifest(fixture("not-ready-unfamiliar.json"))
        self.assertIn("REORDERED_REQUIRED_HOOK", codes(result))

    def test_intact_hook_displaced_after_other_footage_fails(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        for clip in manifest["timeline"]["clips"]:
            clip["timeline_start_frame"] += 30
        result = validate_manifest(manifest)
        self.assertNotIn("MISSING_REQUIRED_HOOK", codes(result))
        self.assertIn("HOOK_START_DISPLACED", codes(result))

    def test_unresolved_speech_cannot_be_reported_ready(self) -> None:
        result = validate_manifest(fixture("not-ready-unfamiliar.json"))
        self.assertIn("UNRESOLVED_SPEECH_DEFECT_REPORTED_READY", codes(result))

    def test_intra_clip_dead_air_requires_disposition_and_reason(self) -> None:
        result = validate_manifest(fixture("not-ready-unfamiliar.json"))
        self.assertIn("UNEXPLAINED_DEAD_AIR", codes(result))
        self.assertIn("UNSPECIFIC_DEAD_AIR_REASON", codes(result))

    def test_waveform_and_asr_cannot_pass_listening_gate(self) -> None:
        result = validate_manifest(fixture("not-ready-unfamiliar.json"))
        self.assertIn("NONAUDITORY_PERCEPTUAL_ACCEPTANCE", codes(result))
        self.assertIn("LISTENING_GATE_NOT_PASSED", codes(result))
        self.assertFalse(result["release_claim"]["supported"])

    def test_resolved_by_removal_fails_if_core_is_still_occupied(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        manifest["known_speech_defects"][0]["resolution"]["source_span"] = [149, 150]
        self.assertIn("RESOLVED_SPEECH_CORE_STILL_RETAINED", codes(validate_manifest(manifest)))

    def test_pending_listening_stays_separate_from_structural_pass(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        manifest["release_claim"]["ready"] = False
        manifest["perceptual_review"] = {"status": "pending", "method": None, "evidence_refs": []}
        result = validate_manifest(manifest)
        self.assertTrue(result["structural_checks"]["passed"])
        self.assertFalse(result["perceptual_review"]["gate_satisfied"])
        self.assertFalse(result["release_claim"]["supported"])

    def test_quiet_source_safe_plus_twelve_gain_is_accepted(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        self.assertEqual(manifest["review_audio"]["gain_db"], 12.0)
        result = validate_manifest(manifest)
        self.assertTrue(result["audio_review"]["gate_satisfied"])
        self.assertAlmostEqual(result["audio_review"]["headroom_db"], 0.2)
        self.assertTrue(result["release_claim"]["supported"])

    def test_loud_source_can_use_lower_safe_gain(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        manifest["review_audio"].update({"gain_db": 2.25, "measured_true_peak_dbtp": -1.1})
        result = validate_manifest(manifest)
        self.assertTrue(result["audio_review"]["gate_satisfied"])
        self.assertNotIn("TRUE_PEAK_EXCEEDS_CEILING", codes(result))

    def test_true_peak_above_ceiling_fails_closed(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        manifest["review_audio"]["measured_true_peak_dbtp"] = -0.6
        result = validate_manifest(manifest)
        self.assertIn("TRUE_PEAK_EXCEEDS_CEILING", codes(result))
        self.assertFalse(result["release_claim"]["supported"])

    def test_positive_true_peak_ceiling_fails_even_when_measurement_is_below_it(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        manifest["review_audio"].update({"measured_true_peak_dbtp": 0.4, "peak_ceiling_dbtp": 0.5})
        result = validate_manifest(manifest)
        self.assertIn("POSITIVE_TRUE_PEAK_CEILING", codes(result))
        self.assertNotIn("TRUE_PEAK_EXCEEDS_CEILING", codes(result))
        self.assertFalse(result["audio_review"]["gate_satisfied"])

    def test_source_prediction_can_record_pending_audio_without_structural_failure(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        manifest["release_claim"]["ready"] = False
        manifest["review_audio"]["measurement_stage"] = "source_prediction"
        result = validate_manifest(manifest)
        self.assertTrue(result["structural_checks"]["passed"])
        self.assertFalse(result["audio_review"]["gate_satisfied"])
        self.assertFalse(result["release_claim"]["supported"])

    def test_source_prediction_cannot_support_final_readiness(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        manifest["review_audio"]["measurement_stage"] = "source_prediction"
        result = validate_manifest(manifest)
        self.assertIn("SOURCE_PREDICTION_NOT_FINAL", codes(result))
        self.assertFalse(result["release_claim"]["supported"])

    def test_reversed_halves_inside_one_hook_block_fail(self) -> None:
        result = validate_manifest(fixture("split-hook-reversed.json"))
        self.assertIn("REORDERED_HOOK_INTERNAL", codes(result))

    def test_schema_v1_fails_closed_on_multiple_sources(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        manifest["timeline"]["clips"][2]["source_id"] = "second-source"
        result = validate_manifest(manifest)
        self.assertIn("MULTIPLE_SOURCES_UNSUPPORTED", codes(result))

    def test_passed_review_without_named_reviewer_cannot_support_readiness(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        manifest["perceptual_review"].pop("reviewer")
        result = validate_manifest(manifest)
        self.assertIn("MISSING_PERCEPTUAL_REVIEWER", codes(result))
        self.assertIn("LISTENING_GATE_NOT_PASSED", codes(result))
        self.assertFalse(result["release_claim"]["supported"])

    def test_continuous_playback_command_is_not_a_review_record(self) -> None:
        manifest = fixture("ready-retime-stale-marker.json")
        manifest["perceptual_review"]["method"] = "continuous_av_playback"
        result = validate_manifest(manifest)
        self.assertIn("NONAUDITORY_PERCEPTUAL_ACCEPTANCE", codes(result))
        self.assertFalse(result["release_claim"]["supported"])


if __name__ == "__main__":
    unittest.main()
