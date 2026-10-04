# Editor Playbook: CapCut Desktop

**Checked October 3, 2026** against CapCut's help and tool pages, the CapCut
hosted installer for its Codex plugin, an installed CapCut 9.5.0 for Mac (its
draft files were read, not changed) and the community draft tools. Labels:
**documented** (CapCut), **verified** (read from the installed app or its
files), **reported** (credible third party), **opinion**. CapCut publishes no
versioned changelog, hides features behind plan tiers that vary by region, and
changes its project format with the app. Verify on the machine in front of you.

## 1. Version and plan facts

- Desktop is in the 9.x series (9.5.0 for Mac, September 24, 2026; 9.4.0 for
  Windows, September 5, 2026; reported from download trackers, verified locally
  for 9.5.0). The Mac App Store "CapCut - Video Editor" listing (19.x) is a
  different build track. Anything written for 5.x to 7.x needs rechecking.
- Plans in 2026: Free, Standard (about $9.99 a month), Pro (about $19.99 a
  month) and an Ultra tier (reported). CapCut's own Pro PC page lists Auto
  Captions, Auto Removal, Normalize Loudness, Enhance Voice, Reduce Noise and
  Color Correction among Pro features (documented), yet free-plan creators use
  Auto Captions and Normalize Loudness in 2025 to 2026 tutorials. Treat the
  free versus Pro boundary as per-feature and region-dependent, and check for
  the diamond badge in the UI. Auto Reframe is Pro on every platform
  (documented help page, April 2026). Desktop 4K export is reported free by two
  independent 2026 sources; confirm on the machine.
- The web editor cannot run Auto Cut and keeps a subset of shortcuts; its
  projects are server-side (documented and reported). Use the desktop app.
- The 2025 terms controversy: CapCut's June 2025 terms grant a broad license to
  content uploaded to its servers (reported, quoted by several outlets). Local
  editing and local export are not uploads. Keep client footage local: no "Sync
  to a space", no cloud backup, unless the client accepts CapCut's upload terms
  (opinion). US users have been under new joint-venture terms since January
  2026 (reported).

## 2. The control routes

### Route A: the official CapCut plugin for Codex (hosted, outside the US)

CapCut x Codex is a plugin for Codex in the ChatGPT desktop app that registers
a hosted MCP server behind OAuth. It generates material, builds a rough cut
into an editable draft, refines captions, transitions and music in chat, and
opens the CapCut editor (documented). It is free, "available outside the U.S.;
U.S. launch coming soon", and its installer refuses authorization when the
network egress resolves to the United States (documented in CapCut's hosted
installer skill). Where the draft lands, limits and credit use were not
documented when checked. Claude Code has no CapCut connector.

### Route B: write a draft file (unofficial, works locally)

CapCut desktop stores projects as plain JSON on 9.x international builds
(verified for 9.5.0). Location:

