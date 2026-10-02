import importlib.util
import unittest
from pathlib import Path
from unittest import mock


SYSTEM_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "video_setup_doctor", SYSTEM_ROOT / "tools" / "setup_doctor.py"
)
setup_doctor = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(setup_doctor)


class SetupDoctorTests(unittest.TestCase):
    def test_check_is_read_only_and_reports_tool_presence(self) -> None:
        with mock.patch.object(setup_doctor.shutil, "which") as which:
            which.side_effect = lambda name: f"bin/{name}"
            payload = setup_doctor.check()
        self.assertTrue(payload["readOnly"])
        self.assertTrue(payload["tools"]["ffmpeg"])
        self.assertTrue(payload["tools"]["ffprobe"])
        self.assertNotIn("path", payload["tools"])


if __name__ == "__main__":
    unittest.main()
