#!/usr/bin/env python3
"""Validate a content-waterfall map before rendering.

Checks map structure, packaging fields, source bounds and duration limits.
This is metadata validation, not visual, listening or native-platform QA.

Usage:
    python3 tools/waterfall_validate.py \
        project/waterfall/<proj>/map/content-map.json /path/to/source.mp4 [--mode more]

More mode accepts the current clips[] schema (horizontal/vertical, start_frame,
end_frame exclusive, title, hook, caption) as well as legacy mids[]/shorts[].
It uses the probed source frame rate and has no minimum horizontal duration.
"""

import argparse
import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

SHORT_BAND = (15.0, 180.0)      # 180 seconds is a hard maximum
MID_BAND = (180.0, 1500.0)      # 3-25 min


def finite_number(value):
    if isinstance(value, bool):
        raise ValueError("boolean is not a timestamp")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("number must be finite")
    return number


def probe_source(media: Path) -> dict:
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "format=duration:stream=duration,width,height,avg_frame_rate,r_frame_rate,nb_frames",
         "-of", "json", str(media)],
        capture_output=True, text=True)
    try:
        data = json.loads(proc.stdout)
        stream = data["streams"][0]
        duration = finite_number(stream.get("duration") or data["format"]["duration"])
        if proc.returncode or duration <= 0:
            raise ValueError("invalid source duration")
    except (ValueError, KeyError, IndexError, TypeError):
        raise ValueError(f"Could not read video duration of {media}") from None
    try:
        fps = float(Fraction(stream.get("avg_frame_rate") or stream.get("r_frame_rate")))
    except (ValueError, TypeError, ZeroDivisionError):
        fps = None
    frames = stream.get("nb_frames")
    return {"duration": duration, "fps": fps,
            "source_frames": int(frames) if str(frames).isdigit() else None,
            "source_size": (int(stream["width"]), int(stream["height"]))}


def probe_duration(media: Path) -> float:
    return probe_source(media)["duration"]


def check_clip(clip, kind, duration, errors, warnings, *, mode="general"):
    if not isinstance(clip, dict):
        errors.append(f"{kind}: clip must be an object")
        return None
    cid = clip.get("id", "?")
    for field in ("id", "title"):
        if not isinstance(clip.get(field), str) or not clip[field].strip():
            errors.append(f"{kind} {cid}: nonempty '{field}' is required")
    if isinstance(clip.get("title"), str) and len(clip["title"]) > 100:
        errors.append(f"{kind} {cid}: YouTube title must be 100 characters or fewer")
    try:
        start, end = finite_number(clip["start"]), finite_number(clip["end"])
    except (KeyError, ValueError, TypeError, OverflowError):
        errors.append(f"{kind} {cid}: start and end must be finite numbers")
        return None
    length = end - start
    if start < 0 or end > duration + 1e-6:
        errors.append(f"{kind} {cid}: {start:.1f}-{end:.1f}s outside source (0-{duration:.1f}s)")
    if length <= 0:
        errors.append(f"{kind} {cid}: end must be after start")
        return None
    band = SHORT_BAND if kind == "short" else MID_BAND
    if kind == "short" and length > 180 + 1e-6:
        errors.append(f"short {cid}: {length:.3f}s exceeds the hard 180-second maximum")
    elif not (kind == "mid" and mode == "more") and not (band[0] <= length <= band[1]):
        warnings.append(f"{kind} {cid}: {length:.0f}s is outside the {band[0]:.0f}-{band[1]:.0f}s band")
    if kind == "short":
        for label, fields in (("text_hook/hook", ("text_hook", "hook")),
                              ("platform caption", ("caption_ig", "caption"))):
            if not any(isinstance(clip.get(f), str) and clip[f].strip() for f in fields):
                errors.append(f"short {cid}: nonempty {label} is required")
    return {**clip, "start": start, "end": end}


