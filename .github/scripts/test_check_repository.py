import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("check_repository", Path(__file__).with_name("check_repository.py"))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class PublicFileChecks(unittest.TestCase):
    def check(self, name, content):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return checker.check_file(root, name)

    def test_rejects_malformed_json_and_python(self):
        self.assertIn("invalid JSON", self.check("config.json", "{"))
        self.assertIn("invalid Python syntax", self.check("tool.py", "def nope("))

    def test_links_must_exist_inside_repository(self):
        self.assertTrue(self.check("README.md", "[missing](missing.md)"))
        self.assertTrue(self.check("README.md", "[escape](../README.md)"))
        self.assertEqual([], self.check("README.md", "[self](README.md) [web](https://example.com)"))

    def test_rejects_credentials_without_printing_them(self):
        self.assertTrue(self.check(".env", "EXAMPLE=value"))
        self.assertTrue(self.check(".env.local", "EXAMPLE=value"))
        self.assertTrue(self.check("note.txt", "ghp_" + "a" * 25))
        self.assertTrue(self.check("memory/note.md", "private notes"))

    def test_templates_and_examples_are_allowed(self):
        self.assertEqual([], self.check(".env.example", "EXAMPLE=YOUR_KEY_HERE"))
        self.assertEqual([], self.check("config.json", '{"account": "YOUR_ACCOUNT"}'))

if __name__ == "__main__":
    unittest.main()
