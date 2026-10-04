# Editor Playbook: DaVinci Resolve

Version details are a dated snapshot. Have the AI check current official docs
and the installed edition before using a version-specific command. Any smoke
test below is an assistant-run capability check, not homework for the user.

**Checked October 3, 2026** against the installed Resolve Studio 21.1 (build
21.1.0.17), its bundled scripting stubs, its bundled MCP server and the current
Blackmagic release notes. Labels: **documented** (Blackmagic manual, readme,
release notes or stubs), **verified** (read live from an installed copy),
**reported** (credible third party), **opinion** (a starting value, not a fact).
Resolve changes several times a year. Recheck the version before trusting a
shortcut or a feature name.

## 1. What edition and version you are dealing with

- 21.1 shipped September 8, 2026. No 21.2 or 22 existed when this was checked
  (documented). Confirm with Help > About or `resolve.GetVersionString()`.
- **Python scripting and the bundled MCP server are Studio-only from 21.1.**
  Blackmagic's 21.1 notes say advanced scripting now requires Studio
  (documented). On the free edition the agent works through file import and
  computer use, not a live connection.
- Studio-only features that matter for a talking head: Voice Isolation,
  Dialogue Separator, Audio Assistant, Music Remixer, IntelliCut (remove
  silence), transcription and text-based editing, Create Subtitles from Audio,
  AI Animated Subtitles, Magic Mask, Smart Reframe, SuperScale, UltraNR, Film
  Look Creator, IntelliScript, hardware H.264/H.265 encoding (documented).
  ColorSlice, Color Warper, Resolve Color Management, Fusion, Fairlight EQ
  and dynamics are in the free edition (documented). Dialogue Leveler in Free
  is reported; verify availability on the installed edition before relying on it.
- Free edition caps output at 3840x2160 and 60 fps (documented).

## 2. The three control routes, in order of preference

### Route A: the bundled MCP server (Studio 21.1 or later)

