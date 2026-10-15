import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import urllib.request

SYSTEM = Path(__file__).resolve().parents[3]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, SYSTEM / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


chapter = load('secure_chapter', 'editing/tools/auphonic_chapter_timer.py')
audio = load('secure_audio', 'editing/tools/auphonic_enhance.py')
music = load('secure_music', 'motion/tools/optional/flow_music.py')


class CredentialBoundaryTests(unittest.TestCase):
    def test_only_exact_api_origin_receives_key(self):
        self.assertEqual(chapter._download_headers('https://auphonic.com/api/download/file', 'test'),
                         {'Authorization': 'Bearer test'})
        for url in ('https://cdn.example.test/audio', 'https://auphonic.com.evil.test/audio',
                    'https://auphonic.com:8443/audio'):
            self.assertEqual(chapter._download_headers(url, 'test'), {})
        for url in ('http://auphonic.com/audio', 'file:///tmp/audio',
                    'https://user:pass@auphonic.com/audio'):
            with self.assertRaises(ValueError):
                chapter._download_headers(url, 'test')

    def test_redirect_drops_key_before_cross_origin_request(self):
        request = urllib.request.Request('https://auphonic.com/api/download/file',
                                         headers={'Authorization': 'Bearer test'})
        handler = chapter._SafeDownloadRedirect()
        same = handler.redirect_request(request, None, 302, 'Found', {},
                                        'https://auphonic.com/download/next')
        self.assertEqual(same.get_header('Authorization'), 'Bearer test')
        foreign = handler.redirect_request(request, None, 302, 'Found', {},
                                           'https://cdn.example.test/signed-file')
        self.assertIsNone(foreign.get_header('Authorization'))
        with self.assertRaises(ValueError):
            handler.redirect_request(request, None, 302, 'Found', {},
                                     'http://cdn.example.test/file')

    def test_invalid_production_never_opens_network(self):
        with patch.object(chapter.urllib.request, 'build_opener') as opener:
            for value in ('../presets', 'id?redirect=other', 'id/extra', '', 'a' * 129):
                with self.assertRaises(ValueError):
                    chapter.fetch_speech_json(value)
            opener.assert_not_called()

    def test_audio_initial_cdn_download_has_no_key(self):
        response = Mock()
        response.iter_content.return_value = [b'audio']
        with tempfile.TemporaryDirectory() as directory, patch.object(audio.requests, 'get', return_value=response) as get:
            output = Path(directory) / 'audio.wav'
            self.assertTrue(audio._download_file('https://cdn.example.test/signed-file', str(output)))
            self.assertEqual(get.call_args.kwargs['headers'], {})
            self.assertEqual(output.read_bytes(), b'audio')

    def test_audio_rejects_unsafe_scheme_before_network(self):
        with patch.object(audio.requests, 'get') as get:
            self.assertFalse(audio._download_file('http://auphonic.com/audio', 'unused.wav'))
            self.assertFalse(audio._download_file('file:///tmp/audio', 'unused.wav'))
            get.assert_not_called()


class TemporaryAudioTests(unittest.TestCase):
    def test_private_intermediate_is_cleaned_after_failure(self):
        observed = []
        def save(path, _audio, _rate):
            path = Path(path)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
            path.write_bytes(b'private intermediate')
            observed.append(path)
        with patch.object(music, 'save_wav', side_effect=save), patch.object(music.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'ffmpeg')):
            with self.assertRaises(subprocess.CalledProcessError):
                music.finish_audio(None, 48000, 'output.wav', -32)
        self.assertEqual(len(observed), 1)
        self.assertFalse(observed[0].parent.exists())

    def test_output_and_arguments_remain_explicit(self):
        paths = []
        def save(path, _audio, _rate):
            Path(path).write_bytes(b'audio')
            paths.append(Path(path))
        with patch.object(music, 'save_wav', side_effect=save), patch.object(music.subprocess, 'run') as run:
            music.finish_audio(None, 48000, 'output with spaces.wav', -32)
            args = run.call_args.args[0]
            self.assertEqual(args[0], 'ffmpeg')
            self.assertIn('-n', args)
            self.assertEqual(args[-1], os.path.abspath('output with spaces.wav'))
            self.assertEqual(args[args.index('-i') + 1], str(paths[0]))
            self.assertNotIn('shell', run.call_args.kwargs)
        self.assertFalse(paths[0].parent.exists())



class ParserBoundaryTests(unittest.TestCase):
    def test_long_timecode_is_rejected_before_conversion(self):
        companion = load('secure_companion', 'editing/tools/resolve_audio_companion.py')
        with self.assertRaises(ValueError):
            companion.timecode_to_frames('9' * 1000000 + ':00:00:00', 24)
        self.assertEqual(companion.timecode_to_frames('01:02:03:04', 24), 89356)

    def test_scene_limits_brand_matching_without_nested_regex(self):
        drawing = load('secure_drawing', 'motion/tools/optional/generate_hand_drawn.py')
        registry = {'apple': {'keywords': ['Apple']}, 'google': {'keywords': ['Google']}}
        prompt = 'SCENE: An Apple computer.\n\nSTYLE LOCK: Google is only an example.'
        self.assertEqual(drawing.detect_brands_in_prompt(prompt, registry), ['apple'])
        self.assertEqual(drawing.detect_brands_in_prompt('An Apple computer', registry), ['apple'])
        malformed = 'SCENE:' + '\n ' * 100000
        self.assertEqual(drawing.detect_brands_in_prompt(malformed, registry), [])

    def test_svg_attributes_decode_and_layout_stays_correct(self):
        script = SYSTEM / 'motion/skills/embedded-captions/scripts/gen-stroke-path.py'
        with tempfile.TemporaryDirectory() as directory:
            font = Path(directory) / 'font.svg'
            font.write_text('<svg><defs><font><glyph d="M 0 0 L 100 100" horiz-adv-x="100" unicode="A"/></font></defs></svg>')
            result = subprocess.run([sys.executable, str(script), str(font), 'A', '100', '100', '10'], capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), 'M 10.0 100.0 L 110.0 0.0')
            font.write_text('<!DOCTYPE svg [<!ENTITY x "unsafe">]><svg/>')
            denied = subprocess.run([sys.executable, str(script), str(font), 'A', '100', '100', '10'], capture_output=True, text=True)
            self.assertNotEqual(denied.returncode, 0)
            self.assertIn('unsupported entities', denied.stderr)

if __name__ == '__main__':
    unittest.main()
