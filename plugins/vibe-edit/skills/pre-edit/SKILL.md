---
name: pre-edit
description: Optional local first pass on a flattened talking-head copy with FFmpeg silence cuts, exact cut and protect ranges, optional spoken restart markers, a dry plan reviewed before any render, and a report. Use when the person wants a quick automatic rough pass before real editing or asks about the "cut cut" and "full stop restart" markers. Never a prerequisite for the edit skill.
---

# Pre-edit

Make a conservative automatic first pass on one copied recording: shorten quiet pauses, remove exact ranges the person chose, optionally remove spoken restart markers, and write a new flattened H.264/AAC MP4 plus a report. This is optional and narrower than [edit](../edit/SKILL.md): it never produces an editable timeline, never touches the original, and is not a step the edit skill needs. For editable cuts, use the edit skill or the marker route in [jump_cut_vad_parallel.py](../edit/tools/jump_cut_vad_parallel.py), which writes FCPXML or video from the same markers.

## Procedure

1. **Read first.** The profile in `Vibe Edit Settings/EDITING PROFILE.md` (or `Vibe Editor Settings/` from 5.x) and the working pace in `Vibe Edit Settings/SETUP STATUS.json`; then [core-pre-edit](references/core-pre-edit.md) for the rules, [SYSTEM](references/SYSTEM.md) for safe defaults and report rules, [TOOL ADAPTER](<references/TOOL ADAPTER.md>) for every flag.
2. **Check the machine.** Run [setup_doctor.py](tools/setup_doctor.py) (read-only: Python 3.11+, ffmpeg, ffprobe) and confirm `libx264` in `ffmpeg -hide_banner -encoders`. Explain anything missing and offer the install; the package manager and password prompt stay with the person. Markers need existing `--words-json` or a local Whisper from [requirements-markers.txt](tools/requirements-markers.txt) in a dedicated environment; a model download is the person's choice.
3. **Qualify the source.** A copied, flattened SDR file with one video and one audio stream. HDR, multitrack, multicamera, subtitle-bearing and edit-master media are rejected; offer a flattened copy through the editor. The source is never an output.
4. **Fill the brief.** Complete [PRE-EDIT BRIEF](<templates/PRE-EDIT BRIEF.md>) from known facts; ask only for missing decisions. Add demonstrations, reading holds, music and deliberate pauses as `--protect` ranges in source time.
5. **Dry run.** `python3 tools/video_pre_edit.py "copy.mp4" "copy_preedit.mp4" --dry-run` from this folder (`py -3.11` on Windows). Read `_dry_run_report.md` and `_plan.json`, check words around joins and any long removal, adjust one setting at a time, rerun.
6. **Render from the plan.** Add `--from-plan "copy_preedit_plan.json"`. Markers stay off until chosen; `full stop restart` also needs `--detect-full-stop-restart` and `--confirm-full-restart`. Use `--enhance-audio` only when no existing audio route handles cleanup, and compare before keeping it. Never add `--overwrite` to make an error disappear.
7. **Verify and deliver.** A new file with one video and one audio stream at the planned duration, protected content intact, every flagged cut watched. Use [REVIEW CHECKLIST](<templates/REVIEW CHECKLIST.md>); write [EDIT REPORT](<templates/EDIT REPORT.md>) in the shape of the [example report](<examples/EXAMPLE EDIT REPORT.md>) and [EDITOR HANDOFF](<templates/EDITOR HANDOFF.md>); continue in the edit skill or the person's editor through [editors](../editors/SKILL.md). Log runs in [TEN-RUN EDIT TRACKER](<templates/TEN-RUN EDIT TRACKER.md>); save an [EDIT PROFILE](<templates/EDIT PROFILE.md>) only after repeated reviewed runs.

Offline checks: `python3 -m unittest discover -s tools/tests -p "test_*.py" -v` from this folder; [make_fixture.py](tools/tests/make_fixture.py) builds a six-second synthetic clip when FFmpeg exists. A failed import or a skip is not a pass; report it. SYSTEM.md and TOOL ADAPTER.md still say `tests/` and `INSTALL.md` from the 5.x layout; here the tests live in `tools/tests/` and the install notes are step 2.

## Everything in this folder

| File | Use |
| --- | --- |
| [core-pre-edit](references/core-pre-edit.md) | Rules, markers, limits |
| [SYSTEM](references/SYSTEM.md) | Safe defaults, report and success rules |
| [TOOL ADAPTER](<references/TOOL ADAPTER.md>) | Flags, modes, when to adapt |
| [PRE-EDIT BRIEF](<templates/PRE-EDIT BRIEF.md>) | Brief the assistant fills |
| [EDIT REPORT](<templates/EDIT REPORT.md>) | Report shape per run |
| [EDITOR HANDOFF](<templates/EDITOR HANDOFF.md>) | Handoff to the editor |
| [REVIEW CHECKLIST](<templates/REVIEW CHECKLIST.md>) | Watch-through checklist |
| [EDIT PROFILE](<templates/EDIT PROFILE.md>) | Reviewed settings profile |
| [TEN-RUN EDIT TRACKER](<templates/TEN-RUN EDIT TRACKER.md>) | Measure ten runs |
| [AUDIO COMPARISON](<templates/AUDIO COMPARISON.md>) | Compare audio routes fairly |
| [MANUAL REVIEW AND CLEAN MASTER](<templates/MANUAL REVIEW AND CLEAN MASTER.md>) | Staged review, clean companion |
| [EXAMPLE EDIT REPORT](<examples/EXAMPLE EDIT REPORT.md>) | Filled synthetic report |
| [video_pre_edit.py](tools/video_pre_edit.py) | The pre-edit tool |
| [setup_doctor.py](tools/setup_doctor.py) | Read-only dependency check |
| [requirements-markers.txt](tools/requirements-markers.txt) | Optional Whisper and torch pins |
| [make_fixture.py](tools/tests/make_fixture.py) | Synthetic test clip |
| [test_video_pre_edit.py](tools/tests/test_video_pre_edit.py) | Tool unit tests |
| [test_setup_doctor.py](tools/tests/test_setup_doctor.py) | Doctor unit tests |
| [jump_cut_vad_parallel.py](../edit/tools/jump_cut_vad_parallel.py) | Marker route that keeps cuts editable |
| [cuts-pacing](../edit/references/core/cuts-pacing.md) | Editable cut in the editor instead |

## Scope and honesty

The result is a first pass, never a finished creative edit, and nothing here promises a time saving or a quality outcome. Report what was rendered and verified in this session apart from what the references document. Cuts happen only for a detected pause under the approved threshold, an exact agreed marker, an exact `--cut` range or a rule the person already authorized; a repeated idea is not a bad take. No installation, model download, upload, paid service, publishing or permission change happens without the person's choice. The original recording is preserved, every output is a new file, and a passing fixture does not approve cuts in a real recording.
