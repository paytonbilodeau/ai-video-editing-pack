---
name: update
description: Update Vibe Edit to a newer version, or move a 5.x folder install to the plugin, keeping the person's editing profile, projects, footage and custom files untouched. Use when a new version is announced, when the person pastes an update line with a version, download link and hash, when the person asks to update or upgrade, or when an old Vibe Editors pack folder is found in a workspace.
---

# Update

The plugin folder is replaced whole on every update. That is safe because nothing of the person's lives inside it: the profile, status file, projects and footage are in their workspace. This skill runs the update for the route in use, confirms the skills loaded, offers each change, and re-tests only what changed. The person never downloads, unzips or sets anything up again. One pasted line is enough:

```text
Update Vibe Edit to 6.1.0 from <link> with hash <sha256> and keep my profile
```

A GitHub install needs only "Update Vibe Edit to the latest version and keep my profile."

## 1. Know the versions

Read the installed version from [VERSION](../../VERSION) and the `plugin_version` recorded in `Vibe Edit Settings/SETUP STATUS.json` (`Vibe Editor Settings/` on a 5.x install). Read the [changelog](../../CHANGELOG.md) entry for the new version. Tell the person in three lines what changed and whether it touches a route they use.

## 2. Run the update for the route in use

| Install route | How to tell | Update |
| --- | --- | --- |
| Claude Code from GitHub | `claude plugin marketplace list` shows `vibe-editors` with a GitHub source | `claude plugin marketplace update vibe-editors`, then `/reload-plugins` or a restart. The person can also turn on auto-update for the `vibe-editors` marketplace under `/plugin` |
| Codex from GitHub | `codex plugin marketplace list` shows `vibe-editors` with a GitHub source | `codex plugin marketplace upgrade`, then a new session; if the app asks, install Vibe Edit again from the Plugins tab. `upgrade` only refreshes Git marketplaces |
| Downloaded folder: the community early release (`vibe-editors-early`) or the public zip | the marketplace list shows a local path, or this skill was loaded from a folder | the member route below |

A new version reaches the person only when the plugin version string changed; a folder install loads whatever the folder holds.

### The member route (downloaded folder)

The release post gives the link to the new zip and its SHA-256. Do not ask the person to download anything; [fetch_release.py](tools/fetch_release.py) does it and refuses any file whose hash does not match.

1. **Find the installed folder.** It is the path listed for `vibe-editors-early` by `claude plugin marketplace list` or `codex plugin marketplace list`. If no marketplace lists it (the plugin was loaded with `--plugin-dir` or by another agent), it is the folder that holds `.claude-plugin/marketplace.json`, two levels above this plugin's `plugins/vibe-edit`.
2. **Move out anything of theirs.** Run `python3 "<this skill>/tools/fetch_release.py" --check "<installed folder>"`. Its `extra` and `root_extra` lists are files that were never shipped: the person's (`node_modules` and caches do not count). Move each one into the workspace, for example `Vibe Edit Custom/`, add a line to the profile naming it, and tell the person where it went. Nothing of theirs stays in a folder that is about to be replaced. `changed` entries are shipped files whose bytes differ, for example one the person edited: they stay in the previous folder after the swap, and the removal step ignores any that match the new release.
3. **Download, verify, swap.** `python3 "<this skill>/tools/fetch_release.py" --url "<link>" --sha256 <hash> --replace "<installed folder>"`. The tool accepts a Google Drive share link, a GitHub release asset, a local path or a file URL; downloads the zip; checks the SHA-256 and stops with a clear message on any mismatch, changing nothing; unzips beside the installed folder; refuses while unshipped files are still inside the plugin; renames the old folder to `<name> (previous <version>)`; puts the new one in its place; and moves `node_modules` across where the package file is unchanged, so no reinstall is needed. On a mismatch, give the person the tool's message as it is and stop; never retry with another hash or install an unverified file.
4. **Reload.** Claude Code reads a local marketplace in place, so `claude plugin list` shows the new version as soon as the folder is swapped; the person then runs `/reload-plugins` or restarts. Codex keeps a cached copy per version: run `codex plugin add vibe-edit@vibe-editors-early` again, which caches the new version (`codex plugin marketplace upgrade` only refreshes Git marketplaces), then the person starts a new session. Say exactly which of these you ran and which the person still has to do; a reload cannot happen inside the running session.
5. **Check, then clear the previous folder.** After step 3 of this skill passes (the twelve skills listed, VERSION reads the new version), run `python3 "<installed folder>/plugins/vibe-edit/skills/update/tools/fetch_release.py" --remove-previous "<previous folder>"`. It deletes the previous folder only when every file in it matches the shipped manifest or the same file in the installed release; otherwise it keeps the folder and lists what differs.

The link and hash never come from a guess. If the person pasted a line without them, ask for the release post or its two values.

## 3. Check, then re-test what changed

Confirm the twelve skills are listed and the version now matches: read the installed [VERSION](../../VERSION) and report the string you observed. Write the new `plugin_version` into `SETUP STATUS.json`. Repeat the [practice edit](<../setup/references/FIRST TEST.md>) only when the changelog names the editor route, export or a tool the person uses; otherwise a short check of the changed feature is enough.

## 4. Offer each change, apply only what is accepted

Read the new changelog entry, the person's `EDITING PROFILE.md` and any custom files it names. For each changelog item, say in one line which of three it is:

- **Improves what you have:** it changes a result for a route, format or look the person uses, and nothing in their profile says otherwise.
- **Optional:** it adds a route, look or tool they do not use yet, or a default their profile already sets differently.
- **Does not apply:** it touches nothing in how they edit.

Then ask once which of the improvements and options they want. Apply only those, by adding to the profile or setting up the route; a saved preference is never overwritten by a new default. Skip the list when the entry has no item that could change their results, and say so in one line.

## 5. Leave the person's files alone

The profile is read, never rewritten, by an update. If a new default conflicts with a saved preference, say so and keep the preference. Custom files the person made belong in their workspace, not in the plugin; if any are found inside a plugin folder, move them out before updating and tell the person where they went.

## Moving from a 5.x install

A 5.x install copied the whole pack into the workspace as `Vibe Editor Pack/`, kept hashes in `.vibe-editor/` and added `vibe-` skill bridges. Follow [MIGRATE FROM 5.x](<references/MIGRATE FROM 5.x.md>): install the plugin, keep the profile, archive the old pack folder instead of deleting it, remove only the old bridges, and run the practice edit once.

## Files in this skill

| File | Use |
| --- | --- |
| [fetch_release.py](tools/fetch_release.py) | Download, verify (SHA-256), unzip and swap a release for a downloaded-folder install; `--check` and `--remove-previous`; tests in `tools/tests` |
| [MIGRATE FROM 5.x](<references/MIGRATE FROM 5.x.md>) | Step by step move from the folder install to the plugin |
| [UPDATES (5.x bootstrap)](<references/UPDATES (5.x bootstrap).md>) | How the old three-way bootstrap update worked; read only to understand an old workspace |
| [UPDATING (5.x core pack)](<references/UPDATING (5.x core pack).md>) | The old core pack's update notes; historical |

## Scope and honesty

An update never publishes, uploads, spends, changes permissions or deletes the person's files. Report the installed version you observed, not the one you expected. If the marketplace command or the download fails, give the exact next step (for example the Plugins tab in Codex, or the tool's mismatch message) instead of claiming the update happened.