Resolve ships `ResolveMCP` inside the app bundle and a **File > Setup AI
Assistants** menu that writes the configuration for Claude Desktop, Claude Code
and Codex (documented, manual chapter "Using DaVinci Resolve with AI
Assistants"). It is a thin server: 14 tools (verified). The important ones:

| Tool | Use |
|---|---|
| `get_resolve_status`, `launch_resolve` | Confirm the app is running before anything else |
| `get_whats_new(since)` | Read the vendor changelog for features newer than the model's training |
| `search_scripting_api(pattern)`, `get_scripting_api(types)`, `get_scripting_docs(section)` | Discover the exact method and property names before calling them |
| `run_script(script)` | Sandboxed Python against the full scripting API; `resolve` and `project` are pre-injected; set `result` to return data |
| `run_script_unsafe` | Same API plus filesystem and subprocess access; use only when the task needs to read media or run ffmpeg |
| `list_luts`, `generate_lut`, `list_dctls`, `update_dctl` | LUT and DCTL tooling inside Resolve's LUT folder |

Preferences the user must set once: Preferences > System > General, **External
scripting using: Local** and **Automatic scripted actions: Allow safe**
(documented). Nothing else. Do not enable network scripting for a local
workflow.

Known trap (verified October 3, 2026): if Resolve is sitting on the Project
Manager with no project open, the API reports no database and no page, and
`CreateProject`, `LoadProject` and `OpenPage` all return nothing. Open any
project (or create one in the UI) before scripting. The vendor readme also
warns that scripts fail during startup.

### Route B: the bundled Python interpreter

`ResolvePython` ships with 21.1 (macOS:
`/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/ResolvePython`;
Windows: `ResolvePython.exe` under the install folder; Linux
`/opt/resolve/bin/ResolvePython`). `import DaVinciResolveScript` works without
environment variables (documented). It has no pip, so keep analysis tools in a
separate Python and use this one only for Resolve calls.

### Route C: file import plus computer use

Works on every edition. Generate an FCPXML, EDL or FCP7 XML from a reviewed cut
list with the pack's exporter (see [CUT LIST EXPORT](CUT%20LIST%20EXPORT.md)),
then File > Import > Timeline, or `MediaPool.ImportTimelineFromFile` on Studio.
Use computer use for the UI-only steps listed in section 4.

## 3. What the scripting API can do (21.1 stubs, documented)

Build timelines from source ranges; it does not trim existing items in place.

| Need | Call |
|---|---|
| Import media | `MediaPool.ImportMedia([{"FilePath": path}])` or a plain list of paths |
| New timeline | `MediaPool.CreateEmptyTimeline(name)`, `ImportTimelineFromFile(path, {"timelineName": ..., "importSourceClips": True})` for AAF, EDL, XML, FCPXML, DRT, ADL and OTIO |
| Place a source range | `MediaPool.AppendToTimeline([{"mediaPoolItem": item, "startFrame": a, "endFrame": b, "recordFrame": r, "trackIndex": 1}])`, one call per range when the same media repeats; omit `mediaType` to keep linked audio (observed on 21.1.0.14 that a batch call kept only the first span of one media item; retest after updates) |
| Remove with ripple | `Timeline.DeleteClips(items, True)` |
| Read the cut back | `Timeline.GetItemListInTrack("video", 1)`, then `GetStart()`, `GetEnd()`, `GetSourceStartFrame()`, `GetSourceEndFrame()`, `GetLeftOffset()`, `GetRightOffset()` |
| Fades and transitions | `TimelineItem.SetFades({"FadeIn": f, "FadeOut": f})`, `AddTransition({"type": "Cross Dissolve", "category": "simple", "position": "start", "duration": frames})` |
| Transform and punch-in | `SetProperties({"ZoomX": 1.15, "ZoomY": 1.15, "ZoomGang": True, "Pan": x, "Tilt": y})`; `DynamicZoomEnabled` and `DynamicZoomEase` for a start-to-end push; arbitrary keyframes are UI or Fusion |
| Clip audio | `SetProperties({"AudioVolume": dB, "AudioVoiceIsolationEnabled": True, "AudioVoiceIsolationAmount": 70, "AudioDialogueLevelerEnabled": True, "AudioDialogueLevelerMode": resolve.DIALOGUE_LEVELER_MODE_OPTIMIZE_MODERATE_LEVELS})` on the active timeline only |
| Normalize | `Timeline.NormalizeAudioLevel(items, {"normalizationMode": "ITU-R BS.1770-4", "targetLoudness": -16.0, "setLevelMode": resolve.NORMALIZE_AUDIO_SET_LEVEL_RELATIVE})`; read `GetNormalizeAudioModes()` first |
| Transcript | `MediaPoolItem.TranscribeAudio(useSpeakerDetection)`, then `GetTranscription()` returns segments with word start and end timecodes; "(...)" marks silence |
| Subtitles | `Timeline.CreateSubtitlesFromAudio({"captionPreset": resolve.AUTO_CAPTION_SUBTITLE_DEFAULT, ...})`; chars per line 1 to 60, default 42 |
| Markers | `Timeline.AddMarker(frame, "Blue", name, note, duration, customData)`; `customData` is invisible in the UI and ideal for machine tags |
| Color | `TimelineItem.GetNodeGraph().SetLUT(nodeIndex, lutPath)`, `SetCDL({...})`, `ApplyGradeFromDRX(path, mode)`, `CopyGrades(targets)`, `CreateMagicMask("F")` (clicks cannot be placed by API) |
| Export project state | `Timeline.Export(path, resolve.EXPORT_FCPXML_1_10, resolve.EXPORT_NONE)`; also EDL, FCP7 XML, OTIO, CSV |
| Render | `Project.LoadRenderPreset(name)` or `SetRenderSettings({...})`, `AddRenderJob()`, `StartRendering([jobId])`, `GetRenderJobStatus(jobId)`; `RenderWithQuickExport("YouTube", {...})` |
| Keyboard preset | `resolve.GetCurrentKeyboardPreset()`, `ExportKeyboardPreset(name, path)` before trusting any default shortcut |

Not in the API (documented by absence): trim, roll, slip, slide, split or razor
on an existing item; playback control; Fairlight track EQ, dynamics, de-esser,
noise reduction or plug-in parameters; Lift, Gamma, Gain, curves, qualifiers or
window setters; Text+ text (reachable only through the Fusion composition
object); subtitle styling; any UI click. Timeline playback frame rate is
read-only in the stubs, so set Project Settings > Master Settings > Playback
frame rate by hand when a scripted 30 fps project previews at 24.

Verification habits that paid off: read properties while the target timeline is
active; `SetTrackEnable(..., False)` has returned success while the track kept
playing, so disable backup audio items with `SetClipEnabled(False)` and check
the render has no doubled voice; save, reopen and read back fades.

## 4. Computer use: what the UI needs from you

Confirm the active keyboard preset first. Blackmagic's defaults are below; many
editors remap Ripple Start/End to Playhead to Q and W and Split to S because the
defaults need two hands (reported from several courses). Verify in DaVinci
Resolve > Keyboard Customization (Option-Command-K), search "All Commands".

| Action | Default (macOS; Command becomes Ctrl on Windows and Linux) | Source |
|---|---|---|
| Play reverse, stop, play | J, K, L; Shift-J and Shift-L fast; K held with J or L for frame steps | documented |
| Mark In, Out; clear both | I, O; Option-X | documented |
| Selection, Trim Edit, Dynamic Trim modes | A, T, W | documented |
| Blade tool; Split Clip at playhead | B; Command-\ | documented |
| Razor selected clips at playhead | Command-B | reported, verify |
| Delete and leave gap; Ripple delete | Delete; Forward Delete (Shift-Delete in community guides) | documented, reported |
| Trim Start / Trim End to playhead | Shift-[ / Shift-] (ripples in Trim mode, resizes in Selection mode) | documented |
| Ripple Start / Ripple End to playhead | Command-Shift-[ / Command-Shift-] | documented |
| Select edit point, choose side, nudge 1 or 5 frames | V, U, comma and period, Shift with them | documented |
| Extend edit; toggle slip or slide | E; S | documented |
| Select clips forward on track | Y | documented |
| Snapping; linked selection | N; Command-Shift-L | documented |
| Add default transition; match frame | Command-T; F | reported |
| Add marker; modify marker | M; Shift-M | documented |
| Zoom to fit; detail zoom | Shift-Z; Option-Shift-Z | documented |
| Pages | Shift-2 Media, Shift-3 Cut, Shift-4 Edit, Shift-5 Fusion, Shift-6 Color, Shift-7 Fairlight, Shift-8 Deliver | reported |
| Color page: serial node, parallel node, toggle grade | Option-S, Option-P, Shift-D | reported, consistent across colorists |
| Undo, redo | Command-Z, Command-Shift-Z | documented |

Rules for a vision-and-keyboard agent in Resolve (opinion, consistent with the
official computer-use guidance of both assistants):

1. Move the playhead by typing timecode into the timeline timecode field, then
   act at the playhead. Do not drag clip edges; one frame is smaller than a
   screenshot pixel at normal zoom.
2. Set a known state: Selection mode (A), snapping as needed, auto-select on the
   target tracks only, lock music tracks before ripple operations.
3. Read back every change in the Inspector or Edit Index, zoomed, before the next
   step. A click that did not land cascades into wrong deletes.
4. Use the Effects search (Shift-Space on any page) and the Workspace > Console
   for one-line Python instead of hunting through menus.
5. Reserve the mouse for the few things only the UI does: Magic Mask clicks,
   Fairlight plug-in parameters, Text+ styling, Deliver dialog options, trim
   editor nudges.

## 5. The talking-head workflow in Resolve, in order

1. **Project.** Create it with a media location path. Match the timeline frame
   rate to the camera and check Playback frame rate too. Color management: RCM
   automatic (DaVinci YRGB Color Managed, SDR Rec.709) for one camera, or
   manual YRGB with a DaVinci Wide Gamut Intermediate timeline and a node-level
   Color Space Transform in and out (reported from Mostyn and Kelly).
2. **Proxies when needed.** Timeline Proxy Mode for a little slowness, Render
   Cache for a few heavy clips, Optimized or Proxy media for a whole project;
   Playback > Proxy Handling > Prefer Proxies (documented).
3. **Transcript first.** Studio transcription of the source clip (AI Tools or
   `TranscribeAudio`), reconcile word gaps with the waveform, then decide the
   cuts in source time. Resolve 20.2 added Ripple Delete Silence for a selected
   clip and IntelliCut Remove Silence exists on Studio (documented); use them as
   a first pass, then review every join.
4. **Assemble from ranges.** `AppendToTimeline` one range per call (Studio) or
   import the exporter's FCPXML, then do the fine pass with the Trim Editor's 1
   and 5 frame nudges and Dynamic Trim (W) with JKL to hear the join.
5. **Punch-ins.** Dynamic Zoom with Ease In and Out for a one-move push;
   Inspector Zoom keyframes when the move needs a hold. Keep 4K to 1080p punches
   between 110 and 130 percent of the base; on a 4K timeline from 4K source stay
   near 105 to 125 percent (opinion; see the craft numbers reference).
6. **Dialogue chain (Fairlight).** Clip gain to match takes, then repairs,
   Voice Isolation only if the room needs it (start 35 to 50 for a good shotgun,
   70 to 80 for a noisy room, lower if consonants vanish), Dialogue Leveler
   (Optimize Moderate Levels, Lift Soft Dialogue off on noisy sources), EQ cuts
   before boosts, light compression, true-peak limit at -1 dBTP. Use Leveler on
   clips or on the track, not both. Values and reasons are in
   [SOUND AND COLOR NUMBERS](SOUND%20AND%20COLOR%20NUMBERS.md).
7. **Color.** Node order: CST in (or RCM) > balance and exposure > contrast >
   saturation > parallel fine-tune nodes > power windows > look > CST out to
   Rec.709 (reported, Mostyn). Save the empty labelled tree as a PowerGrade and
   apply it to every clip; grade one shot, grab a still, copy with middle-click
   or `CopyGrades`. Shift-D toggles the grade for a sanity check.
8. **Graphics behind the person (Studio).** V1 original, V2 graphic, V3
   duplicate of the clip. On V3, Color page Magic Mask on the person, Track
   Forward, add an Alpha Output and connect the key; refine with Matte Finesse.
   Resolve 21 can Render in Place a Magic Mask as an external matte for reuse
   (documented). A black result means V1 is missing. Keep one audio path.
9. **Titles and captions.** Text+ for titles (shading element 2 is the outline,
   element 3 the drop shadow). Timeline > AI Tools > Create Subtitles from
   Audio (Studio) with music tracks muted first; fix words; Update Word Timings
   so AI Animated Subtitles stay in sync; export subtitles as a sidecar with the
   render job (`SubtitleFormat` SeparateFile) or burn them in for shorts.
10. **Vertical derivative.** Duplicate the timeline, custom 1080x1920 timeline
    settings, mismatched resolution "Scale full frame with crop", Smart Reframe
    with a reference point (Studio), then check captions and demos at phone size.
11. **Deliver.** YouTube 4K: MP4, H.264 High (or H.265), AAC 48 kHz, same frame
    rate as recorded, 35 to 45 Mbps at 24 to 30 fps and 53 to 68 Mbps at 48 to
    60 fps (Google's published upload numbers, documented); 1080p 8 Mbps (12 at
    high frame rates). Resolve's YouTube preset covers 720p to 2160p and can
    upload with chapter markers (reported). Render through job IDs, never
    indices, and probe the finished file for duration, frame rate and loudness.
12. **Archive.** ProRes 422 HQ at timeline resolution with all audio tracks, cut
    from the master that has not been through any external audio service, so a
    later derivative is never processed twice.

## 6. Smoke test before promising anything

1. `get_resolve_status`; launch if needed and wait for a loaded project.
2. `run_script`: print `resolve.GetVersionString()`, `resolve.IsStudio()`, the
   current project name and `resolve.GetCurrentKeyboardPreset()`.
3. Create a scratch project, an empty timeline, import one copied clip, append
   two ranges with explicit record frames, read the track back, ripple delete
   the first item and read it again.
4. `GetRenderPresetList()` to confirm presets are visible, then render a 10
   second range to a known folder and probe the file.
5. Delete the scratch project. Report the printed values, not "done".

## 7. Learning path

Three courses worth the time (views and dates as of October 3, 2026, reported
from public metadata; links in [LEARNING PATH](LEARNING%20PATH.md)):

- Beginner: Casey Faris, "Introduction to DaVinci Resolve - Full Course for
  Beginners" (5 h 10 min, about 3.2 million views; Blackmagic certified
  trainer). His one-hand remap of Q, W and S for cutting silence is the fastest
  jump-cut rhythm in Resolve.
- Advanced: Darren Mostyn's node tree and Resolve Color Management videos
  (BBC and Netflix colorist, Blackmagic Master Trainer) and DaVinci Dojo's
  3 h 50 min Fairlight course for the whole audio page.
- Expert: Cullen Kelly, "The simple thing most colorists never learn" (May
  2026) for image formation, pivot contrast and saturation in HSV; Kevin
  Stratvert's Fusion course for reusable lower thirds.

## 8. Open questions

Whether Command-B is Razor in the factory preset is reported, not found in the
manual's tables. Console scripting on the free edition after 21.1 is claimed by
one blog and not confirmed by Blackmagic. The API observations about exclusive
end frames and single-span batch appends were recorded on 21.1.0.14 and should
be retested on the installed build before an agent relies on them.
