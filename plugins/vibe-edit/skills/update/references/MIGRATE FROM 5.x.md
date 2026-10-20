# Move a 5.x folder install to the Vibe Edit plugin

A Vibe Editors 5.x workspace looks like this:

```text
<editing workspace>/
  Vibe Editor Pack/              the whole 5.x bundle, copied by bootstrap.py
  .vibe-editor/                  bases/ (hashes of the supplied pack), backups/, state.json
  Vibe Editor Settings/
    EDITING PROFILE.md           the person's profile (keep)
    SETUP STATUS.json            the status record (keep)
  .agents/skills/vibe-*/         Codex skill bridges pointing into Vibe Editor Pack
  .claude/skills/vibe-*/         Claude Code skill bridges pointing into Vibe Editor Pack
```

The plugin replaces `Vibe Editor Pack/` and the bridges. The profile and status stay.

## Steps

1. **Install the plugin** with [INSTALL](<../../../INSTALL.md>) and confirm the twelve skills load. Do this before touching the old folders, so the person is never without a working setup.
2. **List customizations.** Compare each file in `Vibe Editor Pack/` with the hashes in `.vibe-editor/bases/`. A file whose hash differs, or that has no base entry, is the person's own work. Show that list. For each, ask where it should live: a preference goes into `EDITING PROFILE.md`; a custom skill, template, LUT or script goes into a workspace folder such as `Vibe Edit Custom/`, with a line in the profile naming it. Nothing of theirs is left inside a folder that will be archived.
3. **Keep the profile.** Leave `Vibe Editor Settings/` where it is, or rename it to `Vibe Edit Settings/` if the person prefers, and update any instructions file that names the path. Add `plugin_version` to `SETUP STATUS.json`.
4. **Remove only the old bridges.** Delete the `vibe-*` folders under `.agents/skills/` and `.claude/skills/` that point into `Vibe Editor Pack/`. Leave every other skill alone.
5. **Archive the old pack.** Move `Vibe Editor Pack/` and `.vibe-editor/` into `Vibe Editor Pack (5.x archive)/` in the same workspace. Do not delete them; the person can delete the archive later. Stop any render or dependency install that uses them first, and leave an installed `node_modules` inside the archive rather than copying it around.
6. **Run the practice edit** once with the [setup skill](../../setup/SKILL.md), so the route is verified under the plugin, and report what changed.

## What stays the same

Terms, names and defaults are the same system. Tech Motion is still the default look, the profile format is unchanged, and projects made with 5.x open as before. The old pack's `bootstrap.py` is no longer needed; its update commands in [UPDATES (5.x bootstrap)](<UPDATES (5.x bootstrap).md>) apply only to the archived copy.