def normalize_frame_clip(clip, fps, source_frames, errors):
    cid = clip.get("id", "?")
    try:
        fps = finite_number(fps)
        if fps <= 0:
            raise ValueError("fps must be positive")
    except (TypeError, ValueError, OverflowError):
        errors.append(f"clip {cid}: frame schema requires a valid probed source fps")
        return None
    if any(type(clip.get(f)) is not int for f in ("start_frame", "end_frame")):
        errors.append(f"clip {cid}: start_frame and end_frame must be integers (end exclusive)")
        return None
    start, end = clip["start_frame"], clip["end_frame"]
    if source_frames is not None and end > source_frames:
        errors.append(f"clip {cid}: end_frame {end} exceeds source frame count {source_frames}")
    if "frames" in clip and (type(clip["frames"]) is not int or clip["frames"] != end - start):
        errors.append(f"clip {cid}: frames must equal end_frame minus start_frame")
    for field, expected in (("start_seconds", start / fps), ("end_seconds", end / fps),
                            ("start", start / fps), ("end", end / fps)):
        if field in clip:
            try:
                if abs(finite_number(clip[field]) - expected) > 0.5 / fps:
                    raise ValueError("seconds disagree with frames")
            except (TypeError, ValueError, OverflowError):
                errors.append(f"clip {cid}: {field} disagrees with frame timing")
    return {**clip, "start": start / fps, "end": end / fps}


def check_crop(clip, source_size, errors):
    if "source_crop" not in clip:
        return
    crop = clip["source_crop"]
    cid = clip.get("id", "?")
    if not isinstance(crop, list) or len(crop) != 4 or any(type(v) is not int for v in crop):
        errors.append(f"short {cid}: source_crop must be [x, y, width, height] in integer source pixels")
        return
    x, y, width, height = crop
    if min(x, y) < 0 or min(width, height) <= 0:
        errors.append(f"short {cid}: source_crop needs nonnegative x/y and positive dimensions")
    elif abs(width / height - 9 / 16) > 0.001:
        errors.append(f"short {cid}: source_crop must have a 9:16 aspect ratio")
    if source_size and (x + width > source_size[0] or y + height > source_size[1]):
        errors.append(f"short {cid}: source_crop extends outside the source dimensions")


