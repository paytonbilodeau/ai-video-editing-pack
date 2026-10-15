#!/usr/bin/env python3
"""Index an already reviewed distribution tree. This is not a privacy review."""
import argparse
import json
from pathlib import Path
import re

from bootstrap import MANIFEST, digest, encode, safe_relative, load_bundle


def build(source, version):
    source = Path(source).resolve(strict=True)
    files = {}
    skills = []
    executables = []
    names = set()
    prefix = "Payton Editing System/"
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source).as_posix()
        if path.is_symlink():
            raise ValueError("Distribution contains a symlink: " + relative)
        if not path.is_file() or relative == MANIFEST:
            continue
        safe_relative(relative)
        files[relative] = digest(path.read_bytes())
        if path.stat().st_mode & 0o111:
            executables.append(relative)
        if path.name == "SKILL.md" and relative.startswith(prefix):
            if relative == prefix + "setup/SKILL.md":
                name = "vibe-editor-setup"
            elif relative == prefix + "editing/SKILL.md":
                name = "vibe-editor-editing"
            elif relative == prefix + "motion/SKILL.md":
                name = "vibe-editor-motion"
            else:
                slug = re.sub(r"[^a-z0-9]+", "-", path.parent.name.lower()).strip("-")[:40]
                name = "vibe-" + slug
            if name in names:
                name += "-" + digest(relative.encode())[:8]
            names.add(name)
            label = path.parent.name.replace("-", " ")
            skills.append({"name": name, "path": relative,
                           "description": "Use the Vibe Editors " + label + " workflow when this stage is requested."})
    manifest = {"schema": 1, "version": version,
                "entry": prefix + "setup/SKILL.md",
                "profile": prefix + "editing/profiles/PAYTON EDITING PROFILE.md",
                "skills": skills, "executables": executables, "files": files}
    for field in ("entry", "profile"):
        if manifest[field] not in files:
            raise ValueError("Missing required distribution " + field)
    destination = source / MANIFEST
    if destination.exists():
        raise ValueError("Manifest exists. Preserve the release and build a new staging directory")
    destination.write_bytes(encode(manifest))
    load_bundle(source)
    return {"version": version, "files": len(files), "skills": len(skills),
            "manifest_sha256": digest(encode(manifest))}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.source, args.version), indent=2))
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + "\n")
