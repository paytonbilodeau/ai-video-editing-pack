#!/usr/bin/env python3
"""Load real word timings from local Auphonic HTML/JSON or Whisper word JSON.

No transcription, network calls, segment interpolation, token splitting, rounding,
or automatic offset inference. An offset is added to every source timestamp only
when explicitly supplied. Output times are seconds, without frame snapping.
"""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import sys


class TimingError(ValueError):
    """The supplied source cannot safely drive exact word timing."""


class _JSONScripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts = []
        self.active = None

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            attributes = dict(attrs)
            if attributes.get("id") == "transcriptSourceData" or attributes.get("type") == "application/json":
                self.active = [attributes.get("id"), ""]

    def handle_data(self, data):
        if self.active is not None:
            self.active[1] += data

    def handle_endtag(self, tag):
        if tag == "script" and self.active is not None:
            self.scripts.append(self.active)
            self.active = None


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise TimingError(f"{label} must be a finite number")
    return value


def _entries(data, location="$", version_index=None):
    """Return (word record, source JSON path) pairs without changing timing."""
    if isinstance(data, dict):
        if "transcript_versions" in data:
            versions = data["transcript_versions"]
            if not isinstance(versions, list) or not versions:
                raise TimingError(f"{location}.transcript_versions must be a nonempty list")
            if len(versions) > 1 and version_index is None:
                raise TimingError("Multiple transcript versions; supply --version-index explicitly")
            index = 0 if version_index is None else version_index
            if index < 0 or index >= len(versions):
                raise TimingError("Transcript version index is out of range")
            return _entries(versions[index], f"{location}.transcript_versions[{index}]")
        for key in ("transcript", "results", "segments", "words", "timestamps"):
            if key in data:
                return _entries(data[key], f"{location}.{key}", version_index)
        if data and all(str(key).isdigit() for key in data):
            rows = []
            for key in sorted(data, key=lambda item: int(item)):
                rows.extend(_segment(data[key], f"{location}[{key!r}]"))
            return rows
        raise TimingError(f"No supported word timing at {location}; segment timing is not sufficient")
    if isinstance(data, list):
        rows = []
        for index, item in enumerate(data):
            path = f"{location}[{index}]"
            if isinstance(item, list):
                if len(item) not in (3, 4):
                    raise TimingError(f"{path} must be [word, start, end, optional confidence]")
                rows.append((item, path))
            elif isinstance(item, dict):
                if location.endswith(".segments") or "timestamps" in item or "words" in item:
                    rows.extend(_segment(item, path))
                elif "word" in item and "start" in item and "end" in item:
                    rows.append((item, path))
                elif location.endswith(".words") and "text" in item and "start" in item and "end" in item:
                    rows.append((item, path))
                else:
                    raise TimingError(f"No word timing at {path}; refusing to estimate from a segment")
            else:
                raise TimingError(f"Invalid word record at {path}")
        return rows
    raise TimingError(f"Unsupported timing structure at {location}")


def _segment(segment, location):
    if not isinstance(segment, dict):
        raise TimingError(f"Invalid segment at {location}")
    for key in ("timestamps", "words"):
        if key in segment:
            rows = _entries(segment[key], f"{location}.{key}")
            if not rows and str(segment.get("text", "")).strip():
                raise TimingError(f"Spoken segment has no word timing at {location}")
            return rows
    raise TimingError(f"Segment has no word timing at {location}; refusing to estimate")


def _decode_source(raw, suffix, version_index):
    text = raw.decode("utf-8-sig")
    if suffix not in (".html", ".htm") and not text.lstrip().startswith("<"):
        return _entries(json.loads(text), version_index=version_index), "json"
    parser = _JSONScripts()
    parser.feed(text)
    preferred = [script for script in parser.scripts if script[0] == "transcriptSourceData"]
    candidates = preferred or parser.scripts
    if not candidates:
        raise TimingError("HTML has no embedded word JSON; supply a speech JSON output")
    found = []
    errors = []
    for script_id, content in candidates:
        try:
            entries = _entries(json.loads(content), version_index=version_index)
            found.append((entries, f"html-script:{script_id or 'application/json'}"))
        except (ValueError, TypeError) as error:
            errors.append(str(error))
    if len(found) != 1 or (preferred and len(preferred) != 1):
        detail = errors[0] if not found and errors else "multiple timing scripts"
        raise TimingError(f"Cannot select one embedded word transcript: {detail}")
    return found[0]


