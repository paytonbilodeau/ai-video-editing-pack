---
name: setup
description: Set up Vibe Edit as the person's video editor after the plugin is installed: check the apps and editor already on the computer, keep the editing profile outside the plugin, find a working route to the editor and prove it with one disposable practice edit. Use for a first setup, a new computer or editor, or when a setup stopped working.
---

# Setup

The plugin is already installed when this skill runs (if it is not, follow [INSTALL](<../../INSTALL.md>) first). Setup turns the installed skills into a working editor for this person: a workspace, a profile they own, a verified route to their editing app and one small edit that proves the route. It asks for very little, because most answers are visible on the computer.

## 1. Start from what exists

Observe before asking: the AI app and operating system, the installed editor and its version, Python, Node, FFmpeg and ffprobe, an existing editor connection (for example the Resolve MCP), and an existing profile. A profile can be at `Vibe Edit Settings/EDITING PROFILE.md`, at `Vibe Editor Settings/EDITING PROFILE.md` from a 5.x install, or at a path the person names. Show its path and preserve its bytes. If a `Vibe Editor Pack/` folder from a 5.x install is present, hand that part to the [update skill](../update/SKILL.md) before continuing. Read only the shared workspace; never scan the whole computer or collect account secrets.

Ask at most one question at a time, and only when the answer changes the next step: which editor, where the work should live, or the working pace (careful, balanced, or handle it for me). [Setup pace](references/setup-pace.md) explains the three paces; the app's own permission settings are the real boundary, as [AI app setup](<references/AI APP SETUP.md>) explains.

## 2. Make the workspace

Use the folder the person chooses for editing work. Inside it create `Vibe Edit Settings/` with:

- `EDITING PROFILE.md`, copied from [the Payton-derived starting profile](<../edit/profiles/PAYTON EDITING PROFILE.md>), or from [the blank profile](<../edit/templates/BLANK EDITING PROFILE.md>) when the person wants to start from nothing. An existing profile stays as it is.
- `SETUP STATUS.json`, from [the status template](<templates/SETUP STATUS.template.json>), with the plugin version from [VERSION](../../VERSION).

Never create these inside the plugin folder; it is replaced on every update. The copied profile names a few plugin files by plain name rather than by link, because the plugin folder moves on every update; when a preference points at one, open it inside the installed plugin's `skills/edit` folder. If the project has an instructions file (AGENTS.md or CLAUDE.md), add one line naming the profile path; never overwrite an existing instructions file.

## 3. Find the editor route

Read the [editors skill](../editors/SKILL.md) and the playbook for the installed editor. Prefer an existing working connection. Verify the route on a disposable project, not on the person's real work. Record what was observed in `SETUP STATUS.json`; a capability you did not observe stays `unknown`. [Platform refresh](references/platform-refresh.md) covers re-checking after an app or editor update, and [provider check](<references/PROVIDER CHECK.md>) covers optional paid services, which are never connected without the person's choice.

## 4. Run the practice edit

Follow [FIRST TEST](<references/FIRST TEST.md>) with the included [practice clip](<../../practice/synthetic-lamp/README.md>). Save the editable project, export a short file, decode and watch it, and keep both. A generated timeline file is not a verified native import until the import, save and reopen were observed.

## 5. Adapt once, then report

Ask about one consequential preference at a time (keep the starting look, use existing brand colors, change a caption or pacing choice), showing a comparison where possible. Save only accepted recurring preferences to the profile; project facts belong in a brief. Then report in plain words: the connected app and editor, the route that works, where the profile lives, what the practice edit produced and what was checked, and any step that still needs the person's hand.

## Files in this skill

| File | Use |
| --- | --- |
| [AI APP SETUP](<references/AI APP SETUP.md>) | App choice, plans and permission settings, written for the folder install; the permission and pace guidance still applies |
| [SETUP FLOW](<references/SETUP FLOW.md>) | The adaptive interview and optional installs |
| [setup pace](references/setup-pace.md) | Careful, balanced, or handle it for me |
| [platform refresh](references/platform-refresh.md) | Re-check capabilities after updates |
| [PROVIDER CHECK](<references/PROVIDER CHECK.md>) | Optional paid services and current price checks |
| [SAFETY AND API KEYS](<references/SAFETY AND API KEYS.md>) | Keep credentials out of prompts, profiles and shared files |
| [FIRST TEST](<references/FIRST TEST.md>) | The disposable practice edit |
| [SETUP STATUS template](<templates/SETUP STATUS.template.json>) | The status record |
| [TOOL SETUP template](<templates/TOOL SETUP.md>) | A record of the tools and versions found |
| [setup_doctor.py](tools/setup_doctor.py) | Reads the environment and reports missing dependencies; tests in `tools/tests` |

## Scope and honesty

Setup installs no video editor, graphics engine, paid service or model, changes no app permission and uploads nothing. A successful command or a saved status file is not proof the editor works; only the observed practice edit is. Say which steps were tested and which are documented. The person's existing profile, projects and footage are never changed by setup.
