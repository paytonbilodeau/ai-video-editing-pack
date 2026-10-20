"""Offline fake-API tests. Never imports or controls Resolve."""

import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import resolve_audio_profile as profile


class FakeClip:
    def __init__(self, mismatch=False):
        self.voice = {"isEnabled": False, "amount": 0}
        self.properties = {}
        self.mismatch = mismatch

    def GetVoiceIsolationState(self):
        return dict(self.voice)

    def SetVoiceIsolationState(self, state):
        self.voice = dict(state)
        return True

    def GetProperty(self, key):
        if self.mismatch and key == "AudioDialogueLevelerOutputGain" and key in self.properties:
            return 1
        return self.properties.get(key)

    def SetProperty(self, key, value):
        self.properties[key] = value
        return True


class FakeTimeline:
    def __init__(self, project, name, unique_id, clips=None):
        self.project = project
        self.name = name
        self.unique_id = unique_id
        self.clips = clips or [FakeClip()]
        self.track_voice = {"isEnabled": True, "amount": 50}
        self.duplicate_calls = 0

    def GetName(self):
        return self.name

    def GetUniqueId(self):
        return self.unique_id

    def GetTrackCount(self, kind):
        return 1 if kind == "audio" else 0

    def GetItemListInTrack(self, kind, track):
        return self.clips if kind == "audio" and track == 1 else []

    def GetVoiceIsolationState(self, track):
        return dict(self.track_voice)

    def SetVoiceIsolationState(self, track, state):
        self.track_voice = dict(state)
        return True

    def DuplicateTimeline(self, name):
        self.duplicate_calls += 1
        clips = [FakeClip(mismatch=clip.mismatch) for clip in self.clips]
        duplicate = FakeTimeline(self.project, name, "copy-id", clips)
        self.project.timelines.append(duplicate)
        return duplicate


class FakeProject:
    def __init__(self, name="Expected Project", mismatch=False):
        self.name = name
        self.timelines = []
        original = FakeTimeline(self, "Expected Timeline", "original-id", [FakeClip(mismatch)])
        self.timelines.append(original)
        self.current = original

    def GetName(self):
        return self.name

    def GetUniqueId(self):
        return "project-id"

    def GetCurrentTimeline(self):
        return self.current

    def SetCurrentTimeline(self, timeline):
        self.current = timeline
        return True

    def GetTimelineCount(self):
        return len(self.timelines)

    def GetTimelineByIndex(self, index):
        return self.timelines[index - 1]


class FakeManager:
    def __init__(self, project):
        self.project = project
        self.save_calls = 0

    def GetCurrentProject(self):
        return self.project

    def SaveProject(self):
        self.save_calls += 1
        return True


class FakeResolve:
    DIALOGUE_LEVELER_MODE_MORE_LIFT_FOR_LOW_LEVELS = "more-lift"
    DIALOGUE_LEVELER_MODE_OPTIMIZE_MODERATE_LEVELS = "moderate"

    def __init__(self, project=None):
        self.project = project or FakeProject()
        self.manager = FakeManager(self.project)

    def GetProjectManager(self):
        return self.manager


class ResolveAudioProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def args(self, **changes):
        values = dict(
            project="Expected Project", timeline="Expected Timeline",
            profile="Shotgun35", track=1, receipt=str(self.root / "receipt.json"),
            track_fx_reviewed=False, apply=False,
        )
        values.update(changes)
        return argparse.Namespace(**values)

    def test_profile_values_are_exact_and_do_not_claim_unimplemented_processing(self):
        self.assertIn(str(Path(profile.__file__).resolve().parent), sys.path)
        self.assertIs(profile.resolve_control, sys.modules["resolve_control"])
        self.assertEqual(profile.PROFILES, {
            "NoMic55": (55, "DIALOGUE_LEVELER_MODE_MORE_LIFT_FOR_LOW_LEVELS"),
            "Wireless25": (25, "DIALOGUE_LEVELER_MODE_OPTIMIZE_MODERATE_LEVELS"),
            "Shotgun35": (35, "DIALOGUE_LEVELER_MODE_OPTIMIZE_MODERATE_LEVELS"),
            "Dynamic15": (15, "DIALOGUE_LEVELER_MODE_OPTIMIZE_MODERATE_LEVELS"),
        })
        properties = profile.property_plan(FakeResolve(), profile.PROFILES["NoMic55"][1])
        self.assertEqual(properties["AudioDialogueLevelerMode"], "more-lift")
        self.assertFalse(any(name.lower() in str(properties).lower()
                             for name in ("eq", "compress", "breath")))

    def test_inspect_only_never_duplicates_or_sets_properties(self):
        resolve = FakeResolve()
        original = resolve.project.current
        result = profile.apply_profile(resolve, self.args())
        self.assertEqual(result["status"], "inspected")
        self.assertEqual(original.duplicate_calls, 0)
        self.assertEqual(original.clips[0].properties, {})
        self.assertEqual(resolve.manager.save_calls, 0)
        self.assertEqual(resolve.project.current, original)

    def test_apply_requires_review_and_exact_current_names(self):
        with self.assertRaisesRegex(RuntimeError, "track leveler"):
            profile.validate_request(self.args(apply=True))
        for field, value, message in [
            ("project", "Wrong", "project"),
            ("timeline", "Wrong", "timeline"),
        ]:
            args = self.args(receipt=str(self.root / f"{field}.json"), **{field: value})
            with self.subTest(field=field), self.assertRaisesRegex(RuntimeError, message):
                profile.apply_profile(FakeResolve(), args)

    def test_apply_duplicates_and_verifies_supported_settings(self):
        resolve = FakeResolve()
        original = resolve.project.current
        result = profile.apply_profile(
            resolve, self.args(apply=True, track_fx_reviewed=True)
        )
        copy = resolve.project.current
        self.assertEqual(result["status"], "applied")
        self.assertEqual(copy.GetName(), "Expected Timeline - Shotgun35 audio")
        self.assertEqual(original.duplicate_calls, 1)
        self.assertEqual(copy.track_voice, {"isEnabled": False, "amount": 0})
        self.assertEqual(copy.clips[0].voice, {"isEnabled": True, "amount": 35})
        self.assertEqual(copy.clips[0].properties, {
            "AudioDialogueLevelerEnabled": True,
            "AudioDialogueLevelerMode": "moderate",
            "AudioDialogueLevelerReduceLoudDialogue": True,
            "AudioDialogueLevelerLiftSoftDialogue": True,
            "AudioDialogueLevelerBackgroundReduction": False,
            "AudioDialogueLevelerOutputGain": 0,
        })
        self.assertEqual(resolve.manager.save_calls, 2)

    def test_existing_copy_fails_idempotently_before_saving_or_duplication(self):
        resolve = FakeResolve()
        original = resolve.project.current
        resolve.project.timelines.append(FakeTimeline(
            resolve.project, "Expected Timeline - Shotgun35 audio", "existing-id"
        ))
        with self.assertRaisesRegex(RuntimeError, "existing profile timeline"):
            profile.apply_profile(resolve, self.args(apply=True, track_fx_reviewed=True))
        self.assertEqual(original.duplicate_calls, 0)
        self.assertEqual(resolve.manager.save_calls, 0)
        self.assertEqual(resolve.project.current, original)

    def test_readback_failure_restores_original_active_timeline(self):
        resolve = FakeResolve(FakeProject(mismatch=True))
        original = resolve.project.current
        with self.assertRaisesRegex(RuntimeError, "readback mismatch"):
            profile.apply_profile(resolve, self.args(apply=True, track_fx_reviewed=True))
        self.assertEqual(resolve.project.current, original)
        receipt = json.loads((self.root / "receipt.json").read_text())
        self.assertEqual(receipt["status"], "failed")
        self.assertTrue(receipt["original_timeline_restored"])
        self.assertTrue(receipt["failed_copy_retained"])


if __name__ == "__main__":
    unittest.main()
