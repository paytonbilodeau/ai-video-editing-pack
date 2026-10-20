# 6.0.0 · Vibe Edit becomes a plugin

The AI Video Editing Pack is now **Vibe Edit**, a plugin for Codex and Claude Code. Same system, one install, no folder to unzip into your project.

- **Install with two commands or one line.** Add the `vibe-editors` marketplace and install `vibe-edit`, or tell your assistant "Read INSTALL.md and set up Vibe Edit for me." The assistant runs the install, confirms the skills loaded and makes the practice edit. The customer setup prompt is one sentence.
- **Twelve skills instead of forty-nine.** setup, edit, pre-edit, style, remotion, hyperframes, javascript-animation, captions, shorts, editors, update and help. Every former skill is still here as a guide inside the skill that owns it; the HyperFrames workflow set is complete under hyperframes/workflows.
- **Smaller download.** Lesson drawings and example stills are WebP; rendered example videos, the Gentlemen hybrid overlay, extra practice audio and texture masks moved to an optional asset bundle described in ASSETS.md. Nothing in setup or an ordinary edit needs it.
- **Updates are one command.** Claude Code: `/plugin marketplace update vibe-editors`. Codex: `codex plugin marketplace upgrade`. Your profile, projects and footage are never inside the plugin.
- **Moving from 5.x.** The update skill archives the old `Vibe Editor Pack/` folder, keeps your profile and removes only the old skill bridges. Nothing is deleted.
- **Same content as 5.2.0.** Editing workflow, profile, presets, tools, the six looks, Narrative Motion, dedicated-short finishing, the eight visual lessons, the twenty-two detailed lessons and the practice clip are the 5.2.0 versions, moved into place. New writing is limited to the install page, the skill routers, the update and help skills, and the lessons that described the old install.

Verification and limits: install was tested on this version's build machine in Claude Code and Codex from a local marketplace; GitHub installs, other agents, real learner outcomes and every editor and device remain untested until reported.

Entries below describe the 5.x folder install, before the plugin.

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
