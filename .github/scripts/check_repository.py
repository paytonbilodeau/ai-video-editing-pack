"""Check tracked public files without executing project code or exposing file contents."""
import ast
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

FORBIDDEN = {".env", "credentials.json", "token.json", ".DS_Store", "Thumbs.db"}
PRIVATE_DIRS = {"memory", "private", "customer", "customers", "node_modules", "__pycache__"}
SECRET = re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|-----BEGIN [A-Z ]*PRIVATE KEY-----")
LINK = re.compile(r"\]\((<[^>]+>|[^)\n]+)\)")

def check_file(root, relative):
    path = root / relative
    errors = []
    if path.is_symlink():
        return ["symlink is forbidden"]
    if (path.name.startswith(".env") and not path.name.endswith((".example", ".template"))) or path.name in FORBIDDEN or path.name.endswith((".pem", ".key")) or PRIVATE_DIRS.intersection(path.parts[len(root.parts):]):
        errors.append("private or generated file is forbidden")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return errors
    if SECRET.search(text):
        errors.append("credential pattern detected; inspect locally and rotate any real credential")
    if re.search(r"/" + r"Users/[^/\s]+/|[A-Z]:\\Users\\[^\\\s]+\\", text):
        errors.append("personal filesystem path detected")
    if path.suffix == ".json":
        try:
            json.loads(text)
        except ValueError:
            errors.append("invalid JSON")
    if path.suffix == ".py":
        try:
            ast.parse(text, filename=relative)
        except SyntaxError:
            errors.append("invalid Python syntax")
    if path.suffix == ".md":
        for match in LINK.finditer(text):
            target = match[1].strip().strip("<>")
            if re.match(r"^(?:[a-z][a-z0-9+.-]*:|#|[A-Z][A-Z0-9_]*$)", target):
                continue
            target = unquote(target.split("#", 1)[0])
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                errors.append("broken or escaping local Markdown link")
    return errors

def main():
    root = Path.cwd().resolve()
    tracked = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
    errors = []
    for relative in filter(None, tracked):
        errors.extend(f"{relative}: {error}" for error in check_file(root, relative))
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"Repository hygiene passed for {len(list(filter(None, tracked)))} tracked files.")

if __name__ == "__main__":
    main()
