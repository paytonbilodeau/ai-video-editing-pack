"""Portable-copy regression tests. All provider operations are mocked."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
TOOLS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TOOLS))
import rsvp_captions as captions
import auphonic_enhance as auphonic
import jump_cut_vad_parallel as jump

class PortableTiming(unittest.TestCase):
    def test_word_json_keeps_hyphens_and_real_gap(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'words.json';p.write_text(json.dumps({'words':[{'word':'source-timed','start':0.13791,'end':0.5},{'word':'caption','start':0.8,'end':1.0}]}))
            words=captions.parse_transcript_words(str(p))
            self.assertEqual(words[0]['word'],'source-timed')
            self.assertEqual(words[0]['start'],0.13791)
            self.assertEqual(words[0]['end'],0.5)
    def test_html_uses_same_exact_word_parser(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'words.html';p.write_text('<script type="application/json">'+json.dumps({'words':[{'word':'one','start':0.11111,'end':0.3},{'word':'two','start':0.5,'end':0.7}]})+'</script>')
            words=captions.parse_html_words(str(p))
            self.assertEqual([(w['start'],w['end']) for w in words],[(0.11111,0.3),(0.5,0.7)])
    def test_segments_refused_by_default(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'segments.vtt';p.write_text('WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nhello world\n')
            with self.assertRaisesRegex(ValueError,'not word timing'): captions.parse_transcript_words(str(p))
            self.assertEqual(len(captions.parse_transcript_words(str(p),allow_estimated=True)),2)
    def test_bad_or_ambiguous_words_fail(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'words.json'
            for data in [{'words':[{'word':'bad','start':True,'end':1}]},{'words':[{'word':'bad','start':1,'end':0}]},{'segments':[{'text':'Not real words','start':0,'end':2}]}]:
                p.write_text(json.dumps(data))
                with self.assertRaises(ValueError):captions.parse_transcript_words(str(p))
    def test_caption_output_cannot_overwrite_source(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'source.mp4';p.write_bytes(b'original')
            with self.assertRaises((ValueError,FileExistsError)):captions.rsvp_captions(str(p),'not-read.json',str(p))
            self.assertEqual(p.read_bytes(),b'original')

class PortableProvider(unittest.TestCase):
    def test_exact_preset_name_only(self):
        with patch.object(auphonic,'load_presets',return_value={'Wireless mic':'mock-wireless'}),patch.object(auphonic,'fetch_presets_from_api',return_value=[{'preset_name':'Wireless mic','uuid':'mock-wireless'}]),patch.object(auphonic,'save_presets'):
            self.assertEqual(auphonic.resolve_preset_uuid('WIRELESS MIC'),'mock-wireless')
            with self.assertRaisesRegex(ValueError,'not found'):auphonic.resolve_preset_uuid('mic')
    def test_presets_cache_creates_only_requested_parent(self):
        with tempfile.TemporaryDirectory() as t,patch.object(auphonic,'PRESETS_CONFIG_PATH',Path(t)/'new/cache.json'):
            auphonic.save_presets({'example':'mock-id'})
            self.assertEqual(auphonic.load_presets(),{'example':'mock-id'})
    def test_output_collision_precedes_provider(self):
        with tempfile.TemporaryDirectory() as t,patch.object(auphonic,'create_auphonic_production') as create:
            p=Path(t)/'source.mp4';p.write_bytes(b'original')
            with self.assertRaises(FileExistsError):auphonic.enhance_video(str(p),str(p),preset_name='anything')
            create.assert_not_called();self.assertEqual(p.read_bytes(),b'original')
    def test_sidecar_collision_precedes_provider(self):
        with tempfile.TemporaryDirectory() as t,patch.object(auphonic,'create_auphonic_production') as create:
            p=Path(t)/'source.mp4';p.write_bytes(b'original')
            (Path(t)/'final_chapters.json').write_text('keep')
            with self.assertRaisesRegex(FileExistsError,'sidecar'):auphonic.enhance_video(str(p),str(Path(t)/'final.mp4'),preset_name='anything')
            create.assert_not_called();self.assertEqual((Path(t)/'final_chapters.json').read_text(),'keep')

class PortableCutGuard(unittest.TestCase):
    def test_existing_export_fails_before_analysis(self):
        with tempfile.TemporaryDirectory() as t,patch.object(jump,'get_duration') as probe:
            src=Path(t)/'source.mp4';src.write_bytes(b'original');out=Path(t)/'out.mp4';out.write_bytes(b'keep')
            with patch.object(sys,'argv',['jump',str(src),str(out)]):
                with self.assertRaises(FileExistsError):jump.main()
            probe.assert_not_called();self.assertEqual(out.read_bytes(),b'keep')

if __name__=='__main__':unittest.main()

class PortableRemux(unittest.TestCase):
    def test_mismatched_audio_refuses_before_encode(self):
        with tempfile.TemporaryDirectory() as t,patch.object(auphonic,'media_stream_duration',side_effect=[10.0,9.0]),patch.object(auphonic.subprocess,'run') as run:
            with self.assertRaisesRegex(ValueError,'duration differs'):auphonic.remux_video_with_audio('video.mp4','audio.wav',str(Path(t)/'fresh.mp4'))
            run.assert_not_called()
    def test_matched_mux_preserves_full_video(self):
        with tempfile.TemporaryDirectory() as t,patch.object(auphonic,'media_stream_duration',side_effect=[10.0,10.02]),patch.object(auphonic.subprocess,'run') as run:
            run.return_value.returncode=0
            auphonic.remux_video_with_audio('video.mp4','audio.wav',str(Path(t)/'fresh.mp4'))
            cmd=run.call_args.args[0]
            self.assertNotIn('-shortest',cmd);self.assertIn('-n',cmd)

class PortableDerivatives(unittest.TestCase):
    def test_timestamp_rounding_carries_minutes(self):
        import waterfall_transcribe as wt
        self.assertEqual(wt.fmt_ts(59.9999),'00:01:00.000')
        self.assertEqual(wt.fmt_ts(3599.9999,','),'01:00:00,000')
    def test_real_clip_words_rebase_without_interpolation(self):
        import waterfall_transcribe as wt
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);(d/'transcript.json').write_text(json.dumps({'segments':[{'start':1,'end':3,'text':'One two','words':[{'word':'One','start':1.2,'end':1.5},{'word':'two','start':2.2,'end':2.5}]}]}));(d/'map.json').write_text(json.dumps({'shorts':[{'id':'short_01','start':1,'end':3}]}))
            wt.emit_clip_vtts(d/'map.json',d)
            words=json.loads((d/'short_01.words.json').read_text())['words']
            self.assertAlmostEqual(words[0]['start'],.2);self.assertEqual(words[0]['end'],.5)
            with self.assertRaises(FileExistsError):wt.emit_clip_vtts(d/'map.json',d)
    def test_word_crossing_boundary_and_path_traversal_fail(self):
        import waterfall_transcribe as wt
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);(d/'transcript.json').write_text(json.dumps({'words':[{'word':'whole','start':1,'end':2}]}))
            for clip in [{'id':'short','start':1.5,'end':3},{'id':'../outside','start':0,'end':3}]:
                (d/'map.json').write_text(json.dumps({'shorts':[clip]}))
                with self.assertRaises(ValueError):wt.emit_clip_vtts(d/'map.json',d)
            self.assertEqual(len(list(d.glob('*.vtt'))),0)
    def test_mid_existing_outputs_preserved(self):
        import extract_mid_clips as mid
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);(d/'keep.txt').write_text('existing')
            with self.assertRaises(FileExistsError):mid.extract(Path('source.mp4'),d,[],False)
            self.assertEqual((d/'keep.txt').read_text(),'existing')
