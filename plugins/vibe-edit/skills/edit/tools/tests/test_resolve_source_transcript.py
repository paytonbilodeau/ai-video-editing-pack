import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import resolve_source_transcript as transcript


class SourceTranscriptTests(unittest.TestCase):
    def test_repetitions_and_incomplete_words_are_preserved_as_unverified(self):
        words = [{'word': text, 'start': i * .2, 'end': i * .2 + .15}
                 for i, text in enumerate(['i', 'i', 'th-', 'think'])]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = transcript.write_draft(root, {'source': 'fixture.wav',
                'source_sha256': 'fixture', 'duration_seconds': 1}, words)
            self.assertEqual(json.loads((root/'source-words.auto.json').read_text()), words)
            self.assertFalse(result['source_verified'])
            self.assertEqual(result['state'], 'unverified_asr_draft')
            self.assertIn('th-', (root/'source-transcript.auto.md').read_text())
            self.assertIn('State: pending', (root/'source-review.md').read_text())

    def test_invalid_or_invented_time_intervals_are_rejected(self):
        for start, end in [(-1, .2), (.3, .2), (0, 2), (float('nan'), .2)]:
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                transcript.validate_words([{'word': 'test', 'start': start, 'end': end}], 1)

    def test_source_order_is_required_but_overlap_is_preserved(self):
        words = [{'word': 'one', 'start': .1, 'end': .4},
                 {'word': 'two', 'start': .3, 'end': .5}]
        transcript.validate_words(words, 1)
        with self.assertRaises(ValueError):
            transcript.validate_words(list(reversed(words)), 1)

    def test_timestamp_rolls_minutes_and_hours_correctly(self):
        self.assertEqual(transcript.timestamp(59.9996), '00:01:00.000')
        self.assertEqual(transcript.timestamp(3599.9996), '01:00:00.000')

    def test_existing_review_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root/'source.wav'; source.write_bytes(b'not media')
            destination = root/'review'; destination.mkdir()
            original = destination/'source-review.md'; original.write_text('accepted corrections')
            with self.assertRaises(FileExistsError):
                transcript.prepare(source, destination, 'medium')
            self.assertEqual(original.read_text(), 'accepted corrections')


if __name__ == '__main__':
    unittest.main()
