"""Turn a reviewed cut list into editor-importable timelines.

Reads one JSON cut list for a single source recording and writes any of:

- FCPXML for Final Cut Pro, which DaVinci Resolve also imports
- Final Cut Pro 7 XML (xmeml version 5) for Premiere Pro, which Resolve also imports
- CMX3600 EDL for Resolve, Premiere Pro and most other editors
- a cut sheet in Markdown and CSV for CapCut or any editor, by hand or with computer use

Standard library only. `--probe` optionally reads the source with ffprobe.
Nothing here renders video or changes the source recording.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

TOOL_VERSION = "1.0.0"
PACK_ROOT = Path(__file__).resolve().parent.parent
FORMATS = ("fcpxml", "xmeml", "edl", "sheet")
MAX_CUT_LIST_BYTES = 8 * 1024 * 1024
MAX_EDL_EVENTS = 999
NAMED_RATES = {
    "23.976": Fraction(24000, 1001),
    "23.98": Fraction(24000, 1001),
    "24": Fraction(24),
    "25": Fraction(25),
    "29.97": Fraction(30000, 1001),
    "30": Fraction(30),
    "48": Fraction(48),
    "50": Fraction(50),
    "59.94": Fraction(60000, 1001),
    "60": Fraction(60),
}


class CutListError(ValueError):
    """A problem in the cut list or the requested output that the user must fix."""


# ---------------------------------------------------------------- time helpers


def parse_rate(value: object) -> Fraction:
    """Accept 30, "30", "29.97", "30000/1001" or 29.97 and return an exact fraction."""
    if isinstance(value, bool) or value is None:
        raise CutListError("fps is required (for example 30, 29.97 or \"30000/1001\")")
    if isinstance(value, (int, float)):
        text = f"{value:.3f}".rstrip("0").rstrip(".") if isinstance(value, float) else str(value)
    else:
        text = str(value).strip()
    if text in NAMED_RATES:
        return NAMED_RATES[text]
    if "/" in text:
        num, den = text.split("/", 1)
        try:
            rate = Fraction(int(num), int(den))
        except (ValueError, ZeroDivisionError) as error:
            raise CutListError(f"fps fraction is invalid: {text}") from error
    else:
        try:
            rate = Fraction(text).limit_denominator(1001)
        except (ValueError, ZeroDivisionError) as error:
            raise CutListError(f"fps is invalid: {text}") from error
    if rate <= 0 or rate > 240:
        raise CutListError(f"fps must be between 1 and 240: {text}")
    return rate


def parse_time(value: object, rate: Fraction) -> int:
    """Return a frame count from seconds, "MM:SS.sss", "HH:MM:SS.sss" or "HH:MM:SS:FF"."""
    if isinstance(value, bool) or value is None:
        raise CutListError(f"time value is missing or invalid: {value!r}")
    if isinstance(value, (int, float)):
        seconds = float(value)
    else:
        text = str(value).strip()
        parts = text.split(":")
        try:
            if len(parts) == 4:
                hours, minutes, secs, frames = (int(part) for part in parts)
                return frames + round(Fraction(hours * 3600 + minutes * 60 + secs) * rate)
            if len(parts) == 3:
                seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                seconds = int(parts[0]) * 60 + float(parts[1])
            elif len(parts) == 1:
                seconds = float(text)
            else:
                raise ValueError(text)
        except ValueError as error:
            raise CutListError(f"time value is invalid: {text}") from error
    if not math.isfinite(seconds) or seconds < 0:
        raise CutListError(f"time value must be a finite non-negative number: {value!r}")
    return round(Fraction(seconds).limit_denominator(1_000_000) * rate)


def frames_to_seconds(frames: int, rate: Fraction) -> Fraction:
    return Fraction(frames) / rate


def rational_time(frames: int, rate: Fraction) -> str:
    """FCPXML rational time for a frame count, for example "1001/30000s" or "2s"."""
    seconds = frames_to_seconds(frames, rate)
    if seconds.denominator == 1:
        return f"{seconds.numerator}s"
    return f"{seconds.numerator}/{seconds.denominator}s"


def timecode(frames: int, rate: Fraction) -> str:
    """Non-drop-frame timecode counted at the integer timebase of the rate."""
    timebase = int(round(rate))
    frame = frames % timebase
    total_seconds = frames // timebase
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frame:02d}"


def clock(frames: int, rate: Fraction) -> str:
    seconds = float(frames_to_seconds(frames, rate))
    minutes, secs = divmod(seconds, 60)
    return f"{int(minutes)}:{secs:06.3f}"


# ---------------------------------------------------------------- data model


@dataclass
class Segment:
    source_in: int
    source_out: int  # exclusive, in frames
    note: str = ""
    record_in: int = 0

    @property
    def frames(self) -> int:
        return self.source_out - self.source_in

    @property
    def record_out(self) -> int:
        return self.record_in + self.frames


@dataclass
class Marker:
    source_frame: int
    name: str
    note: str = ""


@dataclass
class CutList:
    source: Path
    rate: Fraction
    width: int
    height: int
    duration_frames: int | None
    name: str
    segments: list[Segment]
    markers: list[Marker]
    audio_channels: int = 2
    audio_rate: int = 48000
    warnings: list[str] = field(default_factory=list)

    @property
    def total_frames(self) -> int:
        return sum(segment.frames for segment in self.segments)


def _as_int(value: object, name: str, default: int | None = None) -> int:
    if value is None:
        if default is None:
            raise CutListError(f"{name} is required")
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)) or int(value) != value:
        raise CutListError(f"{name} must be a whole number")
    if int(value) <= 0:
        raise CutListError(f"{name} must be positive")
    return int(value)


def load_cut_list(path: Path, probe: bool = False) -> CutList:
    if not path.is_file():
        raise CutListError(f"cut list does not exist: {path}")
    if path.stat().st_size > MAX_CUT_LIST_BYTES:
        raise CutListError("cut list is unexpectedly large")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CutListError(f"cut list is not readable JSON: {error}") from error
    if not isinstance(data, dict):
        raise CutListError("cut list must be a JSON object")
    return build_cut_list(data, base_dir=path.parent, probe=probe)


def build_cut_list(data: dict, base_dir: Path, probe: bool = False) -> CutList:
    warnings: list[str] = []
    source_value = data.get("source")
    if not isinstance(source_value, str) or not source_value.strip():
        raise CutListError("source must name the recording file")
    source = Path(source_value).expanduser()
    if not source.is_absolute():
        source = (base_dir / source).resolve()
    explicit_fps = "fps" in data
    if probe:
        data = {**data, **probe_source(source, data)}
    elif not source.exists():
        warnings.append(f"source file was not found at {source}; the editor will ask you to relink it")
    rate = parse_rate(data.get("fps"))
    standard_rates = {Fraction(n) for n in (24, 25, 30, 48, 50, 60, 100, 120)}
    standard_rates.update(Fraction(n, 1001) for n in (24000, 30000, 60000, 120000))
    if probe and not explicit_fps and rate not in standard_rates:
        warnings.append(
            f"probed average frame rate {rate} is unusual and may indicate variable-frame-rate footage; "
            "confirm the editor timeline rate and supply fps explicitly before relying on cut boundaries"
        )
    width = _as_int(data.get("width"), "width", 1920)
    height = _as_int(data.get("height"), "height", 1080)
    audio_channels = _as_int(data.get("audio_channels"), "audio_channels", 2)
    audio_rate = _as_int(data.get("audio_rate"), "audio_rate", 48000)
    duration_frames = None
    if data.get("duration") is not None:
        duration_frames = parse_time(data["duration"], rate)
        if duration_frames <= 0:
            raise CutListError("duration must be positive")
    name = str(data.get("name") or f"{source.stem} cut").strip()[:120]

    keep = data.get("keep")
    remove = data.get("remove")
    if keep is not None and remove is not None:
        raise CutListError("use either keep or remove, not both")
    if keep is None and remove is None:
        raise CutListError("cut list needs a keep list or a remove list")
    if remove is not None:
        if duration_frames is None:
            raise CutListError("a remove list needs the source duration (or use --probe)")
        removed = _parse_ranges(remove, rate, "remove", warnings)
        segments = _invert(removed, duration_frames)
    else:
        segments = _parse_ranges(keep, rate, "keep", warnings)
    if duration_frames is not None:
        clipped = []
        for segment in segments:
            if segment.source_in >= duration_frames:
                warnings.append(f"dropped a keep range starting after the source ends: {clock(segment.source_in, rate)}")
                continue
            if segment.source_out > duration_frames:
                warnings.append(f"shortened a keep range that ran past the source end at {clock(duration_frames, rate)}")
                segment.source_out = duration_frames
            clipped.append(segment)
        segments = clipped
    if not segments:
        raise CutListError("the cut list keeps nothing")
    min_frames = _as_int(data.get("min_clip_frames"), "min_clip_frames", 2)
    for segment in segments:
        if segment.frames < min_frames:
            warnings.append(
                f"kept range at {clock(segment.source_in, rate)} is only {segment.frames} frame(s); check whether it is a stray sliver"
            )
    position = 0
    for segment in segments:
        segment.record_in = position
        position += segment.frames

    markers = []
    for index, item in enumerate(data.get("markers") or []):
        if not isinstance(item, dict) or "time" not in item:
            raise CutListError(f"marker {index + 1} needs a time")
        markers.append(
            Marker(
                source_frame=parse_time(item["time"], rate),
                name=str(item.get("name") or f"Marker {index + 1}")[:120],
                note=str(item.get("note") or "")[:500],
            )
        )
    return CutList(
        source=source,
        rate=rate,
        width=width,
        height=height,
        duration_frames=duration_frames,
        name=name,
        segments=segments,
        markers=markers,
        audio_channels=audio_channels,
        audio_rate=audio_rate,
        warnings=warnings,
    )


def _parse_ranges(items: object, rate: Fraction, label: str, warnings: list[str]) -> list[Segment]:
    if not isinstance(items, list) or not items:
        raise CutListError(f"{label} must be a non-empty list of ranges")
    ranges: list[Segment] = []
    for index, item in enumerate(items):
        if isinstance(item, dict):
            start, end, note = item.get("start"), item.get("end"), str(item.get("note") or "")
        elif isinstance(item, (list, tuple)) and len(item) in (2, 3):
            start, end = item[0], item[1]
            note = str(item[2]) if len(item) == 3 else ""
        else:
            raise CutListError(f"{label} range {index + 1} must be {{start, end}} or [start, end]")
        first, last = parse_time(start, rate), parse_time(end, rate)
        if last <= first:
            if last == first:
                warnings.append(f"dropped an empty {label} range at {clock(first, rate)}")
                continue
            raise CutListError(f"{label} range {index + 1} ends before it starts")
        ranges.append(Segment(first, last, note[:500]))
    ranges.sort(key=lambda segment: (segment.source_in, segment.source_out))
    merged: list[Segment] = []
    for segment in ranges:
        if merged and segment.source_in <= merged[-1].source_out:
            if segment.source_in < merged[-1].source_out:
                warnings.append(f"merged overlapping {label} ranges around {clock(segment.source_in, rate)}")
            merged[-1].source_out = max(merged[-1].source_out, segment.source_out)
            if segment.note and segment.note not in merged[-1].note:
                merged[-1].note = (merged[-1].note + "; " + segment.note).strip("; ")
        else:
            merged.append(segment)
    return merged


def _invert(removed: list[Segment], duration_frames: int) -> list[Segment]:
    kept: list[Segment] = []
    cursor = 0
    for segment in removed:
        if segment.source_in > cursor:
            kept.append(Segment(cursor, min(segment.source_in, duration_frames)))
        cursor = max(cursor, segment.source_out)
    if cursor < duration_frames:
        kept.append(Segment(cursor, duration_frames))
    return [segment for segment in kept if segment.frames > 0]


def probe_source(source: Path, data: dict) -> dict:
    """Fill fps, width, height, duration and audio facts from ffprobe when available."""
    if not source.is_file():
        raise CutListError(f"cannot probe a missing source file: {source}")
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        raise CutListError("ffprobe was not found; install FFmpeg or supply fps, width, height and duration yourself")
    command = [
        ffprobe, "-v", "error", "-show_entries",
        "stream=codec_type,width,height,r_frame_rate,avg_frame_rate,sample_rate,channels:format=duration",
        "-of", "json", str(source),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
    if result.returncode != 0:
        raise CutListError(f"ffprobe failed: {result.stderr.strip()[:300]}")
    info = json.loads(result.stdout or "{}")
    filled = dict(data)
    for stream in info.get("streams", []):
        if stream.get("codec_type") == "video" and "width" in stream and "fps" not in data:
            rate_text = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or ""
            if rate_text and rate_text != "0/0":
                filled["fps"] = rate_text
        if stream.get("codec_type") == "video" and "width" in stream:
            filled.setdefault("width", stream["width"])
            filled.setdefault("height", stream["height"])
        if stream.get("codec_type") == "audio":
            filled.setdefault("audio_channels", int(stream.get("channels") or 2))
            filled.setdefault("audio_rate", int(stream.get("sample_rate") or 48000))
    if "duration" not in data and info.get("format", {}).get("duration"):
        filled["duration"] = float(info["format"]["duration"])
    if "fps" not in filled:
        raise CutListError("ffprobe did not report a video frame rate; supply fps yourself")
    return filled


# ---------------------------------------------------------------- writers


def file_url(path: Path) -> str:
    return "file://" + quote(str(path.resolve()), safe="/:@+,=~-._")


def stable_uid(path: Path) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, file_url(path))).upper()


def _format_name(cut: CutList) -> str | None:
    heights = {2160: "2160p", 1080: "1080p", 720: "720p"}
    rates = {
        Fraction(24000, 1001): "2398", Fraction(24): "24", Fraction(25): "25", Fraction(30000, 1001): "2997",
        Fraction(30): "30", Fraction(50): "50", Fraction(60000, 1001): "5994", Fraction(60): "60",
    }
    if cut.height in heights and cut.rate in rates and cut.width in (3840, 1920, 1280):
        return f"FFVideoFormat{heights[cut.height]}{rates[cut.rate]}"
    return None


def write_fcpxml(cut: CutList, version: str = "1.11") -> str:
    if not re.fullmatch(r"1\.\d{1,2}", version):
        raise CutListError("fcpxml version must look like 1.11")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<!DOCTYPE fcpxml>", f'<fcpxml version="{version}">', "  <resources>"]
    frame_duration = rational_time(1, cut.rate)
    name_attr = f' name="{_format_name(cut)}"' if _format_name(cut) else ""
    lines.append(
        f'    <format id="r1"{name_attr} frameDuration="{frame_duration}" width="{cut.width}" height="{cut.height}" colorSpace="1-1-1 (Rec. 709)"/>'
    )
    asset_duration = cut.duration_frames if cut.duration_frames is not None else max(segment.source_out for segment in cut.segments)
    audio_rate_attr = f' audioRate="{cut.audio_rate}"'
    lines.append(
        f'    <asset id="r2" name="{escape(cut.source.stem, {chr(34): "&quot;"})}" uid="{stable_uid(cut.source)}" start="0s" '
        f'duration="{rational_time(asset_duration, cut.rate)}" hasVideo="1" format="r1" hasAudio="1" audioSources="1" '
        f'audioChannels="{cut.audio_channels}"{audio_rate_attr}>'
    )
    lines.append(f'      <media-rep kind="original-media" src="{escape(file_url(cut.source), {chr(34): "&quot;"})}"/>')
    lines.append("    </asset>")
    lines.append("  </resources>")
    sequence_rate = {32000: "32k", 44100: "44.1k", 48000: "48k", 88200: "88.2k", 96000: "96k"}.get(cut.audio_rate, "48k")
    layout = "mono" if cut.audio_channels == 1 else "stereo"
    safe_name = escape(cut.name, {chr(34): "&quot;"})
    lines += [
        "  <library>",
        f'    <event name="{safe_name}">',
        f'      <project name="{safe_name}">',
        f'        <sequence format="r1" duration="{rational_time(cut.total_frames, cut.rate)}" tcStart="0s" tcFormat="NDF" audioLayout="{layout}" audioRate="{sequence_rate}">',
        "          <spine>",
    ]
    for segment in cut.segments:
        clip_markers = [marker for marker in cut.markers if segment.source_in <= marker.source_frame < segment.source_out]
        attrs = (
            f'ref="r2" offset="{rational_time(segment.record_in, cut.rate)}" name="{escape(cut.source.stem, {chr(34): "&quot;"})}" '
            f'start="{rational_time(segment.source_in, cut.rate)}" duration="{rational_time(segment.frames, cut.rate)}" '
            f'format="r1" tcFormat="NDF" audioRole="dialogue"'
        )
        if not clip_markers and not segment.note:
            lines.append(f"            <asset-clip {attrs}/>")
            continue
        lines.append(f"            <asset-clip {attrs}>")
        if segment.note:
            lines.append(f"              <note>{escape(segment.note)}</note>")
        for marker in clip_markers:
            note_attr = f' note="{escape(marker.note, {chr(34): "&quot;"})}"' if marker.note else ""
            lines.append(
                f'              <marker start="{rational_time(marker.source_frame, cut.rate)}" duration="{frame_duration}" '
                f'value="{escape(marker.name, {chr(34): "&quot;"})}"{note_attr}/>'
            )
        lines.append("            </asset-clip>")
    lines += ["          </spine>", "        </sequence>", "      </project>", "    </event>", "  </library>", "</fcpxml>", ""]
    return "\n".join(lines)


def write_xmeml(cut: CutList) -> str:
    """Final Cut Pro 7 XML (xmeml version 5), the format Premiere Pro imports as 'Final Cut Pro XML'."""
    timebase = int(round(cut.rate))
    ntsc = "TRUE" if cut.rate.denominator == 1001 else "FALSE"
    rate_xml = f"<rate><timebase>{timebase}</timebase><ntsc>{ntsc}</ntsc></rate>"
    total = cut.total_frames
    asset_frames = cut.duration_frames if cut.duration_frames is not None else max(segment.source_out for segment in cut.segments)
    name = escape(cut.name)
    clip_name = escape(cut.source.name)
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<!DOCTYPE xmeml>",
        '<xmeml version="5">',
        '  <sequence id="sequence-1">',
        f"    <name>{name}</name>",
        f"    <duration>{total}</duration>",
        f"    {rate_xml}",
        f"    <timecode>{rate_xml}<string>00:00:00:00</string><frame>0</frame><displayformat>NDF</displayformat></timecode>",
        "    <media>",
        "      <video>",
        f"        <format><samplecharacteristics>{rate_xml}<width>{cut.width}</width><height>{cut.height}</height>"
        "<anamorphic>FALSE</anamorphic><pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics></format>",
        "        <track>",
    ]
    file_full = (
        f'<file id="file-1"><name>{clip_name}</name><pathurl>{escape(file_url(cut.source))}</pathurl>{rate_xml}'
        f"<duration>{asset_frames}</duration><timecode>{rate_xml}<string>00:00:00:00</string><frame>0</frame><displayformat>NDF</displayformat></timecode>"
        f"<media><video><samplecharacteristics>{rate_xml}<width>{cut.width}</width><height>{cut.height}</height></samplecharacteristics></video>"
        f"<audio><samplecharacteristics><depth>16</depth><samplerate>{cut.audio_rate}</samplerate></samplecharacteristics><channelcount>{cut.audio_channels}</channelcount></audio></media></file>"
    )
    file_ref = '<file id="file-1"/>'
    channels = range(1, cut.audio_channels + 1)

    def links(index: int) -> str:
        parts = [
            f"<link><linkclipref>clipitem-{index}</linkclipref><mediatype>video</mediatype><trackindex>1</trackindex><clipindex>{index}</clipindex></link>"
        ]
        for channel in channels:
            parts.append(
                f"<link><linkclipref>clipitem-{index}-a{channel}</linkclipref><mediatype>audio</mediatype><trackindex>{channel}</trackindex>"
                f"<clipindex>{index}</clipindex><groupindex>1</groupindex></link>"
            )
        return "".join(parts)

    for index, segment in enumerate(cut.segments, start=1):
        file_xml = file_full if index == 1 else file_ref
        out.append(
            f'          <clipitem id="clipitem-{index}"><name>{clip_name}</name><enabled>TRUE</enabled><duration>{asset_frames}</duration>{rate_xml}'
            f"<start>{segment.record_in}</start><end>{segment.record_out}</end><in>{segment.source_in}</in><out>{segment.source_out}</out>"
            f"{file_xml}{links(index)}</clipitem>"
        )
    out += ["        </track>", "      </video>", "      <audio>"]
    for channel in channels:
        out.append("        <track>")
        for index, segment in enumerate(cut.segments, start=1):
            out.append(
                f'          <clipitem id="clipitem-{index}-a{channel}"><name>{clip_name}</name><enabled>TRUE</enabled><duration>{asset_frames}</duration>{rate_xml}'
                f"<start>{segment.record_in}</start><end>{segment.record_out}</end><in>{segment.source_in}</in><out>{segment.source_out}</out>"
                f'{file_ref}<sourcetrack><mediatype>audio</mediatype><trackindex>{channel}</trackindex></sourcetrack>{links(index)}</clipitem>'
            )
        out.append("        </track>")
    out += ["      </audio>", "    </media>"]
    if cut.markers:
        for marker in cut.markers:
            record = _record_frame(cut, marker.source_frame)
            if record is None:
                continue
            out.append(
                f"    <marker><name>{escape(marker.name)}</name><comment>{escape(marker.note)}</comment><in>{record}</in><out>-1</out></marker>"
            )
    out += ["  </sequence>", "</xmeml>", ""]
    return "\n".join(out)


def _record_frame(cut: CutList, source_frame: int) -> int | None:
    for segment in cut.segments:
        if segment.source_in <= source_frame < segment.source_out:
            return segment.record_in + (source_frame - segment.source_in)
    return None


def write_edl(cut: CutList) -> str:
    if len(cut.segments) > MAX_EDL_EVENTS:
        cut.warnings.append(
            f"EDL has {len(cut.segments)} events; CMX3600 readers expect at most {MAX_EDL_EVENTS}. Prefer FCPXML or XML for this edit."
        )
    lines = [f"TITLE: {cut.name[:70]}", "FCM: NON-DROP FRAME", ""]
    marker_lines: dict[int, list[str]] = {}
    for marker in cut.markers:
        record = _record_frame(cut, marker.source_frame)
        if record is None:
            continue
        for index, segment in enumerate(cut.segments, start=1):
            if segment.record_in <= record < segment.record_out:
                text = (marker.name + (" " + marker.note if marker.note else "")).replace("\n", " ")[:80]
                marker_lines.setdefault(index, []).append(f"* LOC: {timecode(record, cut.rate)} YELLOW   {text}")
                break
    for index, segment in enumerate(cut.segments, start=1):
        lines.append(
            f"{index:03d}  AX       AA/V  C        {timecode(segment.source_in, cut.rate)} {timecode(segment.source_out, cut.rate)} "
            f"{timecode(segment.record_in, cut.rate)} {timecode(segment.record_out, cut.rate)}"
        )
        lines.append(f"* FROM CLIP NAME: {cut.source.name}")
        if segment.note:
            lines.append(f"* COMMENT: {segment.note.replace(chr(10), ' ')[:80]}")
        lines.extend(marker_lines.get(index, []))
        lines.append("")
    return "\n".join(lines)


def write_sheet(cut: CutList) -> tuple[str, str]:
    rows = []
    for index, segment in enumerate(cut.segments, start=1):
        rows.append(
            {
                "clip": index,
                "source_in_tc": timecode(segment.source_in, cut.rate),
                "source_out_tc": timecode(segment.source_out, cut.rate),
                "source_in_s": f"{float(frames_to_seconds(segment.source_in, cut.rate)):.3f}",
                "source_out_s": f"{float(frames_to_seconds(segment.source_out, cut.rate)):.3f}",
                "frames": segment.frames,
                "output_in_tc": timecode(segment.record_in, cut.rate),
                "output_out_tc": timecode(segment.record_out, cut.rate),
                "note": segment.note,
            }
        )
    removed = []
    cursor = 0
    for segment in cut.segments:
        if segment.source_in > cursor:
            removed.append((cursor, segment.source_in))
        cursor = segment.source_out
    if cut.duration_frames is not None and cursor < cut.duration_frames:
        removed.append((cursor, cut.duration_frames))
    md = [
        f"# Cut sheet: {cut.name}",
        "",
        f"Source: `{cut.source.name}` at {float(cut.rate):.3f} fps, {cut.width}x{cut.height}.",
        f"Kept {len(cut.segments)} clip(s), {clock(cut.total_frames, cut.rate)} total"
        + (f"; removed {clock(sum(b - a for a, b in removed), cut.rate)} in {len(removed)} range(s)." if removed else "."),
        "",
        "Timecodes are non-drop-frame, counted at the integer timebase, starting at 00:00:00:00 in the source.",
        "Work on a copy. In an editor without timeline import, split the source at each source in and out point,",
        "delete the ranges listed under Removed, then play every join with sound before trusting it.",
        "",
        "## Kept clips",
        "",
        "| Clip | Source in | Source out | Length | Output in | Output out | Note |",
        "|---:|---|---|---:|---|---|---|",
    ]
    for row in rows:
        md.append(
            f"| {row['clip']} | {row['source_in_tc']} ({row['source_in_s']}s) | {row['source_out_tc']} ({row['source_out_s']}s) | "
            f"{clock(row['frames'], cut.rate)} | {row['output_in_tc']} | {row['output_out_tc']} | {row['note']} |"
        )
    md += ["", "## Removed ranges (source time)", ""]
    if removed:
        md += ["| Removed in | Removed out | Length |", "|---|---|---:|"]
        for first, last in removed:
            md.append(f"| {timecode(first, cut.rate)} ({float(frames_to_seconds(first, cut.rate)):.3f}s) | {timecode(last, cut.rate)} ({float(frames_to_seconds(last, cut.rate)):.3f}s) | {clock(last - first, cut.rate)} |")
    else:
        md.append("Nothing was removed inside the known source duration.")
    if cut.markers:
        md += ["", "## Markers", "", "| Source time | Output time | Name | Note |", "|---|---|---|---|"]
        for marker in cut.markers:
            record = _record_frame(cut, marker.source_frame)
            out_tc = timecode(record, cut.rate) if record is not None else "removed"
            md.append(f"| {timecode(marker.source_frame, cut.rate)} | {out_tc} | {marker.name} | {marker.note} |")
    if cut.warnings:
        md += ["", "## Warnings", ""] + [f"- {warning}" for warning in cut.warnings]
    md.append("")
    csv_lines = []
    writer_target = _CsvBuffer(csv_lines)
    writer = csv.DictWriter(writer_target, fieldnames=list(rows[0].keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return "\n".join(md), "".join(csv_lines)


class _CsvBuffer:
    def __init__(self, lines: list[str]) -> None:
        self.lines = lines

    def write(self, text: str) -> None:
        self.lines.append(text)


# ---------------------------------------------------------------- orchestration


def summary(cut: CutList, written: dict[str, Path]) -> dict:
    return {
        "tool": "cut_list_to_timeline",
        "toolVersion": TOOL_VERSION,
        "name": cut.name,
        "source": str(cut.source),
        "fps": f"{cut.rate.numerator}/{cut.rate.denominator}",
        "frameSize": f"{cut.width}x{cut.height}",
        "clips": len(cut.segments),
        "keptFrames": cut.total_frames,
        "keptSeconds": round(float(frames_to_seconds(cut.total_frames, cut.rate)), 3),
        "sourceSeconds": round(float(frames_to_seconds(cut.duration_frames, cut.rate)), 3) if cut.duration_frames is not None else None,
        "markers": len(cut.markers),
        "markersOutsideKeptRanges": sum(1 for marker in cut.markers if _record_frame(cut, marker.source_frame) is None),
        "files": {kind: str(path) for kind, path in written.items()},
        "sha256": {kind: hashlib.sha256(path.read_bytes()).hexdigest() for kind, path in written.items()},
        "warnings": list(cut.warnings),
        "notRendered": "These files describe an edit. Open them in the editor and play every join before trusting them.",
    }


def validate_with_dtd(fcpxml_path: Path, dtd: Path) -> str:
    xmllint = shutil.which("xmllint")
    if xmllint is None:
        return "skipped: xmllint not installed"
    if not dtd.is_file():
        return f"skipped: DTD not found at {dtd}"
    # xmllint reads the DTD argument as a URI, so a path with spaces (Apple's own
    # Final Cut Pro.app bundle) fails to load. Validate against a plain-named copy.
    import tempfile

    with tempfile.TemporaryDirectory() as scratch:
        copied = Path(scratch) / "fcpxml.dtd"
        shutil.copyfile(dtd, copied)
        result = subprocess.run(
            [xmllint, "--noout", "--dtdvalid", str(copied), str(fcpxml_path)],
            capture_output=True, text=True, timeout=60, check=False,
        )
    return "valid against " + dtd.name if result.returncode == 0 else "INVALID: " + (result.stderr.strip() or result.stdout.strip())[:1000]


def export(cut: CutList, out_dir: Path, formats: tuple[str, ...], overwrite: bool, fcpxml_version: str) -> dict[str, Path]:
    out_dir = out_dir.expanduser().resolve()
    if out_dir == Path(out_dir.anchor) or out_dir == PACK_ROOT or out_dir.is_relative_to(PACK_ROOT):
        raise CutListError("choose an output folder outside the pack itself, for example your private project folder")
    if out_dir.exists() and (not out_dir.is_dir() or out_dir.is_symlink()):
        raise CutListError("output path must be a real folder or a new path")
    stem = re.sub(r"[^A-Za-z0-9._ -]+", "", cut.name).strip() or cut.source.stem
    targets = {
        "fcpxml": out_dir / f"{stem}.fcpxml",
        "xmeml": out_dir / f"{stem}.premiere.xml",
        "edl": out_dir / f"{stem}.edl",
        "sheet": out_dir / f"{stem}.cut-sheet.md",
        "sheet_csv": out_dir / f"{stem}.cut-sheet.csv",
        "summary": out_dir / f"{stem}.summary.json",
    }
    wanted = [kind for kind in targets if kind.split("_")[0] in formats or kind == "summary"]
    for kind in wanted:
        if targets[kind].exists() and not overwrite:
            raise CutListError(f"refusing to overwrite {targets[kind]}; add --overwrite after reviewing it")
        if targets[kind].is_symlink():
            raise CutListError(f"refusing to write through a link: {targets[kind]}")
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    if "fcpxml" in formats:
        targets["fcpxml"].write_text(write_fcpxml(cut, fcpxml_version), encoding="utf-8")
        written["fcpxml"] = targets["fcpxml"]
    if "xmeml" in formats:
        targets["xmeml"].write_text(write_xmeml(cut), encoding="utf-8")
        written["xmeml"] = targets["xmeml"]
    if "edl" in formats:
        targets["edl"].write_text(write_edl(cut), encoding="utf-8")
        written["edl"] = targets["edl"]
    if "sheet" in formats:
        md, csv_text = write_sheet(cut)
        targets["sheet"].write_text(md, encoding="utf-8")
        targets["sheet_csv"].write_text(csv_text, encoding="utf-8")
        written["sheet"] = targets["sheet"]
        written["sheet_csv"] = targets["sheet_csv"]
    for path in written.values():
        ET.fromstring(path.read_bytes()) if path.suffix in {".fcpxml", ".xml"} else None
    report = summary(cut, written)
    targets["summary"].write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    written["summary"] = targets["summary"]
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cut_list", type=Path, help="JSON cut list (see examples/example-cut-list.json)")
    parser.add_argument("--out-dir", type=Path, required=True, help="private output folder, outside the pack")
    parser.add_argument("--formats", default="fcpxml,xmeml,edl,sheet", help="comma list from: fcpxml, xmeml, edl, sheet")
    parser.add_argument("--fcpxml-version", default="1.11", help="FCPXML version attribute to write (default 1.11)")
    parser.add_argument("--probe", action="store_true", help="read fps, size, duration and audio facts from the source with ffprobe")
    parser.add_argument("--overwrite", action="store_true", help="replace existing output files after reviewing them")
    parser.add_argument("--validate-dtd", type=Path, help="optional Apple FCPXML DTD path; validates the written FCPXML with xmllint")
    args = parser.parse_args(argv)
    formats = tuple(part.strip() for part in args.formats.split(",") if part.strip())
    unknown = [part for part in formats if part not in FORMATS]
    if unknown or not formats:
        parser.error(f"unknown format(s): {', '.join(unknown) or 'none given'}; choose from {', '.join(FORMATS)}")
    try:
        cut = load_cut_list(args.cut_list.expanduser().resolve(), probe=args.probe)
        written = export(cut, args.out_dir, formats, args.overwrite, args.fcpxml_version)
    except CutListError as error:
        print(f"ERROR: {error}")
        return 1
    print(f"{cut.name}: {len(cut.segments)} clip(s), {clock(cut.total_frames, cut.rate)} kept at {float(cut.rate):.3f} fps")
    for kind, path in written.items():
        print(f"  {kind:9s} {path}")
    if args.validate_dtd and "fcpxml" in written:
        print(f"  DTD check {validate_with_dtd(written['fcpxml'], args.validate_dtd.expanduser())}")
    for warning in cut.warnings:
        print(f"WARNING: {warning}")
    print("Import into the editor, relink the source if asked, then play every join with sound.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
