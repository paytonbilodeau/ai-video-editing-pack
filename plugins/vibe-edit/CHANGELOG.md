# 6.1.0 · One paste to update, and your colors

- **Update with one pasted line, even from a downloaded folder.** The release post now opens with "Update Vibe Edit to <version> from <link> with hash <sha256> and keep my profile". The update skill downloads the zip, checks its SHA-256 and refuses anything that does not match, swaps the plugin folder in place (the old folder stays until the check passes), reloads and reads back the installed version. Nobody downloads, unzips or sets up again. GitHub installs keep their one-command update.
- **Every change is offered, not imposed.** After an update the skill reads your profile and custom files and, for each change, says whether it improves your setup, is optional, or does not apply to how you edit. Only what you accept is applied; every saved preference stays.
- **Colors and fonts are yours.** One line in the starting profile, the blank profile, the style skill and lesson 5 says how to change them in a sentence, for example "use a black and white palette" or "use my brand colors #xxxxxx and the font Inter". Payton's looks, palette defaults, examples and references are unchanged.
- **Same editing system as 6.0.0.** No editing skill, tool, look or lesson content changed beyond the update route, the offer step, the colors line and the matching wording in the install page, README, FAQ 22 and lessons 8 and 22. FAQ 23 now names the Updates post, the live community category.

Verification and limits: on the build machine, the fetch tool's 13 unit tests, the plugin's Python suites (edit 131, pre-edit 23, editors 23, setup 11, shorts 13) and Node suites (36 and 6, with 5 browser tests skipped) pass, `claude plugin validate` passes, and isolated Claude Code and Codex homes install 6.1.0 with twelve skills. The member route was exercised from a 6.0.0 folder install against a locally served 6.1.0 zip: the correct hash installed and the profile and custom file stayed byte-identical, a wrong hash was refused with nothing changed, and the new skill's own route (tool, swap, offer step, cleanup) was exercised against a scratch 6.1.1. Both 6.0.0 Google Drive links downloaded anonymously through the tool and matched their hashes. Claude Code reads a swapped local folder in place; Codex needs `codex plugin add` again to cache the new version. Real member machines, live Codex sessions and other agents remain untested until reported.

# 5.2.0 · Cleaner short edits and Narrative Motion

- Dedicated-short guidance now checks whole repeated takes, complete word endings, readable single-line captions and the exact frame where a graphic covers a camera cut. Existing profiles and other formats keep their own preferences.
- Narrative Motion adds an optional persistent-object style, editable motion primitives and a synthetic example. It is a starting point to adapt and review against your footage, not a promise that every scene is approved or suitable.
- Two editable, silent eight-second examples show the new motion approach and the short-form camera/caption handoff. Their rendered previews are included.
- An optional local transcription adapter decodes audio through existing FFmpeg before using an already cached faster-whisper model. It does not install packages, download a model or upload footage. Word timings still need review against the recording.
- Sound sourcing now includes an Openverse audio checklist: inspect the individual source, license and attribution before use. Color and delivery guidance clarify static versus tracked corrections, exact timeline identity and recoverable native handoff.
- Lessons 4, 11 and 12 explain the changed cutting, motion and readability checks. Feedback remains scoped to the format and approval that earned it.

Your working profile, media and project files stay separate. Use the update planner to compare changes and review conflicts before applying this version. Never replace a customized working folder with the download.

## Verification and limits

The two example compositions were rendered and visually inspected; repeated out-of-order seeks produced identical frames. The short-form example covers its native frame boundary. A generated speech control was transcribed locally, and an existing output was preserved. Fresh installation and an upgrade with custom settings are tested separately in the release receipt. These are package and synthetic-behavior checks, not evidence that a learner has completed an edit or that every editor, device, voice or optional provider has been tested.

# 5.1.1 · Setup and teaching repairs

The complete download now has one primary setup route, an explicit working-workspace/profile readback and the same disposable first test. The independent core/plugin route remains available. Navigation labels describe opening a prompt, and the shown motion looks link directly to their existing source, configuration and render commands. Existing profiles and custom edits keep priority. No new engine, paid service or feature is required.

# Vibe Editors 5.1.0

## Start from the system behind Payton’s edits

The download now includes the portable personal system: editing decisions and tools, a filled starting profile, source and transcript review, pacing and mistake removal, color and four microphone routes, captions, motion styles, review and delivery. Reusable Flow/Remotion, JavaScript and HyperFrames code comes with its supporting fonts, tools, examples and license notices.

Setup makes a separate working copy, preserves an existing profile, adds project-local skill entry points and tests the editor route in a disposable project. The included synthetic lamp practice means you can start before your own footage is ready. Updates compare your customized copy with its original base and the next release, preserve conflicts for review and keep a recoverable backup.

The original eight visual lessons and all 22 detailed lessons remain included. Shared setup, profile, motion and update teaching now describe this edition.

## What was checked

Editing tools passed 118 focused tests. A disposable Resolve project rendered a three-second 4K clip with audio, exported the native project and restored the prior project and page. Captions preserved the tested AAC payload; protected audio preserved its PCM bytes. These checks establish those operations on the tested setup. Native Premiere/Final Cut/CapCut operations, global layout/preset import and subjective speech/color quality were not established by these tests. See each module’s verification notes for its own evidence and limits.

## What stays yours

Footage, account credentials, private work, existing editor settings and customer preferences remain outside the supplied pack. Private per-video archives and unlicensed third-party media are not distributed. Useful owned mechanisms remain included; any lawful replacement is identified in the motion license notes. No Payton account access, private logo/media library or paid-source text is required.

The same methods and starting choices cannot guarantee an identical result on different footage or in every editor. Judge the actual edit, then save the changes you want for next time.

The download retains the existing setup and latest-release addresses. Customer profiles and working projects remain separate so a reviewed update can preserve them.

The release review also corrected imported filename boundaries, avatar download redirects, temporary-file handling, credential forwarding and reserved JavaScript property names. Focused regression tests cover these cases with local fixtures and mocked service calls. They do not establish that every optional provider or editor route has been exercised.
