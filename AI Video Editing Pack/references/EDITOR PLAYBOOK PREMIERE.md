# Editor Playbook: Adobe Premiere Pro

Version details are a dated snapshot. Have the AI check current official docs
and the installed edition before using a version-specific command. Any smoke
test below is an assistant-run capability check, not homework for the user.

**Checked October 3, 2026** against Adobe's release notes (current release
26.5.2, September 2026), Adobe's help pages, the UXP developer documentation
and the community bridge projects. Premiere was not installed on the checking
machine, so every statement here is documentary, not reproduced. Labels:
**documented** (Adobe), **reported** (credible third party), **opinion**.
Adobe now calls the product "Adobe Premiere" in its 26.x pages; this playbook
uses both names.

## 1. Version facts that change what the agent can promise

- 26.5.2 is current. Feature releases land roughly every two to three months
  (26.0 January, 26.2 April, 26.3 June, 26.5 September 2026). A 25.6.x branch
  receives only security fixes (documented). Check Help > About; 26.0 and 26.5
  differ materially.
- Features that matter for a talking head, all documented: Text-Based Editing
  with pause and filler-word detection (minimum detectable pause 0.1 s,
  reported by an Adobe community manager); Paper Edit (26.5) to build a sequence
  from selected transcript sentences; Enhance Speech (included in the
  membership, no generative credits); Essential Sound with Loudness Auto-Match
  (targets -23 LUFS for dialogue, reported) and Repair sliders; Auto Color;
  Object Mask (AI person and object masks, 26.0, edge modes 26.2, smoothness
  26.5); Media Intelligence search; Auto Reframe with custom resolution (26.2);
  single-word captions (26.3); Color Management presets (Direct 709 default);
  OTIO import and export (26.0, beta quality per Adobe staff).
- Generative Extend and the Generative Media Tool consume generative credits;
  Enhance Speech, captions, translation, Object Mask, Auto Reframe and
  Text-Based Editing do not (documented, Adobe credit table October 1, 2026).

## 2. The control routes

### Route A: Adobe's own AI Assistant (beta, in-app only)

Window > Assistant (public beta since June 2026). It organizes bins, renames and
labels clips, transcribes, detects slates, adds markers and builds stringouts
and rough assemblies as ordinary editable sequences, with "Always ask" and "Auto
approve" modes (documented). It is not reachable by an external agent. Use it
for the chores it does and keep your own agent for the cut.

### Route B: unofficial MCP bridges (CEP panel inside Premiere)

