"""Offline request-boundary tests. Never imports or controls the Resolve app."""

import argparse
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import resolve_control as rc


class ResolveControlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.mov"
        self.source.write_bytes(b"source-preserved")
        self.output = self.root / "test.mp4"
        self.args = argparse.Namespace(input=str(self.source), output=str(self.output),
                                       project_name="Payton Smoke Test", start=1.0, duration=5.0, timeout=60)

    def test_invalid_time_values_rejected_before_any_app_access(self):
        for field, values in {"duration": [0, -1, 60.1, float("nan"), float("inf")],
                              "start": [-1, float("nan"), float("inf")],
                              "timeout": [0, 3601, float("nan")]}.items():
            original = getattr(self.args, field)
            for value in values:
                with self.subTest(field=field, value=value):
                    setattr(self.args, field, value)
                    with self.assertRaises(RuntimeError):
                        rc.validate_request(self.args)
            setattr(self.args, field, original)

    def test_existing_files_and_broken_symlinks_are_never_overwritten(self):
        for suffix in (".mp4", ".drp", ".receipt.json"):
            path = self.output.with_suffix(suffix)
            path.write_text("keep")
            with self.assertRaisesRegex(RuntimeError, "existing"):
                rc.validate_request(self.args)
            self.assertEqual(path.read_text(), "keep")
            path.unlink()
        self.output.symlink_to(self.root / "absent")
        with self.assertRaisesRegex(RuntimeError, "existing"):
            rc.validate_request(self.args)

    def test_rejects_invalid_source_output_and_project(self):
        self.args.output = str(self.source)
        with self.assertRaises(RuntimeError):
            rc.validate_request(self.args)
        self.args.output = str(self.output)
        for name in ("", "../existing", "bad\nname", "x" * 101):
            self.args.project_name = name
            with self.assertRaises(RuntimeError):
                rc.validate_request(self.args)
        self.args.project_name = "Valid"
        self.args.input = str(self.root)
        with self.assertRaises(RuntimeError):
            rc.validate_request(self.args)

    def test_frame_plan_never_exceeds_sixty_seconds_and_refuses_source_overrun(self):
        for fps in (23.976, 25.0, 29.97, 30.0, 59.94, 60.0):
            first, last, count = rc.frame_range(1, 60, fps, 10000)
            self.assertEqual(last - first + 1, count)
            self.assertLessEqual(count / fps, 60 + 1e-9)
        self.assertEqual(rc.frame_range(2, 5, 30, 210), (60, 209, 150))
        with self.assertRaisesRegex(RuntimeError, "beyond"):
            rc.frame_range(2, 5, 30, 209)
        with self.assertRaisesRegex(RuntimeError, "one source frame"):
            rc.frame_range(0, .001, 30, 100)

    def test_codec_comes_from_runtime_and_ambiguity_fails(self):
        self.assertEqual(rc.select_h264({"MP4": "mp4"}, {"H.264": "runtime_id", "H.265": "other"}),
                         "runtime_id")
        for formats, codecs in [({"MOV": "mov"}, {"H.264": "x"}),
                                ({"MP4": "mp4"}, {"H.265": "x"}),
                                ({"MP4": "mp4"}, {"H.264 A": "a", "H.264 B": "b"})]:
            with self.assertRaises(RuntimeError):
                rc.select_h264(formats, codecs)

    def test_existing_project_and_active_render_fail_before_creation(self):
        resolve = Mock()
        manager = resolve.GetProjectManager.return_value
        manager.GetProjectListInCurrentFolder.return_value = [self.args.project_name]
        with patch.object(rc.shutil, "which", return_value="/test/tool"):
            with self.assertRaisesRegex(RuntimeError, "existing project"):
                rc.smoke_test(resolve, self.args)
            manager.GetProjectListInCurrentFolder.return_value = []
            manager.GetCurrentProject.return_value.IsRenderingInProgress.return_value = True
            with self.assertRaisesRegex(RuntimeError, "rendering"):
                rc.smoke_test(resolve, self.args)
        manager.CreateProject.assert_not_called()
        self.assertFalse(self.output.with_suffix(".receipt.json").exists())

    def test_failed_creation_keeps_source_and_prior_project_untouched(self):
        resolve = Mock()
        manager = resolve.GetProjectManager.return_value
        manager.GetProjectListInCurrentFolder.return_value = []
        previous = manager.GetCurrentProject.return_value
        previous.IsRenderingInProgress.return_value = False
        previous.GetName.return_value = "Work"
        previous.GetUniqueId.return_value = "work-id"
        resolve.GetVersionString.return_value = "21.1"
        manager.CreateProject.return_value = None
        with patch.object(rc.shutil, "which", return_value="/test/tool"):
            with self.assertRaisesRegex(RuntimeError, "refused the new"):
                rc.smoke_test(resolve, self.args)
        manager.SaveProject.assert_not_called()
        manager.LoadProject.assert_not_called()
        self.assertEqual(self.source.read_bytes(), b"source-preserved")
        receipt = json.loads(self.output.with_suffix(".receipt.json").read_text())
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(receipt["source_sha256_before"], receipt["source_sha256_after"])

    def test_faststart_checks_real_atom_order_and_malformed_lengths(self):
        atom = lambda kind: struct.pack(">I4s", 8, kind)
        for content, expected in [(atom(b"ftyp") + atom(b"moov") + atom(b"mdat"), True),
                                  (atom(b"ftyp") + atom(b"mdat") + atom(b"moov"), False),
                                  (struct.pack(">I4s", 4, b"moov"), False),
                                  (struct.pack(">I4s", 1000, b"moov"), False),
                                  (struct.pack(">I4s", 1, b"moov"), False)]:
            self.output.write_bytes(content)
            self.assertEqual(rc.faststart(self.output), expected)

    def test_export_failure_still_restores_prior_project_without_deleting(self):
        resolve = Mock()
        manager = resolve.GetProjectManager.return_value
        previous, project = Mock(), Mock()
        previous.GetName.return_value = "Prior"
        previous.GetUniqueId.return_value = "prior-id"
        previous.IsRenderingInProgress.return_value = False
        project.GetName.return_value = self.args.project_name
        project.GetUniqueId.return_value = "scratch-id"
        project.GetRenderJobList.return_value = []
        project.IsRenderingInProgress.return_value = False
        project.GetMediaPool.return_value.ImportMedia.return_value = []
        manager.GetProjectListInCurrentFolder.return_value = []
        manager.GetCurrentProject.side_effect = [previous, project]
        manager.CreateProject.return_value = project
        manager.ExportProject.return_value = False
        manager.LoadProject.return_value = previous
        resolve.GetVersionString.return_value = "21.1"
        resolve.GetCurrentPage.side_effect = ["edit", "edit"]
        resolve.OpenPage.return_value = True
        with patch.object(rc.shutil, "which", return_value="/test/tool"):
            with self.assertRaisesRegex(RuntimeError, "export"):
                rc.smoke_test(resolve, self.args)
        manager.LoadProject.assert_called_once_with("Prior")
        manager.DeleteProject.assert_not_called()
        project.DeleteAllRenderJobs.assert_not_called()
        project.StartRendering.assert_not_called()
        receipt = json.loads(self.output.with_suffix(".receipt.json").read_text())
        self.assertTrue(receipt["previous_project_restored"])
        self.assertTrue(receipt["previous_page_restored"])
        resolve.OpenPage.assert_called_once_with("edit")


    def test_page_restoration_verifies_readback(self):
        resolve=Mock();resolve.OpenPage.return_value=True;resolve.GetCurrentPage.return_value="edit"
        receipt={};rc.restore_previous_page(resolve,"edit",receipt)
        self.assertEqual(receipt,{"previous_page_restored":True,"page_after_restore":"edit"})
        resolve.OpenPage.assert_called_once_with("edit")

    def test_page_restore_false_success_is_rejected(self):
        resolve=Mock();resolve.OpenPage.return_value=True;resolve.GetCurrentPage.return_value="deliver"
        receipt={}
        with self.assertRaisesRegex(RuntimeError,"differs"):rc.restore_previous_page(resolve,"edit",receipt)
        self.assertFalse(receipt["previous_page_restored"])

    def test_absent_prior_page_is_not_invented(self):
        resolve=Mock();receipt={};rc.restore_previous_page(resolve,None,receipt)
        resolve.OpenPage.assert_not_called();self.assertIsNone(receipt["previous_page_restored"])


if __name__ == "__main__":
    unittest.main()
