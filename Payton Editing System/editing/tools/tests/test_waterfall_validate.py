import copy
import importlib.util
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "waterfall_validate", Path(__file__).resolve().parents[1] / "waterfall_validate.py"
)
waterfall = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(waterfall)


def frame_clip(kind="vertical", length=78):
    return {
        "id": "clip-01", "kind": kind, "start_frame": 300,
        "end_frame": 300 + length * 30, "title": "What I learned about AI",
        "hook": "Fast AI can fool you", "caption": "I still check the work.",
    }


class WaterfallValidationTests(unittest.TestCase):
    def validate(self, cmap, **kwargs):
        return waterfall.validate_map(cmap, 1000, **kwargs)

    def test_current_more_frame_schema_checks_all_clips(self):
        clip = frame_clip("horizontal")
        clip.update(start_seconds=10, end_seconds=88, frames=2340)
        result = self.validate({"clips": [clip]}, mode="more", fps=30)
        self.assertTrue(result["ok"], result)
        self.assertEqual(len(result["mids"]), 1)
        self.assertEqual(result["mids"][0]["end"], 88)
        self.assertEqual(result["warnings"], [])  # More has no arbitrary three-minute floor.

    def test_frames_need_explicit_more_mode_and_real_source_fps(self):
        for options in ({}, {"mode": "more"}):
            result = self.validate({"clips": [frame_clip()]}, **options)
            self.assertFalse(result["ok"], result)

    def test_empty_and_malformed_maps_fail(self):
        for cmap in ({}, {"clips": []}, {"mids": [], "shorts": []}, [],
                     {"clips": {}}, {"clips": [None]}, {"shorts": "invalid"}):
            with self.subTest(cmap=cmap):
                self.assertFalse(self.validate(cmap, mode="more", fps=30)["ok"])

    def test_legacy_interface_remains_supported(self):
        cmap = {"mids": [{"id": "mid", "start": 0, "end": 240, "title": "AI work"}],
                "shorts": [{"id": "short", "start": 30, "end": 70,
                            "title": "AI answers", "text_hook": "Check the answer",
                            "caption_ig": "My own experience."}]}
        self.assertTrue(self.validate(cmap)["ok"])

    def test_short_180_seconds_is_valid_but_one_more_frame_fails(self):
        clip = frame_clip(length=180)
        self.assertTrue(self.validate({"clips": [clip]}, mode="more", fps=30)["ok"])
        clip["end_frame"] += 1
        result = self.validate({"clips": [clip]}, mode="more", fps=30)
        self.assertFalse(result["ok"])
        self.assertTrue(any("180" in error for error in result["errors"]))

    def test_legacy_short_181_seconds_is_an_error_not_warning(self):
        clip = {"id": "s", "start": 0, "end": 181, "title": "AI",
                "text_hook": "Check it", "caption": "My experience."}
        self.assertFalse(self.validate({"shorts": [clip]})["ok"])

    def test_source_frame_bounds_are_strict_and_end_is_exclusive(self):
        clip = frame_clip()
        self.assertTrue(self.validate({"clips": [clip]}, mode="more", fps=30,
                                      source_frames=2640)["ok"])
        result = self.validate({"clips": [clip]}, mode="more", fps=30, source_frames=2639)
        self.assertFalse(result["ok"])
        clip["start_frame"] = -1
        self.assertFalse(self.validate({"clips": [clip]}, mode="more", fps=30)["ok"])

    def test_nonfinite_and_mismatched_timestamps_fail(self):
        for updates in ({"start_frame": True}, {"end_frame": 301.5},
                        {"start_seconds": 12}, {"end_seconds": float("nan")},
                        {"frames": 10}, {"kind": "square"}):
            clip = {**frame_clip(), **updates}
            self.assertFalse(self.validate({"clips": [clip]}, mode="more", fps=30)["ok"], updates)
        legacy = {"id": "s", "start": 0, "end": float("inf"), "title": "AI"}
        self.assertFalse(self.validate({"shorts": [legacy]})["ok"])

    def test_short_title_hook_and_caption_are_required(self):
        for field in ("title", "hook", "caption"):
            clip = {**frame_clip(), field: "  "}
            result = self.validate({"clips": [clip]}, mode="more", fps=30)
            self.assertFalse(result["ok"], field)
        clip = {**frame_clip(), "title": "x" * 101}
        self.assertFalse(self.validate({"clips": [clip]}, mode="more", fps=30)["ok"])

    def test_duplicate_ids_and_mixed_schemas_fail(self):
        clip = frame_clip()
        self.assertFalse(self.validate({"clips": [clip, copy.deepcopy(clip)]},
                                       mode="more", fps=30)["ok"])
        self.assertFalse(self.validate({"clips": [clip], "shorts": []},
                                       mode="more", fps=30)["ok"])

    def test_invalid_nested_metadata_returns_errors_instead_of_crashing(self):
        for fields in ({"main": {"chapters": ["0"]}}, {"main": None},
                       {"text": []}, {"text": {"linkedin": None}}):
            result = self.validate({"clips": [frame_clip()], **fields}, mode="more", fps=30)
            self.assertFalse(result["ok"], fields)
        self.assertFalse(self.validate({"clips": [{**frame_clip(), "kind": []}]},
                                       mode="more", fps=30)["ok"])

    def test_optional_crop_metadata_must_fit_source_and_be_portrait(self):
        clip = {**frame_clip(), "source_crop": [1312, 0, 1215, 2160]}
        options = {"mode": "more", "fps": 30, "source_size": (3840, 2160)}
        self.assertTrue(self.validate({"clips": [clip]}, **options)["ok"])
        for crop in ([3000, 0, 1215, 2160], [0, 0, 1920, 1080], [0, -1, 1215, 2160]):
            clip["source_crop"] = crop
            self.assertFalse(self.validate({"clips": [clip]}, **options)["ok"])


if __name__ == "__main__":
    unittest.main()
