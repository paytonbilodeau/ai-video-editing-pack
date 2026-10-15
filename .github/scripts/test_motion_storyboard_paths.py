"""Offline regressions for filename-only identifiers in imported storyboards."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Payton Editing System/motion/tools/optional/generate_motion_short.py"
spec = importlib.util.spec_from_file_location("motion_storyboard_path_review", SOURCE)
motion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(motion)


def storyboard(slug):
    return {"beats": [{"slug": slug, "line": "A complete idea", "seconds": 1,
                        "keyframe_prompt": "A test image", "motion_prompt": "A test movement"}]}


class StoryboardPaths(unittest.TestCase):
    def test_existing_basename_and_automatic_numbering_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "storyboard.json"
            for supplied, expected in (("01_context-folder", "01_context-folder"),
                                       ("01_My reference", "01_My reference"),
                                       ("context folder", "01_context-folder"),
                                       (None, "01_a-complete-idea")):
                with self.subTest(slug=supplied):
                    source.write_text(json.dumps(storyboard(supplied)))
                    self.assertEqual(motion.all_beats(motion.load_storyboard(source))[0]["slug"], expected)

    def test_malformed_identifiers_fail_before_any_generation_or_force_deletion(self):
        bad_slugs = ["01_x/../../../outside", "../outside", "/tmp/outside", ".", "..",
                     "01_x\\..\\outside", "C:\\outside", "C:outside", "\\\\host\\share",
                     "01_x\x00outside", "01_x\noutside", "01_x\x7foutside", "01_x\x85outside", 12]
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "storyboard.json"
            outside = base / "outside.png"
            outside.write_bytes(b"preserve this existing file")
            for slug in bad_slugs:
                for forced in (False, True):
                    with self.subTest(slug=slug, force=forced):
                        source.write_text(json.dumps(storyboard(slug)))
                        output = base / "chosen-output"
                        argv = [str(SOURCE), str(source), "--out-dir", str(output), "--assemble-only"]
                        if forced:
                            argv += ["--force", str(slug)]
                        with patch("sys.argv", argv), patch.object(motion, "download") as download, \
                                patch.object(motion, "run_ffmpeg") as render, \
                                patch.object(motion.urllib.request, "urlopen") as network, \
                                contextlib.redirect_stderr(io.StringIO()):
                            with self.assertRaises(SystemExit):
                                motion.main()
                            download.assert_not_called()
                            render.assert_not_called()
                            network.assert_not_called()
                        self.assertEqual(outside.read_bytes(), b"preserve this existing file")
                        self.assertFalse(output.exists(), "validation must precede creating output directories")


if __name__ == "__main__":
    unittest.main()
