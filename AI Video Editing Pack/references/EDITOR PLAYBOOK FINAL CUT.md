# Editor Playbook: Final Cut Pro

Version details are a dated snapshot. Have the AI check current official docs
and the installed edition before using a version-specific command. Any smoke
test below is an assistant-run capability check, not homework for the user.

**Checked October 3, 2026** against Apple's release notes, the Final Cut Pro
12.4 user guide, Apple's FCPXML developer pages and an installed copy of Final
Cut Pro 12.4 (its AppleScript dictionary, document types and shipped DTDs were
read directly). Labels: **documented** (Apple), **verified** (read from the
installed app), **reported** (credible third party), **opinion**.

## 1. Version facts

- Final Cut Pro is at **12.4** (September 29, 2026), requires macOS 26.6 or
  later, and costs $299.99 one time or comes with Apple Creator Studio at $12.99
  a month (documented). 11.0 (November 2024) brought Magnetic Mask and Transcribe
  to Captions; 12.0 (January 2026) added Transcript Search, Visual Search and
  Beat Detection; 12.3 (June 2026) added Generate Captions (styled subtitles or
  closed captions), Auto Mask, a rebuilt Match Color and Edit Detection
  (documented). A version 13 was rumored for October 2026 (unverified).
- Apple silicon is required for Transcribe to Captions, Generate Captions,
  Transcript Search, Visual Search and Smooth Slo-Mo; Generate Captions and the
  searches are US English only (documented).
- Since 12.3 proxies default to HEVC and background rendering defaults to Off
  (documented).

## 2. The control routes

### Route A: FCPXML (the only official write path)

Final Cut has no scripting API for editing, no vendor connector, no Shortcuts
actions (verified: no App Intents metadata in the 12.4 bundle) and no
programmatic export. FCPXML is the sanctioned exchange (documented). Import
with File > Import > XML, by double-clicking the file, by dragging it onto the
app icon, or hands-free with:

```sh
open -a "Final Cut Pro" "/path/to/cut.fcpxml"
```

The 12.4 bundle registers the `fcpxml` and `fcpxmld` document types (verified).
Final Cut 12 writes FCPXML 1.14 and reads older versions; write 1.11 to 1.13 for
broad compatibility (documented and verified DTDs 1.0 to 1.14). The pack's
exporter writes 1.11 by default and can validate against Apple's DTD; see
[CUT LIST EXPORT](CUT%20LIST%20EXPORT.md).

Read-back is manual: the person presses File > Export XML (Command-E is Share,
not Export XML), then the agent parses the file. Plan the review around that.

### Route B: AppleScript, read-only (verified)

Final Cut Pro 12.4 ships a small scripting dictionary with one command, `get`,
and the classes library, event, project, sequence and item, exposing names,
ids, durations, frame durations and timecode format. It can confirm that an
imported project exists and how long it is. It cannot edit or export.

### Route C: Workflow Extensions

Apple's SDK lets a signed container app show a panel inside Final Cut, observe
the active sequence, selection and playhead, move the playhead, and hand FCPXML
to Final Cut by drag and drop (documented). It is a developer route, not a
connector a user installs for an agent.

### Route D: computer use

Everything else, including Share and export, Generate Captions, Magnetic Mask
analysis, Smart Conform and Match Color on a chosen frame. Rules in section 4.

### Community tools (reported)

