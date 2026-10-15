import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "video_render_check.py"
SPEC = importlib.util.spec_from_file_location("video_render_check", MODULE_PATH)
render_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render_check)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg tools required")
class RenderCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.silent = cls.root / "silent.mp4"
        cls.audio = cls.root / "audio.mp4"
        cls.counted = cls.root / "counted.mkv"
        cls.rational = cls.root / "rational.mp4"
        for path, rate, sound in [(cls.silent, "10", False), (cls.audio, "10", True),
                                  (cls.counted, "10", False), (cls.rational, "30000/1001", False)]:
            command = ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", f"color=red:s=16x12:r={rate}"]
            if sound:
                command += ["-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=0.5", "-c:a", "aac"]
            else:
                command += ["-an"]
            command += ["-frames:v", "5", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)]
            subprocess.run(command, check=True, capture_output=True)
        cls.approved_audio = cls.root / "approved-audio.mp4"
        cls.remuxed_audio = cls.root / "remuxed-audio.mp4"
        cls.truncated_audio = cls.root / "truncated-audio.mp4"
        short_audio = cls.root / "short-audio.m4a"
        # Mux complete audio after the picture encode, with no video frame limit.
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(cls.silent),
                        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=0.5",
                        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
                        str(cls.approved_audio)], check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(cls.approved_audio),
                        "-c", "copy", str(cls.remuxed_audio)], check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(cls.approved_audio),
                        "-map", "0:a:0", "-t", "0.2", "-c", "copy", str(short_audio)],
                       check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(cls.silent), "-i", str(short_audio),
                        "-map", "0:v:0", "-map", "1:a:0", "-c", "copy", str(cls.truncated_audio)],
                       check=True, capture_output=True)
        cls.alpha = cls.root / "alpha.mov"
        cls.opaque = cls.root / "opaque.mov"
        cls.invisible = cls.root / "invisible.mov"
        for path, pattern in [(cls.alpha, "mixed"), (cls.opaque, "opaque"), (cls.invisible, "invisible")]:
            pixels = bytearray()
            for y in range(12):
                for x in range(16):
                    alpha = 255 if pattern == "opaque" or (pattern == "mixed" and x >= 8) else 0
                    pixels.extend((200, 80, 30, alpha))
            subprocess.run(["ffmpeg", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                            "-s", "16x12", "-r", "10", "-i", "-", "-frames:v", "5",
                            "-an", "-c:v", "qtrle", str(path)], input=bytes(pixels) * 5,
                           check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def check(self, path=None, **overrides):
        options = {"width": 16, "height": 12, "fps": "10/1", "frames": 5, "audio": "none"}
        options.update(overrides)
        return render_check.check_render(path or self.silent, **options)

    def test_valid_silent_render_and_source_receipt(self):
        result = self.check()
        self.assertTrue(result["ok"], result["errors"])
        self.assertTrue(result["checks"]["full_decode"])
        self.assertEqual(len(result["source"]["sha256"]), 64)
        self.assertEqual(result["actual"]["video_duration_seconds"], 0.5)

    def test_missing_and_empty_and_corrupt_files(self):
        empty = self.root / "empty.mp4"
        empty.write_bytes(b"")
        corrupt = self.root / "corrupt.mp4"
        corrupt.write_bytes(b"not a video")
        for path in [self.root / "missing.mp4", empty, corrupt]:
            with self.subTest(path=path):
                result = self.check(path)
                self.assertFalse(result["ok"])
                self.assertFalse(result["checks"]["full_decode"])

    def test_wrong_frames_canvas_fps_and_audio_fail(self):
        for options, check in [({"frames": 6}, "frames"), ({"width": 18}, "canvas"),
                               ({"fps": "11"}, "fps"), ({"audio": "present"}, "audio")]:
            with self.subTest(options=options):
                result = self.check(**options)
                self.assertFalse(result["ok"])
                self.assertFalse(result["checks"][check])
                self.assertTrue(result["checks"]["full_decode"])
        self.assertFalse(self.check(self.audio)["ok"])
        self.assertTrue(self.check(self.audio, audio="present")["ok"])

    def test_corrupt_packet_fails_full_decode_even_with_valid_metadata(self):
        packets = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_packets",
            "-show_entries", "packet=pos,size", "-of", "json", str(self.alpha)]))
        packet = packets["packets"][0]
        broken = bytearray(self.alpha.read_bytes())
        position, size = int(packet["pos"]), int(packet["size"])
        broken[position:position + size] = b"\xff" * size
        path = self.root / "broken-packet.mov"
        path.write_bytes(broken)
        result = self.check(path)
        self.assertEqual(result["actual"]["frames"], 5)
        self.assertTrue(result["checks"]["canvas"])
        self.assertFalse(result["checks"]["full_decode"])
        self.assertFalse(result["ok"])

    def test_rational_fps_and_actual_frame_count_fallback(self):
        result = self.check(self.rational, fps="30000/1001")
        self.assertTrue(result["ok"], result["errors"])
        counted = self.check(self.counted)
        self.assertTrue(counted["ok"], counted["errors"])
        self.assertEqual(counted["actual"]["frame_count_basis"], "ffprobe -count_frames:nb_read_frames")

    def test_preserved_audio_survives_remux_and_detects_truncation(self):
        preserved = self.check(self.remuxed_audio, audio="present", audio_reference=self.approved_audio)
        self.assertTrue(preserved["ok"], preserved["errors"])
        self.assertTrue(preserved["checks"]["audio_payload_unchanged"])
        # Presence, frame count and full decode cannot detect this short tail.
        self.assertTrue(self.check(self.truncated_audio, audio="present")["ok"])
        truncated = self.check(self.truncated_audio, audio="present", audio_reference=self.approved_audio)
        self.assertFalse(truncated["ok"])
        self.assertFalse(truncated["checks"]["audio_payload_unchanged"])
        self.assertTrue(truncated["checks"]["full_decode"])

    def test_audio_reference_configuration_and_source_protection(self):
        with self.assertRaises(ValueError):
            self.check(audio_reference=self.approved_audio)
        for reference in [self.silent, self.root / "missing-reference.mp4"]:
            self.assertFalse(self.check(self.approved_audio, audio="present", audio_reference=reference)["ok"])
        before = self.approved_audio.read_bytes()
        result = subprocess.run([sys.executable, str(MODULE_PATH), str(self.remuxed_audio),
                                 "--width", "16", "--height", "12", "--fps", "10", "--frames", "5",
                                 "--audio", "present", "--audio-reference", str(self.approved_audio),
                                 "--report", str(self.approved_audio)], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.approved_audio.read_bytes(), before)

    def test_audio_reference_rejects_the_render_and_its_aliases(self):
        hardlink = self.root / "audio-reference-hardlink.mp4"
        hardlink.hardlink_to(self.approved_audio)
        symlink = self.root / "audio-reference-symlink.mp4"
        symlink.symlink_to(self.approved_audio)
        before = self.approved_audio.read_bytes()
        for reference in (self.approved_audio, hardlink, symlink):
            with self.subTest(reference=reference):
                result = self.check(self.approved_audio, audio="present", audio_reference=reference)
                self.assertFalse(result["ok"])
                self.assertTrue(any("different file" in error for error in result["errors"]))
                self.assertNotIn("audio_payload_unchanged", result["checks"])
        self.assertEqual(self.approved_audio.read_bytes(), before)

    def test_report_rejects_hardlinks_to_media_and_audio_reference(self):
        before = {path: path.read_bytes() for path in (self.remuxed_audio, self.approved_audio)}
        base = [sys.executable, str(MODULE_PATH), str(self.remuxed_audio),
                "--width", "16", "--height", "12", "--fps", "10", "--frames", "5",
                "--audio", "present", "--audio-reference", str(self.approved_audio)]
        for index, source in enumerate(before):
            report = self.root / f"protected-report-hardlink-{index}.json"
            report.hardlink_to(source)
            with self.subTest(source=source):
                result = subprocess.run(base + ["--report", str(report)], capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertIn(b"Report must not overwrite", result.stderr)
                for path, content in before.items():
                    self.assertEqual(path.read_bytes(), content)

    def test_alpha_samples_show_both_transparency_and_ink(self):
        result = self.check(self.alpha, expect_alpha=True, alpha_times=[0, "0.3"])
        self.assertTrue(result["ok"], result["errors"])
        self.assertTrue(result["alpha"]["pixel_format_has_alpha"])
        self.assertEqual([s["frame_index"] for s in result["alpha"]["samples"]], [0, 3])
        for sample in result["alpha"]["samples"]:
            self.assertEqual((sample["alpha_min_uint8"], sample["alpha_max_uint8"]), (0, 255))

    def test_opaque_invisible_and_missing_alpha_fail(self):
        for path in [self.opaque, self.invisible, self.silent]:
            with self.subTest(path=path):
                self.assertFalse(self.check(path, expect_alpha=True, alpha_times=[0])["ok"])
        outside = self.check(self.alpha, expect_alpha=True, alpha_times=[0, 0.5])
        self.assertFalse(outside["ok"])

    def test_alpha_requires_explicit_samples_and_valid_configuration(self):
        for options in [{"expect_alpha": True}, {"alpha_times": [0]}, {"fps": "0/1"},
                        {"frames": 0}, {"width": -1}, {"expect_alpha": True, "alpha_times": [-1]}]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.check(**options)

    def test_cli_report_exit_status_and_source_protection(self):
        report = self.root / "receipt.json"
        base = [sys.executable, str(MODULE_PATH), str(self.silent), "--width", "16",
                "--height", "12", "--fps", "10", "--frames", "5", "--audio", "none"]
        success = subprocess.run(base + ["--report", str(report)], capture_output=True)
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertTrue(json.loads(report.read_text())["ok"])
        failed = subprocess.run(base + ["--frames", "6", "--report", str(report)], capture_output=True)
        self.assertEqual(failed.returncode, 1)
        self.assertFalse(json.loads(report.read_text())["ok"])
        source_size = self.silent.stat().st_size
        protected = subprocess.run(base + ["--report", str(self.silent)], capture_output=True)
        self.assertEqual(protected.returncode, 2)
        self.assertEqual(self.silent.stat().st_size, source_size)


if __name__ == "__main__":
    unittest.main()