def load_word_timing(source, *, duration=None, offset=0, version_index=None):
    """Return normalized words and provenance; allow genuine overlapping words.

    Start and end times must each be nondecreasing. Positive/zero word duration
    is allowed. All shifted times must fit [0, duration] when duration is given.
    Raw times remain in source_start/source_end, even when an offset is applied.
    """
    path = Path(source).expanduser().resolve()
    offset = _number(offset, "offset")
    if duration is not None and _number(duration, "duration") <= 0:
        raise TimingError("duration must be positive")
    if version_index is not None and (isinstance(version_index, bool) or not isinstance(version_index, int) or version_index < 0):
        raise TimingError("version_index must be a nonnegative integer")
    raw = path.read_bytes()
    try:
        entries, source_format = _decode_source(raw, path.suffix.lower(), version_index)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise TimingError(f"Invalid source encoding or JSON: {error}") from error
    if not entries:
        raise TimingError("No real word timestamps found")
    words = []
    previous_start = previous_end = -1
    for entry, location in entries:
        if isinstance(entry, list):
            word, start, end = entry[:3]
            confidence = entry[3] if len(entry) == 4 else None
        else:
            word = entry.get("word", entry.get("text"))
            start, end = entry["start"], entry["end"]
            confidence = entry.get("confidence", entry.get("probability"))
        if not isinstance(word, str) or not word.strip():
            raise TimingError(f"Empty or non-text word at {location}")
        _number(start, f"{location}.start")
        _number(end, f"{location}.end")
        if start < 0 or end < start:
            raise TimingError(f"Invalid source interval at {location}: start={start}, end={end}")
        if start < previous_start or end < previous_end:
            raise TimingError(f"Word times run backwards at {location}")
        shifted_start, shifted_end = start + offset, end + offset
        if not math.isfinite(shifted_start) or not math.isfinite(shifted_end):
            raise TimingError(f"Offset makes timing non-finite at {location}")
        if shifted_start < 0 or (duration is not None and shifted_end > duration):
            raise TimingError(f"Word is outside the target video interval at {location}")
        row = {"word": word, "start": shifted_start, "end": shifted_end,
               "source_start": start, "source_end": end, "source_index": location}
        if confidence is not None:
            row["confidence"] = _number(confidence, f"{location}.confidence")
        words.append(row)
        previous_start, previous_end = start, end
    return {
        "schema_version": 1,
        "source": {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
                   "format": source_format, "version_index": version_index},
        "offset_seconds": offset, "duration_seconds": duration,
        "word_count": len(words), "words": words,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Local transcript HTML or word JSON")
    parser.add_argument("--duration", type=float, help="Known target video duration in seconds")
    parser.add_argument("--offset", type=float, default=0, help="Known offset to ADD, in seconds")
    parser.add_argument("--version-index", type=int, help="Explicit transcript_versions index")
    parser.add_argument("--output", help="Write normalized JSON here; otherwise print it")
    args = parser.parse_args(argv)
    try:
        if args.output and Path(args.output).expanduser().resolve() == Path(args.source).expanduser().resolve():
            raise TimingError("Output must not overwrite the source transcript")
        result = load_word_timing(args.source, duration=args.duration, offset=args.offset,
                                  version_index=args.version_index)
        serialized = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.output:
            Path(args.output).expanduser().write_text(serialized, encoding="utf-8")
        else:
            sys.stdout.write(serialized)
    except (TimingError, OSError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
