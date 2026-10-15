#!/usr/bin/env python3
"""Install reviewed local bytes or prepare a three-way update. No network calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import uuid
from urllib.parse import quote, unquote, urlsplit, urlunsplit

MANIFEST = "bundle-manifest.json"
WORKING = "Vibe Editor Pack"
CONTROL = ".vibe-editor"
PROFILE = "Vibe Editor Settings/EDITING PROFILE.md"
FORBIDDEN = {".git", "node_modules", "__pycache__", ".venv", "venv", ".env", "credentials.json", "token.json"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def safe_relative(value, allow_local=False):
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Expected a nonempty portable relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(x in (".", "..") for x in value.split("/")):
        raise ValueError("Unsafe relative path: " + value)
    if not allow_local and any(x in FORBIDDEN or x.startswith(".env.") for x in path.parts):
        raise ValueError("Unapproved sensitive or generated path: " + value)
    if ":" in value or "\x00" in value:
        raise ValueError("Unsafe path characters")
    return Path(*path.parts)


def safe_target(root, relative):
    target = root / safe_relative(relative)
    for part in [target, *target.parents]:
        if part == root.parent:
            break
        if part.is_symlink():
            raise ValueError("Refusing a symlink in a managed path: " + str(part))
        if part != target and part.exists() and not part.is_dir():
            raise ValueError("Managed parent is not a directory: " + str(part))
    return target


def file_bytes(root, relative):
    path = safe_target(root, relative)
    if not path.is_file():
        raise ValueError("Required regular file missing: " + relative)
    return path.read_bytes()


def load_bundle(source):
    source = source.resolve(strict=True)
    manifest = json.loads(file_bytes(source, MANIFEST))
    files = manifest.get("files")
    if manifest.get("schema") != 1 or not isinstance(files, dict) or not files:
        raise ValueError("Expected a reviewed schema-1 bundle manifest with file hashes")
    if not isinstance(manifest.get("version"), str) or not manifest["version"]:
        raise ValueError("Missing bundle version")
    for key in ("entry", "profile"):
        if manifest.get(key) not in files:
            raise ValueError("Manifest must include its " + key + " file")
    actual = set()
    for path in source.rglob("*"):
        if path.is_symlink():
            raise ValueError("Bundle contains a symlink: " + str(path.relative_to(source)))
        if path.is_file():
            actual.add(path.relative_to(source).as_posix())
    if actual != set(files) | {MANIFEST}:
        raise ValueError("Manifest does not cover exactly the bundle files")
    folded = [name.casefold() for name in files]
    if len(folded) != len(set(folded)):
        raise ValueError("Case-colliding paths are not portable")
    for name, expected in files.items():
        if not re.fullmatch(r"[0-9a-f]{64}", str(expected)):
            raise ValueError("Invalid SHA-256 for " + name)
        if digest(file_bytes(source, name)) != expected:
            raise ValueError("Bundle hash mismatch: " + name)
    if not isinstance(manifest.get("executables", []), list) or not set(manifest.get("executables", [])).issubset(files):
        raise ValueError("Executable paths must be covered by the manifest")
    skills = manifest.get("skills", [])
    seen = set()
    for skill in skills:
        if not re.fullmatch(r"vibe-[a-z0-9-]{1,58}", skill.get("name", "")):
            raise ValueError("Skill bridge names must be unique vibe- prefixed slugs")
        if skill["name"] in seen or skill.get("path") not in files:
            raise ValueError("Duplicate bridge name or missing skill source")
        seen.add(skill["name"])
        if not skill["path"].endswith("/SKILL.md"):
            raise ValueError("Skill bridge source must be SKILL.md")
    return source, manifest, digest(encode(manifest))


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def copy_manifest(source, manifest, destination):
    for relative, expected in manifest["files"].items():
        data = file_bytes(source, relative)
        if digest(data) != expected:
            raise ValueError("Source changed during copy: " + relative)
        write_new(safe_target(destination, relative), data)
        if relative in manifest.get("executables", []):
            safe_target(destination, relative).chmod(0o755)
    write_new(destination / MANIFEST, encode(manifest))


def bridges(manifest, profile, apps):
    out = {}
    for app in apps:
        directory = ".agents" if app == "codex" else ".claude"
        for skill in manifest.get("skills", []):
            # JSON strings are valid YAML scalars; never interpolate raw descriptions.
            description = skill.get("description", "Use the installed Vibe Editors workflow for this task.")
            text = "---\nname: " + json.dumps(skill["name"]) + "\ndescription: " + json.dumps(description) + "\n---\n\n"
            text += "Read the customer's profile at `../../../" + profile + "` first. Its choices override supplied defaults.\n\n"
            text += "Then read `../../../" + WORKING + "/" + skill["path"] + "`. Resolve that source file's links from its own directory, not this bridge. Follow only the requested stage.\n\n"
            text += "A skill supplies instructions; it does not grant app permissions, install dependencies, connect accounts or authorize spending or publishing.\n"
            out[directory + "/skills/" + skill["name"] + "/SKILL.md"] = text.encode()
    return out


def workspace_path(value, source):
    raw = Path(value).expanduser().absolute()
    for part in [raw, *raw.parents]:
        if part.is_symlink():
            raise ValueError("Choose a workspace path without symlink components")
    workspace = raw.resolve()
    if workspace == source or source in workspace.parents or workspace in source.parents:
        raise ValueError("Source bundle and workspace must be separate directories")
    return workspace


def starting_profile_bytes(working, manifest, profile_path):
    """Keep supplied reference links usable after the profile moves outside the pack."""
    source_profile = safe_target(working, manifest["profile"])
    text = file_bytes(working, manifest["profile"]).decode("utf-8")

    def relocate(match):
        target = match.group(2).strip("<>")
        url = urlsplit(target)
        if url.scheme or url.netloc or not url.path or url.path.startswith("/"):
            return match.group(0)
        linked = (source_profile.parent / unquote(url.path)).resolve()
        try:
            relative = linked.relative_to(working.resolve()).as_posix()
        except ValueError:
            return match.group(0)
        if relative not in manifest["files"]:
            return match.group(0)
        relocated = Path(os.path.relpath(linked, profile_path.parent)).as_posix()
        link = urlunsplit(("", "", quote(relocated, safe="/-._~"), url.query, url.fragment))
        return match.group(1) + link + match.group(3)

    return re.sub(r"(\[[^\]\n]*\]\()(<[^>\n]+>|[^)\s]+)(\))", relocate, text).encode("utf-8")


def install(source, workspace, profile=PROFILE, apps=("codex", "claude"), apply=False):
    source, manifest, key = load_bundle(Path(source))
    workspace = workspace_path(workspace, source)
    profile_path = safe_target(workspace, profile)
    if safe_relative(profile).parts[0] in {WORKING, CONTROL, ".agents", ".claude"}:
        raise ValueError("Keep the customer profile outside managed pack and skill directories")
    working = safe_target(workspace, WORKING)
    control = safe_target(workspace, CONTROL)
    state_path = control / "state.json"
    if state_path.exists():
        state = json.loads(file_bytes(control, "state.json"))
        if state.get("manifest_sha256") == key:
            load_bundle(control / "bases" / key)
            file_bytes(workspace, state["profile"])
            if not working.is_dir() or digest(file_bytes(working, MANIFEST)) != digest(encode(manifest)):
                raise ValueError("Working copy is missing or its manifest changed; inspect the saved base before repair")
            if not set(apps).issubset(set(state.get("apps", []))):
                raise ValueError("This app was not selected at installation. Use the installed setup file directly and review adding its project skill bridges")
            return {"status": "already_installed", "version": manifest["version"], "profile_preserved": True}
        raise ValueError("An earlier version is installed. Use plan-update; do not reinstall over it")
    if working.exists() or control.exists():
        raise ValueError("Managed destination already exists without a receipt. Choose a new workspace; nothing was overwritten")
    if profile_path.exists() and not profile_path.is_file():
        raise ValueError("Existing profile path is not a file")
    targets = bridges(manifest, profile, apps)
    collisions = []
    for name, data in targets.items():
        path = safe_target(workspace, name)
        if path.exists() and (not path.is_file() or path.read_bytes() != data):
            collisions.append(name)
    result = {"status": "planned", "version": manifest["version"], "manifest_sha256": key,
              "files": len(manifest["files"]), "profile": profile,
              "profile_action": "preserve_existing" if profile_path.exists() else "copy_starting_profile",
              "skill_bridges": len(targets), "preserved_bridge_collisions": collisions,
              "account_or_app_changes": False}
    if not apply:
        return result
    workspace.mkdir(parents=True, exist_ok=True)
    # Validate all input before writing; existing customer files are never replaced.
    with tempfile.TemporaryDirectory(prefix=".vibe-install-", dir=workspace) as temp:
        staging = Path(temp)
        copy_manifest(source, manifest, staging / "working")
        copy_manifest(source, manifest, staging / "base")
        os.rename(staging / "working", working)
        base = control / "bases" / key
        base.parent.mkdir(parents=True, exist_ok=True)
        os.rename(staging / "base", base)
    if not profile_path.exists():
        write_new(profile_path, starting_profile_bytes(working, manifest, profile_path))
    for name, data in targets.items():
        path = safe_target(workspace, name)
        if not path.exists():
            write_new(path, data)
    result["status"] = "installed_with_bridge_collisions" if collisions else "installed"
    state = {"schema": 1, "version": manifest["version"], "manifest_sha256": key,
             "profile": profile, "apps": list(apps), "install_receipt": result}
    write_new(state_path, encode(state))
    return result


def tree_files(root):
    out = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValueError("Working copy contains a symlink; review it before updating: " + relative)
        if path.is_file() and relative != MANIFEST:
            out[relative] = file_bytes(root, relative)
    return out


def working_tree(root):
    """Read managed text/assets, but never inspect local secret/cache contents."""
    files, local_paths = {}, []
    local_names = FORBIDDEN | {".venv", "venv"}
    for directory, dirs, names in os.walk(root, followlinks=False):
        directory = Path(directory)
        for name in list(dirs) + names:
            path = directory / name
            relative = path.relative_to(root).as_posix()
            if name in local_names or name.startswith(".env."):
                safe_relative(relative, allow_local=True)
                local_paths.append(relative)
                if name in dirs:
                    dirs.remove(name)
                continue
            if path.is_symlink():
                raise ValueError("Managed working path is a symlink; review before updating: " + relative)
            if name in names and relative != MANIFEST:
                files[relative] = file_bytes(root, relative)
    return files, sorted(local_paths)


def copy_local_paths(source, destination, paths):
    for name in paths:
        relative = safe_relative(name, allow_local=True)
        old, new = source / relative, destination / relative
        new.parent.mkdir(parents=True, exist_ok=True)
        if old.is_symlink():
            new.symlink_to(os.readlink(old), target_is_directory=old.is_dir())
        elif old.is_dir():
            shutil.copytree(old, new, symlinks=True)
        else:
            shutil.copy2(old, new, follow_symlinks=False)


def plan_update(source, workspace, output):
    source, incoming, incoming_key = load_bundle(Path(source))
    workspace = workspace_path(workspace, source)
    state = json.loads(file_bytes(workspace, CONTROL + "/state.json"))
    key = state.get("manifest_sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", key):
        raise ValueError("Invalid installed base reference")
    base_root, base, actual_key = load_bundle(workspace / CONTROL / "bases" / key)
    if key != actual_key:
        raise ValueError("Installed base receipt mismatch")
    current, local_paths = working_tree(safe_target(workspace, WORKING))
    output = Path(output).expanduser().absolute()
    for part in [output, *output.parents]:
        if part.is_symlink():
            raise ValueError("Update output cannot pass through a symlink")
    output = output.resolve()
    if output.exists():
        raise ValueError("Update output exists. Preserve it and choose a new output directory")
    # A candidate must not become part of the source or the active working tree.
    for protected in (source, workspace / WORKING, base_root):
        if output == protected or protected in output.parents or output in protected.parents:
            raise ValueError("Update output overlaps protected input")
    rows = []
    result_files = {}
    result_executables = set()
    conflicts = []
    all_names = sorted(set(base["files"]) | set(incoming["files"]) | set(current))
    for name in all_names:
        before = file_bytes(base_root, name) if name in base["files"] else None
        local = current.get(name)
        new = file_bytes(source, name) if name in incoming["files"] else None
        old_mode = name in base.get("executables", [])
        local_mode = bool((workspace / WORKING / name).stat().st_mode & 0o111) if local is not None else False
        new_mode = name in incoming.get("executables", [])
        if (local, local_mode) == (new, new_mode):
            action, chosen = "same", local
        elif (local, local_mode) == (before, old_mode):
            action, chosen = "take_upstream", new
        elif (new, new_mode) == (before, old_mode):
            action, chosen = "keep_custom", local
        else:
            action, chosen = "review_conflict", local
            conflicts.append(name)
        if chosen is not None:
            result_files[name] = chosen
            chosen_mode = new_mode if action == "take_upstream" else local_mode
            if chosen_mode:
                result_executables.add(name)
        rows.append({"path": name, "action": action,
                     "base": digest(before) if before is not None else None,
                     "customized": digest(local) if local is not None else None,
                     "upstream": digest(new) if new is not None else None,
                     "base_executable": old_mode, "customized_executable": local_mode,
                     "upstream_executable": new_mode})
    output.mkdir(parents=True)
    for name, data in result_files.items():
        write_new(safe_target(output / "candidate", name), data)
        if name in result_executables:
            safe_target(output / "candidate", name).chmod(0o755)
    for name in conflicts:
        for label, root, present in (("base", base_root, name in base["files"]),
                                     ("customized", workspace / WORKING, name in current),
                                     ("upstream", source, name in incoming["files"])):
            if present:
                write_new(safe_target(output / "conflicts" / label, name), file_bytes(root, name))
    report = {"schema": 1, "status": "review_required" if conflicts else "candidate_ready_for_testing",
              "installed_version": state["version"], "incoming_version": incoming["version"],
              "base_manifest": key, "incoming_manifest": incoming_key, "conflicts": conflicts,
              "profile_preserved": state["profile"], "active_installation_changed": False,
              "preserved_local_paths": local_paths,
              "rows": rows}
    write_new(output / "comparison.json", encode(report))
    write_new(output / "UPSTREAM-MANIFEST.json", encode(incoming))
    return report


def apply_update(source, workspace, plan, resolutions=None):
    """Promote an inspected candidate only if every compared input is unchanged."""
    source, incoming, incoming_key = load_bundle(Path(source))
    workspace = workspace_path(workspace, source)
    plan = Path(plan).resolve(strict=True)
    report = json.loads(file_bytes(plan, "comparison.json"))
    state = json.loads(file_bytes(workspace, CONTROL + "/state.json"))
    if report["base_manifest"] != state["manifest_sha256"] or report["incoming_manifest"] != incoming_key:
        raise ValueError("Plan is stale or refers to a different incoming bundle")
    base_root, base, base_key = load_bundle(workspace / CONTROL / "bases" / state["manifest_sha256"])
    if base_key != state["manifest_sha256"]:
        raise ValueError("Installed base mismatch")
    current, local_paths = working_tree(workspace / WORKING)
    # Recompute the comparison rather than trusting edited plan classifications.
    with tempfile.TemporaryDirectory(prefix="vibe-recheck-") as temp:
        fresh = plan_update(source, workspace, Path(temp).resolve() / "plan")
    if fresh["rows"] != report["rows"] or fresh["preserved_local_paths"] != report.get("preserved_local_paths", []):
        raise ValueError("Working files or comparison changed after review; create a fresh plan")
    choices = {} if resolutions is None else json.loads(Path(resolutions).read_text())
    if set(choices) != set(fresh["conflicts"]):
        raise ValueError("Every conflict needs an explicit reviewed resolution; no extra resolution keys")
    candidate = tree_files(plan / "candidate")
    expected = {}
    expected_executables = set()
    for row in fresh["rows"]:
        name = row["path"]
        if row["action"] == "review_conflict":
            choice = choices[name]
            if choice.get("decision") not in {"keep-custom", "take-upstream", "merged", "delete"}:
                raise ValueError("Invalid resolution decision for " + name)
            wanted = choice.get("sha256")
            if choice["decision"] == "keep-custom" and wanted != row["customized"]:
                raise ValueError("Keep-custom resolution does not match original custom bytes")
            if choice["decision"] == "take-upstream" and wanted != row["upstream"]:
                raise ValueError("Take-upstream resolution does not match incoming bytes")
            if choice["decision"] == "delete" and wanted is not None:
                raise ValueError("Delete resolution must use a null hash")
            if choice["decision"] == "merged" and not re.fullmatch(r"[0-9a-f]{64}", str(wanted)):
                raise ValueError("Merged resolution requires the reviewed candidate hash")
            executable = choice.get("executable", row["customized_executable"])
            if choice["decision"] == "take-upstream":
                executable = row["upstream_executable"]
            if choice["decision"] == "keep-custom":
                executable = row["customized_executable"]
            if type(executable) is not bool:
                raise ValueError("Executable resolution must be a boolean")
        else:
            wanted = row["upstream"] if row["action"] == "take_upstream" else row["customized"]
            executable = row["upstream_executable"] if row["action"] == "take_upstream" else row["customized_executable"]
        if wanted is not None:
            expected[name] = wanted
            if executable:
                expected_executables.add(name)
    if {name: digest(data) for name, data in candidate.items()} != expected:
        raise ValueError("Candidate differs from the reviewed comparison/resolutions")
    if {name for name in candidate if (plan / "candidate" / name).stat().st_mode & 0o111} != expected_executables:
        raise ValueError("Candidate executable modes differ from the reviewed comparison/resolutions")
    profile = file_bytes(workspace, state["profile"])
    backup = workspace / CONTROL / "backups" / uuid.uuid4().hex
    control = safe_target(workspace, CONTROL)
    target_base = control / "bases" / incoming_key
    if target_base.exists():
        load_bundle(target_base)
    bridge_targets = bridges(incoming, state["profile"], state["apps"])
    collisions = []
    for name, data in bridge_targets.items():
        path = safe_target(workspace, name)
        if path.exists() and (not path.is_file() or path.read_bytes() != data):
            collisions.append(name)
    with tempfile.TemporaryDirectory(prefix=".vibe-update-", dir=workspace) as temp:
        staging = Path(temp)
        for name, data in candidate.items():
            write_new(safe_target(staging / "working", name), data)
            if name in expected_executables:
                safe_target(staging / "working", name).chmod(0o755)
        write_new(staging / "working" / MANIFEST, encode(incoming))
        if not target_base.exists():
            copy_manifest(source, incoming, staging / "base")
        copy_local_paths(workspace / WORKING, staging / "working", local_paths)
        # Repeat the content guard after staging and before changing active files.
        if working_tree(workspace / WORKING) != (current, local_paths) or file_bytes(workspace, state["profile"]) != profile:
            raise ValueError("Customer files changed while preparing the update")
        backup.mkdir(parents=True)
        write_new(backup / "state.json", encode(state))
        os.rename(workspace / WORKING, backup / WORKING)
        try:
            os.rename(staging / "working", workspace / WORKING)
            if not target_base.exists():
                os.rename(staging / "base", target_base)
            for name, data in bridge_targets.items():
                path = safe_target(workspace, name)
                if not path.exists():
                    write_new(path, data)
            receipt = {"status": "updated", "version": incoming["version"],
                       "backup": backup.relative_to(workspace).as_posix(),
                       "profile_preserved": state["profile"], "resolved_conflicts": list(choices),
                       "preserved_local_paths": local_paths,
                       "preserved_bridge_collisions": collisions, "app_or_account_changes": False}
            new_state = dict(state, version=incoming["version"], manifest_sha256=incoming_key,
                             update_receipt=receipt)
            temporary_state = control / ("state-" + uuid.uuid4().hex + ".json")
            write_new(temporary_state, encode(new_state))
            os.replace(temporary_state, control / "state.json")
        except Exception:
            if (workspace / WORKING).exists():
                os.rename(workspace / WORKING, backup / "failed-candidate")
            os.rename(backup / WORKING, workspace / WORKING)
            raise
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    installer = sub.add_parser("install")
    installer.add_argument("--source", required=True)
    installer.add_argument("--workspace", required=True)
    installer.add_argument("--profile", default=PROFILE)
    installer.add_argument("--app", choices=["codex", "claude", "both"], default="both")
    installer.add_argument("--apply", action="store_true")
    update = sub.add_parser("plan-update")
    update.add_argument("--source", required=True)
    update.add_argument("--workspace", required=True)
    update.add_argument("--output", required=True)
    promote = sub.add_parser("apply-update")
    promote.add_argument("--source", required=True)
    promote.add_argument("--workspace", required=True)
    promote.add_argument("--plan", required=True)
    promote.add_argument("--resolutions")
    args = parser.parse_args()
    try:
        if args.command == "install":
            apps = ("codex", "claude") if args.app == "both" else (args.app,)
            result = install(args.source, args.workspace, args.profile, apps, args.apply)
        elif args.command == "plan-update":
            result = plan_update(args.source, args.workspace, args.output)
        else:
            result = apply_update(args.source, args.workspace, args.plan, args.resolutions)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