def validate_map(cmap, duration, *, mode="general", fps=None, source_frames=None, source_size=None):
    """Validate without mutating the map; no media rendering or perceptual claims."""
    errors, warnings, mids, shorts, chapters = [], [], [], [], []
    result = {"ok": False, "errors": errors, "warnings": warnings,
              "mids": mids, "shorts": shorts, "chapters": chapters}
    if not isinstance(cmap, dict):
        errors.append("Map must be a JSON object")
        return result
    if mode not in {"general", "more"}:
        errors.append("mode must be general or more")
    try:
        duration = finite_number(duration)
        if duration <= 0:
            raise ValueError("source duration must be positive")
    except (TypeError, ValueError, OverflowError):
        errors.append("Source duration must be positive and finite")
        return result

    groups = []
    if "clips" in cmap:
        if mode != "more":
            errors.append("clips[] frame schema requires --mode more; it cannot be ignored")
        if "mids" in cmap or "shorts" in cmap:
            errors.append("Use clips[] or mids[]/shorts[], not both map schemas")
        if not isinstance(cmap["clips"], list):
            errors.append("clips must be an array")
        else:
            for clip in cmap["clips"]:
                if not isinstance(clip, dict) or clip.get("kind") not in ("horizontal", "vertical"):
                    errors.append("Each clips[] entry must be an object with kind horizontal or vertical")
                    continue
                normalized = normalize_frame_clip(clip, fps, source_frames, errors)
                if normalized is not None:
                    groups.append((normalized, "mid" if clip["kind"] == "horizontal" else "short"))
    else:
        for key, kind in (("mids", "mid"), ("shorts", "short")):
            if not isinstance(cmap.get(key, []), list):
                errors.append(f"{key} must be an array")
            else:
                groups.extend((clip, kind) for clip in cmap.get(key, []))

    for clip, kind in groups:
        checked = check_clip(clip, kind, duration, errors, warnings, mode=mode)
        if checked is not None:
            (mids if kind == "mid" else shorts).append(checked)
            if kind == "short":
                check_crop(checked, source_size, errors)
    if not mids and not shorts:
        errors.append("Map must contain at least one valid clip; zero clips is not a render plan")

    ids = [c["id"] for c in mids + shorts if isinstance(c.get("id"), str)]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        errors.append(f"duplicate clip ids: {sorted(dupes)}")

    for i, a in enumerate(shorts):
        for b in shorts[i + 1:]:
            if a["start"] < b["end"] and b["start"] < a["end"]:
                warnings.append(f"shorts {a.get('id')} and {b.get('id')} overlap")

    lf = cmap.get("main", {}) if "clips" in cmap else cmap.get("long_form", {})
    try:
        raw_chapters = lf.get("chapters", [])
        if not isinstance(raw_chapters, list):
            raise ValueError("chapters must be an array")
        for chapter in raw_chapters:
            if not isinstance(chapter, dict) and not (isinstance(chapter, list) and len(chapter) == 2):
                raise ValueError("chapter must be an object or [seconds, title]")
            start = chapter["start"] if isinstance(chapter, dict) else chapter[0]
            chapters.append(finite_number(start))
    except (AttributeError, KeyError, IndexError, TypeError, ValueError, OverflowError):
        errors.append("main/long_form chapters must contain valid source timestamps")
    if chapters:
        if chapters[0] != 0.0:
            warnings.append("long_form chapters do not start at 0 (YouTube requires 00:00 first)")
        if len(chapters) < 3:
            warnings.append("fewer than 3 chapters (YouTube minimum)")
        if any(b <= a for a, b in zip(chapters, chapters[1:])):
            errors.append("long_form chapters not in ascending order")
        if chapters[0] < 0 or max(chapters) >= duration:
            errors.append("main/long_form chapter starts outside the source")
    text = cmap.get("text", {})
    if not isinstance(text, dict):
        errors.append("text must be an object")
    elif any(not isinstance(text.get(key, []), list) for key in ("linkedin", "x_posts")):
        errors.append("text.linkedin and text.x_posts must be arrays")
    result["ok"] = not errors
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("--mode", choices=("general", "more"), default="general")
    args = parser.parse_args()
    map_path, source = args.map, args.source
    for path in (map_path, source):
        if not path.is_file():
            sys.exit(f"Not found: {path}")
    try:
        cmap = json.loads(map_path.read_text(encoding="utf-8"))
        probe = probe_source(source)
        result = validate_map(cmap, mode=args.mode, **probe)
    except (OSError, ValueError) as exc:
        sys.exit(str(exc))
    errors, warnings = result["errors"], result["warnings"]
    mids, shorts, chapters = result["mids"], result["shorts"], result["chapters"]
    duration = probe["duration"]

    text = cmap.get("text", {}) if isinstance(cmap, dict) else {}
    if not isinstance(text, dict):
        text = {}
    text_counts = {key: len(text[key]) if isinstance(text.get(key), list) else 0
                   for key in ("linkedin", "x_posts")}

    print(f"=== Waterfall map: {map_path.name} ===")
    print(f"Source: {source.name}  ({duration/60:.1f} min)")
    print(f"Mode: {args.mode}  |  Main chapters: {len(chapters)}")
    print(f"Mids: {len(mids)}  |  Shorts: {len(shorts)}  |  "
          f"LinkedIn: {text_counts['linkedin']}  X: {text_counts['x_posts']}  "
          f"Carousel: {'yes' if text.get('carousel') else 'no'}  Newsletter: {'yes' if text.get('newsletter') else 'no'}")
    for c in mids:
        if "start" in c and "end" in c:
            print(f"  mid   {c.get('id')}  {c['start']:>8.1f}-{c['end']:<8.1f} ({(c['end']-c['start'])/60:.1f}m)  {str(c.get('title',''))[:60]}")
    for c in shorts:
        if "start" in c and "end" in c:
            print(f"  short {c.get('id')}  {c['start']:>8.1f}-{c['end']:<8.1f} ({c['end']-c['start']:.0f}s)  {str(c.get('title',''))[:60]}")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ! {w}")
    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  X {e}")
        sys.exit(1)
    print("\nMap metadata is valid. Visual, audio and native-platform QA remain separate.")


if __name__ == "__main__":
    main()
