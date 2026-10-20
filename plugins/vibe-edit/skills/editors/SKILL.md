---
name: editors
description: Connect the assistant to the person's video editor, DaVinci Resolve through its Studio native MCP or file import, and Premiere, Final Cut and CapCut through timeline files and screen control, using the route matrix, per-editor playbooks and the cut-list exporter that writes FCPXML, Premiere XML, EDL and cut sheets. Use when choosing or proving an editor route, importing a generated timeline, or when the edit skill needs a native or file handoff.
---

# Editors

Find one route that saves an editable result in the editor the person already uses, prove it in a disposable project, and record it in `Vibe Edit Settings/SETUP STATUS.json`. One working route is enough. Keep the person's projects, presets and tools; never switch editors, replace a working integration, loosen security settings or force a compatibility override to clear an error.

## Procedure

1. **Read the matrix.** [EDITOR CONNECTIONS](<references/EDITOR CONNECTIONS.md>) gives each editor's first route, fallback and local proof. Read the installed edition and version from the app, and any route already proven in `SETUP STATUS.json`. File access, an editor connection and screen control are three different permissions; say which one a step needs.
2. **Open the playbook.** [Resolve](<references/EDITOR PLAYBOOK RESOLVE.md>), [Premiere](<references/EDITOR PLAYBOOK PREMIERE.md>), [Final Cut](<references/EDITOR PLAYBOOK FINAL CUT.md>) or [CapCut](<references/EDITOR PLAYBOOK CAPCUT.md>). For Resolve, [RESOLVE AND MCP](<references/RESOLVE AND MCP.md>): Studio 21.1 bundles `ResolveMCP`, and File > Setup AI Assistants writes the MCP configuration for Claude Code and Codex; back up unrelated MCP settings first. Free Resolve, Final Cut, Premiere and CapCut use timeline files and screen control. [resolve_control.py](../edit/tools/resolve_control.py) runs under the bundled ResolvePython: `doctor` is read-only, `smoke-test` makes a scratch project and a short render. State rules are in [EDITABLE TIMELINE](<../edit/references/EDITABLE TIMELINE.md>); cross-editor limits in [OTHER EDITORS](<../edit/references/OTHER EDITORS.md>).
3. **File route.** Write a cut list shaped like [example-cut-list.json](examples/example-cut-list.json), then run [cut_list_to_timeline.py](tools/cut_list_to_timeline.py) as [CUT LIST EXPORT](<references/CUT LIST EXPORT.md>) describes, with `--out-dir` outside the plugin. It writes FCPXML, Premiere XML, EDL, cut sheets and a summary JSON with SHA-256 values; no OTIO or CapCut drafts. Supply `fps` explicitly, read every warning and the cut sheet before import, and prefer XML over EDL for Resolve.
4. **Screen control.** Computer use is a fallback the assistant may use only where the app supports it and the person has allowed it. Say when it is in use; never describe it as confined to a project folder.
5. **Prove the route.** In a disposable project: two source ranges, save, reopen, export a short sample. Check clip count against the summary, first and last words, linked sound, sequence frame rate equal to the source, and the export's rate, size, duration, sound and ending. Record the result in [EDIT PLAN AND REVIEW](<../edit/templates/core/EDIT PLAN AND REVIEW.md>) and the route in [PROJECT INTAKE](<../edit/templates/core/PROJECT INTAKE.md>). A generated timeline file is not a verified native import until the import, save and reopen were observed.
6. **Report plainly.** What works, what still needs the person's click, the next useful action. Continue in [edit](../edit/SKILL.md); a [pre-edit](../pre-edit/SKILL.md) first pass hands off the same way.

Offline check: `python3 -m unittest discover -s tools/tests -v` from this folder runs [test_cut_list_to_timeline.py](tools/tests/test_cut_list_to_timeline.py); a failed import is not a pass. The exporter needs only Python 3.11+; `--probe` and `--validate-dtd` use ffprobe and xmllint when present.

## Everything in this folder

| File | Use |
| --- | --- |
| [EDITOR CONNECTIONS](<references/EDITOR CONNECTIONS.md>) | Route matrix and setup checks |
| [EDITOR PLAYBOOK RESOLVE](<references/EDITOR PLAYBOOK RESOLVE.md>) | Resolve editions, routes, workflow |
| [EDITOR PLAYBOOK PREMIERE](<references/EDITOR PLAYBOOK PREMIERE.md>) | Premiere XML, UXP, workflow |
| [EDITOR PLAYBOOK FINAL CUT](<references/EDITOR PLAYBOOK FINAL CUT.md>) | FCPXML import, magnetic timeline |
| [EDITOR PLAYBOOK CAPCUT](<references/EDITOR PLAYBOOK CAPCUT.md>) | Official, community and screen routes |
| [RESOLVE AND MCP](<references/RESOLVE AND MCP.md>) | Native MCP setup and troubleshooting |
| [CUT LIST EXPORT](<references/CUT LIST EXPORT.md>) | Cut list schema, formats, import, limits |
| [cut_list_to_timeline.py](tools/cut_list_to_timeline.py) | Cut list to FCPXML, XML, EDL, sheets |
| [test_cut_list_to_timeline.py](tools/tests/test_cut_list_to_timeline.py) | Exporter unit tests |
| [example-cut-list.json](examples/example-cut-list.json) | Working cut-list example |
| [resolve_control.py](../edit/tools/resolve_control.py) | Native Resolve doctor and smoke-test |
| [EDITABLE TIMELINE](<../edit/references/EDITABLE TIMELINE.md>) | Native state and read-back rules |
| [OTHER EDITORS](<../edit/references/OTHER EDITORS.md>) | What interchange does not carry |

## Scope and honesty

No route promises an outcome in a given editor, version or operating system; the Resolve native evidence comes from one tested Mac Studio route and does not transfer to other builds. Separate what was proven in this session (import, save, reopen, export observed) from what the playbooks document. No installation, purchase, account entry, permission change, upload to a hosted service or publishing happens without the person's choice; the person handles any purchase and activation. Original media, the current project and unrelated assistant configuration stay untouched; test in a disposable project and keep generated files outside the plugin.
