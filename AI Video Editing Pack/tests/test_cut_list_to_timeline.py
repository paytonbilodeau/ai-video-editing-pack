"""Offline checks for the cut-list exporter."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree as ET

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
import cut_list_to_timeline as exporter  # noqa: E402

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "example-cut-list.json"
APPLE_DTD = Path("/Applications/Final Cut Pro.app/Contents/Frameworks/Interchange.framework/Versions/A/Resources/FCPXMLv1_11.dtd")


def load_example(**overrides):
    data = json.loads(EXAMPLE.read_text())
    data.update(overrides)
    return exporter.build_cut_list(data, base_dir=EXAMPLE.parent)


class TimeTests(unittest.TestCase):
    def test_rates_are_exact_fractions(self):
        self.assertEqual(exporter.parse_rate(30), Fraction(30))
        self.assertEqual(exporter.parse_rate("29.97"), Fraction(30000, 1001))
        self.assertEqual(exporter.parse_rate(29.97), Fraction(30000, 1001))
        self.assertEqual(exporter.parse_rate("24000/1001"), Fraction(24000, 1001))
        with self.assertRaises(exporter.CutListError):
            exporter.parse_rate("0")

    def test_time_forms_snap_to_frames(self):
        rate = Fraction(30)
        self.assertEqual(exporter.parse_time(1.5, rate), 45)
        self.assertEqual(exporter.parse_time("0:01.500", rate), 45)
        self.assertEqual(exporter.parse_time("00:00:01:15", rate), 45)
        self.assertEqual(exporter.parse_time("1:00:00.000", rate), 108000)
        self.assertEqual(exporter.parse_time(1.0167, rate), 31)
        with self.assertRaises(exporter.CutListError):
            exporter.parse_time(-1, rate)

    def test_rational_time_and_timecode(self):
        self.assertEqual(exporter.rational_time(30, Fraction(30)), "1s")
        self.assertEqual(exporter.rational_time(45, Fraction(30)), "3/2s")
        self.assertEqual(exporter.rational_time(1, Fraction(30000, 1001)), "1001/30000s")
        self.assertEqual(exporter.timecode(108031, Fraction(30)), "01:00:01:01")
        self.assertEqual(exporter.timecode(108001, Fraction(30)), "01:00:00:01")
        self.assertEqual(exporter.timecode(29, Fraction(30000, 1001)), "00:00:00:29")


class CutListTests(unittest.TestCase):
    def test_unusual_probed_rate_warns_without_changing_it(self):
        data = json.loads(EXAMPLE.read_text())
        del data["fps"]
        with patch.object(exporter, "probe_source", return_value={**data, "fps": "14985/499"}):
            cut = exporter.build_cut_list(data, base_dir=EXAMPLE.parent, probe=True)
        self.assertEqual(cut.rate, Fraction(14985, 499))
        self.assertTrue(any("supply fps explicitly" in w for w in cut.warnings))

    def test_explicit_rate_survives_probe_and_avoids_average_rate_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.mp4"
            source.touch()
            data = {"source": str(source), "fps": 30, "keep": [[0, 1]]}
            probe_json = {"streams": [{"codec_type": "video", "width": 640, "height": 360,
                                       "avg_frame_rate": "14985/499", "r_frame_rate": "30/1"}],
                          "format": {"duration": "10"}}
            result = subprocess.CompletedProcess([], 0, json.dumps(probe_json), "")
            with patch.object(exporter.shutil, "which", return_value="ffprobe"), patch.object(exporter.subprocess, "run", return_value=result):
                cut = exporter.build_cut_list(data, base_dir=Path(directory), probe=True)
            self.assertEqual(cut.rate, Fraction(30))
            self.assertEqual(cut.total_frames, 30)
            self.assertFalse(any("probed average" in w for w in cut.warnings))

    def test_example_loads_sorted_with_record_positions(self):
        cut = load_example()
        self.assertEqual(len(cut.segments), 4)
        self.assertEqual(cut.segments[0].source_in, 111)
        self.assertEqual(cut.segments[2].source_in, 46 * 30 + 12)
        self.assertEqual(cut.segments[1].record_in, cut.segments[0].frames)
        self.assertEqual(cut.total_frames, sum(s.frames for s in cut.segments))
        self.assertTrue(any("not found" in warning for warning in cut.warnings))

    def test_remove_list_is_inverted_against_duration(self):
        cut = load_example(keep=None, remove=[{"start": 0, "end": 2}, {"start": 10, "end": 12.5}])
        cut_data = json.loads(EXAMPLE.read_text())
        del cut_data["keep"]
        cut_data["remove"] = [{"start": 0, "end": 2}, {"start": 10, "end": 12.5}]
        cut = exporter.build_cut_list(cut_data, base_dir=EXAMPLE.parent)
        self.assertEqual([(s.source_in, s.source_out) for s in cut.segments], [(60, 300), (375, 2865)])
        with self.assertRaises(exporter.CutListError):
            exporter.build_cut_list({**cut_data, "duration": None}, base_dir=EXAMPLE.parent)

    def test_overlaps_merge_and_slivers_warn(self):
        data = json.loads(EXAMPLE.read_text())
        data["keep"] = [[10, 12], [11, 13], [13, 14], [20, 20.03], [30, 30]]
        cut = exporter.build_cut_list(data, base_dir=EXAMPLE.parent)
        self.assertEqual([(s.source_in, s.source_out) for s in cut.segments], [(300, 420), (600, 601)])
        self.assertTrue(any("merged overlapping" in w for w in cut.warnings))
        self.assertTrue(any("only 1 frame" in w for w in cut.warnings))
        self.assertTrue(any("dropped an empty" in w for w in cut.warnings))

    def test_rejects_bad_input(self):
        base = json.loads(EXAMPLE.read_text())
        for broken in (
            {**base, "keep": None},
            {**base, "keep": [], },
            {**base, "keep": [[5, 4]]},
            {**base, "fps": None},
            {**base, "source": ""},
            {**base, "remove": [[0, 1]]},
        ):
            with self.assertRaises(exporter.CutListError):
                exporter.build_cut_list(broken, base_dir=EXAMPLE.parent)
        with self.assertRaises(exporter.CutListError):
            exporter.build_cut_list({**base, "keep": [[0, 1]], "duration": 95.5, "width": 0}, base_dir=EXAMPLE.parent)


class WriterTests(unittest.TestCase):
    def test_fcpxml_structure_and_timing(self):
        cut = load_example()
        root = ET.fromstring(exporter.write_fcpxml(cut).encode())
        self.assertEqual(root.attrib["version"], "1.11")
        fmt = root.find("resources/format")
        self.assertEqual(fmt.attrib["frameDuration"], "1/30s")
        self.assertEqual(fmt.attrib["name"], "FFVideoFormat2160p30")
        asset = root.find("resources/asset")
        self.assertEqual(asset.attrib["duration"], exporter.rational_time(2865, Fraction(30)))
        self.assertTrue(asset.find("media-rep").attrib["src"].startswith("file:///"))
        clips = root.findall("library/event/project/sequence/spine/asset-clip")
        self.assertEqual(len(clips), 4)
        self.assertEqual(clips[0].attrib["offset"], "0s")
        self.assertEqual(clips[1].attrib["offset"], exporter.rational_time(cut.segments[0].frames, Fraction(30)))
        self.assertEqual(root.find("library/event/project/sequence").attrib["duration"], exporter.rational_time(cut.total_frames, Fraction(30)))
        markers = root.findall(".//marker")
        self.assertEqual(len(markers), 2)
        self.assertEqual(markers[0].attrib["start"], exporter.rational_time(906, Fraction(30)))

    def test_fcpxml_names_fractional_rates(self):
        cut = load_example(fps="29.97", width=1920, height=1080)
        text = exporter.write_fcpxml(cut)
        self.assertIn('frameDuration="1001/30000s"', text)
        self.assertIn('name="FFVideoFormat1080p2997"', text)

    def test_xmeml_links_video_and_audio(self):
        cut = load_example(fps="29.97")
        root = ET.fromstring(exporter.write_xmeml(cut).encode())
        self.assertEqual(root.find("sequence/rate/ntsc").text, "TRUE")
        self.assertEqual(root.find("sequence/rate/timebase").text, "30")
        video_clips = root.findall("sequence/media/video/track/clipitem")
        audio_tracks = root.findall("sequence/media/audio/track")
        self.assertEqual(len(video_clips), 4)
        self.assertEqual(len(audio_tracks), 2)
        self.assertEqual(len(audio_tracks[0].findall("clipitem")), 4)
        first = video_clips[0]
        self.assertEqual(first.find("in").text, "111")
        self.assertEqual(first.find("start").text, "0")
        self.assertEqual(len(first.findall("link")), 3)
        self.assertIsNotNone(first.find("file/pathurl"))
        self.assertIsNone(video_clips[1].find("file/pathurl"))
        self.assertEqual(len(root.findall("sequence/marker")), 2)

    def test_edl_events_and_markers(self):
        cut = load_example()
        edl = exporter.write_edl(cut)
        lines = edl.splitlines()
        self.assertEqual(lines[0], "TITLE: desk-tutorial clean cut v1")
        self.assertEqual(lines[1], "FCM: NON-DROP FRAME")
        events = [line for line in lines if line[:3].isdigit()]
        self.assertEqual(len(events), 4)
        self.assertTrue(events[0].startswith("001  AX       AA/V  C        00:00:03:21 00:00:22:04 00:00:00:00 00:00:18:13"))
        self.assertIn("* FROM CLIP NAME: desk-tutorial-take-2.mp4", edl)
        self.assertEqual(edl.count("* LOC:"), 2)

    def test_sheet_lists_kept_and_removed_ranges(self):
        cut = load_example()
        md, csv_text = exporter.write_sheet(cut)
        self.assertIn("| 1 | 00:00:03:21 (3.700s)", md)
        self.assertIn("## Removed ranges", md)
        self.assertIn("| 00:00:00:00 (0.000s) | 00:00:03:21 (3.700s)", md)
        self.assertEqual(csv_text.splitlines()[0], "clip,source_in_tc,source_out_tc,source_in_s,source_out_s,frames,output_in_tc,output_out_tc,note")
        self.assertEqual(len(csv_text.splitlines()), 5)


class ExportTests(unittest.TestCase):
    def test_export_writes_all_formats_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "exports"
            cut = load_example()
            written = exporter.export(cut, out, exporter.FORMATS, overwrite=False, fcpxml_version="1.11")
            self.assertEqual(set(written), {"fcpxml", "xmeml", "edl", "sheet", "sheet_csv", "summary"})
            report = json.loads(written["summary"].read_text())
            self.assertEqual(report["clips"], 4)
            self.assertEqual(report["markers"], 2)
            self.assertEqual(set(report["sha256"]), set(written) - {"summary"})
            with self.assertRaisesRegex(exporter.CutListError, "refusing to overwrite"):
                exporter.export(cut, out, exporter.FORMATS, overwrite=False, fcpxml_version="1.11")
            again = exporter.export(load_example(), out, exporter.FORMATS, overwrite=True, fcpxml_version="1.11")
            self.assertEqual(json.loads(again["summary"].read_text())["sha256"], report["sha256"])

    def test_output_inside_pack_is_rejected(self):
        with self.assertRaisesRegex(exporter.CutListError, "outside the pack"):
            exporter.export(load_example(), exporter.PACK_ROOT / "exports", exporter.FORMATS, False, "1.11")

    def test_cli_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "out"
            result = subprocess.run(
                [sys.executable, "-B", str(TOOLS / "cut_list_to_timeline.py"), str(EXAMPLE), "--out-dir", str(out), "--formats", "fcpxml,edl"],
                capture_output=True, text=True, check=True,
            )
            self.assertIn("4 clip(s)", result.stdout)
            self.assertTrue((out / "desk-tutorial clean cut v1.fcpxml").is_file())
            self.assertTrue((out / "desk-tutorial clean cut v1.edl").is_file())
            self.assertFalse((out / "desk-tutorial clean cut v1.premiere.xml").exists())
            bad = subprocess.run(
                [sys.executable, "-B", str(TOOLS / "cut_list_to_timeline.py"), str(EXAMPLE), "--out-dir", str(out), "--formats", "edl"],
                capture_output=True, text=True,
            )
            self.assertEqual(bad.returncode, 1)
            self.assertIn("refusing to overwrite", bad.stdout)

    @unittest.skipUnless(APPLE_DTD.is_file() and shutil.which("xmllint"), "Apple FCPXML DTD or xmllint unavailable")
    def test_fcpxml_validates_against_apple_dtd(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            written = exporter.export(load_example(), out, ("fcpxml",), False, "1.11")
            self.assertTrue(exporter.validate_with_dtd(written["fcpxml"], APPLE_DTD).startswith("valid"))


if __name__ == "__main__":
    unittest.main()
