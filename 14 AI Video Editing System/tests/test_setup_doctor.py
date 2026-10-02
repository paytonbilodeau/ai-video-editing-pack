import importlib.util
import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("editing_setup_doctor", Path(__file__).parents[1] / "tools/setup_doctor.py")
doctor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(doctor)


def available(name, flag):
    return {"present": True, "version": "22.4.0" if name == "node" else "7.1", "versionCheck": "passed"}


class SetupDoctorTests(unittest.TestCase):
    def test_ready_does_not_mean_connected(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(doctor, "tool_version", side_effect=available):
            root = Path(tmp)
            marker = root / "keep.txt"
            marker.write_text("keep unchanged")
            before = list(root.iterdir())
            report = doctor.check(root, motion=True, resolve_mcp=marker)
            self.assertTrue(report["localPrerequisitesReady"])
            self.assertTrue(report["resolve"]["mcpBinaryPresent"])
            self.assertIsNone(report["resolve"]["connected"])
            self.assertFalse(report["resolve"]["editionAndLicenseVerified"])
            self.assertEqual(marker.read_text(), "keep unchanged")
            self.assertEqual(list(root.iterdir()), before)
            self.assertNotIn(tmp, str(report))

    def test_missing_tools_are_actionable(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(doctor.shutil, "which", return_value=None):
            report = doctor.check(Path(tmp), motion=True)
            self.assertFalse(report["localPrerequisitesReady"])
            self.assertTrue(any("ffprobe" in s for s in report["nextSteps"]))
            self.assertTrue(any("Node.js" in s for s in report["nextSteps"]))

    def test_old_node_blocks_only_motion(self):
        def versions(name, flag):
            value = available(name, flag)
            if name == "node": value["version"] = "20.11.0"
            return value
        with tempfile.TemporaryDirectory() as tmp, patch.object(doctor, "tool_version", side_effect=versions):
            self.assertTrue(doctor.check(Path(tmp))["localPrerequisitesReady"])
            self.assertFalse(doctor.check(Path(tmp), motion=True)["localPrerequisitesReady"])

    def test_invalid_workspace(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(doctor, "tool_version", side_effect=available):
            self.assertFalse(doctor.check(Path(tmp) / "missing")["localPrerequisitesReady"])

    def test_not_writable(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(doctor, "tool_version", side_effect=available), patch.object(doctor.os, "access", return_value=False):
            self.assertFalse(doctor.check(Path(tmp))["localPrerequisitesReady"])

    def test_version_timeout_is_not_presence_success(self):
        with patch.object(doctor.shutil, "which", return_value="ffmpeg"), patch.object(doctor.subprocess, "run", side_effect=subprocess.TimeoutExpired("ffmpeg", 10)):
            result = doctor.tool_version("ffmpeg", "-version")
            self.assertTrue(result["present"])
            self.assertEqual(result["versionCheck"], "failed")

    def test_unexpected_version_output_not_exposed(self):
        completed = subprocess.CompletedProcess([], 0, "unexpected local diagnostics", "")
        with patch.object(doctor.shutil, "which", return_value="node"), patch.object(doctor.subprocess, "run", return_value=completed) as run:
            result = doctor.tool_version("node", "--version")
            self.assertIsNone(result["version"])
            self.assertNotIn("diagnostics", str(result))
            self.assertFalse(run.call_args.kwargs["shell"])

    def test_node_version_parsed(self):
        completed = subprocess.CompletedProcess([], 0, "v22.18.0\n", "")
        with patch.object(doctor.shutil, "which", return_value="node"), patch.object(doctor.subprocess, "run", return_value=completed):
            self.assertEqual(doctor.tool_version("node", "--version")["version"], "22.18.0")

    def test_nonzero_version_call_fails(self):
        completed = subprocess.CompletedProcess([], 1, "ffprobe version 7.1", "")
        with patch.object(doctor.shutil, "which", return_value="ffprobe"), patch.object(doctor.subprocess, "run", return_value=completed):
            self.assertEqual(doctor.tool_version("ffprobe", "-version")["versionCheck"], "failed")

    def test_linux_custom_path_not_guessed(self):
        self.assertIsNone(doctor.standard_mcp_path("Linux"))

    def test_cli_failure_exit(self):
        with patch.object(doctor, "check", return_value={"localPrerequisitesReady": False}), redirect_stdout(io.StringIO()):
            self.assertEqual(doctor.main(["--workspace", "missing"]), 1)


if __name__ == "__main__":
    unittest.main()
