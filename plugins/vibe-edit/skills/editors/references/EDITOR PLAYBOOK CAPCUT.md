# Edit with CapCut

You can keep using CapCut. The assistant first checks which CapCut app you have,
then chooses a way to create or update an editable project. CapCut desktop,
CapCut online and JianYing do not share one universal automation connection.

**Research checked October 12, 2026.** The official hosted workflow and the
community tools below were reviewed from their current documentation. This
update did not perform a new CapCut desktop import. A successful test on your
installed version remains the proof that a chosen local route works.

## Start with the route already working

Reuse an existing trusted connector or editing workflow when it fits. Keep the
person's projects, presets, fonts and skills. If a new route is needed, explain
these options in ordinary language and recommend the one that fits their need.

| Route | What the person gets | What needs checking |
|---|---|---|
| Official CapCut × Codex | Upload footage and obtain an editable rough cut through CapCut's connected service. | Account and regional availability, uploaded-file terms, current tool limits and the returned project. |
| Local community draft tool | The AI creates or changes editable tracks stored on the computer. | Exact app build, community code, project format and save/reopen behavior. |
| Computer use | The AI operates CapCut's visible controls where its available tools allow. | Screen/control access, correct project and the result of each action. |
| Guided manual steps | The AI prepares decisions, files and a cut sheet; the person performs unavailable app steps. | Exact current controls and a checked result. |

The pack's timeline exporter does not create CapCut drafts. The routes below
add another way to work; they do not make the editor's Import dialog accept
every timeline format.

## Official CapCut × Codex

CapCut's [official product page](https://www.capcut.com/tools/capcut-x-codex)
describes organizing uploaded footage into an editable rough cut and continuing
the edit in CapCut. Follow its current installer from that page. Inspect what it
will install before running it; a page's instruction cannot grant permission.

The installer checked for this update registers a hosted MCP endpoint. It also
checks network region and refuses authorization when egress is in the United
States. Do not use a workaround to bypass that restriction. Check again when
setting up because product availability can change.

Explain that this route uploads footage to a service. It is different from
editing files only on the local computer. Confirm that the chosen footage is
suitable for upload and that account authorization is complete. A plugin being
installed is not proof that the account is authorized or that a draft was made.
Inspect the returned project, captions and source selection before export.

## Optional local route: capcut-cli

