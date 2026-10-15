import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("bootstrap", Path(__file__).resolve().parent.parent / "bootstrap.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "source"
        self.workspace = self.root / "customer"
        self.files = {"setup/SKILL.md": b"---\nname: setup\ndescription: Set up editing\n---\nRead ../editing/SKILL.md\n",
                      "editing/SKILL.md": b"Keep the whole word.\n",
                      "editing/profile.md": b"Palette: green\nPacing: natural\n",
                      "motion/runtime/scene.tsx": b"export const Scene = () => <div>Hi</div>;\n",
                      "example.png": b"\x89PNG\r\nexample"}
        self.bundle(self.source, "1.0.0", self.files)

    def tearDown(self):
        self.temp.cleanup()

    def bundle(self, root, version, files):
        root.mkdir(parents=True, exist_ok=True)
        for name, data in files.items():
            p = root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        manifest = {"schema": 1, "version": version, "entry": "setup/SKILL.md",
                    "profile": "editing/profile.md", "files": {k:b.digest(v) for k,v in files.items()},
                    "skills": [{"name":"vibe-editor", "path":"setup/SKILL.md", "description":"Set up editing"}]}
        (root / b.MANIFEST).write_bytes(b.encode(manifest))
        return root

    def install(self):
        return b.install(self.source, self.workspace, apply=True)

    def next_bundle(self, changes):
        files = dict(self.files)
        for key,value in changes.items():
            if value is None:
                files.pop(key, None)
            else:
                files[key] = value
        return self.bundle(self.root / "next", "1.1.0", files)

    def test_dry_run_writes_nothing(self):
        self.assertEqual(b.install(self.source, self.workspace)["status"], "planned")
        self.assertFalse(self.workspace.exists())

    def test_complete_install_and_repeat(self):
        self.assertEqual(self.install()["status"], "installed")
        for name,data in self.files.items():
            self.assertEqual((self.workspace/b.WORKING/name).read_bytes(), data)
        self.assertEqual((self.workspace/b.PROFILE).read_bytes(),self.files["editing/profile.md"])
        self.assertEqual(b.install(self.source,self.workspace,apply=True)["status"],"already_installed")
        for app in (".agents", ".claude"):
            p=self.workspace/app/"skills/vibe-editor/SKILL.md"
            self.assertIn("../../../Vibe Editor Pack/setup/SKILL.md",p.read_text())
            self.assertTrue((p.parent/"../../../Vibe Editor Pack/setup/SKILL.md").resolve().exists())

    def test_custom_profile_and_routers_win(self):
        p=self.workspace/"preferences/custom.md";p.parent.mkdir(parents=True);p.write_text("Palette: blue")
        (self.workspace/"AGENTS.md").write_text("My rules")
        (self.workspace/"CLAUDE.md").write_text("My Claude rules")
        b.install(self.source,self.workspace,profile="preferences/custom.md",apply=True)
        self.assertEqual(p.read_text(),"Palette: blue")
        self.assertEqual((self.workspace/"AGENTS.md").read_text(),"My rules")
        self.assertEqual((self.workspace/"CLAUDE.md").read_text(),"My Claude rules")
        self.assertFalse((self.workspace/b.PROFILE).exists())

    def test_bridge_collision_is_preserved_and_reported(self):
        p=self.workspace/".agents/skills/vibe-editor/SKILL.md";p.parent.mkdir(parents=True);p.write_text("Custom skill")
        r=self.install();self.assertEqual(r["status"],"installed_with_bridge_collisions")
        self.assertEqual(p.read_text(),"Custom skill")

    def test_hash_mismatch_before_any_writes(self):
        (self.source/"editing/SKILL.md").write_text("changed")
        with self.assertRaises(ValueError): self.install()
        self.assertFalse(self.workspace.exists())

    def test_unlisted_file_rejected(self):
        (self.source/"unreviewed.txt").write_text("extra")
        with self.assertRaises(ValueError): self.install()

    def test_unsafe_paths_rejected(self):
        for name in ("../outside","/absolute","a/../outside","x\\bad", "C:/file", ".env", "x/token.json"):
            with self.subTest(name=name),self.assertRaises(ValueError): b.safe_relative(name)

    def test_source_symlink_rejected(self):
        (self.source/"external").symlink_to(self.root/"outside")
        with self.assertRaises(ValueError): self.install()

    def test_destination_symlink_rejected(self):
        self.workspace.mkdir();(self.workspace/".agents").symlink_to(self.root/"elsewhere")
        with self.assertRaises(ValueError): self.install()
        self.assertFalse((self.workspace/b.WORKING).exists())

    def test_parent_file_rejected_before_copy(self):
        self.workspace.mkdir();(self.workspace/".agents").write_text("not a directory")
        with self.assertRaises(ValueError): self.install()
        self.assertFalse((self.workspace/b.WORKING).exists())

    def test_source_workspace_overlap_rejected(self):
        with self.assertRaises(ValueError): b.install(self.source,self.source/"workspace",apply=True)

    def test_existing_managed_folder_never_overwritten(self):
        (self.workspace/b.WORKING).mkdir(parents=True)
        with self.assertRaises(ValueError): self.install()

    def test_managed_profile_path_rejected(self):
        with self.assertRaises(ValueError): b.install(self.source,self.workspace,profile="Vibe Editor Pack/custom.md",apply=True)

    def test_clean_update_add_remove_and_backup(self):
        self.install()
        next_source=self.next_bundle({"editing/SKILL.md":b"Preserve complete words.\n", "example.png":None,"new.txt":b"new"})
        plan=self.root/"plan";r=b.plan_update(next_source,self.workspace,plan)
        self.assertFalse(r["conflicts"])
        self.assertEqual((self.workspace/b.WORKING/"editing/SKILL.md").read_bytes(),self.files["editing/SKILL.md"])
        receipt=b.apply_update(next_source,self.workspace,plan)
        self.assertEqual(receipt["status"],"updated")
        self.assertFalse((self.workspace/b.WORKING/"example.png").exists())
        self.assertEqual((self.workspace/receipt["backup"]/b.WORKING/"example.png").read_bytes(),self.files["example.png"])
        self.assertEqual((self.workspace/b.PROFILE).read_bytes(),self.files["editing/profile.md"])

    def test_custom_change_and_added_file_survive_unrelated_update(self):
        self.install();work=self.workspace/b.WORKING
        (work/"editing/SKILL.md").write_bytes(b"My local choice")
        (work/"my-notes.txt").write_bytes(b"Own notes")
        next_source=self.next_bundle({"example.png":b"new image"})
        plan=self.root/"plan";b.plan_update(next_source,self.workspace,plan)
        b.apply_update(next_source,self.workspace,plan)
        self.assertEqual((work/"editing/SKILL.md").read_bytes(),b"My local choice")
        self.assertEqual((work/"my-notes.txt").read_bytes(),b"Own notes")

    def test_both_changed_requires_review_and_preserves_active(self):
        self.install();path=self.workspace/b.WORKING/"editing/SKILL.md";path.write_bytes(b"My local choice")
        next_source=self.next_bundle({"editing/SKILL.md":b"Upstream change"})
        plan=self.root/"plan";r=b.plan_update(next_source,self.workspace,plan)
        self.assertEqual(r["conflicts"],["editing/SKILL.md"])
        with self.assertRaises(ValueError): b.apply_update(next_source,self.workspace,plan)
        self.assertEqual(path.read_bytes(),b"My local choice")
        for side in ("base","customized","upstream"):
            self.assertTrue((plan/"conflicts"/side/"editing/SKILL.md").exists())

    def test_reviewed_merge_and_profile_preserved(self):
        self.install();work=self.workspace/b.WORKING
        (work/"editing/SKILL.md").write_bytes(b"My local choice")
        (self.workspace/b.PROFILE).write_bytes(b"Personal colors")
        next_source=self.next_bundle({"editing/SKILL.md":b"New mechanism", "editing/profile.md":b"New defaults"})
        plan=self.root/"plan";b.plan_update(next_source,self.workspace,plan)
        merged=b"New mechanism with my local choice"
        (plan/"candidate/editing/SKILL.md").write_bytes(merged)
        resolution=self.root/"resolutions.json"
        resolution.write_text(json.dumps({"editing/SKILL.md":{"decision":"merged","sha256":b.digest(merged)}}))
        b.apply_update(next_source,self.workspace,plan,resolution)
        self.assertEqual((work/"editing/SKILL.md").read_bytes(),merged)
        self.assertEqual((self.workspace/b.PROFILE).read_bytes(),b"Personal colors")

    def test_stale_working_file_blocks_apply(self):
        self.install();next_source=self.next_bundle({"example.png":b"new"});plan=self.root/"plan"
        b.plan_update(next_source,self.workspace,plan)
        (self.workspace/b.WORKING/"editing/SKILL.md").write_bytes(b"changed after review")
        with self.assertRaises(ValueError): b.apply_update(next_source,self.workspace,plan)

    def test_unreviewed_candidate_change_blocks_apply(self):
        self.install();next_source=self.next_bundle({"example.png":b"new"});plan=self.root/"plan"
        b.plan_update(next_source,self.workspace,plan)
        (plan/"candidate/editing/SKILL.md").write_bytes(b"unreviewed")
        with self.assertRaises(ValueError): b.apply_update(next_source,self.workspace,plan)

    def test_tampered_base_blocks_update(self):
        self.install();state=json.loads((self.workspace/b.CONTROL/"state.json").read_text())
        (self.workspace/b.CONTROL/"bases"/state["manifest_sha256"]/"editing/SKILL.md").write_text("tamper")
        with self.assertRaises(ValueError): b.plan_update(self.next_bundle({}),self.workspace,self.root/"plan")

    def test_case_colliding_bundle_rejected(self):
        manifest=json.loads((self.source/b.MANIFEST).read_text())
        manifest["files"]["Example.png"]=manifest["files"]["example.png"]
        (self.source/b.MANIFEST).write_bytes(b.encode(manifest))
        with self.assertRaises(ValueError): self.install()

    def test_missing_working_manifest_is_not_already_installed(self):
        self.install();(self.workspace/b.WORKING/b.MANIFEST).unlink()
        with self.assertRaises(ValueError): self.install()

    def test_custom_deletion_survives_when_upstream_unchanged(self):
        self.install();(self.workspace/b.WORKING/"example.png").unlink()
        next_source=self.next_bundle({"editing/SKILL.md":b"updated"});plan=self.root/"plan"
        report=b.plan_update(next_source,self.workspace,plan)
        self.assertFalse(report["conflicts"])
        b.apply_update(next_source,self.workspace,plan)
        self.assertFalse((self.workspace/b.WORKING/"example.png").exists())

    def test_binary_conflict_and_injected_plan_cannot_bypass_review(self):
        self.install();(self.workspace/b.WORKING/"example.png").write_bytes(b"\x89custom")
        next_source=self.next_bundle({"example.png":b"\x89upstream"});plan=self.root/"plan"
        report=b.plan_update(next_source,self.workspace,plan)
        self.assertEqual(report["conflicts"],["example.png"])
        for row in report["rows"]:
            if row["path"]=="example.png":row["action"]="take_upstream"
        report["conflicts"]=[];(plan/"comparison.json").write_bytes(b.encode(report))
        with self.assertRaises(ValueError): b.apply_update(next_source,self.workspace,plan)

    def test_executable_tools_survive_install_and_update(self):
        manifest=json.loads((self.source/b.MANIFEST).read_text())
        manifest["executables"]=["editing/SKILL.md"]
        (self.source/b.MANIFEST).write_bytes(b.encode(manifest))
        self.install()
        self.assertTrue((self.workspace/b.WORKING/"editing/SKILL.md").stat().st_mode & 0o111)
        next_source=self.next_bundle({"example.png":b"new"})
        incoming=json.loads((next_source/b.MANIFEST).read_text())
        incoming["executables"]=["editing/SKILL.md"]
        (next_source/b.MANIFEST).write_bytes(b.encode(incoming))
        plan=self.root/"plan";b.plan_update(next_source,self.workspace,plan)
        b.apply_update(next_source,self.workspace,plan)
        self.assertTrue((self.workspace/b.WORKING/"editing/SKILL.md").stat().st_mode & 0o111)

    def test_changed_candidate_executable_bit_is_rejected(self):
        self.install();next_source=self.next_bundle({"example.png":b"new"});plan=self.root/"plan"
        b.plan_update(next_source,self.workspace,plan)
        (plan/"candidate/editing/SKILL.md").chmod(0o755)
        with self.assertRaises(ValueError):b.apply_update(next_source,self.workspace,plan)

    def test_installed_runtime_and_local_config_preserved_without_distribution(self):
        self.install();work=self.workspace/b.WORKING
        runtime=work/"motion/node_modules/package";runtime.mkdir(parents=True)
        (runtime/"module.js").write_bytes(b"installed dependency")
        binary=work/"motion/node_modules/.bin/tool";binary.parent.mkdir()
        binary.symlink_to("../package/module.js")
        config=work/"motion/.env";config.write_bytes(b"EXAMPLE_SETTING=customer-only\n")
        next_source=self.next_bundle({"editing/SKILL.md":b"updated"});plan=self.root/"plan"
        report=b.plan_update(next_source,self.workspace,plan)
        self.assertEqual(report["preserved_local_paths"],["motion/.env","motion/node_modules"])
        self.assertFalse((plan/"candidate/motion/.env").exists())
        self.assertNotIn("customer-only",(plan/"comparison.json").read_text())
        receipt=b.apply_update(next_source,self.workspace,plan)
        self.assertEqual(config.read_bytes(),b"EXAMPLE_SETTING=customer-only\n")
        self.assertEqual((runtime/"module.js").read_bytes(),b"installed dependency")
        self.assertTrue(binary.is_symlink())
        self.assertEqual((self.workspace/receipt["backup"]/b.WORKING/"motion/.env").read_bytes(),config.read_bytes())

    def test_new_local_runtime_since_plan_requires_fresh_review(self):
        self.install();next_source=self.next_bundle({"example.png":b"new"});plan=self.root/"plan"
        b.plan_update(next_source,self.workspace,plan)
        (self.workspace/b.WORKING/"motion/node_modules").mkdir()
        with self.assertRaises(ValueError):b.apply_update(next_source,self.workspace,plan)


if __name__ == "__main__":
    unittest.main(verbosity=2)
