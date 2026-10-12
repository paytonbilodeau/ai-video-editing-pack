# Connect your AI to your editor

Keep the editor, projects, presets, and working tools you already like. The AI
first checks what you have, then chooses a route that can save an editable result.
You do not need to learn these technical names before starting.

## What the AI should explain

Use one short explanation, tied to the person's next step:

> Your AI can prepare the cuts and pass them to your editor. To also click buttons
> and finish steps inside the app, it may need computer access. That lets it see
> the screen and operate the interface. File access lets it work in the project
> folder. These are different permissions. The AI will explain which one is needed
> before asking you to turn it on.

Ask only for information that cannot be read safely: the intended editor or
project, a choice with a cost, or a permission the person must grant. Reuse their
existing authorization. Offer to perform the approved setup through available
computer use; if the operating system requires the person's click, show the exact
setting and continue after that click. Never describe screen or computer access
as confined to a project folder.

A local connection sends editing commands to the app. A timeline file hands over
an editable sequence. Computer use clicks the app's controls. An online service
receives uploaded files. State which route is being used, especially before an
upload. One working route is enough to begin.

## Pick the practical route

| Editor | First route to check | Useful fallback | What must be proved locally |
|---|---|---|---|
| [DaVinci Resolve](EDITOR%20PLAYBOOK%20RESOLVE.md) | Existing working integration; supported Studio installations include Blackmagic's local MCP connector. | Import the pack's FCPXML or Premiere XML, then use the editor interface. | Correct project, readable state, two cuts, save, reopen, export. |
| [Final Cut Pro](EDITOR%20PLAYBOOK%20FINAL%20CUT.md) | FCPXML creates an editable project that refers to the original footage. | Computer use for controls, effects and export. | Clips and sound arrive correctly and the saved project reopens. |
| [Premiere](EDITOR%20PLAYBOOK%20PREMIERE.md) | Existing trusted integration or the pack's Premiere XML. | Native interface; an optional reviewed UXP integration for needs beyond XML. | Imported sequence, frame rate, linked sound and final export. |
| [CapCut](EDITOR%20PLAYBOOK%20CAPCUT.md) | A working local route already installed; otherwise compare official CapCut × Codex with the optional community draft route. | Computer use with a cut sheet. | Exact app version, draft acceptance, save/reopen persistence and export. |

If choosing an editor from scratch, explain the free and paid routes before a
purchase. Resolve is a useful starting option because it offers a free editor
and a separate Studio edition with additional automation. A purchase is not a
prerequisite for using this pack's file handoff and guides.

## CapCut can receive an editable draft

There is more than one way to do this. CapCut's official
[Codex workflow](https://www.capcut.com/tools/capcut-x-codex) describes uploaded
footage becoming an editable rough cut. Its hosted installer, checked October
12, 2026, refuses authorization from US network egress. Availability may change;
check the current installer and account before promising access.

The independent [capcut-cli](https://github.com/renezander030/capcut-cli) project
can write local drafts and documents an OTIO import command. This is a conversion
through a third-party tool, not proof that CapCut's own Import dialog accepts
FCPXML, Premiere XML or OTIO. Its [version matrix](https://github.com/renezander030/capcut-cli/blob/master/docs/version-support.md)
separates fixture tests, user reports, expected compatibility and blocked writes.
Follow the CapCut playbook to test a disposable draft before using this route.

## What the pack's timeline exporter writes

The included exporter creates **FCPXML, Premiere XML, EDL and readable cut
sheets**. It does not create OTIO or CapCut drafts. See
[CUT LIST EXPORT](CUT%20LIST%20EXPORT.md). Format support in an editor or another
tool does not add that format to this exporter.

## Make setup useful without making the user do technical homework

The assistant runs these checks within the approved setup. Use synthetic media
or authorized copies; the person does not need to record a test clip.

1. Read the editor's edition/version and the existing connection. Keep unrelated
   assistant settings, skills and projects intact.
2. Confirm the intended project without changing it. Record the route in
   [PROJECT INTAKE](../templates/PROJECT%20INTAKE.md).
3. In a disposable project, create two source ranges, save and reopen. Check
   their boundaries and linked audio through the editor's own state or interface.
4. Export a short sample. Check its frame rate, size, duration, sound and ending.
5. Report plain results: what now works, what needs a manual click, and the next
   useful action. An installed connector or a valid file alone is not this result.

If a check fails, inspect the cause and try a suitable documented alternative.
Do not switch editors, replace a working integration, loosen security settings,
or force a third-party compatibility override merely to clear an error.
