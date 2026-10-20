#!/usr/bin/env python3
"""Small native Resolve 21.1 helper. Run with the bundled ResolvePython.

doctor is read-only. smoke-test creates a NEW scratch project and renders at
most 60 seconds; it never changes source media or deletes projects/render jobs.
Save open work first. Resolve Studio must be activated, running, and configured
for External scripting: Local. Only the installed documented API is used.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time
from fractions import Fraction

INTERPRETER = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/ResolvePython"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def connect():
    try:
        import DaVinciResolveScript
    except ImportError as exc:
        raise RuntimeError(f"Use Resolve 21.1's bundled interpreter: {INTERPRETER}") from exc
    resolve = DaVinciResolveScript.scriptapp("Resolve")
    require(resolve is not None,
            "Resolve is unavailable. Activate Studio, finish launching it, and set External scripting to Local.")
    require("studio" in str(resolve.GetProductName()).lower(),
            "This helper requires activated DaVinci Resolve Studio for external scripting.")
    return resolve


def doctor(resolve):
    project = resolve.GetProjectManager().GetCurrentProject()
    formats = project.GetRenderFormats() if project else None
    return {
        "status": "connected", "read_only": True,
        "product": resolve.GetProductName(), "version": resolve.GetVersionString(),
        "current_project": project.GetName() if project else None,
        "keyboard_preset": resolve.GetCurrentKeyboardPreset(),
        "keyboard_presets": resolve.GetKeyboardPresetList(),
        "render_formats": formats,
        "render_codecs": {ext: project.GetRenderCodecs(ext)
                          for ext in sorted(set(formats.values()))} if formats else None,
        "audio_formats": project.GetAudioRenderFormats() if project else None,
        "note": "Formats require an open project; doctor never creates one.",
    }


def validate_request(args):
    require(math.isfinite(args.start) and args.start >= 0, "start must be finite and >= 0 seconds")
    require(math.isfinite(args.duration) and 0 < args.duration <= 60,
            "duration must be finite and in (0, 60] seconds")
    require(math.isfinite(args.timeout) and 1 <= args.timeout <= 3600,
            "timeout must be finite and in [1, 3600] seconds")
    require(bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _.-]{0,99}", args.project_name)),
            "project-name must be 1-100 plain letters, digits, spaces, underscores, dots or hyphens")
    source = Path(args.input).expanduser().resolve(strict=True)
    require(source.is_file(), "input must be a regular media file")
    output = Path(args.output).expanduser().absolute()
    require(output.suffix.lower() == ".mp4", "output must end with .mp4")
    require(output.resolve() != source, "output must not overwrite input")
    for path in (output, output.with_suffix(".drp"), output.with_suffix(".receipt.json")):
        require(not os.path.lexists(path), f"Refusing existing output or sidecar: {path}")
    require(output.parent.is_dir(), "Create the output directory before running the smoke test")
    return source, output


def frame_range(start, duration, fps, source_frames):
    require(math.isfinite(fps) and fps > 0, "Source FPS is missing or invalid")
    require(math.isfinite(start) and start >= 0, "Invalid source start")
    require(math.isfinite(duration) and 0 < duration <= 60, "Invalid sample duration")
    first = math.floor(start * fps + 0.5)
    count = math.floor(duration * fps + 1e-8)
    require(count >= 1, "Sample is shorter than one source frame")
    require(first + count <= source_frames, "Requested sample extends beyond the source")
    return first, first + count - 1, count


def select_h264(formats, codecs):
    require("mp4" in formats.values(), "This Resolve runtime does not expose MP4 export")
    matches = [(label, codec) for label, codec in codecs.items()
               if "h264" in re.sub(r"[^a-z0-9]", "", label.lower())]
    exact = [(label, codec) for label, codec in matches
             if re.sub(r"[^a-z0-9]", "", label.lower()) == "h264"]
    choices = exact or matches
    require(len(choices) == 1, f"No unambiguous runtime H.264 codec: {codecs}")
    return choices[0][1]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def faststart(path):
    """Confirm the real MP4 moov atom precedes media data, without loading it."""
    size = path.stat().st_size
    with path.open("rb") as stream:
        while stream.tell() + 8 <= size:
            offset = stream.tell()
            length, kind = struct.unpack(">I4s", stream.read(8))
            header_size = 8
            if length == 1:
                extra = stream.read(8)
                if len(extra) != 8:
                    return False
                length = struct.unpack(">Q", extra)[0]
                header_size = 16
            if length == 0:
                length = size - offset
            if length < header_size or offset + length > size:
                return False
            if kind in (b"moov", b"mdat"):
                return kind == b"moov"
            stream.seek(offset + length)
    return False


def verify_output(output, fps, frames):
    require(output.is_file() and output.stat().st_size > 0, "Resolve reported complete without the expected MP4")
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format",
         "-of", "json", str(output)], capture_output=True, text=True, check=True, timeout=180)
    probe = json.loads(result.stdout)
    video = next((s for s in probe["streams"] if s["codec_type"] == "video"), {})
    audio = next((s for s in probe["streams"] if s["codec_type"] == "audio"), {})
    require(video.get("codec_name") == "h264" and
            (video.get("width"), video.get("height")) == (3840, 2160), "Output is not UHD H.264")
    require(abs(float(Fraction(video.get("avg_frame_rate", "0/1"))) - fps) < 0.001,
            "Output frame rate differs from source")
    require(int(video.get("nb_read_frames", -1)) == frames, "Decoded frame count differs from the sample plan")
    require(audio.get("codec_name") == "aac" and int(audio.get("sample_rate", 0)) == 48000,
            "Output audio is not AAC at 48 kHz")
    require(faststart(output), "MP4 is not optimized for progressive playback (moov must precede mdat)")
    subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(output), "-f", "null", "-"],
                   capture_output=True, check=True, timeout=180)
    return {"probe": probe, "full_decode": "passed", "faststart": True, "sha256": sha256(output)}


def restore_previous_page(resolve, previous_page, receipt):
    """Restore only the captured page after the owned scratch project is closed."""
    if previous_page is None:
        receipt["previous_page_restored"] = None
        receipt["page_restore_note"] = "No prior page was available; no page change requested"
        return
    receipt["previous_page_restored"] = False
    require(resolve.OpenPage(previous_page), "Could not restore the prior Resolve page")
    actual = resolve.GetCurrentPage()
    receipt["page_after_restore"] = actual
    require(actual == previous_page, "Restored Resolve page differs from captured prior page")
    receipt["previous_page_restored"] = True


def smoke_test(resolve, args):
    source, output = validate_request(args)
    require(shutil.which("ffprobe") and shutil.which("ffmpeg"),
            "ffprobe and ffmpeg are required for output verification; no dependencies are installed automatically")
    manager = resolve.GetProjectManager()
    require(args.project_name not in manager.GetProjectListInCurrentFolder(), "Refusing an existing project name")
    previous = manager.GetCurrentProject()
    require(previous is None or not previous.IsRenderingInProgress(), "An existing project is rendering; wait first")
    prior_name = previous.GetName() if previous else None
    prior_id = previous.GetUniqueId() if previous else None
    page = resolve.GetCurrentPage()
    prior_page = page if isinstance(page, str) and page else None
    receipt_path, drp = output.with_suffix(".receipt.json"), output.with_suffix(".drp")
    receipt = {"status": "started", "source": str(source), "source_sha256_before": sha256(source),
               "output": str(output), "scratch_project": args.project_name,
               "previous_project": prior_name, "previous_page": prior_page, "requested_start_seconds": args.start,
               "requested_duration_seconds": args.duration, "version": resolve.GetVersionString()}
    with receipt_path.open("x") as stream:
        json.dump(receipt, stream, indent=2)
    project = None
    error = None
    try:
        project = manager.CreateProject(args.project_name)
        require(project is not None, "Resolve refused the new scratch project")
        require(project.GetName() == args.project_name, "Created project identity mismatch")
        receipt["scratch_project_id"] = project.GetUniqueId()
        require(not project.GetRenderJobList(), "New scratch project unexpectedly has render jobs")
        pool = project.GetMediaPool()
        # Resolve 21.1's runtime accepts plain paths for ordinary movie files;
        # its typed FilePath dictionaries are for image-sequence imports.
        clips = pool.ImportMedia([str(source)])
        require(clips and len(clips) == 1, "Expected exactly one imported source clip")
        props = clips[0].GetClipProperty()
        fps = float(props["FPS"])
        first, last, count = frame_range(args.start, args.duration, fps, int(props["Frames"]))
        require(int(props.get("Audio Ch", "0")) > 0, "The source has no audio channels for the AAC smoke test")
        settings = {"timelineFrameRate": str(fps), "timelineResolutionWidth": "3840",
                    "timelineResolutionHeight": "2160", "timelineInputResMismatchBehavior": "scaleToFit"}
        require(project.SetSettings(settings), "Resolve refused source-FPS/UHD project settings")
        timeline = pool.CreateTimelineFromClips("Smoke test", [
            # 21.1 native range probe: [30, 60) produces exactly 30 frames.
            {"mediaPoolItem": clips[0], "startFrame": first, "endFrame": last + 1}])
        require(timeline is not None and project.SetCurrentTimeline(timeline), "Could not create/select the sample timeline")
        items = timeline.GetItemListInTrack("video", 1)
        require(len(items) == 1 and int(items[0].GetDuration()) == count,
                "Timeline sample length differs from requested source frames")
        codec = select_h264(project.GetRenderFormats(), project.GetRenderCodecs("mp4"))
        require(project.SetCurrentRenderFormatAndCodec("mp4", codec), "Resolve refused runtime MP4/H.264 codec")
        require(project.SetCurrentRenderMode(1), "Resolve refused single-clip render mode")
        render = {"SelectAllFrames": True, "TargetDir": str(output.parent), "CustomName": output.stem,
                  "UseUniqueFilenames": False,
                  "ExportVideo": True, "ExportAudio": True, "FormatWidth": 3840, "FormatHeight": 2160,
                  "FrameRate": fps, "PixelAspectRatio": "square", "VideoQuality": 0,
                  "AudioCodec": "aac", "AudioSampleRate": 48000, "NetworkOptimization": True,
                  "DataBurnIn": "None"}
        require(project.SetRenderSettings(render), "Resolve refused documented MP4 render settings")
        job = project.AddRenderJob()
        require(isinstance(job, str) and bool(job), "Resolve did not return an owned render job ID")
        jobs = project.GetRenderJobList()
        require(len(jobs) == 1 and jobs[0].get("JobId") == job, "Scratch queue ownership mismatch")
        receipt.update({"fps": fps, "first_source_frame": first, "last_source_frame_inclusive": last,
                        "expected_frames": count, "actual_sample_seconds": count / fps,
                        "runtime_codec_id": codec, "render_requested": render, "render_job_id": job,
                        "render_job_readback": jobs[0]})
        queued = jobs[0]
        require((queued.get("FormatWidth"), queued.get("FormatHeight")) == (3840, 2160)
                and queued.get("AudioSampleRate") == 48000 and queued.get("NetworkOptimization") is True,
                "Queued job readback does not confirm UHD, 48 kHz audio and network optimization")
        require(Path(queued.get("TargetDir", "")).resolve() == output.parent.resolve()
                and queued.get("OutputFilename") == output.name,
                "Queued output filename/directory differs from the requested MP4")
        current = manager.GetCurrentProject()
        require(current is not None and current.GetUniqueId() == project.GetUniqueId(),
                "The current project changed before render; refusing to save/start")
        require(manager.SaveProject(), "Could not save scratch project before render")
        require(project.StartRendering([job], False), "Resolve refused to start the owned render job")
        deadline = time.monotonic() + args.timeout
        last_status = None
        while True:
            status = project.GetRenderJobStatus(job)
            receipt["render_status"] = status
            if status != last_status:
                print(json.dumps({"job_id": job, **status}), file=sys.stderr, flush=True)
                last_status = status
            state = status.get("JobStatus")
            if state == "Complete":
                break
            require(state not in {"Failed", "Cancelled", "Background Render Cancelled", "Remote Render Cancelled"},
                    f"Owned render did not complete: {status}")
            require(time.monotonic() < deadline,
                    "Render wait timed out. No global stop was issued; inspect this job before another run.")
            time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))
        receipt["output_verification"] = verify_output(output, fps, count)
        receipt["status"] = "validated"
    except Exception as exc:
        error = str(exc)
        receipt.update({"status": "failed", "error": error})
    finally:
        cleanup_errors = []
        try:
            receipt["source_sha256_after"] = sha256(source)
            require(receipt["source_sha256_after"] == receipt["source_sha256_before"], "Source changed during smoke test")
        except Exception as exc:
            cleanup_errors.append(str(exc))
        try:
            current = manager.GetCurrentProject()
            owned = project is not None and current is not None and current.GetUniqueId() == project.GetUniqueId()
            if owned and not project.IsRenderingInProgress():
                try:
                    require(manager.SaveProject(), "Could not save scratch project")
                    require(not drp.exists() and manager.ExportProject(args.project_name, str(drp), False),
                            "Could not export new scratch .drp")
                    require(drp.is_file() and drp.stat().st_size > 0, "Export returned without a .drp file")
                    receipt["project_export"] = str(drp)
                except Exception as exc:
                    cleanup_errors.append(str(exc))
                # A failed export must not strand the user in the scratch project.
                restored = manager.LoadProject(prior_name) if prior_name else manager.CloseProject(project)
                require(restored is not None and restored is not False, "Could not restore the prior project state")
                if prior_name:
                    require(restored.GetUniqueId() == prior_id, "Restored project identity mismatch")
                receipt["previous_project_restored"] = True
                restore_previous_page(resolve, prior_page, receipt)
            elif project is not None:
                receipt["previous_project_restored"] = False
                raise RuntimeError("Scratch render remains active or the user switched projects; prior project was not restored")
        except Exception as exc:
            cleanup_errors.append(str(exc))
        if cleanup_errors:
            error = "; ".join(([error] if error else []) + cleanup_errors)
            receipt.update({"status": "failed", "error": error})
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    require(error is None, f"{error} Receipt: {receipt_path}")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Read-only connection, project, keyboard and format inventory")
    smoke = commands.add_parser("smoke-test", help="Create a NEW scratch project and validate a <=60-second MP4")
    for name in ("input", "output", "project-name"):
        smoke.add_argument("--" + name, required=True)
    smoke.add_argument("--start", type=float, required=True, help="Source-relative seconds")
    smoke.add_argument("--duration", type=float, required=True)
    smoke.add_argument("--timeout", type=float, default=900, help="Maximum render wait in seconds")
    args = parser.parse_args()
    try:
        if args.command == "smoke-test":
            validate_request(args)  # Refuse invalid requests before importing/calling Resolve.
        resolve = connect()
        result = doctor(resolve) if args.command == "doctor" else smoke_test(resolve, args)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
