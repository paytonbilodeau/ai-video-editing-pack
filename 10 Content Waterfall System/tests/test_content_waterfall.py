import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SYSTEM_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "content_waterfall", SYSTEM_ROOT / "tools" / "content_waterfall.py"
)
content_waterfall = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(content_waterfall)


def valid_map(source_hash="0" * 64, duration=24.0):
    return {
        "schema": "ai-mentorship-content-map-v1",
        "source": {
            "label": "source.mp4",
            "sha256": source_hash,
            "durationSeconds": duration,
        },
        "claimLedger": [
            {
                "id": "claim-01",
                "text": "A receipt records what happened.",
                "sourceStart": 1.0,
                "sourceEnd": 18.0,
            }
        ],
        "outputs": [
            {
                "id": "short-01",
                "type": "short",
                "title": "Keep a Receipt",
                "sourceStart": 1.0,
                "sourceEnd": 22.0,
                "claimIds": ["claim-01"],
                "approved": True,
            }
        ],
    }


def transcript():
    return {
        "schema": "ai-mentorship-transcript-v1",
        "sourceLabel": "source.mp4",
        "durationSeconds": 24.0,
        "segments": [
            {
                "start": 1.0,
                "end": 4.0,
                "text": "Keep a receipt.",
                "words": [
                    {"word": "Keep", "start": 1.25, "end": 1.55},
                    {"word": "a", "start": 1.65, "end": 1.8},
                    {"word": "receipt.", "start": 1.9, "end": 2.5},
                ],
            }
        ],
    }


class ContentMapValidationTests(unittest.TestCase):
    def test_valid_map_passes(self) -> None:
        self.assertEqual(content_waterfall.validate_content_map(valid_map()), [])

    def test_unknown_claim_and_unapproved_type_fail(self) -> None:
        payload = valid_map()
        payload["outputs"][0]["claimIds"] = ["claim-missing"]
        payload["outputs"][0]["approved"] = "yes"
        errors = content_waterfall.validate_content_map(payload)
        self.assertTrue(any("unknown claim" in item for item in errors))
        self.assertTrue(any("true or false" in item for item in errors))

    def test_short_duration_and_absolute_source_fail(self) -> None:
        payload = valid_map()
        payload["source"]["label"] = "../private/source.mp4"
        payload["outputs"][0]["sourceEnd"] = 10.0
        errors = content_waterfall.validate_content_map(payload)
        self.assertTrue(any("basename" in item for item in errors))
        self.assertTrue(any("between 20 and 90" in item for item in errors))

    def test_claim_range_must_be_inside_output(self) -> None:
        payload = valid_map()
        payload["claimLedger"][0]["sourceEnd"] = 23.0
        errors = content_waterfall.validate_content_map(payload)
        self.assertTrue(any("full range" in item for item in errors))

    def test_exact_word_times_are_rebased_without_estimation(self) -> None:
        _, words = content_waterfall.transcript_words(transcript())
        cues = content_waterfall.clip_word_cues(words, 1.0, 22.0)
        self.assertEqual(cues[0], {"text": "Keep", "start": 0.25, "end": 0.55})
        self.assertEqual(cues[2], {"text": "receipt.", "start": 0.9, "end": 1.5})

    def test_caption_receipt_names_exact_timing_method(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "captions"
            receipt = content_waterfall.create_captions(transcript(), valid_map(), output)
            self.assertEqual(
                receipt["timingMethod"], "exact_supplied_word_times_rebased"
            )
            vtt = (output / "short-01.vtt").read_text(encoding="utf-8")
            self.assertIn("00:00:00.250 --> 00:00:00.550", vtt)

    def test_caption_text_cannot_inject_a_vtt_timing_line(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "safe.vtt"
            content_waterfall.write_vtt(
                output,
                [{"text": "bad --> cue\nnext", "start": 0.0, "end": 0.5}],
            )
            vtt = output.read_text(encoding="utf-8")
            self.assertIn("bad → cue next", vtt)
            self.assertEqual(vtt.count(" --> "), 1)


@unittest.skipUnless(
    shutil.which("ffmpeg") and shutil.which("ffprobe"),
    "FFmpeg and ffprobe are required for the synthetic end-to-end test",
)
class SyntheticEndToEndTests(unittest.TestCase):
    def test_extracts_short_and_preserves_source(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source.mp4"
            subprocess.run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=blue:s=160x90:r=15:d=24",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:sample_rate=44100:duration=24",
                    "-shortest",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "aac",
                    str(source),
                ],
                check=True,
                capture_output=True,
            )
            before = hashlib.sha256(source.read_bytes()).hexdigest()
            payload = valid_map(before, content_waterfall.probe_duration(source))
            output_dir = root / "waterfall-output"
            receipt = content_waterfall.extract_clips(source, payload, output_dir)
            after = hashlib.sha256(source.read_bytes()).hexdigest()

            self.assertEqual(before, after)
            self.assertTrue(receipt["sourceUnchanged"])
            self.assertEqual(receipt["sourceLabel"], "source.mp4")
            self.assertEqual(receipt["outputs"][0]["outputLabel"], "short-01.mp4")
            self.assertAlmostEqual(receipt["outputs"][0]["durationSeconds"], 21.0, delta=0.75)
            self.assertNotIn(str(root.resolve()), json.dumps(receipt))
            self.assertTrue((output_dir / "short-01.mp4").is_file())
            self.assertTrue((output_dir / "extraction-receipt.json").is_file())

    def test_existing_output_directory_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source.mp4"
            source.write_bytes(b"not used because output check runs first")
            output = root / "existing"
            output.mkdir()
            with self.assertRaisesRegex(content_waterfall.WaterfallError, "already exists"):
                content_waterfall.extract_clips(source, valid_map(), output)


if __name__ == "__main__":
    unittest.main()
