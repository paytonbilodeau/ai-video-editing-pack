"""Local-only and output-preservation contracts for the optional adapter."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location('transcribe_local', Path(__file__).parents[1] / 'transcribe_local.py')
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)

class LocalTranscription(unittest.TestCase):
    def invoke(self, args):
        with patch.object(sys, 'argv', ['transcribe_local.py'] + args), contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            adapter.main()

    def test_existing_output_is_untouched_before_model_or_media_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'kept.json'; out.write_text('keep this')
            with patch.object(adapter.subprocess, 'run') as run, self.assertRaises(SystemExit):
                self.invoke([str(Path(tmp)/'missing.wav'), '--output', str(out)])
            run.assert_not_called(); self.assertEqual(out.read_text(), 'keep this')

    def test_cached_model_only_and_ffmpeg_decoding(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'control.wav'; source.write_bytes(b'local fixture')
            out = Path(tmp)/'result.json'
            model = Mock(); model.transcribe.return_value = ([], types.SimpleNamespace())
            factory = Mock(return_value=model)
            numpy = types.SimpleNamespace(float32='float32', frombuffer=Mock(return_value='decoded PCM'))
            modules = {'numpy': numpy, 'faster_whisper': types.SimpleNamespace(WhisperModel=factory)}
            with patch.dict(sys.modules, modules), patch.object(adapter.subprocess, 'run', return_value=types.SimpleNamespace(stdout=b'PCM')) as run:
                self.invoke([str(source), '--output', str(out), '--ffmpeg', '/example/ffmpeg', '--model', 'cached-control'])
            self.assertTrue(factory.call_args.kwargs['local_files_only'])
            self.assertEqual(model.transcribe.call_args.args, ('decoded PCM',))
            self.assertIn('f32le', run.call_args.args[0])
            result=json.loads(out.read_text());self.assertEqual(result['source'], 'control.wav')
            self.assertIn('estimates', result['alignment']);self.assertNotIn(tmp, out.read_text())

    def test_missing_ffmpeg_stops_without_install_or_decode(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'control.wav';source.write_bytes(b'control')
            with patch.object(adapter.shutil,'which',return_value=None),patch.object(adapter.subprocess,'run') as run,self.assertRaises(SystemExit):
                self.invoke([str(source),'--output',str(Path(tmp)/'result.json')])
            run.assert_not_called()

if __name__ == '__main__': unittest.main()
