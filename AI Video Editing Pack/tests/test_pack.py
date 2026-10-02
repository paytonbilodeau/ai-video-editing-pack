"""Offline checks for standalone packaging and safe project setup."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import json
import os
import zipfile


TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
import build_pack  # noqa: E402
import setup_project  # noqa: E402


class PackTests(unittest.TestCase):
    def test_current_pack_and_internal_links(self):
        self.assertEqual(build_pack.validate(), [])

    def test_native_manifests_are_consistent(self):
        root_manifest = json.loads((build_pack.ROOT / "plugin.json").read_text())
        claude_manifest = json.loads((build_pack.ROOT / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(root_manifest["name"], claude_manifest["name"])
        self.assertEqual(root_manifest["version"], claude_manifest["version"])
        self.assertEqual(root_manifest["author"], claude_manifest["author"])
        self.assertTrue(root_manifest["$schema"].startswith("https://agent-plugins.org/schemas/"))

    def test_broken_link_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "pack"
            shutil.copytree(build_pack.ROOT, copied)
            (copied / "START HERE.md").write_text(
                (copied / "START HERE.md").read_text() + "\n[missing](no-such-file.md)\n"
            )
            self.assertTrue(any("broken or escaping link" in item for item in build_pack.validate(copied)))

    def test_incomplete_intake_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "pack"
            shutil.copytree(build_pack.ROOT, copied)
            intake = copied / "templates/PROJECT INTAKE.md"
            intake.write_text(intake.read_text().replace("AI app", "assistant"))
            self.assertIn("project intake lacks ai app", build_pack.validate(copied))

    def test_unlisted_private_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "pack"
            shutil.copytree(build_pack.ROOT, copied)
            (copied / ".env").write_text("placeholder=example\n")
            self.assertIn("undeclared pack file: .env", build_pack.validate(copied))

    def test_local_metadata_is_ignored_but_never_packaged(self):
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "pack"
            shutil.copytree(build_pack.ROOT, copied, ignore=shutil.ignore_patterns("__pycache__"))
            for folder in (copied, copied / "references"):
                for name in (".DS_Store", "Thumbs.db"):
                    (folder / name).write_text("metadata fixture\n")
            cache = copied / "tools/__pycache__"
            cache.mkdir()
            (cache / "fixture.pyc").write_bytes(b"bytecode fixture")
            self.assertEqual(build_pack.validate(copied), [])
            output = Path(directory) / "pack.zip"
            build_pack.build(output, copied)
            with zipfile.ZipFile(output) as archive:
                self.assertFalse(any(
                    "__pycache__" in name or name.endswith((".DS_Store", "Thumbs.db"))
                    for name in archive.namelist()
                ))

    def test_metadata_names_do_not_bypass_link_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "pack"
            shutil.copytree(build_pack.ROOT, copied, ignore=shutil.ignore_patterns("__pycache__"))
            for name in (".DS_Store", "Thumbs.db", "__pycache__"):
                linked = copied / name
                linked.symlink_to(copied / "README.md")
                self.assertIn(f"undeclared pack file: {name}", build_pack.validate(copied))
                linked.unlink()

    def test_zip_is_deterministic_and_self_contained(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.zip"
            second = Path(directory) / "second.zip"
            self.assertEqual(build_pack.build(first), build_pack.build(second))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                self.assertEqual(
                    archive.namelist(),
                    [f"AI Video Editing Pack/{name}" for name in build_pack.FILES],
                )
                self.assertIn("Free Use Terms", archive.read("AI Video Editing Pack/LICENSE AND USE.md").decode())


class SetupTests(unittest.TestCase):
    def test_first_run_with_bytecode_enabled(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            copied = base / "pack"
            shutil.copytree(build_pack.ROOT, copied, ignore=shutil.ignore_patterns("__pycache__"))
            project = base / "project"
            environment = dict(os.environ)
            environment.pop("PYTHONDONTWRITEBYTECODE", None)
            command = [sys.executable, str(copied / "tools/setup_project.py"), "--project", str(project)]
            preview = subprocess.run(command, env=environment, capture_output=True, text=True, check=True)
            self.assertTrue((copied / "tools/__pycache__").is_dir())
            self.assertIn("Preview only", preview.stdout)
            self.assertFalse(project.exists())
            applied = subprocess.run(command + ["--apply"], env=environment, capture_output=True, text=True, check=True)
            self.assertIn("Created 3 files", applied.stdout)
            self.assertEqual(len(list(project.iterdir())), 3)

    def test_cli_preview_does_not_write_and_apply_does(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            command = [sys.executable, "-B", str(TOOLS / "setup_project.py"), "--project", str(project)]
            preview = subprocess.run(command, capture_output=True, text=True, check=True)
            self.assertIn("Preview only", preview.stdout)
            self.assertFalse(project.exists())
            applied = subprocess.run(command + ["--apply"], capture_output=True, text=True, check=True)
            self.assertIn("Created 3 files", applied.stdout)
            self.assertTrue((project / "PROJECT INTAKE.md").is_file())

    def test_profile_preview_apply_and_reuse_across_projects(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project = base / "project-one"
            profile = base / "shared-profile"
            command = [
                sys.executable, "-B", str(TOOLS / "setup_project.py"),
                "--project", str(project), "--profile-dir", str(profile),
            ]
            preview = subprocess.run(command, capture_output=True, text=True, check=True)
            self.assertIn("Reusable private profile", preview.stdout)
            self.assertFalse(profile.exists())
            applied = subprocess.run(command + ["--apply"], capture_output=True, text=True, check=True)
            self.assertIn("Created 4 files", applied.stdout)
            profile_file = profile / "EDITING PROFILE.md"
            self.assertTrue(profile_file.is_file())
            repeated = subprocess.run(command + ["--apply"], capture_output=True, text=True, check=True)
            self.assertIn("Created 0 files", repeated.stdout)
            profile_file.write_text("accepted private rules\n")
            second_project = base / "project-two"
            second_command = [
                sys.executable, "-B", str(TOOLS / "setup_project.py"),
                "--project", str(second_project), "--profile-dir", str(profile), "--apply",
            ]
            second = subprocess.run(second_command, capture_output=True, text=True, check=True)
            self.assertIn("Created 3 files", second.stdout)
            self.assertIn("Existing private editing profile will be reused", second.stdout)
            self.assertTrue((second_project / "PROJECT INTAKE.md").is_file())
            self.assertEqual(profile_file.read_text(), "accepted private rules\n")

    def test_linked_profile_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            profile = base / "profile"
            profile.mkdir()
            (profile / "EDITING PROFILE.md").symlink_to(build_pack.ROOT / "templates/EDITING PROFILE.md")
            with self.assertRaisesRegex(ValueError, "refusing linked destination"):
                setup_project.plan(base / "project", profile_dir=profile)

    def test_preview_apply_and_repeat(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            skills = Path(directory) / "skills"
            copies = setup_project.plan(project, skills)
            self.assertFalse(project.exists())
            self.assertFalse(skills.exists())
            self.assertEqual(setup_project.apply(copies), len(copies))
            self.assertEqual(setup_project.plan(project, skills), copies)
            self.assertEqual(setup_project.apply(copies), 0)
            self.assertTrue((project / "PROJECT INTAKE.md").is_file())
            self.assertTrue((skills / "AI Video Editing Pack" / "SKILL.md").is_file())

    def test_edited_file_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            setup_project.apply(setup_project.plan(project))
            (project / "PROJECT INTAKE.md").write_text("my answers\n")
            with self.assertRaisesRegex(ValueError, "refusing to replace"):
                setup_project.plan(project)

    def test_project_inside_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside the source pack"):
            setup_project.plan(build_pack.ROOT / "_MY WORK")

    def test_project_ancestor_of_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside the source pack"):
            setup_project.plan(build_pack.ROOT.parent)

    def test_project_sibling_in_public_repo_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "public-repo"
            repo.mkdir()
            (repo / ".git").mkdir()
            copied = repo / "pack"
            shutil.copytree(build_pack.ROOT, copied, ignore=shutil.ignore_patterns("__pycache__"))
            with self.assertRaisesRegex(ValueError, "outside the public repository"):
                setup_project.plan(repo / "_MY WORK", root=copied)

    def test_standalone_pack_allows_a_separate_sibling_project(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            copied = base / "pack"
            shutil.copytree(build_pack.ROOT, copied, ignore=shutil.ignore_patterns("__pycache__"))
            project = base / "my-project"
            copies = setup_project.plan(project, root=copied)
            self.assertEqual(len(copies), 3)
            self.assertFalse(project.exists())

    def test_linked_destination_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            project.mkdir()
            (project / "PROJECT INTAKE.md").symlink_to(build_pack.ROOT / "templates/PROJECT INTAKE.md")
            with self.assertRaisesRegex(ValueError, "refusing linked destination"):
                setup_project.plan(project)

    def test_linked_intermediate_skills_folder_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            skills = base / "skills"
            skills.mkdir()
            (skills / "AI Video Editing Pack").symlink_to(base, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "refusing linked destination"):
                setup_project.plan(base / "project", skills)


if __name__ == "__main__":
    unittest.main()
