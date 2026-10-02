#!/usr/bin/env python3
"""Unit tests for the public Video Pre-Edit tool."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


SYSTEM_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = SYSTEM_ROOT / "tools" / "video_pre_edit.py"
FIXTURE_PATH = SYSTEM_ROOT / "tests" / "make_fixture.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


video_pre_edit = load_module("video_pre_edit", TOOL_PATH)
fixture_builder = load_module("make_fixture", FIXTURE_PATH)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class RenderSafetyTests(unittest.TestCase):
    def test_render_preserves_existing_filter_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "source.mp4"
            output = base / "output.mp4"
            sidecar = base / "output.filters.txt"
            sidecar.write_text("existing user file\n", encoding="utf-8")
            with mock.patch.object(video_pre_edit, "run_command"):
                video_pre_edit.render_cut_video(source, output, [(0.0, 1.0)])
            self.assertEqual(sidecar.read_text(encoding="utf-8"), "existing user file\n")


class ParsingTests(unittest.TestCase):
    def test_timestamps_accept_seconds_minutes_and_hours(self) -> None:
        self.assertEqual(video_pre_edit.parse_timestamp("5.5"), 5.5)
        self.assertEqual(video_pre_edit.parse_timestamp("1:05"), 65.0)
        self.assertEqual(video_pre_edit.parse_timestamp("1:02:03"), 3723.0)

    def test_invalid_timestamp_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            video_pre_edit.parse_timestamp("1:65")
        with self.assertRaises(ValueError):
            video_pre_edit.parse_time_range("5-4")

    def test_protected_range_splits_a_cut(self) -> None:
        cuts = [video_pre_edit.EditRange(1.0, 5.0, ("silence",))]
        result = video_pre_edit.normalize_cuts(
            cuts,
            10.0,
            protected=[(2.0, 3.0)],
        )
        self.assertEqual(
            [(item.start, item.end) for item in result],
            [(1.0, 2.0), (3.0, 5.0)],
        )

    def test_silence_padding_keeps_audio_on_each_side(self) -> None:
        result = video_pre_edit.silence_ranges_to_cuts(
            [(2.0, 4.0)],
            duration=10.0,
            padding_seconds=0.15,
        )
        self.assertAlmostEqual(result[0].start, 2.15)
        self.assertAlmostEqual(result[0].end, 3.85)


class MarkerTests(unittest.TestCase):
    @staticmethod
    def words(*items: tuple[str, float, float]):
        return [
            {"word": word, "start": start, "end": end}
            for word, start, end in items
        ]

    def test_exact_restart_marker_is_found(self) -> None:
        words = self.words(
            ("mistake", 1.0, 1.4),
            ("cut", 1.8, 2.0),
            ("cut", 2.05, 2.25),
            ("corrected", 2.5, 2.9),
        )
        self.assertEqual(
            video_pre_edit.find_exact_marker_spans(words, "cut cut"),
            [(1.8, 2.25)],
        )

    def test_non_exact_or_loose_phrase_is_not_a_marker(self) -> None:
        words = self.words(
            ("cutting", 1.0, 1.2),
            ("cut", 1.3, 1.5),
            ("cut", 3.0, 3.2),
        )
        self.assertEqual(
            video_pre_edit.find_exact_marker_spans(words, "cut cut"),
            [],
        )

    def test_restart_cut_keeps_the_corrected_take(self) -> None:
        cuts = video_pre_edit.restart_marker_cuts(
            [(0.0, 4.0), (5.6, 12.0)],
            [(8.0, 8.4)],
        )
        self.assertEqual(len(cuts), 1)
        self.assertAlmostEqual(cuts[0].start, 5.6)
        self.assertAlmostEqual(cuts[0].end, 8.4)
        kept = video_pre_edit.invert_cuts(cuts, 12.0)
        self.assertIn((8.4, 12.0), kept)

    def test_restart_cut_never_crosses_an_existing_cut_gap(self) -> None:
        cuts = video_pre_edit.restart_marker_cuts(
            [(0.0, 4.4), (5.6, 12.0)],
            [(8.0, 8.4)],
        )
        self.assertEqual(
            [(item.start, item.end) for item in cuts],
            [(5.6, 8.4)],
        )

    def test_corrupt_repeated_transcript_disables_markers(self) -> None:
        words = [
            {"word": "loop", "start": index * 0.1, "end": index * 0.1 + 0.05}
            for index in range(60)
        ]
        self.assertIsNotNone(video_pre_edit.transcript_problem(words))

    def test_local_whisper_boundary_artifact_is_ignored(self) -> None:
        class FakeModel:
            def transcribe(self, *_args, **_kwargs):
                return {
                    "segments": [
                        {
                            "words": [
                                {"word": "cut", "start": 1.0, "end": 1.2},
                                {"word": " ", "start": 1.2, "end": 1.2},
                            ]
                        }
                    ]
                }

        fake_whisper = types.SimpleNamespace(
            load_model=lambda _name: FakeModel(),
        )
        with mock.patch.dict(sys.modules, {"whisper": fake_whisper}):
            words = video_pre_edit.transcribe_with_local_whisper(
                Path("unused.mp4"),
                "base",
                "en",
                "cut cut",
                "full stop restart",
            )
        self.assertEqual(
            words,
            [{"word": "cut", "start": 1.0, "end": 1.2}],
        )


class SafetyTests(unittest.TestCase):
    def test_report_neutralizes_untrusted_markdown_values(self) -> None:
        report = video_pre_edit.report_markdown(
            source_name="raw`clip\n## injected heading.mp4",
            output_name="out|clip.mp4",
            rendered=False,
            source_duration=10.0,
            expected_duration=9.0,
            cuts=[
                video_pre_edit.EditRange(
                    1.0,
                    2.0,
                    ("user | reason\n|---| [link](https://example.invalid)",),
                )
            ],
            protected=[],
            settings={"language": "en\n# injected setting"},
            marker_summary={
                "restart phrase": "[click](https://example.invalid)\n# injected marker"
            },
            audio_summary={"method": "none"},
            verification=None,
            warnings=["review this\n## injected warning"],
            plan_name="out`plan.json",
        )
        self.assertNotIn("\n## injected heading", report)
        self.assertNotIn("\n## injected warning", report)
        self.assertNotIn("\n# injected marker", report)
        self.assertIn("raw`clip ## injected heading.mp4", report)
        self.assertIn("&#124;", report)
        self.assertNotIn("[link](https://example.invalid)", report)

    def test_source_and_output_cannot_be_the_same_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.mp4"
            path.write_bytes(b"source")
            with self.assertRaises(video_pre_edit.PreEditError):
                video_pre_edit.install_output_safely(
                    path,
                    path,
                    path,
                    overwrite=True,
                )

    def test_existing_output_is_not_replaced_without_permission(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.mp4"
            temporary = root / "temporary.mp4"
            output = root / "output.mp4"
            source.write_bytes(b"source")
            temporary.write_bytes(b"new")
            output.write_bytes(b"existing")
            with self.assertRaises(video_pre_edit.PreEditError):
                video_pre_edit.install_output_safely(
                    temporary,
                    output,
                    source,
                    overwrite=False,
                )
            self.assertEqual(output.read_bytes(), b"existing")

    def test_multistream_and_hdr_inputs_are_rejected(self) -> None:
        multistream = video_pre_edit.MediaInfo(
            duration=5.0,
            has_video=True,
            has_audio=True,
            video_streams=1,
            audio_streams=2,
            video_pixel_format="yuv420p",
            video_transfer="bt709",
        )
        hdr = video_pre_edit.MediaInfo(
            duration=5.0,
            has_video=True,
            has_audio=True,
            video_streams=1,
            audio_streams=1,
            video_pixel_format="yuv420p10le",
            video_transfer="smpte2084",
        )
        with self.assertRaises(video_pre_edit.PreEditError):
            video_pre_edit.reject_unsafe_source_layout(multistream)
        with self.assertRaises(video_pre_edit.PreEditError):
            video_pre_edit.reject_unsafe_source_layout(hdr)

    def test_subtitle_and_chapter_layouts_are_rejected(self) -> None:
        subtitle_source = video_pre_edit.MediaInfo(
            duration=5.0,
            has_video=True,
            has_audio=True,
            video_streams=1,
            audio_streams=1,
            video_pixel_format="yuv420p",
            video_transfer="bt709",
            subtitle_streams=1,
        )
        chapter_source = video_pre_edit.MediaInfo(
            duration=5.0,
            has_video=True,
            has_audio=True,
            video_streams=1,
            audio_streams=1,
            video_pixel_format="yuv420p",
            video_transfer="bt709",
            chapter_count=1,
        )
        with self.assertRaises(video_pre_edit.PreEditError):
            video_pre_edit.reject_unsafe_source_layout(subtitle_source)
        with self.assertRaises(video_pre_edit.PreEditError):
            video_pre_edit.reject_unsafe_source_layout(chapter_source)

    def test_from_plan_rejects_retyped_edit_flags(self) -> None:
        stderr = io.StringIO()
        with mock.patch("sys.stderr", stderr):
            exit_code = video_pre_edit.main(
                [
                    "source.mp4",
                    "output.mp4",
                    "--from-plan",
                    "approved.json",
                    "--cut",
                    "0-1",
                ]
            )
        self.assertEqual(exit_code, 2)
        self.assertIn("--from-plan already supplies", stderr.getvalue())

    def test_optional_marker_requirements_use_exact_top_level_pins(self) -> None:
        requirements = (
            SYSTEM_ROOT / "requirements-markers.txt"
        ).read_text(encoding="utf-8")
        packages = [
            line
            for line in requirements.splitlines()
            if line and not line.startswith("#")
        ]
        self.assertEqual(
            packages,
            ["openai-whisper==20240930", "torch==2.2.2"],
        )


@unittest.skipUnless(
    shutil.which("ffmpeg") and shutil.which("ffprobe"),
    "FFmpeg and ffprobe are not installed",
)
class LocalFfmpegIntegrationTests(unittest.TestCase):
    def test_synthetic_render_is_verified_and_source_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = fixture_builder.build_fixture(root / "source.mp4")
            original_hash = file_hash(source)
            output = root / "output.mp4"
            report = root / "report.md"
            exit_code = video_pre_edit.main(
                [
                    str(source),
                    str(output),
                    "--report",
                    str(report),
                    "--min-silence",
                    "0.8",
                    "--padding-ms",
                    "150",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(file_hash(source), original_hash)
            self.assertTrue(output.exists())
            self.assertTrue(report.exists())
            output_info = video_pre_edit.probe_media(output)
            self.assertTrue(output_info.has_video)
            self.assertTrue(output_info.has_audio)
            self.assertGreater(output_info.duration, 3.0)
            self.assertLess(output_info.duration, 4.2)
            report_text = report.read_text(encoding="utf-8")
            self.assertIn(
                "rendered; video stream, audio stream, and duration verified",
                report_text,
            )
            self.assertNotIn(str(root), report_text)

    def test_dry_run_plan_carries_exact_options_into_render(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = fixture_builder.build_fixture(root / "source.mp4")
            original_hash = file_hash(source)
            output = root / "approved-output.mp4"
            dry_report = root / "approved-output_dry_run_report.md"
            final_report = root / "approved-output_report.md"
            plan = root / "approved-output_plan.json"

            dry_exit = video_pre_edit.main(
                [
                    str(source),
                    str(output),
                    "--dry-run",
                    "--keep-silence",
                    "--cut",
                    "0.5-1.0",
                    "--protect",
                    "2.0-2.5",
                ]
            )
            self.assertEqual(dry_exit, 0)
            self.assertFalse(output.exists())
            self.assertTrue(dry_report.exists())
            self.assertTrue(plan.exists())
            plan_data = json.loads(plan.read_text(encoding="utf-8"))
            self.assertTrue(plan_data["options"]["keep_silence"])
            self.assertEqual(plan_data["options"]["cut"], ["0.5-1.0"])
            self.assertEqual(plan_data["options"]["protect"], ["2.0-2.5"])

            render_exit = video_pre_edit.main(
                [
                    str(source),
                    str(output),
                    "--from-plan",
                    str(plan),
                ]
            )
            self.assertEqual(render_exit, 0)
            self.assertEqual(file_hash(source), original_hash)
            self.assertTrue(output.exists())
            self.assertTrue(dry_report.exists())
            self.assertTrue(final_report.exists())
            output_info = video_pre_edit.probe_media(output)
            self.assertAlmostEqual(output_info.duration, 5.5, delta=0.25)
            report_text = final_report.read_text(encoding="utf-8")
            self.assertIn("- silence cuts enabled: `False`", report_text)
            self.assertIn("- user-approved exact ranges: `1`", report_text)
            self.assertIn(
                "- Approved plan file: `approved-output_plan.json`",
                report_text,
            )
            self.assertIn(
                "Container and stream metadata are not preserved",
                report_text,
            )

    def test_synthetic_subtitle_and_chapter_source_is_detected_and_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = fixture_builder.build_fixture(root / "source.mp4")
            subtitles = root / "captions.srt"
            chapters = root / "chapters.ffmeta"
            composite = root / "subtitle-and-chapter.mp4"
            subtitles.write_text(
                "1\n00:00:00,000 --> 00:00:01,000\nSynthetic caption\n",
                encoding="utf-8",
            )
            chapters.write_text(
                ";FFMETADATA1\n"
                "[CHAPTER]\n"
                "TIMEBASE=1/1000\n"
                "START=0\n"
                "END=1000\n"
                "title=Synthetic chapter\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    "ffmpeg",
                    "-n",
                    "-hide_banner",
                    "-nostats",
                    "-i",
                    str(source),
                    "-f",
                    "srt",
                    "-i",
                    str(subtitles),
                    "-i",
                    str(chapters),
                    "-map",
                    "0:v:0",
                    "-map",
                    "0:a:0",
                    "-map",
                    "1:s:0",
                    "-map_chapters",
                    "2",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "copy",
                    "-c:s",
                    "mov_text",
                    str(composite),
                ],
                capture_output=True,
                text=True,
                shell=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            info = video_pre_edit.probe_media(composite)
            self.assertEqual(info.subtitle_streams, 1)
            self.assertEqual(info.chapter_count, 1)
            with self.assertRaises(video_pre_edit.PreEditError):
                video_pre_edit.reject_unsafe_source_layout(info)


if __name__ == "__main__":
    unittest.main()
