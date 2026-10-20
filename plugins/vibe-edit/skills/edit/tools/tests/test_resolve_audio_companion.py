import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import resolve_audio_companion as companion


SRT = """1
00:00:00,000 --> 00:00:02,250
Five < seven & "safe"

2
01:00:00,125 --> 01:00:02,500
<b>After an hour</b>
"""


class ResolveAudioCompanionTests(unittest.TestCase):
    def test_srt_writes_segment_timed_outputs_and_escapes_html(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "timeline.srt"
            source.write_text(SRT)
            paths = companion.build(source, root / "output", 3610)

            self.assertEqual(
                {path.name for path in paths},
                {"transcript.html", "transcript.txt", "transcript.vtt", "speech.json"},
            )
            speech = json.loads((root / "output/speech.json").read_text())
            self.assertEqual(speech["timing_granularity"], "subtitle_segment")
            self.assertFalse(speech["word_timestamps"])
            self.assertEqual(speech["segments"][1]["start_seconds"], 3600.125)
            self.assertNotIn("word", speech["segments"][0])
            html = (root / "output/transcript.html").read_text()
            self.assertIn("Five &lt; seven &amp; &quot;safe&quot;", html)
            self.assertIn("After an hour", html)
            self.assertNotIn("<b>After", html)
            self.assertIn("01:00:00.125 --> 01:00:02.500", (root / "output/transcript.vtt").read_text())

    def test_vtt_cue_identifier_and_settings_are_supported(self):
        vtt = """WEBVTT

speaker-1
00:00:01.000 --> 00:00:03.000 align:start position:10%
Hello
world
"""
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "timeline.vtt"
            source.write_text(vtt)
            segments = companion.parse_subtitles(source, 5)
            self.assertEqual(segments[0]["text"], "Hello world")
            self.assertEqual(segments[0]["start_seconds"], 1)

    def test_native_resolve_json_preserves_word_times_with_fractional_fps(self):
        native = {
            "language": "en",
            "segments": [{
                "start": "01:00:02:05",
                "end": "01:00:04:10",
                "text": "Native words",
                "speaker": None,
                "words": [
                    {"start": "01:00:02:05", "end": "01:00:02:20", "text": "Native"},
                    {"start": "01:00:02:20", "end": "01:00:04:10", "text": " words"},
                ],
            }],
        }
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "native.json"
            source.write_text(json.dumps(native))
            companion.build(
                source, root / "output", 5, fps="30000/1001",
                timecode_origin="01:00:00:00",
            )
            speech = json.loads((root / "output/speech.json").read_text())
            segment = speech["segments"][0]
            self.assertEqual(speech["source"], "resolve_native_transcription")
            self.assertEqual(speech["timing_granularity"], "word_and_segment")
            self.assertTrue(speech["word_timestamps"])
            self.assertFalse(speech["word_timestamps_invented"])
            self.assertEqual(speech["word_timestamp_source"], "resolve_native_transcription")
            self.assertEqual(speech["fps"], "30000/1001")
            self.assertAlmostEqual(segment["start_seconds"], 65 / (30000 / 1001))
            self.assertAlmostEqual(segment["words"][1]["end_seconds"], 130 / (30000 / 1001))
            self.assertEqual(segment["words"][1]["text"], " words")

    def test_one_long_native_segment_becomes_readable_word_bounded_cues(self):
        words = []
        tokens = [" One", " two", " three", " four."] + [f" word{i}" for i in range(5, 19)]
        for index, token in enumerate(tokens):
            start_frame = index * 15
            end_frame = start_frame + 12
            words.append({
                "start": f"00:00:{start_frame // 30:02}:{start_frame % 30:02}",
                "end": f"00:00:{end_frame // 30:02}:{end_frame % 30:02}",
                "text": token,
            })
        native = {"language": "en", "segments": [{
            "start": words[0]["start"], "end": words[-1]["end"],
            "text": "".join(tokens), "speaker": None, "words": words,
        }]}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "native.json"
            source.write_text(json.dumps(native))
            companion.build(
                source, root / "output", 10, fps="30",
                timecode_origin="00:00:00:00",
            )
            speech = json.loads((root / "output/speech.json").read_text())
            self.assertEqual(len(speech["segments"]), 1)
            self.assertEqual(speech["segments"][0]["words"], companion.parse_native_transcription(
                source, 10, "30", "00:00:00:00"
            )[0][0]["words"])
            self.assertGreater(speech["presentation_cue_count"], 1)
            vtt = (root / "output/transcript.vtt").read_text()
            self.assertEqual(vtt.count(" --> "), speech["presentation_cue_count"])
            self.assertIn("One two three four.", vtt)

    def test_native_json_requires_explicit_timing_context(self):
        native = {"segments": [
            {"start": "01:00:00:00", "end": "01:00:01:00", "text": "Hello", "words": []}
        ]}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "native.json"
            path.write_text(json.dumps(native))
            for fps, origin in [(None, None), ("30", None), (None, "01:00:00:00")]:
                with self.subTest(fps=fps, origin=origin), self.assertRaises(ValueError):
                    companion.parse_native_transcription(path, 2, fps, origin)

    def test_native_json_rejects_dropframe_malformed_and_out_of_range_times(self):
        invalid = [
            {"start": "01:00:00;00", "end": "01:00:01:00", "text": "Drop", "words": []},
            {"start": "01:00:00:30", "end": "01:00:01:00", "text": "Frame", "words": []},
            {"start": "00:59:59:29", "end": "01:00:01:00", "text": "Before", "words": []},
            {"start": "01:00:00:00", "end": "01:00:03:00", "text": "Past", "words": []},
            {"start": "01:00:00:00", "end": "01:00:01:00", "text": None, "words": []},
            {"start": "01:00:00:00", "end": "01:00:01:00", "text": "Word", "words": [
                {"start": "01:00:00:00", "end": "01:00:01:01", "text": "Word"}
            ]},
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "native.json"
            for segment in invalid:
                with self.subTest(segment=segment):
                    path.write_text(json.dumps({"segments": [segment]}))
                    with self.assertRaises(ValueError):
                        companion.parse_native_transcription(
                            path, 2, "30", "01:00:00:00"
                        )

    def test_reviewed_chapters_write_valid_youtube_hours(self):
        chapters = [
            {"start": 0, "title": "Opening"},
            {"start": 20, "title": "The useful middle"},
            {"start": 3600, "title": "After one hour"},
        ]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "timeline.srt"
            source.write_text(SRT)
            reviewed = root / "reviewed.json"
            reviewed.write_text(json.dumps(chapters))
            companion.build(source, root / "output", 3610, reviewed)

            self.assertEqual(
                (root / "output/YouTube chapters.txt").read_text(),
                "0:00 Opening\n0:20 The useful middle\n1:00:00 After one hour\n",
            )
            written = json.loads((root / "output/chapters.json").read_text())
            self.assertEqual(written[2], {"start": 3600.0, "title": "After one hour"})

    def test_invalid_youtube_chapter_rules_are_rejected(self):
        invalid = [
            [{"start": 0, "title": "A"}, {"start": 10, "title": "B"}],
            [{"other": 0}, {"start": 10, "title": "B"}, {"start": 20, "title": "C"}],
            [{"start": 1, "title": "A"}, {"start": 11, "title": "B"}, {"start": 21, "title": "C"}],
            [{"start": 0, "title": "A"}, {"start": 20, "title": "B"}, {"start": 19, "title": "C"}],
            [{"start": 0, "title": "A"}, {"start": 9, "title": "B"}, {"start": 20, "title": "C"}],
            [{"start": 0, "title": "A"}, {"start": 10, "title": "B"}, {"start": 25, "title": "C"}],
            [{"start": 0, "title": "A"}, {"start": 10, "title": "B"}, {"start": 31, "title": "C"}],
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "chapters.json"
            for value in invalid:
                with self.subTest(value=value):
                    path.write_text(json.dumps(value))
                    with self.assertRaises(ValueError):
                        companion.load_chapters(path, 30)

    def test_bad_subtitle_intervals_are_rejected(self):
        examples = [
            "1\n00:00:03,000 --> 00:00:02,000\nBackwards\n",
            "1\n00:00:00,000 --> 00:00:06,000\nPast duration\n",
            "1\n00:00:03,000 --> 00:00:04,000\nLater\n\n2\n00:00:01,000 --> 00:00:02,000\nEarlier\n",
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "timeline.srt"
            for value in examples:
                with self.subTest(value=value):
                    path.write_text(value)
                    with self.assertRaises(ValueError):
                        companion.parse_subtitles(path, 5)

    def test_existing_output_is_preserved_without_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "timeline.srt"
            source.write_text("1\n00:00:00,000 --> 00:00:01,000\nHello\n")
            output = root / "output"
            output.mkdir()
            transcript = output / "transcript.txt"
            transcript.write_text("reviewed copy")
            with self.assertRaises(FileExistsError):
                companion.build(source, output, 2)
            self.assertEqual(transcript.read_text(), "reviewed copy")
            self.assertFalse((output / "speech.json").exists())

            companion.build(source, output, 2, overwrite=True)
            self.assertEqual(transcript.read_text(), "Hello\n")


if __name__ == "__main__":
    unittest.main()
