#!/usr/bin/env python3
"""Waterfall stage 1: transcribe a long recording with word-level timestamps.

Part of the content-waterfall skill (one capture -> long + mids + shorts + text).
Runs local mlx-whisper on the Apple GPU. Local inference; model files may download if not already available.

Requires the workspace venv python3 (it has mlx_whisper):

    python3 tools/waterfall_transcribe.py \
        /path/to/recording.mp4 project/waterfall/2026-08-15-topic/transcript/

Outputs into the given directory:
    transcript.json   full whisper result (segments + word timestamps)
    transcript.txt    plain text with [HH:MM:SS] stamps every ~30s (for the content map)
    transcript.vtt    cue-level VTT for the full recording
    transcript.srt    same content as SRT

Clip caption mode (run AFTER the content map is approved) rebases word timings
to each clip's start. Real *.words.json sidecars drive strict word captions;
VTT remains a subtitle file:

    python3 tools/waterfall_transcribe.py \
        --emit-clip-vtt project/waterfall/<proj>/map/content-map.json \
        project/waterfall/<proj>/transcript/
"""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_MODEL = "mlx-community/whisper-large-v3-turbo"


def fmt_ts(seconds: float, sep: str = ".") -> str:
    total_ms = round(max(0, seconds) * 1000)
    h, remainder = divmod(total_ms, 3600000)
    m, remainder = divmod(remainder, 60000)
    sec, ms = divmod(remainder, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d}{sep}{ms:03d}"


def write_vtt(segments, out_path: Path, offset: float = 0.0, clip_end: float = None):
    lines = ["WEBVTT", ""]
    for seg in segments:
        start, end = seg["start"], seg["end"]
        if clip_end is not None and (end <= offset or start >= clip_end):
            continue
        text = seg["text"].strip()
        if not text:
            continue
        s = max(start - offset, 0.0)
        e = max(end - offset, 0.0)
        if clip_end is not None:
            e = min(e, clip_end - offset)
        if e <= s:
            continue
        lines.append(f"{fmt_ts(s)} --> {fmt_ts(e)}")
        lines.append(text)
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_srt(segments, out_path: Path):
    lines = []
    for i, seg in enumerate(s for s in segments if s["text"].strip()):
        lines.append(str(i + 1))
        lines.append(f"{fmt_ts(seg['start'], sep=',')} --> {fmt_ts(seg['end'], sep=',')}")
        lines.append(seg["text"].strip())
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_plain(segments, out_path: Path, stamp_every: int = 30):
    out, buf = [], []
    last_stamp = -10**9
    for seg in segments:
        text = seg["text"].strip()
        if not text:
            continue
        if seg["start"] - last_stamp >= stamp_every:
            if buf:
                out.append(" ".join(buf))
                buf = []
            h = int(seg["start"] // 3600)
            m = int((seg["start"] % 3600) // 60)
            s = int(seg["start"] % 60)
            out.append(f"[{h:02d}:{m:02d}:{s:02d}]")
            last_stamp = seg["start"]
        buf.append(text)
    if buf:
        out.append(" ".join(buf))
    out_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def transcribe(media: Path, out_dir: Path, model: str, language: str):
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError("Use a fresh transcript directory")
    try:
        import mlx_whisper
    except ImportError:
        sys.exit(
            "mlx_whisper not available in this Python. "
            "Run with the workspace venv python3 with mlx-whisper available"
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Transcribing {media.name} with {model} (first run may download/load the model) ...")
    result = mlx_whisper.transcribe(
        str(media),
        path_or_hf_repo=model,
        language=language,
        word_timestamps=True,
    )
    segments = [
        {
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"],
            "words": [
                {"start": w["start"], "end": w["end"], "word": w["word"]}
                for w in seg.get("words", [])
            ],
        }
        for seg in result["segments"]
    ]
    (out_dir / "transcript.json").write_text(
        json.dumps({"language": result.get("language", language), "segments": segments},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    write_plain(segments, out_dir / "transcript.txt")
    write_vtt(segments, out_dir / "transcript.vtt")
    write_srt(segments, out_dir / "transcript.srt")
    total = segments[-1]["end"] if segments else 0
    words = sum(len(s["text"].split()) for s in segments)
    print(f"Done: {len(segments)} segments, ~{words} words, {total/60:.1f} min")
    print(f"Outputs in {out_dir}/: transcript.json .txt .vtt .srt")


def emit_clip_vtts(map_path: Path, transcript_dir: Path):
    """Write reviewed contiguous clip cues and real word JSON; never interpolate."""
    import re
    from video_word_timing import load_word_timing
    cmap = json.loads(map_path.read_text(encoding="utf-8"))
    words = load_word_timing(transcript_dir / "transcript.json")["words"]
    planned = []
    used = set()
    for kind in ("mids", "shorts"):
        for clip in cmap.get(kind, []):
            cid = str(clip["id"])
            if not re.fullmatch(r"[A-Za-z0-9_-]+", cid) or cid in used:
                raise ValueError("Clip IDs must be unique plain names")
            used.add(cid)
            start, end = float(clip["start"]), float(clip["end"])
            if not 0 <= start < end:
                raise ValueError("Invalid clip interval")
            selected=[]
            for w in words:
                if w["end"] <= start or w["start"] >= end:continue
                if w["start"] < start or w["end"] > end:
                    raise ValueError("Clip boundary crosses a word; review the source and adjust the clip")
                selected.append({"word":w["word"],"start":w["start"]-start,"end":w["end"]-start})
            if not selected:raise ValueError("Clip contains no verified word cues")
            out=transcript_dir/f"{cid}.vtt";wordout=transcript_dir/f"{cid}.words.json"
            if any(p.exists() or p.is_symlink() for p in (out,wordout)):
                raise FileExistsError("Clip sidecar already exists; preserve prior work")
            planned.append((out,wordout,selected))
    for out,wordout,selected in planned:
        write_vtt([dict(w,text=w["word"]) for w in selected],out)
        wordout.write_text(json.dumps({"words":selected},indent=2)+"\n")
        print(f"Wrote {out.name} and {wordout.name}; real source words rebased only")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Media file to transcribe, or content-map.json with --emit-clip-vtt")
    p.add_argument("output_dir", help="Transcript directory")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--language", default="en", help="Pinned to en by default (auto-detect on dead air returns junk)")
    p.add_argument("--emit-clip-vtt", action="store_true",
                   help="Treat input as content-map.json; write per-clip rebased VTTs")
    args = p.parse_args()

    src = Path(args.input).expanduser()
    out_dir = Path(args.output_dir).expanduser()
    if not src.exists():
        sys.exit(f"Not found: {src}")
    if args.emit_clip_vtt:
        emit_clip_vtts(src, out_dir)
    else:
        transcribe(src, out_dir, args.model, args.language)


if __name__ == "__main__":
    main()
