#!/usr/bin/env python3
"""Read-only dependency check for the Video Pre-Edit System."""

from __future__ import annotations

import json
import shutil
import sys


def check() -> dict[str, object]:
    return {
        "schema": "ai-mentorship-video-pre-edit-doctor-v1",
        "readOnly": True,
        "python": {
            "version": ".".join(str(part) for part in sys.version_info[:3]),
            "supported": sys.version_info >= (3, 11),
        },
        "tools": {
            "ffmpeg": shutil.which("ffmpeg") is not None,
            "ffprobe": shutil.which("ffprobe") is not None,
        },
    }


def main() -> int:
    payload = check()
    payload["ready"] = bool(
        payload["python"]["supported"]
        and payload["tools"]["ffmpeg"]
        and payload["tools"]["ffprobe"]
    )
    print(json.dumps(payload, indent=2))
    return 0 if payload["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
