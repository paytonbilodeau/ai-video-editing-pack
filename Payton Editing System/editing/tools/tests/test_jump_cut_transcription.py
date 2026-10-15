import contextlib
import io
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jump_cut_vad_parallel as speech


class TranscriptionPromptTests(unittest.TestCase):
    def setUp(self):
        self.recognition = {'segments': [{'words': [
            {'word': ' Hello ', 'start': 1, 'end': 1.5, 'probability': .9},
            {'word': ' WORLD', 'start': 1.5, 'end': 2, 'score': .7},
            {'word': ' Again', 'start': 2, 'end': 2.5},
        ]}]}
        self.expected = [
            {'word': 'hello', 'start': 1.0, 'end': 1.5, 'confidence': .9},
            {'word': 'world', 'start': 1.5, 'end': 2.0, 'confidence': .7},
            {'word': 'again', 'start': 2.0, 'end': 2.5, 'confidence': .8},
        ]

    def check_backend(self, fallback, prompt, explicit):
        mlx = SimpleNamespace(transcribe=Mock(
            return_value=self.recognition,
            side_effect=RuntimeError('MLX unavailable') if fallback else None))
        cpu_model = SimpleNamespace(transcribe=Mock(return_value=self.recognition))
        cpu = SimpleNamespace(load_model=Mock(return_value=cpu_model))
        kwargs = {'initial_prompt': prompt} if explicit else {}
        with patch.dict(sys.modules, {'mlx_whisper': mlx, 'whisper': cpu}), \
                contextlib.redirect_stdout(io.StringIO()):
            result = speech.transcribe_with_whisper('fixture.wav', 'medium', **kwargs)

        self.assertEqual(result, self.expected)
        common = dict(word_timestamps=True, initial_prompt=prompt,
                      language='en', condition_on_previous_text=False)
        mlx.transcribe.assert_called_once_with(
            'fixture.wav', path_or_hf_repo=speech.MLX_WHISPER_REPOS['medium'], **common)
        if fallback:
            cpu.load_model.assert_called_once_with('medium')
            cpu_model.transcribe.assert_called_once_with('fixture.wav', **common)
        else:
            cpu.load_model.assert_not_called()

    def test_mlx_default_is_unprimed(self):
        self.check_backend(fallback=False, prompt=None, explicit=False)

    def test_mlx_explicit_prompt_is_preserved(self):
        self.check_backend(fallback=False, prompt='A deliberate source hint.', explicit=True)

    def test_cpu_fallback_default_is_unprimed(self):
        self.check_backend(fallback=True, prompt=None, explicit=False)

    def test_cpu_fallback_explicit_prompt_is_preserved(self):
        self.check_backend(fallback=True, prompt='cut cut. full stop restart.', explicit=True)

    def test_prompt_is_keyword_only(self):
        with self.assertRaises(TypeError):
            speech.transcribe_with_whisper('fixture.wav', 'medium', 'source hint')


if __name__ == '__main__':
    unittest.main()