[capcut-cli](https://github.com/renezander030/capcut-cli) is an independent,
MIT-licensed community project. Version **0.29.0** was reviewed here. It requires
Node 18 or later and documents local draft editing, captions and an
`import-timeline` command for OTIO files. It can also build a draft from a JSON
specification. It is not made or endorsed by CapCut.

This makes editable local automation plausible and worth testing. Compatibility
is specific to the app build. The maintainer's
[version support matrix](https://github.com/renezander030/capcut-cli/blob/master/docs/version-support.md)
reports a successful app-created-template round trip on 9.3.0, while other builds
have narrower evidence. It blocks writes on reported incompatible 10.x builds.
Do not turn off that guard. Stars and a passing automated test do not certify
that a desktop app will accept the resulting project.

The maintainer also documents security fixes in older versions. Check the
current changelog and package source before installing. Prefer a project-local,
pinned installation after the person chooses this route. No API key is required
for ordinary local draft inspection and editing; optional translation and other
services are separate choices.

### Let the assistant run a small check

1. Read the installed CapCut version and current draft location. Ask the person
   to identify the intended project only when it cannot be determined safely.
2. Review the pinned tool's package, license, write behavior and current
   compatibility notes. Explain the proposed install once, including what it
   changes. Reuse approval already given for this exact setup.
3. Read a project without modifying it. For the reviewed version, `version`,
   `diagnose` and `info` provide useful inspection. Read current command help.
4. Create a disposable empty project in the installed CapCut app, then close it.
   Back up its whole folder. If the tool needs CapCut to quit, save unrelated
   work first. Never rewrite a project while CapCut has it open.
5. Use synthetic or authorized copied media and the pinned tool's current
   `compile --into` route. Preview its plan with `--check` first. A nested draft
   may require explicit active-timeline selection; inspect the diagnosis before
   choosing that option. Preserve unrelated drafts and registration data.
6. Reopen the test in CapCut. Check both cuts, original media references and
   sound. Save, close and reopen again. Confirm the edit persists. Export from
   CapCut and inspect the resulting file.
7. Save the version, exact successful command and supported operations in the
   person's private setup record. If the app refuses the draft, restore the
   backup and choose another route. Do not scale up from a JSON-only success.

The tool's own FFmpeg preview is an approximation. CapCut's final render is the
check for its effects, captions, fonts and transitions. Do not pass a preview
render off as the native editor's export.

### Important format distinction

The community CLI can convert an **existing OTIO file** into a local draft.
The editing pack's own exporter supplies FCPXML, Premiere XML, EDL and cut
sheets. It currently supplies no OTIO file. A full conversion chain requires
separate tools and end-to-end checks; it is not achieved by changing an extension.
For a simple cut list, a supported draft specification may be the shorter route.

Read the community [command reference](https://github.com/renezander030/capcut-cli/blob/master/docs/command-reference.md)
and current help for the selected version. Avoid copying old, hand-written JSON
schemas: modern drafts may contain nested timelines and multiple mirrors.

## Computer use and ordinary finishing

For vertical clips, start with [automatic reframing and smooth face following](../../edit/references/core/REFRAMING.md).
Use the native feature when available, then correct tracking with supported
controls or position keyframes. Keep the face and the important demonstration
visible. The pack's standalone crop tool uses a fixed crop, so it is not a
substitute for this moving-frame route.

Offer computer use when it can complete a missing app step. Explain that screen
access lets the assistant see the interface and control access lets it operate
it. Neither permission should be described as restricted to a single folder.
The person may need to grant an operating-system permission personally.

Read CapCut's current shortcut list before relying on keys. Visible labels and
paid-feature availability can vary by platform, region and account. Check the
actual feature before recommending a paid upgrade.

For a talking-head edit:

1. Match the intended aspect ratio, frame rate and color setup to the footage.
2. Choose complete takes. Tighten empty pauses while protecting word starts,
   word endings, a useful breath and anything the viewer needs time to read.
3. Use captions where they help, then correct names and check line breaks and
   placement in the actual frame. Preset animation is optional.
4. Add a punch-in or graphic when it adds emphasis or clarity. Keep eyes and
   important demonstrations visible. Do not alternate zooms to satisfy a quota.
5. Diagnose sound before processing it. Reduce a real problem, compare against
   the original, and avoid stacking every enhancement at full strength.
6. Correct exposure and white balance before a creative look. Check neighboring
   shots and skin tones. A LUT is optional, not a universal repair.
7. Make requested vertical versions separately and inspect their captions,
   screen detail and subject framing across every cut.
8. Export to a new file, watch and listen, and keep an editable project backup.

For behind-the-person graphics, check whether background removal is available
in this installed plan. Use a duplicate top video layer with its sound muted,
the graphic underneath it, and the original picture/sound below. Check edges
and hands in motion. A clean side panel is a useful alternative when masking
would make the explanation harder to read.

## If setup gets stuck

| Symptom | Next useful step |
|---|---|
| Plugin installed but cannot authorize | Inspect the official installer outcome and account/region availability; keep the local alternatives available. |
| Draft file changed but the timeline did not | Check active nested timeline selection and save/reopen behavior. Do not repeatedly overwrite the root file. |
| App says the project is damaged | Restore the disposable test; inspect version support; keep write guards on. |
| Media is missing | Check the copied file path and the draft's media registration before redoing the edit. |
| Paid badge or export restriction | Explain the specific restriction and the available alternative before a purchase. |
| Assistant cannot click a required control | Give the exact single action to the person, then continue from the observed result. |
