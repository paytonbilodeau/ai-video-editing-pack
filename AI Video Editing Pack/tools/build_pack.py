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
ARCHIVE_ROOT = "AI Video Editing Pack"
FILES = (
    ".claude-plugin/plugin.json",
    "LICENSE AND USE.md",
    "README.md",
    "SKILL.md",
    "SOURCES.md",
    "START HERE.md",
    "examples/example-cut-list.json",
    "plugin.json",
    "references/AI APP SETUP.md",
    "references/AUDIO GUIDE.md",
    "references/CUT LIST EXPORT.md",
    "references/EDIT WORKFLOW.md",
    "references/EDITING CRAFT NUMBERS.md",
    "references/EDITING JUDGMENT.md",
    "references/EDITOR CONNECTIONS.md",
    "references/EDITOR PLAYBOOK CAPCUT.md",
    "references/EDITOR PLAYBOOK FINAL CUT.md",
    "references/EDITOR PLAYBOOK PREMIERE.md",
    "references/EDITOR PLAYBOOK RESOLVE.md",
    "references/LEARNING PATH.md",
    "references/MOTION AND LUTS.md",
    "references/PROVIDER CHECK.md",
    "references/SAFETY AND API KEYS.md",
    "references/SOUND AND COLOR NUMBERS.md",
    "skills/audio/SKILL.md",
    "skills/color/SKILL.md",
    "skills/cuts-pacing/SKILL.md",
    "skills/intake/SKILL.md",
    "skills/platform-refresh/SKILL.md",
    "skills/pre-edit/SKILL.md",
    "skills/review-delivery/SKILL.md",
    "skills/source-research/SKILL.md",
    "skills/style-motion/SKILL.md",
    "skills/vibe-editing-setup/SKILL.md",
    "skills/waterfall/SKILL.md",
    "templates/DELIVERY AND LEARNING.md",
    "templates/EDIT PLAN AND REVIEW.md",
    "templates/EDITING PROFILE.md",
    "templates/PROJECT INTAKE.md",
    "tests/test_cut_list_to_timeline.py",
    "tests/test_pack.py",
    "tools/build_pack.py",
    "tools/cut_list_to_timeline.py",
    "tools/setup_project.py",
)


def validate(root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    declared = set(FILES)
    actual = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_symlink() or (
            p.is_file()
            and "__pycache__" not in p.parts
            and p.name not in {".DS_Store", "Thumbs.db"}
        )
    }
    for extra in sorted(actual - declared):
        problems.append(f"undeclared pack file: {extra}")
    for missing in sorted(declared - actual):
        problems.append(f"missing pack file: {missing}")

    for relative in FILES:
        file = root / relative
        if file.is_symlink():
            problems.append(f"symbolic link is not allowed: {relative}")
            continue
        if not file.exists():
            continue
        if file.stat().st_size == 0:
            problems.append(f"empty pack file: {relative}")
        if file.suffix != ".md":
            continue
        content = file.read_text(encoding="utf-8")
        for target in re.findall(r"(?<!!)\[[^]]+\]\(([^)]+)\)", content):
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            decoded = unquote(target.split("#", 1)[0])
            linked = (file.parent / decoded).resolve()
            if not linked.is_relative_to(root.resolve()) or not linked.is_file():
                problems.append(f"broken or escaping link: {relative} -> {target}")

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
    if output.is_relative_to(root.resolve()):
        raise ValueError("ZIP output must be outside the pack source folder")
    public_repo = root.resolve().parent
    if (public_repo / ".git").exists() and output.is_relative_to(public_repo):
        raise ValueError("ZIP output must be outside the public repository")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in FILES:
            info = zipfile.ZipInfo(f"{ARCHIVE_ROOT}/{relative}", (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (root / relative).read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
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
    print(f"Pack valid: {len(FILES)} declared files, internal links and intake checked")
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