Adobe has no official connector; a community feature request for one was open
with no reply when checked. The working bridges run a Node MCP server outside
Premiere and a CEP panel inside it that executes ExtendScript. All of them
require **CEP debug mode**, which disables Adobe's extension signature check
(documented in Adobe's CEP cookbook; the installers set it for you). Adobe has
said ExtendScript support was planned "through September 2026" and the
replacement is UXP (documented); the bridges still reported working on 26.5.2
in September 2026. Treat them as working-but-deprecated.

| Project | What it offers | Caveats stated by the maintainers |
|---|---|---|
| hetpatel-11/Adobe_Premiere_Pro_MCP (npm `adobe-premiere-pro-mcp`) | 283 catalogued tools: import, bins, sequences, timeline edits, transitions, effects, keyframes, captions, markers, proxies, color, audio, exports | "Premiere scripting still does not expose every UI operation cleanly"; self-signed panel, not Marketplace approved |
| leancoderkavy/premiere-pro-mcp | 386 tools including ripple delete, slip, trim, split, LUT, export via Media Encoder, caption tracks | No speed or direction setters, no transcript text deletion, no OTIO or EDL by script |
| ayushozha/AdobePremiereProMCP | 1,066 schemas, 74 curated tools; tested on 26.5.2 macOS | Snapshots are audit records, not whole-sequence rollback |

Say to the user in plain words: this disables Adobe's signature check and lets a
local panel run arbitrary ExtendScript. Pin a version. Keep a project backup.

### Route C: UXP plugin (Adobe's supported platform)

UXP for Premiere is official since 25.6 and documented at
developer.adobe.com/premiere-pro/uxp. Everything is an asynchronous Action
executed inside `project.lockedAccess` and `project.executeTransaction`, so a
batch becomes one undo step (documented). Coverage: import files, create
sequences from presets or media, insert and overwrite at a time and track,
set clip in, out, start and end, move items, markers, effects and keyframes
through component parameters, transitions, MOGRT insertion, export through
Media Encoder, export FCP7 XML, OTIO and AAF, transcript export and import as
JSON. Not covered (documented by absence or Adobe forum replies): razor at a
time, speed setters, audio gain setters, caption track creation, drag and drop,
Text-Based Editing deletion, Essential Sound operations, Enhance Speech, Auto
Reframe, Object Mask creation. A UXP plugin runs inside Premiere; an external
agent needs a bridge the plugin exposes, which is how the MCP projects work.
Enable Preferences > Plugins > developer mode and load with the UXP Developer
Tool (reported from an Adobe community manager).

### Route D: file import plus computer use (works on every install)

Write a **Final Cut Pro 7 XML** (xmeml) from the reviewed cut list with the
pack's exporter, import it with File > Import, relink if asked, then finish in
the UI. EDL is the fallback (one video track, 999 events). OTIO is beta and
drops clip names on round trip (reported); do not promise it. Details in
[CUT LIST EXPORT](CUT%20LIST%20EXPORT.md).

## 3. Interchange facts for the hand-built sequence

- Rate: write 23.976, 29.97 and 59.94 as `<timebase>24|30|60</timebase>` with
  `<ntsc>TRUE</ntsc>`, and positions as integer frames (reported practitioner
  knowledge; the exporter does this).
- Paths: `<pathurl>` is a `file://` URL; Premiere relinks by path, then by file
  name, and shows the Link Media dialog for anything offline (reported).
- Links: without `<link>` elements the video and audio items arrive unlinked;
  the exporter writes one link group per clip so picture and sound stay
  together.
- Sequence settings may need a manual pass after import; create the sequence
  from a known preset first or check Sequence Settings afterwards (opinion).
- Export from Premiere for round-tripping: File > Export > Final Cut Pro XML
  (writes a translation results log), EDL (Timeline panel active, 32-character
  names option), AAF, OTIO (documented).

## 4. Computer use: layout and shortcuts

Panels (default Editing workspace, documented): Source Monitor with Effect
Controls as a tab, Program Monitor, Project panel with Media Browser, Effects,
Markers and History, Timeline, Tools strip, Properties panel on the right in
26.x. Workspaces: Option-Shift-1 to 0 (Alt on Windows); the Color workspace
opens Lumetri and Scopes, Audio opens Essential Sound, Captions and Graphics
opens the Text panel. Panel focus: Shift-1 Project, Shift-2 Source, Shift-3
Timeline, Shift-4 Program, Shift-5 Effect Controls; panel shortcuts only work in
the focused panel, which is the most common failure in the course transcripts.

| Action | macOS (Windows swaps Command for Ctrl and Option for Alt) | Source |
|---|---|---|
| Add Edit at playhead on targeted tracks; on all tracks | Command-K; Shift-Command-K | documented |
| Ripple trim previous or next edit to playhead | Q; W | reported, consistent across courses |
| Ripple delete | Shift-Forward Delete (Edit menu); Option-Delete with the Timeline focused | documented |
| Clear (leave gap) | Forward Delete | documented |
| Lift; Extract | ; and ' | documented |
| Mark In, Out, Clip, Selection | I, O, X, / | documented |
| Insert; Overwrite from Source Monitor | , and . | documented |
| Tools: Selection, Track Select Forward, Ripple, Rolling, Rate Stretch, Razor, Slip, Slide, Pen, Hand, Zoom, Type | V, A, B, N, R, C, Y, U, P, H, Z, T | reported |
| J K L transport; next and previous edit | J, K, L; Down and Up Arrow | reported |
| Select clip at playhead on targeted tracks | D | reported |
| Nudge 1 or 5 frames (Timeline focused) | Command-Left or Right; add Shift | documented |
| Snap; zoom in and out; fit sequence | S; = and -; \ | documented, reported |
| Add marker; next marker | M; Shift-M | documented |
| Speed/Duration | Command-R | documented |
| Audio Gain | G | documented |
| Default video, audio, both transitions | Command-D, Shift-Command-D, Shift-D | documented |
| Link or unlink | Command-L | documented |
| Export Media; Send to Media Encoder | Command-M; Option-Shift-M | documented |
| Keyboard Shortcuts dialog | Command-Option-K | documented |

There is no default Close Gap shortcut; assign one (reported from Adobe's own
2025 course, which hit a macOS collision on Shift-Command-G). Track targeting
decides what Command-K cuts; a selection overrides targeting. Linked Selection,
Sync Lock and Track Lock change what a ripple moves. Reset to the saved
workspace (Option-Shift-0) before trusting coordinates. Type timecode into the
Program Monitor field to position the playhead exactly.

### Text-Based Editing pause removal, step by step (documented mechanics)

1. Window > Workspaces > Text-Based Editing. Click the Timeline so the Text
   panel shows the sequence transcript, not a source clip. Transcribe if asked.
2. Text panel menu > Transcript View Options > set the pause threshold. Start at
   0.5 s; a second pass at 0.3 s only on sections that still feel slow; 0.1 s is
   the floor (threshold values opinion and reported).
3. Filter icon > Pauses. Click any pause to audition it. Delete > Extract
   (ripple) > Delete all. Repeat with the Filler words filter.
4. Verify in the Timeline: no stray gaps (Sequence > Close Gap), audio still
   linked, upper-track graphics still aligned. Lock tracks that must not move.
5. Then punch in on alternating clips or checkerboard two angles (V1 and V2,
   toggle Enable) to hide the jump cuts.

## 5. The talking-head workflow in Premiere, in order

1. **Sequence.** Match the camera (1920x1080 or 3840x2160; 23.976, 25, 29.97 or
   30). Color setup Direct 709 (SDR) unless grading log. Turn on automatic
   transcription at import with speaker labeling. Number sequences by pass
   (01 STRINGOUT, 02 ROUGH, 03 TIGHT, 04 AUDIO, 05 GRAPHICS) and duplicate before
   each pass (reported from Adobe's course).
2. **Proxies.** Right-click > Proxy > Create Proxies, Half, ProRes Proxy; needs
   Media Encoder; add the Toggle Proxies button to the Program Monitor (documented
   and reported).
3. **Cut.** Text-Based Editing first pass (above), Paper Edit for scripted or
   interview footage, then the keyboard loop: Command-K, Q, W, ripple delete,
   Up and Down to jump edits. Shift-Command-K when B-roll rides above the A-roll.
4. **Punch-ins.** Scale lives in Motion or the Properties panel. On a 4K source
   in a 1080 sequence alternate 50 percent and about 60 to 65 percent; on 1080
   in 1080 alternate 100 and 110 to 120 percent; anchor on the eyes; hold the
   scale for a hidden cut, or animate 6 to 10 frames with Ease Out for a push
   (opinion). Morph Cut is slow; apply it late and only where the same framing
   continues.
5. **Audio.** Tag clips Dialogue, Loudness > Auto-Match (-23 LUFS reported),
   then raise the master so the whole mix lands near -14 to -16 LUFS integrated
   with peaks under -1 dBTP. Repair sliders are 0 to 10: Reduce Noise 2 to 4,
   Reduce Rumble 2 to 3, DeHum 60 Hz only if present, DeEss 2 to 4, Reduce
   Reverb 2 to 4 for echoey rooms; Clarity Dynamics 3 to 5, EQ preset "Podcast
   Voice" or "Vocal Presence" at Amount 4 to 6 (values opinion). Enhance Speech
   only for bad rooms, Mix Amount 50 to 70 percent to avoid the processed sound
   (opinion). Music: tag Music, Auto-Match, Essential Sound ducking or rubber
   band keyframes around -25 dB under speech (reported values). Shift-D on every
   cut for 2 frame constant power fades (opinion). 26.5's Match Source export
   honours channel layout; verify stereo 48 kHz on export.
6. **Color.** Lumetri top to bottom: Basic Correction (Auto, then exposure,
   white balance, contrast with the Luma waveform between about 5 and 95),
   Creative for a Look at reduced intensity, Curves (gentle S on RGB; Hue vs Sat
   for skin and background), Color Wheels, HSL Secondary, Vignette last.
   Separate Lumetri effects per job, renamed; the shared look on an adjustment
   layer; Color Match for a B-cam. Check skin on the YUV vectorscope line with a
   temporary opacity mask (reported). Viewer gamma 2.2 for a YouTube audience,
   kept constant across videos.
7. **Graphics behind the presenter.** Duplicate the A-roll above the graphic,
   Object Mask on the person on the top copy (one click, track forward, Smooth
   edge mode for hair), graphic between the copies (documented tool, workflow
   opinion). Classic feathered pen mask with Track Selected Mask Forward when
   Object Mask misfires. One voice path only.
8. **Captions and titles.** Create captions from the transcript; save a Track
   Style; single-word layout for shorts; burn in for Shorts, sidecar SRT for
   long-form. MOGRTs from the Properties or Essential Graphics panel for lower
   thirds; Responsive Design pinning so intros survive duration changes.
9. **Vertical.** Sequence > Auto Reframe Sequence, 9:16, Default motion, custom
   1080x1920 resolution, "Don't nest" unless there are keyframes or speed
   changes; fix titles afterwards (documented and reported).
10. **Export.** YouTube 4K: H.264, 3840x2160, matching frame rate, VBR 1-pass at
    about 40 Mbps target (50 max) or 2-pass when time allows, High profile, AAC
    320 kbps 48 kHz; 1080p about 16 Mbps (reported values). Export a 30 second
    In to Out range first to validate settings. Content Credentials are optional
    since 26.2 (documented).
11. **Archive.** Project Manager to consolidate, plus an exported FCP XML or
    OTIO beside the project so the cut survives a software change (opinion).

## 6. Smoke test before promising anything

1. Confirm the version in Help > About and whether a bridge or UXP plugin is
   installed and connected (bridge: `--doctor` or the panel's status line).
2. Ask the bridge for the project name and sequence list, or import a two-clip
   FCP7 XML written from one copied clip and confirm two linked clipitems with
   no Link Media dialog. If the dialog appears, the path URL encoding is wrong.
3. Create a sequence named for the test, insert one clip, read back name, in,
   out and track by the same route, then delete the sequence.
4. Export a 10 second range through Export mode or Media Encoder and probe the
   file.

## 7. Learning path

- Beginner: Adobe Video, "Premiere Pro For Beginners, 2025 Edition" with
  Valentina Vee (3 h 27 min, about 1.7 million views, Adobe's official channel).
  Its "Command-K, Q and W are your three main shortcuts" is the cutting loop.
- Advanced: Hammad Sayed, "Adobe Premiere Pro Masterclass: Complete Editing
  Workflow" (7 h, July 2026) for the audio chain, Lumetri with scopes, Auto
  Reframe, multicam, proxies and export in one place; small channel, verify
  claims against Adobe pages.
- Expert color and masking: Zac Watson, "Adobe Premiere Pro Color Grading
  Tutorial 2025" (and the 2026 edition), plus John The Video Guy on the Object
  Mask tool (February 2026). For MOGRTs, Adobe's MOGRT workflow with Parker
  Walbeck and Ben Marriott's hour-long After Effects course remain the
  references, though both are from 2023.

## 8. Open questions

Whether 26.x still writes `<xmeml version="4">`; whether the drop-frame flag
survives XML export; whether UXP's ProjectConverter has import methods; and the
exact date Adobe removes CEP. None of these change the recommended route.
