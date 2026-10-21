"""Tests for fetch_release.py. No network: links are local paths, file URLs or mocked responses."""
import hashlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1] / "fetch_release.py"
spec = importlib.util.spec_from_file_location("fetch_release", TOOL)
fr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fr)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def make_folder(root, version, extra=None):
    """A minimal Vibe Edit folder with a correct bundle-manifest.json."""
    root = Path(root)
    plugin = root / "plugins/vibe-edit"
    files = {
        "VERSION": f"{version}\n",
        "plugin.json": json.dumps({"name": "vibe-edit", "version": version}),
        "skills/update/SKILL.md": f"# Update {version}\n",
        "skills/remotion/flow/package.json": '{"name": "flow", "dependencies": {"remotion": "4"}}',
    }
    manifest = {}
    for rel, text in files.items():
        p = plugin / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        manifest[rel] = sha(text.encode())
    (plugin / "bundle-manifest.json").write_text(json.dumps({"name": "vibe-edit", "version": version, "files": manifest}))
    for rel, text in {".claude-plugin/marketplace.json": '{"name": "vibe-editors-early"}',
                      ".agents/plugins/marketplace.json": '{"name": "vibe-editors-early"}',
                      "README.md": "# Vibe Edit\n"}.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    for rel, text in (extra or {}).items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return root


def make_zip(folder, zip_path, arc_prefix="Vibe Edit"):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(Path(folder).rglob("*")):
            if p.is_file():
                zf.write(p, arc_prefix + "/" + p.relative_to(folder).as_posix())
    return sha(Path(zip_path).read_bytes())


class FetchReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.t = Path(self.tmp.name)
        self.release_src = make_folder(self.t / "src-6.1.0", "6.1.0")
        self.zip = self.t / "vibe-edit-6.1.0-early.zip"
        self.hash = make_zip(self.release_src, self.zip)

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with patch("sys.stdout", out), patch("sys.stderr", err):
            code = fr.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_path_with_correct_hash_installs_into_dest(self):
        dest = self.t / "member"
        code, out, err = self.run_main("--url", str(self.zip), "--sha256", self.hash, "--dest", str(dest))
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["new_version"], "6.1.0")
        self.assertEqual((dest / "Vibe Edit/plugins/vibe-edit/VERSION").read_text().strip(), "6.1.0")
        self.assertEqual(sorted(p.name for p in dest.iterdir()), ["Vibe Edit"])  # work folder cleaned

    def test_wrong_hash_is_refused_and_nothing_is_written(self):
        dest = self.t / "member"
        wrong = "0" * 64
        code, out, err = self.run_main("--url", str(self.zip), "--sha256", wrong, "--dest", str(dest))
        self.assertEqual(code, 2)
        self.assertIn("Refused", err)
        self.assertIn(self.hash, err)
        self.assertIn(wrong, err)
        self.assertEqual(list(dest.iterdir()), [])

    def test_file_url_and_uppercase_hash_work(self):
        dest = self.t / "member"
        code, out, err = self.run_main("--url", self.zip.as_uri(), "--sha256", self.hash.upper(), "--dest", str(dest))
        self.assertEqual(code, 0, err)
        self.assertTrue((dest / "Vibe Edit/plugins/vibe-edit/VERSION").exists())

    def test_replace_swaps_in_place_keeps_previous_and_carries_node_modules(self):
        existing = make_folder(self.t / "member/Vibe Edit", "6.0.0")
        modules = existing / "plugins/vibe-edit/skills/remotion/flow/node_modules/remotion"
        modules.mkdir(parents=True)
        (modules / "index.js").write_text("module")
        # Files of the person's outside the plugin folder are untouched by the swap.
        profile = self.t / "member/workspace/Vibe Edit Settings/EDITING PROFILE.md"
        profile.parent.mkdir(parents=True)
        profile.write_text("# mine\n")
        code, out, err = self.run_main("--url", str(self.zip), "--sha256", self.hash, "--replace", str(existing))
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["old_version"], "6.0.0")
        self.assertEqual(result["new_version"], "6.1.0")
        self.assertEqual((existing / "plugins/vibe-edit/VERSION").read_text().strip(), "6.1.0")
        previous = Path(result["previous"])
        self.assertEqual(previous.name, "Vibe Edit (previous 6.0.0)")
        self.assertEqual((previous / "plugins/vibe-edit/VERSION").read_text().strip(), "6.0.0")
        self.assertEqual(result["node_modules_carried"], ["plugins/vibe-edit/skills/remotion/flow"])
        self.assertTrue((existing / "plugins/vibe-edit/skills/remotion/flow/node_modules/remotion/index.js").exists())
        self.assertEqual(profile.read_text(), "# mine\n")
        self.assertEqual(sorted(p.name for p in (self.t / "member").iterdir()), ["Vibe Edit", "Vibe Edit (previous 6.0.0)", "workspace"])

    def test_replace_refuses_when_the_persons_files_are_inside_the_plugin(self):
        existing = make_folder(self.t / "member/Vibe Edit", "6.0.0",
                               extra={"plugins/vibe-edit/skills/style/my-brand.lut": "custom"})
        code, out, err = self.run_main("--url", str(self.zip), "--sha256", self.hash, "--replace", str(existing))
        self.assertEqual(code, 3)
        self.assertIn("skills/style/my-brand.lut", err)
        self.assertEqual((existing / "plugins/vibe-edit/VERSION").read_text().strip(), "6.0.0")
        self.assertEqual(sorted(p.name for p in (self.t / "member").iterdir()), ["Vibe Edit"])

    def test_check_reports_extra_changed_and_root_files(self):
        folder = make_folder(self.t / "member/Vibe Edit", "6.0.0",
                             extra={"plugins/vibe-edit/notes.md": "x", "my-cut.fcpxml": "y"})
        (folder / "plugins/vibe-edit/skills/update/SKILL.md").write_text("edited by hand")
        code, out, err = self.run_main("--check", str(folder))
        self.assertEqual(code, 3)
        report = json.loads(out)
        self.assertEqual(report["extra"], ["notes.md"])
        self.assertEqual(report["changed"], ["skills/update/SKILL.md"])
        self.assertEqual(report["root_extra"], ["my-cut.fcpxml"])
        clean = make_folder(self.t / "member/Clean", "6.0.0")
        (clean / "plugins/vibe-edit/skills/remotion/flow/node_modules").mkdir()
        (clean / "plugins/vibe-edit/.DS_Store").write_bytes(b"")
        code, out, err = self.run_main("--check", str(clean))
        self.assertEqual(code, 0, out)

    def test_changed_shipped_file_does_not_block_swap_and_is_reported(self):
        existing = make_folder(self.t / "member/Vibe Edit", "6.0.0")
        (existing / "plugins/vibe-edit/skills/update/SKILL.md").write_text("edited by hand\n")
        code, out, err = self.run_main("--url", str(self.zip), "--sha256", self.hash, "--replace", str(existing))
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["changed_kept_in_previous"], ["skills/update/SKILL.md"])
        previous = Path(result["previous"])
        self.assertEqual((previous / "plugins/vibe-edit/skills/update/SKILL.md").read_text(), "edited by hand\n")
        # The edited file keeps the previous folder from being removed.
        code, out, err = self.run_main("--remove-previous", str(previous))
        self.assertEqual(code, 3)
        self.assertTrue(previous.exists())

    def test_stale_manifest_entry_matching_the_new_release_never_blocks(self):
        # 6.0.0 shipped a manifest whose entry for one file is stale while the file equals the 6.1.0 file.
        existing = make_folder(self.t / "member/Vibe Edit", "6.0.0")
        manifest_path = existing / "plugins/vibe-edit/bundle-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"]["skills/remotion/flow/package.json"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest))
        code, out, err = self.run_main("--url", str(self.zip), "--sha256", self.hash, "--replace", str(existing))
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["changed_kept_in_previous"], [])
        code, out, err = self.run_main("--remove-previous", result["previous"])
        self.assertEqual(code, 0, err)
        self.assertFalse(Path(result["previous"]).exists())

    def test_remove_previous_only_when_clean(self):
        dirty = make_folder(self.t / "Vibe Edit (previous 6.0.0)", "6.0.0", extra={"plugins/vibe-edit/keep.txt": "mine"})
        code, out, err = self.run_main("--remove-previous", str(dirty))
        self.assertEqual(code, 3)
        self.assertTrue(dirty.exists())
        clean = make_folder(self.t / "Vibe Edit (previous 6.0.0) 2", "6.0.0")
        (clean / "plugins/vibe-edit/skills/remotion/flow/node_modules").mkdir()
        code, out, err = self.run_main("--remove-previous", str(clean))
        self.assertEqual(code, 0, err)
        self.assertFalse(clean.exists())

    def test_drive_links_become_direct_downloads(self):
        for link in ("https://drive.google.com/file/d/1dCvtC_ElDopV6MckbVDpaijD8juJHmu7/view?usp=drivesdk",
                     "https://drive.google.com/open?id=1dCvtC_ElDopV6MckbVDpaijD8juJHmu7",
                     "https://drive.google.com/uc?id=1dCvtC_ElDopV6MckbVDpaijD8juJHmu7&export=download"):
            self.assertEqual(fr.direct_url(link),
                             "https://drive.google.com/uc?export=download&id=1dCvtC_ElDopV6MckbVDpaijD8juJHmu7&confirm=t")
        self.assertEqual(fr.direct_url("https://github.com/x/y/releases/download/v1/a.zip"),
                         "https://github.com/x/y/releases/download/v1/a.zip")

    def test_unsafe_links_are_refused_before_any_network_call(self):
        with patch.object(fr.urllib.request, "urlopen") as urlopen:
            for link in ("http://example.com/a.zip", "ftp://example.com/a.zip", "http://evil.test/127.0.0.1/a.zip"):
                with self.assertRaises(ValueError):
                    fr.download(link, self.t / "x.zip")
            urlopen.assert_not_called()
        fr.check_scheme("http://127.0.0.1:8765/a.zip")
        fr.check_scheme("http://localhost/a.zip")

    def test_web_page_instead_of_zip_is_refused(self):
        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        with patch.object(fr.urllib.request, "urlopen", return_value=Response(b"<html>sign in</html>")):
            with self.assertRaises(ValueError):
                fr.download("https://example.test/a.zip", self.t / "x.zip")

    def test_zip_slip_is_refused(self):
        bad = self.t / "bad.zip"
        with zipfile.ZipFile(bad, "w") as zf:
            zf.writestr("Vibe Edit/plugins/vibe-edit/VERSION", "9.9.9\n")
            zf.writestr("../escape.txt", "x")
        with self.assertRaises(ValueError):
            fr.unzip(bad, self.t / "out")
        self.assertFalse((self.t / "escape.txt").exists())


if __name__ == "__main__":
    unittest.main()
