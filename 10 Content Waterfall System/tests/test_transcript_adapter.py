import importlib.util
import tempfile
import unittest
from pathlib import Path


SYSTEM_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "transcript_adapter", SYSTEM_ROOT / "tools" / "transcript_adapter.py"
)
transcript_adapter = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(transcript_adapter)


def sample_payload():
    return {
        "duration": 8.0,
        "segments": [
            {
                "start": 1.0,
                "end": 4.0,
                "text": "One useful sentence.",
                "words": [
                    {"word": "One", "start": 1.0, "end": 1.3},
                    {"word": "useful", "start": 1.4, "end": 2.0},
                    {"word": "sentence.", "start": 2.1, "end": 3.0},
                ],
            }
        ],
    }


class TranscriptAdapterTests(unittest.TestCase):
    def test_normalizes_supplied_exact_word_times(self) -> None:
        result = transcript_adapter.normalize(sample_payload(), "source.mp4")
        self.assertEqual(result["schema"], "ai-mentorship-transcript-v1")
        self.assertEqual(result["sourceLabel"], "source.mp4")
        self.assertEqual(result["segments"][0]["words"][1]["start"], 1.4)

    def test_rejects_absolute_source_label(self) -> None:
        with self.assertRaises(transcript_adapter.TranscriptError):
            transcript_adapter.normalize(sample_payload(), "/private/source.mp4")

    def test_rejects_estimated_segment_without_word_times(self) -> None:
        payload = sample_payload()
        del payload["segments"][0]["words"]
        with self.assertRaisesRegex(transcript_adapter.TranscriptError, "word timings"):
            transcript_adapter.normalize(payload, "source.mp4")

    def test_write_refuses_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "transcript.json"
            path.write_text("old", encoding="utf-8")
            with self.assertRaises(transcript_adapter.TranscriptError):
                transcript_adapter.write_new(path, {"new": True}, overwrite=False)
            self.assertEqual(path.read_text(encoding="utf-8"), "old")


if __name__ == "__main__":
    unittest.main()
