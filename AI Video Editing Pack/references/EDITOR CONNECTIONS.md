# Editor Connections

**Checked October 3, 2026.** Recheck the chosen editor's current documentation
and the installed version before setup. The same pack skills plan an edit for
any editor, but there is no universal timeline connector, and a browser-only
chat cannot inspect a local editor or confirm that a project saved.

Only one of the four editors ships a vendor connector for AI assistants:
DaVinci Resolve Studio 21.1. Everything else is a file handoff, an unofficial
bridge, or computer use. Say which one you are using. Each editor has its own
playbook with the version facts, shortcuts, workflow and smoke test:
[Resolve](EDITOR%20PLAYBOOK%20RESOLVE.md),
[Premiere](EDITOR%20PLAYBOOK%20PREMIERE.md),
[Final Cut](EDITOR%20PLAYBOOK%20FINAL%20CUT.md),
[CapCut](EDITOR%20PLAYBOOK%20CAPCUT.md).

## Choose the route in the intake interview

Keep the editor the person already uses when it fits. If they are choosing from
scratch, recommend DaVinci Resolve (free edition for file-import workflows,
Studio for the live connection). Ask for editor, edition, version, AI app and
local tool access, then record the route as **scripted**, **file import**,
**computer use** or **manual**. Do not switch editors or install connectors
without asking.

## What each route can do

Legend: S scripted (API or vendor connector, no human in the loop); I file
import (the agent writes a file, the editor imports it); C computer use
(screenshot-driven GUI control, slow and least deterministic); M manual (a
person performs the step). Verified means checked on an installed copy or in
vendor files; the rest is reported from current documentation and community
sources.

| Operation | Resolve Studio 21.1 | Resolve Free 21.1 | Premiere 26.5 | Final Cut Pro 12.4 | CapCut 9.5 desktop |
|---|---|---|---|---|---|
| Import media | S (verified) | I or C | S via unofficial bridge, I through XML | I (media referenced in FCPXML) | I (paths in a draft) or C |
| Create a timeline | S | I: File > Import > Timeline | S via bridge, I: FCP7 XML | I: FCPXML project | I: draft folder, or C |
| Assemble cuts from a cut list | S: append ranges | I: FCPXML or EDL | I: FCP7 XML (preferred), S via bridge | I: FCPXML asset-clips | I: segments in draft JSON (unofficial) |
| Ripple trim an existing cut | partial: delete with ripple and rebuild; C for one trim | I regenerate, or C | C, or regenerate XML | I regenerate, or C | I rewrite ranges, or C |
| Audio effects | S partial: normalize, volume, Voice Isolation, Dialogue Leveler; plug-in parameters are C | C or M | S partial via bridge; Essential Sound is C | I partial (volume, some adjustments); effects C | I partial; C safer |
| Color | S: LUT, CDL, DRX grades, Magic Mask creation | C | S partial via bridge (Lumetri parameters); C | I partial; LUT effects C or M | I partial; C safer |
| Titles and captions | S: Create Subtitles from Audio, Fusion titles | C or M | S via bridge for tracks; design needs real MOGRTs | I: title and caption elements referencing installed templates | I: text materials and SRT; C |
| Graphics layers | S: higher tracks, transform properties | I: multi-track FCPXML | I: extra tracks in XML; S via bridge | I: connected clips on lanes | I: extra tracks; C |
| Person masks | C (Magic Mask clicks are UI) | C | C (Object Mask) | C (Magnetic Mask, Auto Mask) | I partial, C safer |
| Keyframed zooms | S partial: Dynamic Zoom per clip; C for arbitrary keys | C | S via bridge or C | I: adjust-transform keyframes | I: keyframe arrays; C |
| Export with presets | S: render presets and jobs | C or M | S via bridge to Media Encoder; C | C or M (Share dialog) | C (Export dialog) |
| Read project state back | S: full read API | M | S via bridge | I or M: Export XML by hand, then parse | I: parse the draft JSON |

Notes. The Resolve Free column assumes 21.1, where Python scripting moved to
Studio (documented). The Premiere column rests on community bridges that run a
panel inside Premiere after the user turns on Adobe's extension debug mode; Adobe
has no official connector and its own AI Assistant is in-app only. Final Cut has
no scripting surface beyond read-only AppleScript; FCPXML is the sanctioned
exchange and Apple offers no programmatic export. CapCut's draft format is
undocumented and version-sensitive; the official CapCut plugin for Codex is a
hosted service that was unavailable to US network egress when checked.

## Interchange formats that each editor reads

| Format | Resolve | Premiere | Final Cut | CapCut |
|---|---|---|---|---|
| FCPXML (1.11 to 1.14) | import and export | no (needs a converter) | native | no |
| Final Cut Pro 7 XML (xmeml) | import and export | native | no | no |
| EDL (CMX3600) | import and export | import and export | no | no |
| OTIO | import and export | beta only | no | no |
| CapCut draft JSON | no | no | no | native, unofficial to write |

The pack's exporter writes the first four from one cut list; see
[CUT LIST EXPORT](CUT%20LIST%20EXPORT.md).

## Permissions each route needs

- Resolve Studio: Preferences > System > General, External scripting Local,
  Automatic scripted actions Allow safe; File > Setup AI Assistants writes the
  assistant configuration (documented). Studio 21.1 or later. No Python install.
- Premiere unofficial bridge: Adobe CEP debug mode (disables the extension
  signature check), Node.js, a third-party panel inside Premiere. Tell the user
  plainly that this runs unsigned third-party code with full scripting access.
  UXP bridges need Premiere 25.6 or later and the UXP Developer Tool.
- Final Cut: none beyond file access. `open -a "Final Cut Pro" cut.fcpxml`
  hands the file to the import path.
- CapCut: file access to the drafts folder. Close the project in CapCut before
  writing a draft, and back the folder up first.
- Computer use (either assistant): macOS Accessibility and Screen Recording,
  per-app approval, and a short scoped session. Both vendors describe it as the
  broadest and slowest route.

## Connection smoke test

1. Record editor, edition, version, OS, AI app, connector and the documentation
   date in [PROJECT INTAKE](../templates/PROJECT%20INTAKE.md).
2. Prove a read-only step: Resolve status and version, a bridge's project name,
   a parsed FCPXML export, a parsed CapCut draft.
3. Create a disposable project from a copied 20 to 60 second clip. Make two cuts
   by the chosen route, then read the result back by the same editor's own
   means (API, Export XML, draft file or a zoomed screenshot of the timeline).
4. Save, reopen, export a short review file, and check its path, duration,
   dimensions, sound and complete ending. Watch and listen to it.
5. Record each operation as **supported**, **UI fallback** or **unavailable**.
   Name the unsupported operation instead of calling the whole editor connected.

Community connectors can have different capabilities and trust boundaries from
vendor tools; choose one only for a stated need and test it separately. The pack
does not bundle a connector or change any editor setting automatically.
