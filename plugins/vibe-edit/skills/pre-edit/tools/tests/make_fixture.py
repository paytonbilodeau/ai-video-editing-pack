#!/usr/bin/env python3
"""Create a tiny synthetic talking-head-style fixture with two quiet pauses."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def build_fixture(destination: Path, *, force: bool = False) -> Path:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required to create the synthetic fixture.")

    destination = destination.expanduser().resolve()
    if destination.suffix.lower() != ".mp4":
        raise RuntimeError("Fixture output must end in .mp4.")
    if not destination.parent.exists():
        raise RuntimeError("Fixture output folder does not exist.")
    if destination.exists() and not force:
        raise RuntimeError(
            f"{destination.name} already exists. Use --force only for a disposable fixture."
        )

    command = [
        ffmpeg,
        "-y" if force else "-n",
        "-hide_banner",
        "-nostats",
        "-f",
        "lavfi",
        "-i",
        "color=c=0x17201b:s=320x180:r=24:d=6",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=440:sample_rate=48000:duration=1.5",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=48000:cl=mono:d=1.5",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=660:sample_rate=48000:duration=1.5",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=48000:cl=mono:d=1.5",
        "-filter_complex",
        "[1:a][2:a][3:a][4:a]concat=n=4:v=0:a=1[a]",
        "-map",
        "0:v:0",
        "-map",
        "[a]",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-crf",
        "28",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        "-shortest",
        str(destination),
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=False,
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout or "").strip().splitlines()
        raise RuntimeError(
            "FFmpeg could not create the fixture.\n" + "\n".join(details[-12:])
        )
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output",
        nargs="?",
        default="synthetic-pre-edit-fixture.mp4",
        help="New MP4 fixture path",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing disposable fixture",
    )
    args = parser.parse_args()
    try:
        path = build_fixture(Path(args.output), force=args.force)
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(f"Created {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
