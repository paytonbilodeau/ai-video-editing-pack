"""Validate this portable pack and build a reproducible standalone ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
import zipfile


ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_ROOT = "Vibe Editors"
CORE_FOLDER = "AI Video Editing Pack"
SUPPORTING_FOLDERS = (
    "05 Video Pre-Edit System",
    "09 Visual Storytelling and Motion System",
    "10 Content Waterfall System",
    "14 AI Video Editing System",
)
PERSONAL_FOLDER = "Payton Editing System"
EXTRA_FOLDERS = (PERSONAL_FOLDER, "Practice")
ROOT_FILES = {"START HERE.md", "LICENSE AND USE.md", "README.md", "VERSION.txt", "RELEASE NOTES.md", "bundle-manifest.json"}
IGNORED = {"__pycache__", "node_modules", ".venv", ".venv-markers", "dist", ".DS_Store", "Thumbs.db"}


def bundle_files(root: Path = ROOT) -> tuple[str, ...]:
    """Read the explicit allowlist; never discover release files by wildcard."""
    data = json.loads((root / "bundle-manifest.json").read_text(encoding="utf-8"))
    names = data.get("files")
    if data.get("schemaVersion") != 1 or data.get("archiveRoot") != ARCHIVE_ROOT:
        raise ValueError("unsupported bundle manifest")
    if not isinstance(names, list) or not names or any(not isinstance(n, str) for n in names):
        raise ValueError("bundle files must be a nonempty list of paths")
    if names != sorted(set(names)):
        raise ValueError("bundle file paths must be unique and sorted")
    for name in names:
        parts = Path(name).parts
        if not parts or Path(name).is_absolute() or ".." in parts or "\\" in name:
            raise ValueError(f"invalid bundle path: {name}")
        allowed = name in ROOT_FILES or (
            parts[0] in (CORE_FOLDER, *SUPPORTING_FOLDERS, *EXTRA_FOLDERS)
        ) or name == "Kit Email Workflow/SEQUENCE.md" or name.startswith((
            "Kit Email Workflow/lessons/", "Kit Email Workflow/assets/", "Kit Email Workflow/visual-guide/"
        ))
        if not allowed or any(part in IGNORED for part in parts):
            raise ValueError(f"outside downloadable editing scope: {name}")
        if any(part in {".env", "credentials.json", "token.json", "private", "customer", "customers", "memory", ".git"} for part in parts):
            raise ValueError(f"private file is forbidden: {name}")
        if Path(name).suffix in {".pem", ".key", ".pyc"} or Path(name).name.startswith(".env"):
            raise ValueError(f"private or generated file is forbidden: {name}")
    required = {"START HERE.md", f"{CORE_FOLDER}/START HERE.md", f"{CORE_FOLDER}/SKILL.md",
                f"{CORE_FOLDER}/bundle-manifest.json", "Kit Email Workflow/SEQUENCE.md", "Kit Email Workflow/visual-guide/README.md"}
    required.update(f"{scope}/START HERE.md" for scope in SUPPORTING_FOLDERS)
    required.update({"bundle-manifest.json", "Payton Editing System/setup/SKILL.md",
                     "Payton Editing System/editing/SKILL.md", "Payton Editing System/motion/SKILL.md",
                     "Payton Editing System/editing/profiles/PAYTON EDITING PROFILE.md",
                     "Practice/synthetic-lamp/START HERE.md"})
    required.update(f"Kit Email Workflow/lessons/{n:02}.md" for n in range(1, 23))
    if not required.issubset(names):
        raise ValueError("bundle manifest omits a required entry point or lesson")
    return tuple(names)


# Existing consumers can still enumerate the core skill without losing its identity.
FILES = tuple(n[len(CORE_FOLDER) + 1:] for n in bundle_files() if n.startswith(CORE_FOLDER + "/"))


def actual_files(folder: Path):
    """Ignore local runtime output, but never follow symbolic links."""
    if folder.is_symlink():
        yield folder
    elif folder.is_dir():
        for item in sorted(folder.iterdir()):
            if item.is_symlink():
                yield item
            elif item.name not in IGNORED:
                if item.is_dir():
                    yield from actual_files(item)
                elif item.is_file():
                    yield item



def validate(root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    try:
        declared = set(bundle_files(root))
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        return [f"invalid bundle manifest: {exc}"]
    bundle = root.parent
    actual = set()
    for scope in (CORE_FOLDER, *SUPPORTING_FOLDERS, *EXTRA_FOLDERS, "Kit Email Workflow/lessons", "Kit Email Workflow/assets", "Kit Email Workflow/visual-guide"):
        actual.update(p.relative_to(bundle).as_posix() for p in actual_files(bundle / scope))
    for name in (*ROOT_FILES, "Kit Email Workflow/SEQUENCE.md"):
        if (bundle / name).exists() or (bundle / name).is_symlink():
            actual.add(name)
    for extra in sorted(actual - declared):
        problems.append(f"undeclared pack file: {extra}")
    for missing in sorted(declared - actual):
        problems.append(f"missing pack file: {missing}")

    for relative in sorted(declared):
        file = bundle / relative
        if any(part.is_symlink() for part in (file, *file.parents) if part == bundle or part.is_relative_to(bundle)):
            problems.append(f"symbolic link is not allowed: {relative}")
            continue
        if not file.is_file():
            continue
        if file.stat().st_size == 0:
            problems.append(f"empty pack file: {relative}")
        try:
            content = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if re.search(r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|-----BEGIN [A-Z ]*PRIVATE KEY-----", content):
            problems.append(f"credential pattern in pack file: {relative}")
        if re.search(r"/" + r"Users/[^/\s]+/|[A-Z]:\\Users\\[^\\\s]+\\", content):
            problems.append(f"personal filesystem path in pack file: {relative}")
        if file.suffix != ".md":
            continue
        for target in re.findall(r"\]\((<[^>]+>|[^)\n]+)\)", content):
            target = target.strip().strip("<>")
            if re.match(r"^(?:[a-z][a-z0-9+.-]*:|#|[A-Z][A-Z0-9_]*$)", target):
                continue
            decoded = unquote(target.split("#", 1)[0])
            linked = (file.parent / decoded).resolve()
            in_bundle = linked.is_relative_to(bundle.resolve())
            linked_name = linked.relative_to(bundle.resolve()).as_posix() if in_bundle else ""
            included = linked_name in declared or (linked.is_dir() and any(n.startswith(linked_name + "/") for n in declared))
            if not in_bundle or not included or not linked.exists():
                problems.append(f"broken or escaping link: {relative} -> {target}")

    # The full-system installer consumes its own exact byte manifest.
    try:
        installation = json.loads((bundle / "bundle-manifest.json").read_text(encoding="utf-8"))
        installed_files = installation.get("files")
        expected_files = declared - {"bundle-manifest.json"}
        if installation.get("schema") != 1 or not isinstance(installed_files, dict) or set(installed_files) != expected_files:
            problems.append("installation manifest differs from the downloadable allowlist")
        else:
            for name, expected_hash in installed_files.items():
                source = bundle / name
                if source.is_file() and not any(p.is_symlink() for p in (source, *source.parents) if p == bundle or p.is_relative_to(bundle)) and hashlib.sha256(source.read_bytes()).hexdigest() != expected_hash:
                    problems.append(f"installation manifest hash mismatch: {name}")
        executable_files = installation.get("executables")
        if not isinstance(executable_files, list) or any(name not in expected_files for name in executable_files):
            problems.append("installation manifest has an invalid executable list")
    except (OSError, ValueError, TypeError, AttributeError):
        problems.append("installation manifest must be valid JSON")

    launch = bundle / "START HERE.md"
    if launch.is_file() and launch.read_text(encoding="utf-8").count("```text") != 1:
        problems.append("root START HERE.md must contain exactly one copyable setup message")

    entry = root / "START HERE.md"
    if entry.is_file() and entry.read_text(encoding="utf-8").count("```text") != 1:
        problems.append("START HERE.md must contain exactly one copyable setup message")
    intake = root / "templates/PROJECT INTAKE.md"
    if intake.is_file():
        content = intake.read_text(encoding="utf-8").lower()
        for field in ("ai app", "editor", "operating system", "source footage", "privacy", "setup handoff"):
            if field not in content:
                problems.append(f"project intake lacks {field}")
    try:
        portable = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        for field in ("name", "version", "description"):
            if not portable.get(field) or portable.get(field) != claude.get(field):
                problems.append(f"native manifests disagree on {field}")
        if portable.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
            problems.append("portable plugin schema is missing or changed")
    except (OSError, json.JSONDecodeError, AttributeError):
        problems.append("native plugin manifests must be valid JSON objects")
    return problems


def build(output: Path, root: Path = ROOT) -> str:
    problems = validate(root)
    if problems:
        raise ValueError("\n".join(problems))
    if output.expanduser().absolute().is_symlink():
        raise ValueError("ZIP output must not be a symbolic link")
    output = output.expanduser().resolve()
    if output.is_relative_to(root.resolve().parent):
        raise ValueError("ZIP output must be outside the complete pack source folder")
    public_repo = root.resolve().parent
    if (public_repo / ".git").exists() and output.is_relative_to(public_repo):
        raise ValueError("ZIP output must be outside the public repository")
    output.parent.mkdir(parents=True, exist_ok=True)
    executable_files = set(json.loads((root.parent / "bundle-manifest.json").read_text())["executables"])
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in bundle_files(root):
            info = zipfile.ZipInfo(f"{ARCHIVE_ROOT}/{relative}", (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100755 if relative in executable_files else 0o100644) << 16
            archive.writestr(info, (root.parent / relative).read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return hashlib.sha256(output.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate only; write nothing")
    parser.add_argument("--output", type=Path, help="write a standalone ZIP outside this folder")
    args = parser.parse_args()
    if not args.check and not args.output:
        parser.error("choose --check or --output")
    problems = validate()
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1
    print(f"Pack valid: {len(bundle_files())} bundled files, local links, scope and intake checked")
    if args.output:
        try:
            digest = build(args.output)
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 1
        print(f"ZIP: {args.output.expanduser().resolve()}")
        print(f"SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