DareDev256/fcp-mcp-server (MIT, about 115 stars) parses, diagnoses and writes
FCPXML, generates rough cuts from local Whisper transcripts, and in live mode
imports through the Open Document Apple event without accessibility scripting;
it reads FCPXML 1.8 to 1.14 and writes 1.13 and was verified by its author
against Final Cut 12.2. Other 2026 projects (dreliq9/fcp-mcp, Poechant's CLI,
elliotttate's server) are small; two have no license. Prefer XML-only modes;
live modes that use System Events need Accessibility permission, which grants
full keyboard and mouse control to that process. Pin a commit and test in a
disposable library.

## 3. FCPXML facts an agent must get right

- Time is a rational number of seconds with an `s` suffix: `1001/30000s` is one
  frame at 29.97, `1/30s` at 30, `5s` five seconds. Decimal seconds such as
  `6.81s` are rejected at import; values off the frame grid insert a gap with a
  warning (documented; the decimal rejection is from an Apple engineer's forum
  reply).
- `offset` is where the clip sits in its parent timeline; `start` is the source
  in-point; `duration` is the length. Each spine clip's `offset` equals the
  previous offset plus duration, so there are no gaps. Markers and keywords
  inside a clip use source time, not timeline time (documented).
- Every `asset` needs a `format` and a `media-rep` with a percent-encoded
  `file:///` URL; supply a stable `uid` so re-imports do not duplicate the clip
  (documented and forum reply).
- Child element order inside `asset-clip` is enforced by the DTD: note, timing,
  video adjustments, audio adjustments, anchored items (titles, captions,
  connected clips), then markers and keywords, then filters. A marker placed
  before a title fails validation and Final Cut rejects the whole file
  (verified by DTD validation).
- Titles reference an installed Motion template by `effect uid`; copy the uid
  from a real Final Cut export, never invent it (documented and opinion).
- Caption roles must embed the format: `"Subtitles?captionFormat=ITT.en"`.
  Generated subtitles from 12.3 are title clips in the Subtitles role, not
  caption elements (documented).
- FCPXML does not carry Magnetic Mask data, render files or analysis data
  (documented statement plus reported specifics). Expect ML features to need
  re-analysis after a round trip.
- Validate before sending: copy the DTD from
  `/Applications/Final Cut Pro.app/Contents/Frameworks/Interchange.framework/Versions/A/Resources/`
  to a path without spaces and run `xmllint --noout --dtdvalid FCPXMLv1_11.dtd cut.fcpxml`.
  Add your own checks the DTD cannot do: every time string matches the rational
  form, every time is a multiple of the frame duration, every ref resolves,
  spine offsets are contiguous. The pack's exporter does the first two.

## 4. Computer use: layout, magnetic timeline rules and shortcuts

Panels (documented): Sidebar (Libraries Command-1), Browser, Viewer,
Inspector (Command-4; Color Command-6; Audio Enhancements Command-8), Timeline
(Command-2 to focus), Timeline Index (Shift-Command-2) with Clips, Tags, Roles
and Captions panes. Effects browser Command-5, Video Scopes Command-7,
Background Tasks Command-9, Command Editor Option-Command-K.

Magnetic timeline behavior (documented):

- Delete ripples everything after the selection and takes connected clips with
  it. Shift-Delete replaces with a gap and keeps timing. Hold Grave Accent while
  pressing Delete to remove a primary clip without its connected clips.
- Trims ripple by default. The Position tool (P) suspends magnetism and leaves
  gaps.
- Trim Start (Option-[) and Trim End (Option-]) trim the clip under the skimmer
  or playhead to that point and ripple. Option-\ is labeled Trim to Selection by
  Apple and described as Trim to Playhead by practitioners; confirm in the
  Command Editor.
- Skimming on means Blade, Trim Start and Trim End act at the skimmer, not the
  playhead. For deterministic automation turn skimming off (S) and position the
  playhead by typing timecode (type a number, or `+` or `-` then a value).
- Delete in the Browser rejects a clip instead of deleting; focus the timeline
  (Command-2) first.
- Blade (Command-B) cuts the primary clip or selection at the skimmer or
  playhead; Blade All (Shift-Command-B) cuts every lane; a through edit (dotted
  line) is removed with Trim > Join Clips.
- Connected clips attach at their first frame; Command-Option-click moves the
  connection point; Create Storyline (Command-G) groups connected clips.

| Action | Default | Source |
|---|---|---|
| Tools: Select, Trim, Position, Range Selection, Blade, Zoom, Hand | A, T, P, R, B, Z, H | documented |
| Connect, Insert, Append, Overwrite | Q, W, E, D | documented |
| Blade; Blade All | Command-B; Shift-Command-B | documented |
| Delete (ripple); Replace with Gap | Delete; Shift-Delete | documented |
| Trim Start; Trim End; Trim to Selection | Option-[; Option-]; Option-\ | documented |
| Extend Edit; Change Duration | Shift-X; Control-D | documented |
| Range start and end; clear; select clip range | I, O; Option-X; X | documented |
| Select clip under playhead | C | documented |
| Play, reverse, JKL, play around | Space, Shift-Space, J K L, Shift-? | documented |
| Next and previous edit | Down and Up Arrow (or ' and ;) | documented |
| Zoom to fit; vertical fit | Shift-Z; Option-Shift-Z | documented |
| Skimming; audio skimming; snapping | S; Shift-S; N | documented |
| Marker; marker and modify; to-do and chapter via modify | M; Option-M | documented |
| Favorite; Reject (browser); Unrate; Keyword Editor | F; Delete; U; Command-K | documented |
| Transform; Crop (Trim, Crop, Ken Burns) | Shift-T; Shift-C | documented |
| Add keyframe; Video Animation editor | Option-K; Control-V | documented |
| Expand audio; Detach audio | Control-S; Control-Shift-S | documented |
| Volume up and down 1 dB; relative volume | Control-= and Control--; Control-L | documented |
| Add default title; basic lower third | Control-T; Control-Shift-T | documented |
| Add Magnetic Mask; Magnetic Mask Editor; Add Auto Mask | Control-Command-M; Control-Option-Command-M; Control-Command-K | documented |
| Balance Color; Match Color | Option-Command-B; Option-Command-M | documented |
| Generate Captions > Subtitles; > Closed Captions | Shift-Command-S; Shift-Command-C | documented |
| Detect Edits; Beat Detection | Shift-E; Option-B | documented |
| Share to default destination; Background Tasks | Command-E; Command-9 | documented |
| New Project; New Event; Import Media | Command-N; Option-N; Command-I | documented |

Creators remap heavily (one widely followed instructor uses X for delete, G and
H for trim start and end, C for blade); switch the command set to Default before
automation and read back state in the Timeline Index and Inspector after each
step (opinion).

## 5. The talking-head workflow in Final Cut, in order

1. **Library and events.** One library per video on fast local storage; events
   for Camera, Screen, Audio, Graphics, Music. Import with Leave files in place
   for camera files, From folders keywords on, and decide Visual Search and
   English transcription at import because analysis is slow later (documented).
2. **Project.** Command-N; match the camera (4K 29.97 or 30, stereo 48 kHz); use
   custom settings when the first clip is a screen recording at an odd size.
3. **Proxies only if playback stutters.** HEVC proxy at 50 percent; switch the
   Viewer to Proxy while cutting and back to Optimized or Original before
   export (documented).
4. **Rate and keyword while reviewing.** F favorite, Delete reject, Control-1 to
   Control-9 keywords by topic; Transcript Search ("Includes" for exact words,
   "Is Related To" for concepts) to find a soundbite; keep the interview angle
   alone in its event to scope results (documented and reported).
5. **Rough cut by key.** Select ranges and press E to append. Jump-cut pass with
   skimming off: playhead, Option-[ or Option-], Command-B, Delete. Shift-Delete
   when synced graphics must keep timing. For bulk silence removal import an
   FCPXML cut list from the exporter or a transcript tool, then finish by hand.
6. **Second pass.** J and L cuts with Control-S to expand audio and trim the
   audio edge independently; keep every take until this pass so the best halves
   of two sentences can be spliced (reported).
7. **Punch-ins.** Duplicate-angle feel needs about a 30 percent scale change
   (130 percent) with the eyes aligned by Shift-T and Position Y (reported);
   Ken Burns (Shift-C, Ken Burns mode) for slow pushes, under about 5 percent
   over 10 seconds on faces; Option-K keyframes on Scale for a 2 to 4 frame pop
   to 110 to 115 percent (opinion). Picture in Picture and Callout effects for
   face-over-screen and highlights (documented).
8. **Camera plus screen.** Multicam with the screen as a second angle; Sync
   Selection to Monitoring Angle against the camera, never the reverse; switch
   angles with Option-1 and Option-2 (reported workflow).
9. **Audio.** Dialogue role on the voice, Music and Effects on the rest; Show
   Audio Lanes. On the dialogue component: Voice Isolation only if room noise is
   audible (start 50, lower if hollow), Loudness Amount about 30 to 50 and
   Uniformity 20 to 40, Equalization "Voice Enhance" or a Channel EQ with a low
   cut near 80 Hz, then level (documented controls, opinion values). Final Cut
   has no built-in LUFS meter; measure the export or use an Audio Unit meter.
   Music under speech about -20 to -30 dB on the meters, carved with Channel EQ
   where the voice sits; Range Selection plus a volume change writes the ducking
   ramps (documented). Match Audio (Shift-Command-M) across takes.
10. **Color.** Balance Color (White Balance eyedropper on something neutral),
    Match Color across takes, then one Color Wheels or Color Adjustments
    correction; Enhance Light and Color as a starting point; check skin on the
    vectorscope line (Command-7); Auto Mask > Skin inside a corrector for skin
    secondaries; camera LUT in the Info inspector for log; creative look on an
    adjustment clip (Option-A) over the whole timeline (documented and reported).
11. **Graphics behind the person.** Duplicate the clip, Lift from Storyline,
    Magnetic Mask on the top copy (click subject, Analyze), put the title or
    blurred copy between the layers; negative Feather tightens hair edges
    (documented mechanics, reported recipe).
12. **Titles and captions.** Control-T and Control-Shift-T for defaults; build
    reusable lower thirds in Motion with published parameters and drop zones;
    pre-render heavy animations with alpha. Edit > Generate Captions > Subtitles
    for burned-in styled words (Highlight by Word reads best, opinion) and
    > Closed Captions for an iTT or SRT sidecar; Command-A on one subtitle
    selects all for style changes; Vertical Social Media Safe when cutting
    verticals (documented).
13. **Vertical.** Edit > Duplicate Project As > Vertical with Smart Conform,
    then fix framing with Transform in overscan view and recheck subtitles
    (documented).
14. **Export.** Background rendering is Off by default since 12.3, so Render
    All (Control-Shift-R) before the final playback check; switch proxies off.
    Share > Export File: Format Computer or Video and Audio, H.264 (or HEVC
    10-bit for HDR), highest resolution, Multi-pass when time allows, Include
    chapter markers, captions embedded or sidecar (documented). Compressor for
    several outputs at once; both apps must share a license type (documented).
    Verify the file with ffprobe against the project duration.

## 6. Smoke test before promising anything

1. `ls` the Interchange framework Resources folder to read the newest DTD
   version, then write a two-clip FCPXML at or below it from one copied clip.
2. Validate with xmllint against a plain-path copy of the DTD.
3. `open -a "Final Cut Pro" cut.fcpxml`; confirm the import dialog, choose the
   library, confirm two clips with attached audio.
4. Ask the person to Export XML on the imported project; parse it and compare
   clip count and durations. This is the only read-back path.
5. Record each step as supported, UI fallback or unavailable.

## 7. Learning path

- Beginner: Dylan Bates (The Final Cut Bro), "The Ultimate Beginners Guide To
  Final Cut Pro 11" (42 min, January 2025; Apple certified instructor). Justin
  Brown's 2026 complete guide is the higher-reach alternative.
- Advanced: Dylan Bates, "Editing a Full Video in Final Cut Pro (entire
  workflow)" (70 min, July 2025): a complete talking-head plus screen-recording
  edit including the multicam-with-screen trick, three editing passes and a
  processed-audio round trip. Ripple Training's "Final Cut Pro 12 Deep Dive"
  and "12.3 Full Breakdown" for the new features.
- Expert: Dylan Bates, "How to use Apple Motion 2026" for reusable templates
  with published parameters; Ripple Training's "Color Correction and Grading in
  FCP in Under 60 Minutes" (2022, still the clearest tool tour).

## 8. Open questions

Final Cut 13 timing; whether Magnetic Mask data survives FCPXML in 12.4; the
exact Option-\ label; default shortcuts for assigning Dialogue and Music roles.
