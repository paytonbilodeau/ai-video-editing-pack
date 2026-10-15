import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

SCRIPT = Path(__file__).resolve().parent.parent / 'bootstrap.py'
spec = importlib.util.spec_from_file_location('candidate_bootstrap', SCRIPT)
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)

class ProfileLinksTests(unittest.TestCase):
    def fixture(self, root):
        source = root / 'source'
        files = {
            'editing/SKILL.md': '# Editing\n',
            'editing/profiles/PROFILE.md': '# Taste\n[One](TIGHT%20TEACHING.md)\n[Two](<../references/Advanced handoffs.md>)\n[Part](TIGHT%20TEACHING.md?view=full#pace)\n[Site](https://example.com/docs)\n[Local](#taste)\n',
            'editing/profiles/TIGHT TEACHING.md': '# Timing\n',
            'editing/references/Advanced handoffs.md': '# Handoffs\n'
        }
        for name, text in files.items():
            p = source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        manifest = {'schema': 1, 'version': 'test', 'entry': 'editing/SKILL.md', 'profile': 'editing/profiles/PROFILE.md', 'files': {p: hashlib.sha256(s.encode()).hexdigest() for p,s in files.items()}, 'skills': []}
        (source / 'bundle-manifest.json').write_bytes(bootstrap.encode(manifest))
        return source

    def run_install(self, profile):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            source = self.fixture(root)
            workspace = root / 'workspace'
            bootstrap.install(source, workspace, profile=profile, apps=('codex',), apply=True)
            p = workspace / profile
            text = p.read_text()
            links = re.findall(r'\]\(([^)]+)\)', text)
            for link in links[:3]:
                self.assertTrue((p.parent / unquote(urlsplit(link).path)).is_file(), link)
                self.assertNotIn(' ', link)
            self.assertTrue(links[2].endswith('?view=full#pace'))
            self.assertIn('[Site](https://example.com/docs)', text)
            self.assertIn('[Local](#taste)', text)
            self.assertEqual((source/'editing/profiles/PROFILE.md').read_bytes(), (workspace/'Vibe Editor Pack/editing/profiles/PROFILE.md').read_bytes())

    def test_default_profile_links_resolve(self):
        self.run_install(bootstrap.PROFILE)

    def test_custom_nested_profile_links_resolve(self):
        self.run_install('preferences/brand choices/CUSTOM PROFILE.md')

    def test_existing_custom_profile_bytes_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();source=self.fixture(root);workspace=root/'workspace';p=workspace/'prefs/profile.md';p.parent.mkdir(parents=True)
            original=b'# My choices\n[Keep](../my-reference.md)\n'
            p.write_bytes(original)
            result=bootstrap.install(source,workspace,profile='prefs/profile.md',apps=('codex',),apply=True)
            self.assertEqual(result['profile_action'],'preserve_existing')
            self.assertEqual(p.read_bytes(),original)
            self.assertTrue(bootstrap.install(source,workspace,profile='prefs/profile.md',apps=('codex',),apply=True)['profile_preserved'])
            self.assertEqual(p.read_bytes(),original)

if __name__=='__main__': unittest.main()
