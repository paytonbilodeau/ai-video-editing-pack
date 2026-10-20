#!/usr/bin/env python3
"""Inspect an approved workspace and named local tools without changing setup."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path


def tool_version(name: str, flag: str) -> dict[str, object]:
    executable = shutil.which(name)
    if not executable:
        return {"present": False, "version": None, "versionCheck": "missing"}
    try:
        result = subprocess.run(
            [executable, flag], capture_output=True, text=True,
            timeout=10, check=False, shell=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"present": True, "version": None, "versionCheck": "failed"}
    # Return a version token, never raw tool output or local executable paths.
    pattern = r"^v(\d+\.\d+\.\d+)" if name == "node" else rf"^{name} version (\S+)"
    match = re.search(pattern, result.stdout)
    return {
        "present": True,
        "version": match.group(1) if match and result.returncode == 0 else None,
        "versionCheck": "passed" if match and result.returncode == 0 else "failed",
    }


def standard_mcp_path(system: str) -> Path | None:
    if system == "Darwin":
        return Path("/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/ResolveMCP")
    if system == "Windows":
        return Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Blackmagic Design/DaVinci Resolve/ResolveMCP.exe"
    # Do not guess a Linux/custom location; the user may supply the vendor path.
    return None


def check(workspace: Path, motion: bool = False, resolve_mcp: Path | None = None) -> dict[str, object]:
    system = platform.system()
    usable = workspace.is_dir()
    readable = usable and os.access(workspace, os.R_OK)
    writable = usable and os.access(workspace, os.W_OK)
    try:
        free = round(shutil.disk_usage(workspace).free / 1024**3, 2) if usable else None
    except OSError:
        free = None
    tools = {name: tool_version(name, flag) for name, flag in
             [("ffmpeg", "-version"), ("ffprobe", "-version"), ("node", "--version")]}
    node_version = tools["node"]["version"]
    node_ok = bool(node_version and int(str(node_version).split(".")[0]) >= 22)
    mcp_path = resolve_mcp if resolve_mcp is not None else standard_mcp_path(system)
    mcp_present = mcp_path.is_file() if mcp_path is not None else None
    missing = []
    if not readable or not writable:
        missing.append("Choose an existing readable and writable workspace.")
    if sys.version_info < (3, 11):
        missing.append("Use Python 3.11 or newer for this checker.")
    for name in ("ffmpeg", "ffprobe"):
        if tools[name]["versionCheck"] != "passed":
            missing.append(f"Install or repair {name} with approval, then rerun.")
    if motion and not node_ok:
        missing.append("The selected motion route needs Node.js 22 or newer.")
    return {
        "schema": "ai-video-editing-setup-v1",
        "readOnly": True,
        "platform": system,
        "pythonVersion": ".".join(map(str, sys.version_info[:3])),
        "workspace": {"exists": usable, "readable": readable, "writable": writable, "freeGiB": free},
        "tools": tools,
        "motionRequested": motion,
        "node22OrNewer": node_ok,
        "resolve": {"mcpBinaryPresent": mcp_present, "connected": None, "editionAndLicenseVerified": False},
        "localPrerequisitesReady": not missing,
        "nextSteps": missing + ["Verify editor edition and license, then prove a read-only connection and a disposable sample edit."],
        "limits": "No media read, installation, settings change, editor connection or render performed. Presence is not connectivity.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--motion", action="store_true", help="Require Node.js 22+ for the optional motion route.")
    parser.add_argument("--resolve-mcp", type=Path, help="Known custom vendor MCP executable; existence check only.")
    args = parser.parse_args(argv)
    report = check(args.workspace, args.motion, args.resolve_mcp)
    print(json.dumps(report, indent=2))
    return 0 if report["localPrerequisitesReady"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