- macOS: `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/<draft>/`
- Windows: `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\<draft>\`

Inside: `draft_info.json` (on 9.5.0 Mac the index `root_meta_info.json` points
at this file; other builds use `draft_content.json`), `draft_meta_info.json`,
a `.bak` copy, `Timelines/`, `Resources/` and settings files (verified). Time
values are microseconds; a jump cut is two consecutive segments on the primary
video track that share one `material_id` with non-overlapping `source_timerange`
windows; captions are text-track segments; keyframes live in each segment's
`common_keyframes` with `KFTypeScaleX`, `KFTypeScaleY`, `KFTypePositionX`,
`KFTypePositionY` and `KFTypeAlpha`; emit ScaleX and ScaleY together (reported
from the maintainers' schema notes, consistent with the verified file).

Rules the maintainers agree on (reported):

- Never write a draft while CapCut has it open; CapCut overwrites the file on
  its next save. Close the project, write, reopen.
- Back up the draft folder first. Preserve unknown fields verbatim.
- Keep `draft_content.json`, the root `draft_info.json` and the
  `Timelines/<guid>/draft_info.json` mirror consistent, or CapCut may open a
  stale copy and discard new tracks on close.
- Projects downloaded from the template library and JianYing 6+ drafts are
  encrypted; only locally created drafts are editable.
- Export cannot be triggered from outside the app on CapCut international.

Tools: pyJianYingDraft and pyCapCut (Python), VectCutAPI (HTTP and MCP wrapper,
writes a `dfd_` folder you copy into the drafts root), capcut-cli and
capcut-cli-david (Node, edit drafts in place, schema docs, Claude Code skill),
small MCP wrappers over VectCutAPI. All unofficial; version-pin and test with a
disposable draft before relying on one.

### Route C: computer use

CapCut is a Chromium plus Qt hybrid with a custom UI, so accessibility-tree
automation is unreliable and screenshots with coordinates are needed (opinion
from the tool survey). Good for well-defined dialogs: Auto captions, Auto
reframe, Transcript delete, Export. Not for bulk cutting.

### Route D: guide the human

CapCut's labels are stable and the courses below are good; a text walkthrough
with exact labels works. The pack's cut sheet (from the exporter) lists every
split and delete point in CapCut-friendly timecode.

## 3. Computer use: layout and shortcuts

Layout (documented resource page and consistent tutorials): top tabs Media,
Audio, Text, Captions (newer builds), Stickers, Effects, Transitions, Filters,
Adjustment, plus AI entry points; Player in the center with playback quality
("Full" button) and Ratio; right-side property panel whose tabs change by
selection (Video: Basic, Remove BG, Mask, Stabilize; Audio: Volume, Fade,
Normalize loudness, Enhance voice, Reduce noise, Isolate voice; Speed;
Animation; Adjust: Basic, LUT, Adjust, Curves, HSL, Color wheel, Mask); Timeline
at the bottom with its own toolbar (split, delete, marker, freeze frame,
Transcript button) and a keyboard icon that opens CapCut's own rebindable
shortcut list. Screenshot that list before using shortcuts.

| Action | Mac (Windows uses Ctrl) | Confidence |
|---|---|---|
| Split at playhead | Command-B | confirmed in 2025 to 2026 transcripts |
| Delete left of playhead (ripple); delete right | Q; W | confirmed |
| Play, pause; undo; redo | Space; Command-Z; Command-Shift-Z | confirmed |
| Add marker | M | confirmed (one cheat sheet lists M as mute; verify) |
| Zoom timeline | Command-scroll, or + and - | confirmed |
| Step frames | Left and Right Arrow; Shift for a jump | confirmed |
| Split every track; fit timeline | Command-Shift-B; Shift-Z | cheat sheets, verify |
| Delete; delete and close gap | Delete; Command-Shift-D | cheat sheets, verify |
| Export; Import; New project | Command-Shift-E; Command-I; Command-N | cheat sheets, verify |
| Mark in and out; snapping; enable clip | I and O; N; V | cheat sheets, verify |
| Speed panel; keyframe panel | Command-R; Option-K | cheat sheets, verify |

Procedures the agent can run or supervise (documented paths, reported details):

- **Auto captions:** select the clip; Text (or Captions) > Auto captions >
  spoken language and audio track; tick Identify filler words if wanted;
  Generate. Style with Presets, Templates (portrait-oriented), Bubble, Effects;
  Animation for caption animations. Fix words by double-clicking a block.
- **Transcript editing:** Transcript button in the timeline toolbar; silences
  are marked; highlight words or silence and Delete; Restore undoes. One-click
  filler removal reports a count (Pro where gated); review every join. Primal
  Video describes a pause threshold starting near 1.8 s (reported).
- **Caption-gap method when AI tools are gated:** generate Auto captions, treat
  gaps between caption blocks as silence, place the playhead at the gap edges
  and use Command-B then Q or W.
- **Auto reframe (Pro):** finish the structural edit first; select clip >
  Video > Auto reframe > 9:16, stabilization, camera speed > Apply; check
  tracking at start, middle, end and across cuts; move captions into the
  vertical safe area.
- **Export:** name, destination, Resolution (1080p or 4K to match the source),
  Bit rate Recommended or Higher, Codec H.264 (HEVC when size matters), Format
  MP4, Frame rate matching the project, optional Captions export (SRT), Check
  for copyright, Edit cover. Then probe the file with ffprobe.

## 4. The talking-head and shorts workflow in CapCut, in order

1. **Project.** Create, then Modify in the details panel: aspect ratio (16:9 or
   9:16), resolution and frame rate matching the camera, color space. Settings >
   Performance > Proxy on for 4K; lower the player quality while editing; export
   uses the originals (reported).
2. **Cut.** Q and W jump cuts at the playhead; Command-B when both sides stay.
   Transcript editing for an hour-long recording; caption-gap method when gated.
   Keep a 1 to 3 frame pad of breath around cuts (opinion). Markers (M) for
   B-roll points; Separate audio for J and L cuts, then compound or group the
   pair so it cannot drift.
3. **Captions.** Auto captions, fix names immediately, style once and save as a
   preset: a heavy geometric sans (Inter Bold, Montserrat, Poppins), uppercase,
   slight negative tracking, soft shadow (low blur, distance about 10, opacity
   about 25), bottom third for 16:9 and center-lower for 9:16 (reported style,
   placement opinion). Subtle pop or fade over bouncing templates for a talking
   head (opinion). Word-level emphasis: individual text layers, one highlighted
   word per line.
4. **Punch-ins.** Scale and Position keyframes: 100 percent at the sentence
   start, 110 to 120 percent 8 to 15 frames later (115 is the common demo
   value), eyes held in place; right-click > Show variable speed animation >
   Quad ease so the move decelerates; cut back to 100 on the next hard cut.
   Alternate 100 and about 115 at jump cuts; stay under about 125 percent on
   1080p sources (opinion).
5. **Graphics behind the presenter.** Duplicate the clip onto the track above,
   Video > Remove BG > Auto removal on the top copy, place the text or graphic
   between them (documented steps). Masks (rectangle, circle, linear with
   feather) with keyframed position to wipe a chart on. Chroma key when a green
   screen exists.
6. **Audio.** Per clip: Normalize loudness first, then Reduce noise, then
   Enhance voice if the room is dull; avoid all three at full strength (reported
   as muffled). Isolate voice for noisy locations (paid where gated). Music under
   speech around -20 to -30 dB, four volume keyframes per spoken section, fades
   on every music and effect clip (reported starting points). CapCut's loudness
   normalization target is not documented; measure the export.
7. **Color.** One Custom adjustment layer across the whole timeline for the
   grade; per-clip Adjust only for exposure or white balance mismatches. Turn on
   the Color oscilloscope (hamburger menu), fix temperature and tint, keep the
   trace off the floor and ceiling, protect skin; LUT (Adjust > LUT > Import
   .cube or .3dl) at reduced Intensity; a light vignette so eyes stay on the
   subject (reported from the color course). Apply to all; Save as preset.
8. **Shorts from the 16:9 master.** Duplicate the project, Ratio 9:16, Auto
   reframe (Pro) or manual scale and position keyframes following the
   presenter, captions moved into the safe band, export 1080x1920 at the
   project frame rate.
9. **Export and back up.** 4K when shot in 4K, else 1080p; H.264 MP4 at
   Recommended or Higher; Check for copyright for library music; verify with
   ffprobe; copy the draft folder from `com.lveditor.draft` to a dated archive
   before closing, because CapCut's own `.bak` rotation and cloud backup are not
   your copy (opinion).

## 5. Smoke test before promising anything

1. Read `root_meta_info.json` in the drafts root; confirm the draft JSON is
   plaintext with `json.loads`. If it is not, this build encrypts drafts; stop
   and use computer use or guidance.
2. In CapCut, create an empty draft at the target resolution and frame rate,
   add the source clip once, quit CapCut.
3. Back up the draft folder. Change `tracks[0].segments[]` to two segments with
   microsecond `source_timerange` and `target_timerange` and the existing
   `material_id`; update `duration`; keep the mirrors consistent.
4. Reopen CapCut and the draft; confirm two segments at the right positions.
   If it is blank or refuses, restore the backup and fall back to the cut sheet.
5. For the official Codex plugin: confirm the account's region first; US egress
   fails authorization by design.

## 6. Learning path

- Beginner: Metics Media, "CapCut Tutorial for Beginners 2026" (64 min, June
  2025, about 471,000 views; a start-to-finish desktop edit). Lerin Nic's
  94 minute full course (January 2026) and Justin Brown's July 2026 desktop
  walkthrough are current alternatives.
- Advanced: Modern Millie, "10 MUST-KNOW Editing Hacks in CapCut (desktop)"
  (October 2025) for talking-head tricks, and Matt Loui, "How to Create Smooth
  Style Captions in CapCut" (August 2025) for word-by-word caption craft with
  exact values.
- Expert: Content Creators, "Master CapCut Color Grading in 30 Minutes"
  (September 2025): scopes, log curves, HSL, LUTs and the free glow trick.

## 7. Open questions

Exact free versus Pro gating per feature and region; CapCut's loudness
normalization target; whether the Codex plugin writes a local draft; HDR export
on desktop; which cheat-sheet shortcuts are defaults in 9.5.
