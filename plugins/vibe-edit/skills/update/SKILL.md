---
name: update
description: Update Vibe Edit to a newer version, or move a 5.x folder install to the plugin, keeping the person's editing profile, projects, footage and custom files untouched. Use when a new version is announced, when the person asks to update or upgrade, or when an old Vibe Editors pack folder is found in a workspace.
---

# Update

The plugin folder is replaced whole on every update. That is safe because nothing of the person's lives inside it: the profile, status file, projects and footage are in their workspace. This skill runs the update for the app in use, confirms the skills loaded, and re-tests only what changed.

## 1. Know the versions

Read the installed version from [VERSION](../../VERSION) and the `plugin_version` recorded in `Vibe Edit Settings/SETUP STATUS.json`. Read the [changelog](../../CHANGELOG.md) for the new version and tell the person in three lines what changed and whether it touches a route they use.

## 2. Run the update for the route in use

| Install route | Update |
| --- | --- |
| Claude Code from GitHub | `claude plugin marketplace update vibe-editors`, then `/reload-plugins` or a restart. The person can also turn on auto-update for the `vibe-editors` marketplace under `/plugin` |
| Codex from GitHub | `codex plugin marketplace upgrade`, then a new session; if the app asks, install Vibe Edit again from the Plugins tab |
| Downloaded folder (public or community early release) | Download the new folder, replace the old one in the same place, then reload or start a new session. Keep the old folder until the check in step 3 passes |

A new version reaches the person only when the plugin version string changed; a folder install reloads whatever the folder contains.

## 3. Check, then re-test what changed

Confirm the twelve skills are listed and the version now matches. Write the new `plugin_version` into `SETUP STATUS.json`. Repeat the [practice edit](<../setup/references/FIRST TEST.md>) only when the changelog names the editor route, export or a tool the person uses; otherwise a short check of the changed feature is enough.

## 4. Leave the person's files alone

The profile is read, never rewritten, by an update. If a new default conflicts with a saved preference, say so and keep the preference. Custom files the person made belong in their workspace, not in the plugin; if any are found inside a plugin folder, move them out before updating and tell the person where they went.

## Moving from a 5.x install

A 5.x install copied the whole pack into the workspace as `Vibe Editor Pack/`, kept hashes in `.vibe-editor/` and added `vibe-` skill bridges. Follow [MIGRATE FROM 5.x](<references/MIGRATE FROM 5.x.md>): install the plugin, keep the profile, archive the old pack folder instead of deleting it, remove only the old bridges, and run the practice edit once.

## Files in this skill

| File | Use |
| --- | --- |
| [MIGRATE FROM 5.x](<references/MIGRATE FROM 5.x.md>) | Step by step move from the folder install to the plugin |
| [UPDATES (5.x bootstrap)](<references/UPDATES (5.x bootstrap).md>) | How the old three-way bootstrap update worked; read only to understand an old workspace |
| [UPDATING (5.x core pack)](<references/UPDATING (5.x core pack).md>) | The old core pack's update notes; historical |

## Scope and honesty

An update never publishes, uploads, spends, changes permissions or deletes the person's files. Report the installed version you observed, not the one you expected. If the marketplace command fails, give the exact next step (for example the Plugins tab in Codex) instead of claiming the update happened.
