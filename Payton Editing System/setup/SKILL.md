---
name: vibe-editor-setup
description: Set up or update the complete Vibe Editors Payton-derived editing system in a local project, preserve an existing profile, discover the available editor route, and verify a disposable first edit. Use for first setup or an installation problem, not every later edit.
---

# Adaptive setup

Read [START HERE](<START HERE.md>), [the contents map](CONTENTS.md), and the bundle's `bundle-manifest.json`. The complete bundle root also contains `AI Video Editing Pack/` and `Kit Email Workflow/`. Keep that structure: editing and motion references can use these sibling resources. Instructions and a successful installation do not prove editor control or an acceptable video.

## Begin with existing facts

1. Identify the current AI app, operating system, chosen editor and available file/tool access from observable state. Read only the relevant editor capability guide. Reuse an existing working connection. Do not collect account secrets, scan unrelated folders, infer credentials from a key name, or silently install an alternative editor.
2. Look for an editing profile in the current project and any profile the user names. Show its path and preserve its bytes. Existing customized preferences win. If several profiles disagree, ask which is authoritative; do not combine them silently. Do not search the entire computer for one.
3. Ask only what remains unknown and changes the next step: the editor if none is selected, where the work should live, or which short clip may be used. Give one recommendation based on existing tools. Defer brand and style questions until the first result makes the choices concrete. A default is a starting choice, not evidence that it suits this footage.

## Make an isolated working copy

Use [bootstrap.py](bootstrap.py) with Python 3.11 or later. It uses only the standard library. Source is the complete reviewed bundle root, not this setup subfolder. Workspace is a separate project folder. Resolve symlinked folder aliases to their real paths first and explain the actual destination.

Run the install command without `--apply` first, inspect its proposed paths and preserved collisions, then apply within the user's setup request. Select `--app codex`, `--app claude`, or `--app both` to match the app actually used. If an authoritative customer profile already exists, provide its workspace-relative path with `--profile`. A profile outside the selected workspace remains unchanged; copy it into the settings folder only with the user's intended project scope, record its origin locally, and keep it authoritative.

The bootstrap copies every manifest-listed byte into `Vibe Editor Pack/`, keeps a hashed original base in `.vibe-editor/`, and creates `Vibe Editor Settings/EDITING PROFILE.md` only when no selected profile exists. It creates project-local skill bridges; it does not overwrite existing bridges, AGENTS.md, CLAUDE.md, app settings or provider configuration. Resolve any reported bridge collision through the explicit file path. Do not call integration complete if the app loaded another skill with the same name.

## Test the selected route

Read [FIRST TEST](<FIRST TEST.md>), `../editing/START HERE.md` and the relevant editor playbook. Record observations in the customer's `Vibe Editor Settings/SETUP STATUS.json`, using [the blank status template](<SETUP STATUS.template.json>). Record unknown capability as unknown; do not invent a successful connection.

Test only the needed dependency chain. The first edit does not require a graphics engine, speech model, image-generation account or paid audio service. If a local dependency is missing, explain its purpose and follow the app's supported installation route within the requested setup. Spending, account connections and wider permissions need the user's actual choice. Never disable an approval boundary to finish setup.

If direct native control is unavailable, use the supported interchange route or a precise manual import step. Verify the resulting project in the actual editor where accessible. Do not label XML generation, a screenshot or a command exit code as a successful import. Complete all independently available checks and name the remaining step.

## Adapt after the test

Ask for one consequential preference at a time: keep the starting look, use existing brand colors, or change a specific caption/pacing choice. Show a short comparison when possible. Update the customer profile with only accepted recurring preferences and their scope. Recording facts belong in the current project brief, not permanent taste defaults. Preserve explicit exceptions and existing profile wording outside the changed preference.

## Finish with evidence

Show the exact working folder, active profile and next action. Distinguish installed instructions, observed editor access, saved/reopened editable project, rendered export, technical checks and actual watch/listen coverage. State the shortest manual next step for an unavailable capability. Setup does not promise that every later video or editor will produce Payton's result.

Later edits use `../editing/SKILL.md` and, when appropriate, `../motion/SKILL.md`. Reuse the established setup; repeat a disposable test only when the relevant tool or operation changes. Updates follow [UPDATES](UPDATES.md), comparing the old supplied base, customized working files and new supplied version before changing active work.
