# Editor Connections

**Checked 2026-09-28.** Recheck the chosen editor's current official docs and
the installed UI before setup. The same plugin skills can plan an edit across
editors, but they do not create a universal timeline connector. A browser-only
chat cannot inspect a local editor or verify that a project saved.
The routes below describe official integration surfaces. This pack has not
run an end-to-end local automation test in Final Cut, Premiere or CapCut and
does not bundle their connectors. Use the manual or approved Computer Use
route until the user's exact installation passes the smoke test below.

## Choose the route in the intake interview

Keep Final Cut, Premiere, CapCut, Resolve, or another editor the person already
uses if it fits. If they are choosing from scratch, recommend DaVinci Resolve,
then check the current edition, OS, license and connector. Ask for editor and
version, AI app and local tool access, then select **connected**, **manual**,
or **not yet tested**. Do not silently switch editors or install connectors.

| Editor | Current official route | First connection proof and limit |
|---|---|---|
| DaVinci Resolve Studio 21.1 | Blackmagic's vendor-native Resolve MCP and scripting are available in the Studio route. [Studio features](https://www.blackmagicdesign.com/products/davinciresolve/studio) | Follow the [public connection guide](https://github.com/paytonbilodeau/paytons-ai-systems/blob/v4.0.0/14%20AI%20Video%20Editing%20System/guides/RESOLVE%20AND%20MCP.md) for vendor bundle import or client registration. Prove status/read-only query, then a copied-clip edit. Search the installed API before promising an operation. Some Fairlight and visual controls may require the UI. Studio MCP is not a Free-edition feature. |
| Final Cut Pro | [FCPXML, workflow extensions and FxPlug](https://developer.apple.com/documentation/professional-video-applications) | This pack bundles no Final Cut connector. Test an FCPXML round trip if you choose that route; Apple's [timeline proxy](https://developer.apple.com/documentation/professional-video-applications/interacting-with-the-final-cut-pro-timeline) is limited. Otherwise guide the person through verified UI actions or approved Computer Use. Do not promise full timeline automation. |
| Premiere Pro | [UXP plugin and versioned Premiere DOM](https://developer.adobe.com/premiere-pro/uxp/) | This pack bundles no UXP connector. Structured control needs a separately installed, purpose-built plugin with each required [DOM method](https://developer.adobe.com/premiere-pro/uxp/ppro-reference/) checked against the installed version. Until then, use manual editing or approved Computer Use. |
| CapCut | [CapCut x Codex](https://www.capcut.com/tools/capcut-x-codex) is an official connected route | As of this check it is outside the US and varies by desktop app, account and region. If unavailable, use manual editing or approved Computer Use; do not promise connected control. Prove authorization and a disposable draft before relying on it. CapCut does not call it a generic MCP. |
| Another editor or unavailable connection | Manual checklist guided by this pack | The person performs named steps in the editor and reports or supplies project/export evidence. Label the result human-performed, not AI-controlled. |

On a local Resolve Studio route, inspect the current vendor instructions and
UI for **External scripting: Local** and **Automatic scripted actions: Allow
safe**. Test only the named project. Network scripting is unnecessary for this
local workflow. Do not toggle wider system security settings to make a
connector appear. Editor permissions and the AI app's computer access are
separate checks.

## Connection smoke test

1. Record editor, edition, version, OS, AI app, connector and official docs
   date in [PROJECT INTAKE](../templates/PROJECT%20INTAKE.md).
2. Verify what the assistant can read and run. Query project or app status
   without changing it. If that fails, use the manual route.
3. Create a disposable project using a copy of a short clip. Import it, make
   one reversible linked video/audio cut, and check sync.
4. Save, reopen, and export a short review file. Confirm its file path,
   dimensions, duration, sound, and complete ending. Watch and listen to it.
5. Record each operation as **supported**, **UI/manual fallback**, or
   **unavailable**. Name the unsupported operation instead of claiming the
   whole editor is connected.

Check current requirements before a new install or paid edition. Community
connectors can have different capabilities and trust boundaries from vendor
tools; choose one only for a stated need and test it separately. The pack does
not bundle an MCP server or change any editor setting automatically.
