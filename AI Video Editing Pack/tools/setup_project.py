"""Preview or create a private video project and optional portable skill copy."""

from __future__ import annotations

import argparse
from pathlib import Path

from build_pack import FILES, ROOT, validate


TEMPLATES = (
    "PROJECT INTAKE.md",
    "EDIT PLAN AND REVIEW.md",
    "DELIVERY AND LEARNING.md",
)


def inside(path: Path, parent: Path) -> bool:
    return path == parent or path.is_relative_to(parent)


def reject_linked_path(base: Path, destination: Path) -> None:
    current = base
    for part in destination.relative_to(base).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"refusing linked destination: {current}")
        if current != destination and current.exists() and not current.is_dir():
            raise ValueError(f"destination parent is not a directory: {current}")


def plan(
    project: Path,
    skills_dir: Path | None = None,
    profile_dir: Path | None = None,
    root: Path = ROOT,
) -> list[tuple[Path, Path]]:
    if project.expanduser().absolute().is_symlink():
        raise ValueError("project path must not be a symbolic link")
    project = project.expanduser().resolve()
    source = root.resolve()
    public_repo = source.parent if (source.parent / ".git").exists() else None
    if project == Path(project.anchor) or inside(project, source) or inside(source, project):
        raise ValueError("project folder must be outside the source pack and filesystem root")
    if public_repo and inside(project, public_repo):
        raise ValueError("project folder must be outside the public repository")
    if project.exists() and (not project.is_dir() or project.is_symlink()):
        raise ValueError("project path must be a real directory or a new path")
    copies = [(root / "templates" / name, project / name) for name in TEMPLATES]
    if skills_dir is not None:
        if skills_dir.expanduser().absolute().is_symlink():
            raise ValueError("skills path must not be a symbolic link")
        skills_dir = skills_dir.expanduser().resolve()
        if skills_dir == Path(skills_dir.anchor) or inside(skills_dir, source) or inside(source, skills_dir):
            raise ValueError("skills folder must be outside the source pack and filesystem root")
        if public_repo and inside(skills_dir, public_repo):
            raise ValueError("skills folder must be outside the public repository")
        if inside(project, skills_dir) or inside(skills_dir, project):
            raise ValueError("project and skills folders must be separate")
        if skills_dir.exists() and (not skills_dir.is_dir() or skills_dir.is_symlink()):
            raise ValueError("skills path must be a real directory or a new path")
        destination = skills_dir / "AI Video Editing Pack"
        copies.extend((root / name, destination / name) for name in FILES)
    if profile_dir is not None:
        if profile_dir.expanduser().absolute().is_symlink():
            raise ValueError("profile path must not be a symbolic link")
        profile_dir = profile_dir.expanduser().resolve()
        if profile_dir == Path(profile_dir.anchor) or inside(profile_dir, source) or inside(source, profile_dir):
            raise ValueError("profile folder must be outside the source pack and filesystem root")
        if public_repo and inside(profile_dir, public_repo):
            raise ValueError("profile folder must be outside the public repository")
        if inside(project, profile_dir) or inside(profile_dir, project):
            raise ValueError("project and profile folders must be separate")
        if skills_dir and (inside(skills_dir, profile_dir) or inside(profile_dir, skills_dir)):
            raise ValueError("skills and profile folders must be separate")
        if profile_dir.exists() and (not profile_dir.is_dir() or profile_dir.is_symlink()):
            raise ValueError("profile path must be a real directory or a new path")
        copies.append((root / "templates/EDITING PROFILE.md", profile_dir / "EDITING PROFILE.md"))
    for source_file, destination_file in copies:
        base = (
            project if destination_file.is_relative_to(project)
            else skills_dir if skills_dir and destination_file.is_relative_to(skills_dir)
            else profile_dir
        )
        reject_linked_path(base, destination_file)
        if destination_file.exists():
            if not destination_file.is_file():
                raise ValueError(f"refusing to replace edited file: {destination_file}")
            if profile_dir and destination_file == profile_dir / "EDITING PROFILE.md":
                continue
            if destination_file.read_bytes() != source_file.read_bytes():
                raise ValueError(f"refusing to replace edited file: {destination_file}")
    return copies


def apply(copies: list[tuple[Path, Path]]) -> int:
    created = 0
    for source_file, destination_file in copies:
        if destination_file.exists():
            continue
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        with destination_file.open("xb") as stream:
            stream.write(source_file.read_bytes())
        created += 1
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path, help="private working project folder")
    parser.add_argument("--skills-dir", type=Path, help="optional folder where a portable skill copy will be placed")
    parser.add_argument("--profile-dir", type=Path, help="optional durable private folder for a reusable editing profile")
    parser.add_argument("--apply", action="store_true", help="create files after preview; never overwrite edits")
    args = parser.parse_args()
    problems = validate()
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1
    try:
        copies = plan(args.project, args.skills_dir, args.profile_dir)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    pending = [destination for _, destination in copies if not destination.exists()]
    print(f"Project: {args.project.expanduser().resolve()}")
    if args.skills_dir:
        print(f"Portable skill copy: {args.skills_dir.expanduser().resolve() / 'AI Video Editing Pack'}")
        print("Check your AI app's current skill-folder rules; copying files does not activate a plugin.")
    if args.profile_dir:
        print(f"Reusable private profile: {args.profile_dir.expanduser().resolve() / 'EDITING PROFILE.md'}")
        if (args.profile_dir.expanduser().resolve() / "EDITING PROFILE.md").exists():
            print("Existing private editing profile will be reused without changes.")
    for destination in pending:
        print(f"CREATE {destination}")
    print(f"{len(pending)} new files; {len(copies) - len(pending)} already present")
    if not args.apply:
        print("Preview only. Add --apply to create these files.")
        return 0
    created = apply(copies)
    print(f"Created {created} files. Open PROJECT INTAKE.md in the private project folder.")
    if args.profile_dir:
        print("Record this durable profile path in PROJECT INTAKE.md and keep it for later projects.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
