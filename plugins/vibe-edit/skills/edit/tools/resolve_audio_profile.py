#!/usr/bin/env python3
"""Inspect or apply a verified native Resolve dialogue profile on a timeline copy.

Run with Resolve 21.1's bundled ResolvePython. The default is inspect-only.
Applying always saves the original timeline, duplicates it, and changes only
the named audio track on the copy. EQ, compression and de-breath are not set.
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys

HELPER_DIR = str(Path(__file__).resolve().parent)
if HELPER_DIR not in sys.path:
    sys.path.insert(0, HELPER_DIR)
import resolve_control


PROFILES = {
    "NoMic55": (55, "DIALOGUE_LEVELER_MODE_MORE_LIFT_FOR_LOW_LEVELS"),
    "Wireless25": (25, "DIALOGUE_LEVELER_MODE_OPTIMIZE_MODERATE_LEVELS"),
    "Shotgun35": (35, "DIALOGUE_LEVELER_MODE_OPTIMIZE_MODERATE_LEVELS"),
    "Dynamic15": (15, "DIALOGUE_LEVELER_MODE_OPTIMIZE_MODERATE_LEVELS"),
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def validate_request(args):
    for label, value in (("project", args.project), ("timeline", args.timeline)):
        require(bool(re.fullmatch(r"[^\r\n]{1,150}", value or "")),
                f"{label} must be an exact non-empty name without line breaks")
    require(args.profile in PROFILES, f"Unknown profile: {args.profile}")
    require(args.track >= 1, "track must be a one-based positive integer")
    if args.apply:
        require(args.track_fx_reviewed,
                "--apply requires --track-fx-reviewed after verifying the track leveler is off")
    receipt = Path(args.receipt).expanduser().absolute()
    require(receipt.suffix.lower() == ".json", "receipt must end with .json")
    require(receipt.parent.is_dir(), "Create the receipt directory first")
    require(not os.path.lexists(receipt), f"Refusing existing receipt: {receipt}")
    return receipt


def timeline_names(project):
    return [project.GetTimelineByIndex(index).GetName()
            for index in range(1, project.GetTimelineCount() + 1)]


def property_plan(resolve, mode_name):
    require(hasattr(resolve, mode_name), f"Resolve runtime is missing {mode_name}")
    return {
        "AudioDialogueLevelerEnabled": True,
        "AudioDialogueLevelerMode": getattr(resolve, mode_name),
        "AudioDialogueLevelerReduceLoudDialogue": True,
        "AudioDialogueLevelerLiftSoftDialogue": True,
        "AudioDialogueLevelerBackgroundReduction": False,
        "AudioDialogueLevelerOutputGain": 0,
    }


def voice_matches(actual, expected):
    return (isinstance(actual, dict)
            and actual.get("isEnabled") is expected["isEnabled"]
            and actual.get("amount") == expected["amount"])


def inspect_timeline(timeline, track, properties):
    require(track <= timeline.GetTrackCount("audio"), "Requested audio track does not exist")
    clips = timeline.GetItemListInTrack("audio", track)
    require(clips, "Requested audio track contains no timeline items")
    return clips, {
        "track_voice_isolation": timeline.GetVoiceIsolationState(track),
        "clips": [{
            "index": index,
            "voice_isolation": clip.GetVoiceIsolationState(),
            "dialogue_leveler": {key: clip.GetProperty(key) for key in properties},
        } for index, clip in enumerate(clips, 1)],
    }


def apply_profile(resolve, args):
    receipt_path = validate_request(args)
    receipt = {
        "status": "started",
        "mode": "apply" if args.apply else "inspect_only",
        "expected_project": args.project,
        "expected_timeline": args.timeline,
        "profile": args.profile,
        "audio_track": args.track,
        "track_fx_reviewed": args.track_fx_reviewed,
        "unsupported": ["track_dialogue_leveler_api", "eq", "compression", "debreath"],
    }
    with receipt_path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)

    manager = resolve.GetProjectManager()
    project = None
    original = None
    duplicate = None
    try:
        project = manager.GetCurrentProject()
        require(project is not None and project.GetName() == args.project,
                "Current project does not match --project exactly")
        original = project.GetCurrentTimeline()
        require(original is not None and original.GetName() == args.timeline,
                "Current timeline does not match --timeline exactly")
        profile_amount, mode_name = PROFILES[args.profile]
        properties = property_plan(resolve, mode_name)
        _, before = inspect_timeline(original, args.track, properties)
        copy_name = f"{args.timeline} - {args.profile} audio"
        existing_names = timeline_names(project)
        receipt.update({
            "project_id": project.GetUniqueId(),
            "original_timeline_id": original.GetUniqueId(),
            "copy_name": copy_name,
            "before": before,
        })

        if not args.apply:
            receipt["status"] = "inspected"
            receipt["copy_name_available"] = copy_name not in existing_names
            return receipt

        require(copy_name not in existing_names, f"Refusing existing profile timeline: {copy_name}")
        require(manager.SaveProject(), "Could not save the original project before duplication")
        duplicate = original.DuplicateTimeline(copy_name)
        require(duplicate is not None and duplicate.GetName() == copy_name,
                "Resolve failed to create the exact dedicated timeline copy")
        require(project.SetCurrentTimeline(duplicate), "Could not activate the dedicated timeline copy")
        require(project.GetCurrentTimeline().GetUniqueId() == duplicate.GetUniqueId(),
                "Dedicated timeline activation readback mismatch")

        clips, _ = inspect_timeline(duplicate, args.track, properties)
        track_state = {"isEnabled": False, "amount": 0}
        require(duplicate.SetVoiceIsolationState(args.track, track_state),
                "Resolve refused to disable track voice isolation")
        require(voice_matches(duplicate.GetVoiceIsolationState(args.track), track_state),
                "Track voice isolation readback mismatch")

        clip_state = {"isEnabled": True, "amount": profile_amount}
        readbacks = []
        for index, clip in enumerate(clips, 1):
            require(clip.SetVoiceIsolationState(clip_state),
                    f"Resolve refused clip {index} voice isolation")
            require(voice_matches(clip.GetVoiceIsolationState(), clip_state),
                    f"Clip {index} voice isolation readback mismatch")
            for key, value in properties.items():
                require(clip.SetProperty(key, value),
                        f"Resolve refused clip {index} property {key}")
                require(clip.GetProperty(key) == value,
                        f"Clip {index} property readback mismatch: {key}")
            readbacks.append({
                "index": index,
                "voice_isolation": clip.GetVoiceIsolationState(),
                "dialogue_leveler": {key: clip.GetProperty(key) for key in properties},
            })
        require(manager.SaveProject(), "Could not save the applied profile timeline")
        receipt.update({
            "status": "applied",
            "copy_timeline_id": duplicate.GetUniqueId(),
            "track_voice_isolation": duplicate.GetVoiceIsolationState(args.track),
            "clip_readbacks": readbacks,
        })
        return receipt
    except Exception as exc:
        error = str(exc)
        receipt.update({"status": "failed", "error": error})
        if args.apply and duplicate is not None and project is not None and original is not None:
            try:
                restored = project.SetCurrentTimeline(original)
                require(restored and project.GetCurrentTimeline().GetUniqueId() == original.GetUniqueId(),
                        "Could not restore the original active timeline")
                receipt["original_timeline_restored"] = True
                receipt["failed_copy_retained"] = duplicate is not None
                require(manager.SaveProject(), "Could not save after restoring the original timeline")
            except Exception as restore_error:
                receipt["original_timeline_restored"] = False
                receipt["restore_error"] = str(restore_error)
        raise RuntimeError(f"{error} Receipt: {receipt_path}") from exc
    finally:
        receipt_path.write_text(json.dumps(receipt, indent=2, default=str) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Exact currently open project name")
    parser.add_argument("--timeline", required=True, help="Exact currently active timeline name")
    parser.add_argument("--profile", choices=sorted(PROFILES), required=True)
    parser.add_argument("--track", type=int, required=True, help="One-based audio track index")
    parser.add_argument("--receipt", required=True, help="New JSON receipt path")
    parser.add_argument("--track-fx-reviewed", action="store_true",
                        help="Confirm the track dialogue leveler was verified off in the UI")
    parser.add_argument("--apply", action="store_true",
                        help="Save, duplicate, activate and modify the dedicated timeline copy")
    args = parser.parse_args()
    try:
        validate_request(args)
        result = apply_profile(resolve_control.connect(), args)
        print(json.dumps(result, indent=2, default=str))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
