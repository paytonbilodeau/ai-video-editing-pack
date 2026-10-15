import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "auphonic_enhance.py"
SPEC = importlib.util.spec_from_file_location("auphonic_enhance", MODULE_PATH)
assert SPEC and SPEC.loader
auphonic_enhance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(auphonic_enhance)


class AuphonicChapterTests(unittest.TestCase):
    def test_save_chapters_uses_output_relative_timestamps(self):
        production = {
            "uuid": "test-production",
            "chapters": [
                {
                    "title": "Introduction",
                    "start_sec": 0,
                    "start_output_sec": 5,
                },
                {
                    "title": "Main idea",
                    "start_sec": 60,
                    "start_output_sec": 65,
                },
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            result = auphonic_enhance.save_chapters(production, directory, "video")
            assert result is not None
            payload = json.loads(Path(result["json"]).read_text(encoding="utf-8"))
            self.assertEqual(payload["chapters"][0]["time"], "00:00")
            self.assertEqual(payload["chapters"][0]["original_start_output_seconds"], 5)
            self.assertEqual(payload["chapters"][1]["time"], "01:05")
            self.assertEqual(
                Path(result["text"]).read_text(encoding="utf-8"),
                "00:00 Introduction\n01:05 Main idea\n",
            )


class AuphonicPollingTests(unittest.TestCase):
    @staticmethod
    def response(status, status_string, error_message=None):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "data": {
                "status": status,
                "status_string": status_string,
                "error_message": error_message,
            }
        }
        return response

    @patch.object(auphonic_enhance.time, "sleep")
    @patch.object(auphonic_enhance.time, "time", return_value=0)
    @patch.object(auphonic_enhance.requests, "get")
    def test_processing_and_encoding_can_exceed_six_polls(self, get, _time, sleep):
        get.side_effect = (
            [self.response(4, "Audio Processing")] * 7
            + [self.response(14, "Speech Recognition")]
            + [self.response(5, "Audio Encoding")] * 7
            + [self.response(3, "Done")]
        )

        result = auphonic_enhance.poll_for_completion(
            "test-production", poll_interval=0, timeout=60
        )

        self.assertEqual(result["status"], 3)
        self.assertEqual(get.call_count, 16)
        self.assertEqual(sleep.call_count, 15)

    @patch.object(auphonic_enhance.time, "time", side_effect=[0, 0])
    @patch.object(auphonic_enhance.requests, "get")
    def test_error_status_two_raises_immediately(self, get, _time):
        get.return_value = self.response(2, "Error", "processing failed")

        with self.assertRaisesRegex(RuntimeError, "failed: processing failed"):
            auphonic_enhance.poll_for_completion(
                "test-production", poll_interval=0, timeout=60
            )

        self.assertEqual(get.call_count, 1)

    @patch.object(auphonic_enhance.time, "time", side_effect=[0, 0])
    @patch.object(auphonic_enhance.requests, "get")
    def test_stopping_status_thirteen_raises_immediately(self, get, _time):
        get.return_value = self.response(13, "Stopping the Production")

        with self.assertRaisesRegex(RuntimeError, "is stopping"):
            auphonic_enhance.poll_for_completion(
                "test-production", poll_interval=0, timeout=60
            )

        self.assertEqual(get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
