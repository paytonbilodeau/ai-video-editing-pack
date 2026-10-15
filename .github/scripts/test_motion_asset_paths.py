"""Offline path-boundary tests. No provider calls or actual media rendering."""
import base64
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2] / "Payton Editing System/motion/tools"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # Only path/command functions are exercised, before CI installs Pillow.
    # No image operations are tested or claimed here.
    with patch.dict(sys.modules, {"PIL": types.SimpleNamespace(Image=None)}):
        spec.loader.exec_module(module)
    return module


hand = load("hand_drawn_path_review", ROOT / "optional/generate_hand_drawn.py")
overlay = load("overlay_path_review", ROOT / "overlay_visuals.py")


class AssetPaths(unittest.TestCase):
    def test_nested_local_assets_remain_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            asset = root / "logos" / "brand.png"
            asset.parent.mkdir()
            asset.write_bytes(b"selected reference fixture")
            for module in (hand, overlay):
                self.assertEqual(module.contained_asset_path(root, "logos/brand.png"), asset.resolve())
            references = hand.load_logo_images(["brand"], {"brand": {"files": ["logos/brand.png"]}}, root)
            self.assertEqual(base64.b64decode(references[0][3].split(",", 1)[1]), asset.read_bytes())

    def test_absolute_traversal_windows_and_control_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            for value in ["../private.png", "logos/../../private.png", "/tmp/private.png",
                          "C:\\private.png", "C:private.png", "..\\private.png",
                          "\\\\server\\private.png", "logo\x00.png", "logo\n.png", "logo\x7f.png", "logo\x85.png"]:
                for module in (hand, overlay):
                    with self.subTest(value=value, module=module.__name__):
                        with self.assertRaises(ValueError):
                            module.contained_asset_path(temp, value)

    def test_symlink_escape_is_rejected_before_reading(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            selected = root / "assets"
            selected.mkdir()
            (root / "private.png").write_bytes(b"not selected")
            (selected / "logo.png").symlink_to(root / "private.png")
            for module in (hand, overlay):
                with self.assertRaises(ValueError):
                    module.contained_asset_path(selected, "logo.png")
            with patch.object(hand.urllib.request, "urlopen") as network:
                with self.assertRaises(ValueError):
                    hand.load_logo_images(["brand"], {"brand": {"files": ["logo.png"]}}, selected)
                network.assert_not_called()

    def test_imported_visual_manifest_is_validated_before_rendering(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "visual_manifest.json").write_text(json.dumps({"moments": [
                {"status": "success", "timestamp_seconds": 0, "filename": "../private.png"}]}))
            with patch.object(overlay, "render_zoom_clip") as render:
                with self.assertRaises(ValueError):
                    overlay.load_manifest(root)
                render.assert_not_called()

    def check_private_passes(self, fail):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "output.mp4"
            sibling = root / "output_pass0.mp4"
            sibling.write_bytes(b"existing customer file")
            intermediates = []

            def fake_run(command, **kwargs):
                target = Path(command[-1])
                if target != output:
                    self.assertNotEqual(target.parent, output.parent)
                    intermediates.append(target)
                    target.write_bytes(b"mock generated pass")
                if fail:
                    return subprocess.CompletedProcess(command, 1, "", "mock failure")
                return subprocess.CompletedProcess(command, 0, "", "")

            with patch.object(overlay.subprocess, "run", side_effect=fake_run), \
                    contextlib.redirect_stdout(io.StringIO()):
                if fail:
                    with self.assertRaises(RuntimeError):
                        overlay.overlay_clips_onto_video("input.mp4", ["a.mp4", "b.mp4"],
                            [{"start": 0, "end": 1}, {"start": 1, "end": 2}], str(output), 1)
                else:
                    overlay.overlay_clips_onto_video("input.mp4", ["a.mp4", "b.mp4"],
                        [{"start": 0, "end": 1}, {"start": 1, "end": 2}], str(output), 1)
            self.assertTrue(intermediates)
            self.assertTrue(all(not p.exists() and not p.parent.exists() for p in intermediates))
            self.assertEqual(sibling.read_bytes(), b"existing customer file")

    def test_intermediate_pass_cleanup_preserves_existing_sibling(self):
        self.check_private_passes(False)

    def test_intermediate_pass_cleanup_on_failure_preserves_existing_sibling(self):
        self.check_private_passes(True)


if __name__ == "__main__":
    unittest.main()
