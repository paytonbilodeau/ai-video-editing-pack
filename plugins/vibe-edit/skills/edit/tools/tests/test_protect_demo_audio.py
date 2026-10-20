import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np
import soundfile as sf

spec = importlib.util.spec_from_file_location('protect_demo_audio', Path(__file__).parents[1] / 'protect_demo_audio.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ProtectedAudioTests(unittest.TestCase):
    def test_loud_quiet_sequence_preserved_and_narration_processed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            phase = np.arange(10000) * 0.071
            original = np.column_stack([np.sin(phase), np.cos(phase)]).astype(np.float32) * .1
            original[3000:4000] *= 5
            original[4000:5000] *= .1
            processed = np.full_like(original, .02)
            sf.write(root/'original.wav', original, 1000, subtype='FLOAT')
            sf.write(root/'processed.wav', processed, 1000, subtype='FLOAT')
            manifest = {'fps': 10, 'frames': 100, 'ranges': [{'start_frame': 30, 'end_frame': 50}]}
            report = mod.restore(root/'original.wav', root/'processed.wav', manifest, root/'out.wav', 40)
            out, _ = sf.read(root/'out.wav', dtype='float32', always_2d=True)
            np.testing.assert_array_equal(out[3000:5000], original[3000:5000])
            np.testing.assert_array_equal(out[:2960], processed[:2960])
            np.testing.assert_array_equal(out[5040:], processed[5040:])
            self.assertEqual(len(out), 10000)
            self.assertTrue(report['protected_samples_identical'])

    def test_adjacent_and_overlapping_ranges_merge(self):
        spans = mod.normalize_ranges([{'start_frame': 3, 'end_frame': 5}, {'start_frame': 5, 'end_frame': 7}, {'start_frame': 4, 'end_frame': 6}], 10, 1000, 1000)
        self.assertEqual(spans, [(300, 700)])
        np.testing.assert_array_equal(mod.weights(300, 400, spans, 40), np.ones(400))

    def test_range_at_file_edges_has_no_internal_fade(self):
        w = mod.weights(0, 1000, [(0, 100), (900, 1000)], 40)
        np.testing.assert_array_equal(w[:100], np.ones(100))
        np.testing.assert_array_equal(w[900:], np.ones(100))
        self.assertEqual(w[500], 0)

    def test_invalid_range_rejected(self):
        for row in [{'start_frame': 3, 'end_frame': 2}, {'start_frame': 0, 'end_frame': 11}, {'start_frame': .5, 'end_frame': 2}]:
            with self.assertRaises(ValueError):
                mod.normalize_ranges([row], 10, 1000, 1000)

    def test_duration_shift_is_not_silently_fixed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sf.write(root/'a.wav', np.zeros(1000), 1000, subtype='FLOAT')
            sf.write(root/'b.wav', np.zeros(1300), 1000, subtype='FLOAT')
            with self.assertRaisesRegex(ValueError, 'duration'):
                mod.restore(root/'a.wav', root/'b.wav', {'fps': 10, 'frames': 10, 'ranges': [{'start_frame': 2, 'end_frame': 3}]}, root/'out.wav')


if __name__ == '__main__':
    unittest.main()
