import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "video_word_timing.py"
SPEC = importlib.util.spec_from_file_location("video_word_timing", MODULE_PATH)
timing = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(timing)


class WordTimingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def load(self, data, **kwargs):
        path = self.root / "source.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return timing.load_word_timing(path, **kwargs)

    def test_auphonic_current_html_preserves_words_and_hash(self):
        data = {"transcript": {"results": {
            "100": {"timestamps": [["second", 1.5, 1.9, 0.8]]},
            "9": {"timestamps": [[" first-person", 0.02, 0.14, 1.0]]},
        }}}
        path = self.root / "source.html"
        path.write_text('<script type="application/json">{"unrelated": true}</script>'
                        '<script id="transcriptSourceData" type="application/json">'
                        + json.dumps(data) + '</script>', encoding="utf-8")
        result = timing.load_word_timing(path, duration=2)
        self.assertEqual(result["source"]["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(result["words"][0]["word"], " first-person")
        self.assertEqual(result["words"][0]["end"], 0.14)
        self.assertEqual(result["words"][0]["confidence"], 1.0)
        self.assertEqual(result["word_count"], 2)

    def test_legacy_versions_require_selection_when_ambiguous(self):
        version = {"transcript": {"results": [{"timestamps": [["yes", 0, 0.5]]}]}}
        data = {"transcript_versions": [version, version]}
        with self.assertRaisesRegex(timing.TimingError, "Multiple transcript versions"):
            self.load(data)
        result = self.load(data, version_index=1)
        self.assertIn("transcript_versions[1]", result["words"][0]["source_index"])

    def test_legacy_json_script(self):
        data = {"transcript_versions": [{"transcript": {"results": {
            "0": {"timestamps": [["yes", 0, 0.5]]}}}}]}
        path = self.root / "source.html"
        path.write_text('<script type="application/json">' + json.dumps(data) + '</script>')
        self.assertEqual(timing.load_word_timing(path)["word_count"], 1)

    def test_speech_segments_and_whisper_words(self):
        sources = [
            [{"timestamps": [["hello", 0.1, 0.3, 0.99]]}],
            {"segments": [{"text": "hello", "words": [{"word": "hello", "start": 0.1, "end": 0.3, "probability": 0.99}]}]},
            {"words": [{"text": "hello", "start": 0.1, "end": 0.3, "confidence": 0.99}]},
            [{"word": "hello", "start": 0.1, "end": 0.3, "confidence": 0.99}],
            [["hello", 0.1, 0.3, 0.99]],
        ]
        for source in sources:
            with self.subTest(source=source):
                word = self.load(source)["words"][0]
                self.assertEqual((word["word"], word["start"], word["end"], word["confidence"]),
                                 ("hello", 0.1, 0.3, 0.99))

    def test_known_offset_preserves_source_intervals(self):
        result = self.load([["word", 1, 2]], offset=-0.5, duration=1.5)
        word = result["words"][0]
        self.assertEqual((word["start"], word["end"], word["source_start"], word["source_end"]),
                         (0.5, 1.5, 1, 2))

    def test_overlapping_words_are_preserved(self):
        words = self.load([["a", 0, 0.5], ["b", 0.3, 0.7]])["words"]
        self.assertEqual(words[0]["end"], 0.5)
        self.assertEqual(words[1]["start"], 0.3)

    def test_no_segment_estimation_or_partial_success(self):
        bad = [
            {"segments": [{"text": "hello", "start": 0, "end": 1}]},
            {"text": "hello world", "start": 0, "end": 1},
            [{"text": "hello", "start": 0, "end": 1}],
            [{"timestamps": [["good", 0, 1]]}, {"text": "missing", "timestamps": []}],
            {"results": {"0": {"text": "missing", "start": 0, "end": 1}}},
            [],
        ]
        for source in bad:
            with self.subTest(source=source), self.assertRaises(timing.TimingError):
                self.load(source)

    def test_invalid_intervals_numbers_and_order_fail(self):
        bad = [
            [["a", -1, 0]], [["a", 1, 0]], [["a", True, 1]],
            [["a", "0", 1]], [["a", 0, float("inf")]],
            [["a", float("nan"), 1]], [["a", 0, 1, float("nan")]],
            [["a", 1, 2], ["b", 0, 3]], [["a", 0, 2], ["b", 1, 1.5]],
            [[" ", 0, 1]],
        ]
        for source in bad:
            with self.subTest(source=source), self.assertRaises(timing.TimingError):
                self.load(source)

    def test_bounds_and_parameter_validation(self):
        for options in [{"duration": 0}, {"duration": float("nan")}, {"duration": 0.5},
                        {"offset": -1}, {"offset": float("inf")}, {"version_index": -1}]:
            with self.subTest(options=options), self.assertRaises(timing.TimingError):
                self.load([["a", 0, 1]], **options)

    def test_html_ambiguity_and_corrupt_primary_fail(self):
        valid = json.dumps({"words": [{"word": "a", "start": 0, "end": 1}]})
        for html in [
            '<p data-start="0">No word timings</p>',
            '<script type="application/json">' + valid + '</script>'
            + '<script type="application/json">' + valid + '</script>',
            '<script id="transcriptSourceData">{broken}</script>'
            + '<script type="application/json">' + valid + '</script>',
        ]:
            path = self.root / "bad.html"
            path.write_text(html)
            with self.subTest(html=html), self.assertRaises(timing.TimingError):
                timing.load_word_timing(path)

    def test_cli_writes_json_and_protects_source(self):
        source = self.root / "words.json"
        source.write_text('[["hello", 0, 1]]')
        original = source.read_bytes()
        output = self.root / "timing.json"
        completed = subprocess.run([sys.executable, str(MODULE_PATH), str(source),
                                    "--duration", "1", "--output", str(output)], capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(output.read_text())["word_count"], 1)
        denied = subprocess.run([sys.executable, str(MODULE_PATH), str(source),
                                 "--output", str(source)], capture_output=True)
        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(source.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
