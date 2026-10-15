# Flow production manual

Current customer instructions and the portable skill entry override historical examples below. In particular: no required count or ratio of effects, no automatic physics beat, no fixed graphics cadence, no automatic red/brand choice, no idle atmosphere. The old lane router is included for compatibility; the customer example bypasses it; inspect the reason for each beat. Master audio stays separate until the selected final-program audio route. All rates and safe areas adapt to the actual project. References to past scene names explain mechanisms; source video projects are not prerequisites.

## PALETTE ROUTING (mandatory)

Canonical source: the customer project record. Implemented in
`flow/src/theme.ts` as `setPalette('<name>')`, which every scene component
MUST call as its first line. Both lanes are NEUTRAL-FIRST: white, black,
and every gray between are shared base colors for both brands; the accent
family is what makes it a lane.

Lane by topic:
- **AI or AI-adjacent → mentorship lane** (green family, never blue).
- **Everything else (self-improvement, mindset, learning, fitness, life)
  → echo lane** (navy/aqua family).

Background mode: black or white both work for both lanes. **Default is
dark (Payton prefers black backgrounds).** Use the `-light` variant when
he asks for a white/light look.

- `mentorship` (black bg): white and light-gray text/elements; **Mint
  #72DFA5 is THE accent** (emphasis words, marks, packets, fills). Old
  Money Green #0F583D is depth only: tone-on-tone labels inside mint
  fills, glow falloff. Never prominent on black (too dark to read).
- `mentorship-light` (off-white bg): black and dark-gray elements; **Old
  Money Green #0F583D is THE accent**; mint only as small highlights and
  tone-on-tone inside green fills.
- `echo` (dark navy-black bg): off-white and light-gray elements; **Light
  Aqua #72C7DF is THE accent**; Dark Turquoise #1F6F78 is depth only;
  navy panels.
- `echo-light` (off-white bg): black and dark-gray elements; **Dark
  Turquoise #1F6F78 (with navy) is THE accent**; aqua only as small
  highlights and tone-on-tone.
- `lab` (light Train Bloom paper, blue) is legacy: demo/v0725 only.

**CONTRAST PAIRING LAW:** on a dark background the LIGHT accent variant
carries everything that must be seen and the deep brand shade is depth
only; on a light background the DEEP accent variant carries everything
and the light shade is highlight only. If any element would sit
low-contrast against the background, it is the wrong variant. Visibility
of text and animation beats palette purity every time.

- One accent family per scene. Negatives are carried by X marks,
  strikethrough, or muted gray, NOT red; red only if Payton explicitly
  asks (the brand file forbids default red in both lanes).
- Use current official assets from an authoritative source and preserve their
  recognizable structure. Authentic screenshots and native brand assets stay
  unchanged. For generated imagery, render the logo in the scene's own style
  under the shared logo rule; do not impose a white tile or flat overlay.
- Verified styleguides for all four brand palettes: comps
  `kit-styleguide-mentorship`, `-mentorship-light`, `-echo`, `-echo-light`
  (renders in `flow/out/kit/`).


## READABILITY LAWS (from Payton feedback 2026-07-25)

Nothing may be hard to read on a phone. Hard rules:

- Minimum sizes at 1080x1920: hero lockups ≥72, sub/kicker lines ≥36,
  connector labels ≥30 (component default 31), chart/axis labels ≥28,
  note/annotation rows ≥28, bar inside-labels ≥26. NOTHING below 26px.
- The `muted` tone is for de-emphasis on text ≥36px only. Smaller text
  uses `ink`, `label`, or an accent. Never stack faint-on-faint.
- Dark palettes: ink is near-white; muted #BEC3C6 is readable on dark and
  allowed at ≥30px. `dim` #868583 only for decorative text ≥40px.
- Emphasis token colors (mint/aqua/blue) must be the BRIGHT variant on
  dark backgrounds; deep fills (#0F583D, #1F6F78) are for shapes, never
  for small text.
- QA gate includes a squint test on extracted frames: if a word does not
  read at a glance at phone size, fix it before delivering.
- Evidence images keep their native aspect ratio. Use `contain`, a native-ratio
  crop, or a deliberately reframed excerpt. Never squeeze a chart, paper, row,
  screenshot, or source artifact to make it fit a card.


## DURATION LAW (from Payton feedback 2026-07-25)

Time each useful reveal to the actual spoken idea. A non-spoiling entrance
may start 0.3 to 0.8s before its anchor; preserve enough settled reading time.
There is no arbitrary six-second cap. Typical clips run 3 to 9s, but meaning
and reading time determine duration. If a thought needs several visual states,
progress them through the relevant words. Once the graphic has finished
explaining, reveal a useful next relationship or return to the presenter. Do not keep
packets looping or hold a completed diagram just to cover the whole passage.

The lead time above is for a non-spoiling entrance, not permission to reveal the
next claim early. Meaningful words, values and changed states land on their actual
spoken cues, and the previous state holds through its final relevant word.


## TWO DELIVERY MODES (reuse the established preference)

**Mode B is Payton's stated preference as of 2026-07-30** ("one overlay
is a lot easier for timing and lining up the SFX track"). Default to the
master unless he explicitly asks for separate clips.

**Mode A: clips.** Separate files, one per beat, placement-named,
full-frame with background. Payton overlays and cuts them himself.

**Mode B: master (when he says "one clip", "master", "single overlay",
"Train Bloom style one file").** ONE full-length transparent overlay the
exact duration of the video. Build with `MasterTrack` from
`flow/src/lib/master.tsx`:

```tsx
export const MyMaster: React.FC = () => (
  <MasterTrack
    beats={[
      {start: 3.2, dur: 5.5, node: <S01 />},
      {start: 11.9, dur: 3.5, node: <S02 />},
      // ...every beat at its transcript timestamp
    ]}
  />
);
// Register at width 1080, height 1920, durationInFrames = Math.round(videoSeconds * fps)
```

Each beat fades in over his footage (7f), plays with its opaque background,
and fades back out (10f); gaps are fully transparent so his face shows.
If the next beat starts within ~0.7s of the current one ending, extend the
current beat to the next start (butt cut) so the scenes chain with the
Flash transition instead of dipping back to camera. Butt-cut mechanics
(hardened on send5 after a real flicker Payton caught): make the beats
exactly adjacent, set `fadeOut: 0` on the outgoing beat and `fadeIn: 0`
on the incoming one (FadeWrap treats 0 as a true hard cut, fully opaque
on the boundary frame), and let the incoming scene's black Flash mask
the cut. Any nonzero fade at a butt cut leaves 1-2 transparent frames
where the talking head flickers through. AND the incoming scene's board
backdrop must be OPAQUE FROM FRAME 0 (short6 round 3, 2026-08-09): a
backdrop that fades in under the decaying Flash gives combined alpha
1-(1-flash)(1-bg) < 1 for ~9 frames — the face bleeds through a
half-transparent wash for ~0.3s at every cut. Frame 0 passes (flash=1)
while frames 1-9 leak, so checking only the boundary frame MISSES it.
BoardShell now forces backdrop opacity 1 whenever `flash` is set; keep
that invariant in any new shell. For a long
continuous passage, prefer ONE beat holding a single state-machine scene
(send5 run.tsx) over many chained beats: internal phases mutate with
no fade dips at all. Verify butt-cut opacity NUMERICALLY, by frame
index, not with -ss composites: ffmpeg `-ss <t>` + overlay onto magenta
returned false fully-transparent frames at exact beat boundaries on
aiwater while the file was actually opaque. Scan a +-0.5s WINDOW around
every chained cut, never a single frame:
`select='between(t,<cut-0.5>,<cut+0.5>)',alphaextract,signalstats,`
`metadata=print:key=lavfi.signalstats.YAVG:file=-` and require YAVG=3760
(12-bit limited max) on EVERY frame in the window; 256 = transparent,
anything between = the face is bleeding through. Render with the alpha
trio and warn about size (~10MB/s; a 100s master is ~1GB):

```bash
npx remotion render <slug>-master "out/<slug>/<slug>-master.mov" \
  --codec=prores --prores-profile=4444 --image-format=png --pixel-format=yuva444p10le
```

Deliver ONE .mov named `master overlay - drop at 0m00s (<len>s).mov`.

**STRIP THE AUDIO TRACK before delivering any master** (found 2026-08-09,
short6): Remotion muxes a "silent" PCM track into the .mov; ffmpeg reads
it as silence but Finder hover-preview and CapCut can render it as a
brutal screech, attached to the clip where Payton cannot mute it. The
overlay needs no audio (SFX + music are separate WAVs), so always remux
video-only after rendering, losslessly:

```bash
ffmpeg -i master.mov -map 0:v -c:v copy -an master-clean.mov
```

Then re-verify one opaque and one transparent frame (YAVG 3760/256).

**NORMALIZE THE FINAL MASTER FOR CAPCUT before delivery** (Shorts 7 and 8,
2026-08-20). A valid FFmpeg-authored ProRes 4444 file can contain a working
alpha plane while still reporting an undetermined alpha mode. Re-encode the
video-only master through Apple's native VideoToolbox ProRes encoder so the
interchange file carries straight, independent alpha:

```bash
ffmpeg -i master-clean.mov -map 0:v:0 \
  -c:v prores_videotoolbox -profile:v 4 -pix_fmt bgra -allow_sw 1 \
  -tag:v ap4h -r <project-fps> -fps_mode cfr -an -movflags +faststart \
  "CAPCUT SAFE alpha overlay - drop at 0m00s.mov"
```

Use a fresh `CAPCUT SAFE` filename rather than overwriting an asset CapCut has
already imported because its media cache can retain the earlier interpretation.
Keep any asset still referenced by a project; import the new normalized filename for the test. QA the normalized file with all of these checks: exact duration
and frame count, zero audio streams, full decode, transparent and opaque
`alphaextract` samples, `colordetect=mode=alpha_mode` across a PARTIALLY
transparent transition returning `straight / independent`, and a full
composite against the actual Auphonic base. A fully transparent or fully opaque
window may report `undetermined`; the transition window is the deciding check.


## VARIETY LAW (from Payton feedback 2026-07-25)

Do not let every beat be cards-plus-lines-plus-text. Rules:

- At least 3 distinct archetypes per video; never the same archetype twice
  in a row; at least one playful concrete-metaphor beat per video.
- Match the archetype to what is being said:
  - Number, stat, count, price → `Counter` (big count-up)
  - Percentage, progress, how-far-along → `Meter`
  - Trend over time → `Axes` + `Bars` or `Curve`
  - Do/don't, steps done, criteria → `Checklist` (X = negative, no red)
  - Journey, effort, race, goal, "getting there" → `Mover` (pictogram
    travels a dashed track to a flag; any lucide icon: PersonStanding,
    Rocket, Car, Bike)
  - Process, who-talks-to-what → `Card`s + `Connector`s with packets
  - Tool/typing/commands → `Terminal`
  - Product or model reveal ("Claude dropped Opus 5") → `LogoTile` with the
    official logo popping in + `Lockup` beneath with the name; logo from
    public/logos only
  - Big claim → hero `Lockup` + `Aside` legend
  - Ranking/verdict → keycap number chips row (see v0725 shared.tsx;
    on dark palettes chip bg is T.chip with numerals in T.bg)
- Composition still: ONE idea per screen, max ~3 grouped elements + one
  lockup, staggered entries, settled hold ending.


### Technique menu (researched + first proven on the context video, 2026-08-03)

Rotate these so no two videos animate the same way; keep 30fps timings:
masked reveal (14-20f sweep) · split-flip value swap (6-8f/flip) ·
word-cascade (4-6f/word) · typewriter (Terminal, ~10-15cps) · elastic
follow-through (secondary lags 4-6f) · squash-stretch impact (<=10%,
3-4f in, 8-10f rebound) · match-cut shape morph (interpolatePath,
16-24f) · seeded particle burst (Remotion random(), 20-30f, rare) ·
dashed route-trace + Mover walker · isometric card flip (14-18f) ·
parallax drift on holds >=60f · screen-shake accent (3-5f, max once) ·
progress-ring wipe (30-40f) · ghost-echo trail (2-3 copies, 0.5->0.25
opacity) · grid-snap FLIP re-layout (18-24f) · anticipation micro-recoil
(3-4f, silent). Fill-level metaphors (jars/pictograms filling) are the
Train Bloom signature move — use for any proportion/comparison.

Phase transitions for state machines (beyond crossfade): shared-element
carry-over (file chips fly into the folder, then live inside the project
panel — proven), directional wipe (10-14f), camera push (scale 1.0->1.08
over last 20-30f), mint-accent handoff (the highlight travels 10-16f to
the next phase's first element), persistent chrome (the #tally/StepRail
anchor). Pick ONE persistent anchor per long scene.

SFX pairing for new techniques (replace a cue, never stack): wipes =
whoosh+air · flips/cascades = ticks · morphs = whoosh or draw · bursts =
shimmer/ting + chime only on wins · route-trace = draw · re-layout =
staggered step · parallax holds and micro-recoils = SILENT. Checks =
check, typing = key. Keep the step two-tone as the recurring signature.


### Second proven style: BLUEPRINT/SCHEMATIC (2026-08-03, context video option B)

A full alternate design language in the same palettes, primitives in
`flow/src/components/Blueprint.tsx` (promote to components/ if it wins):
faint mint dot grid + corner registration marks, outlined rects that
DRAW on (BPRect), typewriter caps labels with blinking cursor (BPType),
dashed leaders with traveling nodes (BPLeader), measurement brackets
(BPMeasure), drawn check/X strokes (BPMark), scanline phase sweeps
(BPScan) instead of crossfades, frame MORPHS for shared-element phase
transitions. No fills, no shadows, no pop-overshoot (lucide stroke
icons and white logo tiles are the exceptions). SFX language: keys +
draws + scan whooshes, step signature kept. Gotcha: zero-length SVG
lines with strokeLinecap round render as stray DOTS - gate every drawn
primitive on frame >= at (caught on BPMark).


## Standard Flow board grammar (approved style and channel rules take precedence)

For overlays on a recorded lesson or waterfall, the final composed frame follows
the Resolve [portrait proof gate](../../../../editing/references/MOTION%20AND%20EDITORIAL%20CRAFT.md#prove-portrait-composition-before-the-full-render)
and [comparison layout classes](../../../../editing/references/COMPARISONS%20AND%20ADVANCED%20HANDOFFS.md).
Check top navigation as well as sides/right rail/bottom, with the actual footage,
longest caption and all labels enabled. Do not treat a transparent overlay preview
or maximum panel size as proof. Preserve the locked edit and use a parent transform
for an accepted group that needs only a small margin correction.

- Existing standard boards use Departure Mono with Instrument Serif asides.
  Use the narrower current channel and style specification when it selects
  clean type, Gentlemen fonts or Sketch lettering; do not force pixel caps on it.
- Motion: entries stagger one at a time; pops overshoot slightly; lines
  draw on ~0.5s; bars grow together ~1s ease-out; scenes mutate rather
  than get replaced; nothing exits frame; `Flash` (palette-aware: white on
  lab, black on dark palettes) opens full-frame cutaways when appropriate.
  Omit idle sparkles and purposeless motion from the current personal baseline.
- Persistent source/date, provenance, or changing test-condition footers
  default off when the main graphic already teaches the point. Keep supporting
  metadata in the beat map, caption, or source artifact. If attribution must be
  visible, give it a dedicated evidence state that earns the screen space.
- Directional data graphics must follow the evidence: move the value toward
  the side the source occupies and place its bracket and measurement label on
  that same side.
- **House safe-zone guide at 1080x1920 (not a universal platform spec):**
  ALL meaningful content inside **x 90 to 940,
  y 200 to 1500**, center-biased. Nothing readable in the bottom 420px or
  the right 140px (like/comment/share rail). Because the zone is
  asymmetric, the OLD rule centered scenes on x=515; SUPERSEDED by
  Payton 2026-07-30: center scenes on TRUE center x=540 (off-center
  reads worse than a tight margin). Keep every glyph inside x 100..930
  and treat the top edge as y>=220, because Instagram sometimes zooms
  the crop slightly (it nearly clipped a G at x~50 on the aiwater golf
  beat). Scale content down before letting it approach an edge; solve
  crowded beats by phasing (info cluster fades out, chart fades in)
  instead of shifting off-center. Decorative sparkles may drift
  slightly only in a requested treatment; omit them from the current default.
  Before release, inspect the intended platform's current UI/template and caption
  length. Ads and additional controls may require more bottom clearance. See
  `directives/video_production.md` for primary sources and the per-output check.
- Existing examples use 30fps and 1080-coordinate layout guides. New graphics
  match the locked source/project frame rate and intended delivery canvas.
  Scale guides for the supported 4K delivery rather than silently reducing the
  final export. Compose portrait and landscape independently.


## Picking the Moments

- Roughly one clip per 9 to 12 seconds and about half a dense short are
  historical starting references, not quotas. Keep the camera as the narrative
  spine and protect its hook/punchline when appropriate. Place graphics where
  they explain the exact idea, not at mechanically scheduled intervals.
- Anchor to concrete language; quote the exact words in the timeline.
- Durations per the Duration Law above, from word timestamps
  from actual local Whisper word data or a matching existing Auphonic export.
  Auphonic is not required to obtain timing.


## POST-FILM FACT PARITY GATE (added 2026-08-04)

The verified word transcript of the locked edit is the timing source, but it
is not automatically the factual authority. Payton may improve the script while filming, and he may
also make a numerical slip. Before scene design, build a quick parity ledger
for every number, model name, study, product claim, and provenance claim:

| Spoken audio | Primary source | Overlay | Caption |
|---|---|---|---|
| Exact filmed wording | Exact supported fact | Must match the supported fact | Must match and carry limitations |

- Verify the filmed wording against the primary source, not only the approved
  draft. The AI-image-detection short is the standing example: the locked
  reasoning used 29%, the recorded take said 20%, and the Frontiers table
  reported 29.04%.
- Never repeat an incorrect spoken number in the overlay merely because it
  keeps audio and graphics visually consistent. Correct the graphic and hold
  final delivery for an audio pickup or an explicit visible correction.
- Obvious ASR substitutions such as "gateway information" for "visual
  giveaway at all" are timing clues, not approved on-screen copy. Listen to
  the passage or resolve it from the controlling script and context.
- Final QA fails if audio, overlay, caption, and source disagree. Record the
  resolved wording in the video's README or final-transcript artifact so the
  next agent does not resurrect the stale value.


## SFX SYNC LAW (Payton feedback 2026-08-03, round 3)

Every SFX event time must be DERIVED from the scene code: video time =
beat start + S(delay) of the element it scores. Never hand-copy or
estimate times; drifted or orphaned events (a sound with no matching
on-screen motion) read as "off beat" instantly. After any scene timing
edit, regenerate the timeline from the updated delays before rendering
the WAV. Sounds with no visual anchor are only allowed on Flash cuts
(thump) and beat fade-ins (air).

Every non-cut, non-fade emphasis cue must have a readable visual event on its
exact rendered frame. A spoken payoff such as `wrong` needs a visible state
change on that word before it can morph into the next proof graphic. An
audio-only emphasis is an orphan and fails review.

Transcript seconds are not automatically rendered-frame seconds. Snap each
cue to the exact global Remotion frame, including the owning `Sequence` start
and its local rounded delay. For slow-attack `air`, `draw`, `shimmer`, and
`whoosh` sounds, derive a small one-to-two-frame lead from that visual anchor
so the audible onset meets the motion. Store the visual anchor in the timeline
for QA. In combined reviews, enable the limiter's latency compensation; an
uncompensated look-ahead delays voice and SFX against the video even when the
standalone stem is correct.


## Render Commands

```bash
cd flow
npx remotion render <comp-id> "out/<slug>/<file>.mp4" --codec=h264
# alpha overlay / master (ALL THREE flags or alpha silently drops):
npx remotion render <comp-id> "out/<slug>/<file>.mov" \
  --codec=prores --prores-profile=4444 --image-format=png --pixel-format=yuva444p10le
```

h264 needs even dimensions. Renders sequential. ~20 to 60s per clip;
master = roughly the video length in render time. `npm run studio` for
live preview.


## Component Cheat Sheet

Core: `Background {transparent}` + `Flash` (palette-aware) · `Lockup {y,
lines:[{segs:[{t,tone}],size}]}` · `Aside {y,text,chip}` · `Card {x,y,icon,
label}` · `Connector {d,delay,arrow,label,packets,dashed}` · `Terminal {y,
delay,command,outputs}` (NOTE: popStyle overrides its translateY(-50%),
so `y` is effectively the window TOP, not center — position accordingly;
window height also grows as typed text wraps) · `LogoTile {x,y,label,
src|icon}` (tile bg is T.tile = white in every palette so official logos
stay on white; `logos/chatgpt.svg` = current black OpenAI blossom, added
2026-07-28) · `Axes` · `Bars` · `Curve` · `Sparkle`.

send5 (`components/StepRail.tsx`): `CX=540` · `S(sec, fps)` · `phaseO(frame,
enter, exit)` · `StepRail {delay, steps:[{name,at}]}` (numbered chips:
todo hollow, active mint w/ black numeral, done deep-green w/ mint
numeral) · `Kicker {y,text,delay}`.

Variety (`components/Variety.tsx`): `Counter {x,y,value,prefix,suffix,
label,size,dur}` · `Meter {x,y,w,pct,label}` · `Checklist {x,y,items:[{t,
ok}]}` · `Mover {fromX,toX,y,icon,dur,flag}`.

Master (`lib/master.tsx`): `MasterTrack {beats:[{start,dur,node,fadeIn,
fadeOut}]}` · `FadeWrap`.

Helpers `lib/anim.ts`: `pop, ease, easeOut, fadeUp, popStyle`. WARNING:
`fadeUp`/`popStyle` return a `transform`; never spread onto an element with
its own transform (rotation/centering); use `opacity: ease(...)` there.


## Troubleshooting

- Scene renders in wrong colors: missing `setPalette()` first line, or
  another module set a different palette; every scene sets its own.
- Word-by-word "typing" text: words that have not appeared yet must
  render `null`, not opacity-0 — invisible spans still take layout space,
  wrap the line, and leave the cursor floating alone (caught on send5).
  Gate with `frame >= at ? <span> : null`; reflow then reads as streaming.
- Auphonic word timestamps: some HTML exports embed JSON in
  `<script id="transcriptSourceData">`; other exports need the production's
  speech JSON. Use `editing/tools/video_word_timing.py` in the sibling editing module to detect supported shapes and
  preserve actual word intervals. Reject missing timing rather than estimating.
  On-screen text never copies Whisper misspellings ("Chachapiti").
- "easing is not a function": use `Easing.poly(5)`, not `Easing.quint`.
- Boxy glyphs: headless Chrome has no system fonts; load via src/fonts.ts.
- Misplaced rotated/centered element: transform conflict (see anim.ts).
- Opaque overlay: one of the three alpha flags missing.
- Stuck render: unpaired `delayRender()`; `--log=verbose`.
- Long master render dies with 'A delayRender() "Loading fonts" was
  called but not cleared after 28000ms': fonts re-load when a later
  Sequence mounts mid-render. Add `--timeout=180000` to the render
  command (proven on the 170s aiwater master).
- Version errors: all remotion packages same version (`npx remotion
  upgrade`).
- Fallback if Remotion becomes friction: HyperFrames (Apache 2.0),
  evaluate on one video first.



## HOUSE STYLE v1 (APPROVED by Payton 2026-08-03: "much better...
positioning, SFX, music, all outstanding")

The default grammar for every Flow short until superseded. Base grammar:

- PACING from the card system: crossfaded phases (phaseO), solid cards
  pop, text fadeUps, full read-holds. NO scanline hard swaps between
  phases (tried in option B, read as glitchy).
- ATMOSPHERE from the blueprint system on every beat: BPGrid faint mint
  dot grid + corner registration marks; drawn BPRect frames for
  schematic objects; BPMeasure brackets for spans; BPNode pulses;
  BracketTitle for persistent section headers (Tony's bracket-mask).
- TYPEWRITER ONLY WHERE IT MEANS TYPING: terminal commands, prompt
  strings ("> make this amazing", "AMAZING = ?"). Everything else
  fades/pops. Cursor blink is EASED, never binary (bp.tsx).
- Tally pattern: drawn box + #N + step two-tone, redraws per increment.
- Primitives PROMOTED to `flow/src/components/Blueprint.tsx`
  (2026-08-03): BPGrid, BPType, BPRect, BPLeader, BPMeasure, BPMark,
  BPNode, BPScan, BracketTitle. Import from there; videos/context/bp.tsx
  is a legacy re-export shim.

Remotion craft rules adopted from research (2026-08-03, remotion.dev +
official skills repo):

- Vary spring configs per element class; one uniform pop is the amateur
  tell. Punchy chip {damping 10-12, stiffness 120-140}; controlled
  premium entrance damping 18-20 (no overshoot); use
  spring({durationInFrames}) to land staggered elements together;
  measureSpring() to sequence after a spring actually settles.
- Big moves: Easing.bezier(0.19, 1, 0.22, 1) (ease-out-expo). Entrances
  ease-out ~8-9f; exits ease-in; 4-8f opacity overlap on text swaps.
- Organic holds: @remotion/noise noise3D drift (2-6px, frame*0.02) on
  decorative elements only - never on text being read.
- Paths: evolvePath draw-ons; getPointAtLength + getTangentAtLength to
  ROTATE travelers along paths (prevents sliding-sticker look);
  interpolatePath for morphs; warpPath + noise for organic squiggle.
- Kinetic type: per-char/word springs with 2-3f stagger wave via
  measureText; masked line reveals via clip-path on a spring. Typewriter
  = text.slice, never per-char opacity.
- Transitions library exists (@remotion/transitions TransitionSeries,
  springTiming, fade/slide/wipe/flip/clockWipe) - candidate for beat
  fades if MasterTrack ever feels flat; not adopted yet.
- Reference libraries to study: remotion-dev/skills rule files,
  template-prompt-to-motion-graphics-saas, lifeprompt remotion-scenes,
  spring-editor. (seblavoie/remotion-kit was REMOVED from this list on
  2026-08-08: it carries no licence grant at all, so it cannot be used or
  copied from. The full rejected-source list and the reasons live in
  `references/upstream-provenance.md`.)


## ADVANCED LANES (added 2026-08-08) — READ BEFORE MAPPING BEATS

Flow used to have exactly one way to make a beat: a designed board. That is
what produced Payton's standing complaint ("cards+pills every beat", "not much
change in style"). There are now FOUR creative lanes, and a router that picks
between them from the argument, not from a coin flip.

### The four lanes

- **designed** — the board grammar (House Style v1 + Blueprint). Flow's native
  voice. Cards, charts, rails, checklists.
- **evidence** — footage as proof. A real screen recording, a real generated
  asset, an official logo card, a device frame. Opaque, full-bleed.
- **physical** — a baked physics metaphor. Matter that pours, stacks, tips.
  This is Flow's originality lane; neither reference creator uses it and stock
  Remotion does not ship it.
- **hybrid** — a restrained designed board carrying ONE evidence or physical
  element, usually under a camera move.

### The router (`flow/src/lib/lanes.ts`) — use it at beat-mapping time

Do not hand-pick lanes. Build a `BeatBrief[]` (id, verbatim quote, argument
job, start, dur, plus `hasEvidenceAsset` / `onCamera` / optional `force`) and
call `routeLanes()`. It scores each beat from the argument job first and the
transcript language second, then applies sequencing rules:

- never the same lane twice in a row
- at least one **physical** beat per video (the Variety Law's concrete-metaphor
  requirement, and the originality clause)
- evidence capped at 40% of beats — an all-proof video is somebody else's
  format
- designed capped at 50% — this is the anti-cards-and-pills rule, enforced in
  code
- at least 3 distinct lanes when a video has 4+ beats
- it rotates the TECHNIQUE inside a lane too, so two designed beats never
  animate the same way

Two refusals it will not negotiate:

- **No real artifact, no evidence lane.** `hasEvidenceAsset` must mean a
  genuine screen recording, a real screenshot, an official logo, or something
  Payton actually made. Never set it to unlock a nicer treatment. A mocked-up
  product screenshot is a fabrication and also breaks the official-logo rule.
- **Beats under 2.5s do not get physics.** Nothing can fall and settle in that
  time, and an unsettled ending fails QA.

`explainRoute()` prints a one-line-per-beat trace for the beat map.
`auditRoute()` returns [] when a route is compliant — run it before building.

### When to use which

| The beat is... | Lane |
|---|---|
| explaining a mechanism, a process, criteria, a list | designed |
| showing something real that exists on screen | evidence |
| a proportion, a tradeoff, a comparison, "how much" | physical |
| a story or claim that needs one real thing inside a board | hybrid |
| the hook, the pivot, or the verdict | the presenter. Annotate around him, never full-bleed over him. |

### New components

**`components/Motion.tsx`** (adapted from Remocn, MIT, pinned — see
`references/upstream-provenance.md`)
`Drift` (nothing on screen is ever frozen; never on text being read) ·
`CameraMove {kind: focus-in|focus-out|push-through|settle}` ·
`GrainDissolve` (textured phase transition, the approved alternative to
crossfade) · `InkUnderline` · `InkArrow` · `ScribbleCircle` (hand-drawn
annotation, seeded wobble + stepped reveal)

**`components/Evidence.tsx`** (mechanics reimplemented from the Remotion
Recorder, which carries NO licence — read it, never paste from it)
`groupWords` + `WordCaptions` (word-accurate captions straight from the
Auphonic timestamps, with single-token emphasis) · `EvidenceBeat` (opaque
full-bleed real asset) · `ScreenCallout` (drawn box + label on real footage) ·
`CropZoom` (push into the region that carries the claim) · `DeviceFrame` ·
`AssetSwitch` (cut on the spoken noun) · `LayoutSwitch` (face / proof / board
state machine) · `BigFigure`

**`components/Physical.tsx`** + **`lib/physics.ts`** (matter-js 0.20.0, MIT)
`PourFill` · `TippingScale` · `BlockStack`, all driven by `bake()`.

### Physics rules

- Simulate ONCE at a fixed timestep, store per-frame transforms, play back by
  frame index. Never step an engine inside a component: Remotion renders frames
  out of order and in parallel workers, so a live sim flickers and never
  reproduces.
- Seeds are strings. Same seed + same code = byte-identical frames. Proven:
  two independent renders of `bench-c-physical` produced identical file hashes.
- **The picture cannot lie.** If the claim is "most cases fail", make the jar
  genuinely too narrow and let most tokens genuinely miss. Do not animate a
  failure rate.
- Keep specs in their own React-free module (see
  `videos/bench0808/specs.ts`) so the SFX generator can bake the SAME numbers.
- **SFX comes free.** `collisionsToSfx(bake, beatStart)` emits cue times
  derived from real impact frames. Run `scripts/bench-sfx.mjs` to write
  `sfx-timeline.json`. Never hand-time a physical beat.

### Two frame-space traps (both caused real defects)

1. **`LayoutSwitch` gives each segment its OWN frame space** (0 = the frame
   that layout took over). Segment children must write anchors as
   `S(spokenTime - segment.at)`. Getting this wrong made every credit chip
   appear at once and a quote card land 2.8s before it was spoken.
2. **Grain-dissolve ordering.** A phase must stay fully opaque until the NEXT
   phase has finished building on top of it, and only in-dissolves should be
   used. If the outgoing phase erodes while the incoming one builds, both are
   partially transparent at once and the talking head shows through the middle
   of every transition.

### Type sizes under a scale wrapper

The 0.86 global scale multiplies every font size. The 26px readability floor
therefore becomes a **32px floor in source units**. Check the final pixel size,
not the number in the code.

### Anti-copy boundary (the point of all this)

The goal is an original Flow style, not an imitation. Concretely:

- Do not reproduce a reference creator's identity: their caption styling,
  colour choices, pacing signature, or brand marks.
- Captions go ABOVE the bottom 420px, not in the bottom third, because that
  lane belongs to the platform UI.
- The physical lane exists specifically so every video carries a device that
  is Flow's own. Keep at least one per video.
- Cite what you borrow. Every adapted mechanic has an attribution header in
  the component file and a row in `references/upstream-provenance.md`.

### Benchmark reference

`~/Documents/Motion Graphics/2026-08-08 Advanced Flow Benchmark/` holds three
directions (A motion, B evidence, C physical) over the SAME real 22.10s
segment, plus the alpha integration test and frame-indexed contact sheets.
Comps live in `flow/src/videos/bench0808/`. Use them as the worked example of
what each lane looks like.

### QA gate for the new lanes (in addition to the existing gate)

```bash
cd flow
# 1. behaviour: router rules + physics determinism + the shipped specs
npx tsc src/lib/lanes.ts src/lib/physics.ts src/videos/bench0808/specs.ts \
  --outDir /tmp/flowcheck --module commonjs --target ES2022 \
  --moduleResolution node --esModuleInterop --skipLibCheck --strict
NODE_PATH="$PWD/node_modules" node scripts/verify-flow-lanes-physics.mjs /tmp/flowcheck

# 2. alpha: any new component must survive a transparent render
npx remotion render bench-alpha-test out/alpha.mov \
  --codec=prores --prores-profile=4444 --image-format=png --pixel-format=yuva444p10le
# opaque frames must read 3760, transparent gaps 256, BY FRAME INDEX:
ffmpeg -i out/alpha.mov -vf "select='eq(n,40)',alphaextract,signalstats,\
metadata=print:key=lavfi.signalstats.YAVG" -frames:v 1 -f null -

# 3. visual: frame-INDEXED contact sheet (fps=1/N tiling mislabels cells)
./scripts/qa-contact-sheet.sh out/x.mp4 /tmp/qa.png 7 20 80 140 200 260 320 380
```

Then LOOK at the sheet. Check: settled endings, no element crossing falling
matter, nothing appearing before its spoken anchor, no empty board at a phase
cut, type above the floor, and that A/B/C-style variants are actually
different from each other.

### Updating any of this

`references/upstream-provenance.md` has the pinned SHAs, the licence position
for each source, the WebGL decision, the rejected-source list, the update
procedure, and the rollback steps. Read it before pulling anything new in.
Never run an upstream installer (`npx shadcn add`, `npx skills add`) or
curl-pipe-shell.


## PACING AND RESTRAINT (Payton feedback 2026-07-30, aiwater round 2)

Shipped and approved, with two refinements for every future video:

- **Let text breathe.** Some beats felt "ever so slightly rushed" and text
  faded out "in a rushed manner." Text that matters holds until its
  thought is fully spoken plus the settled hold; fade-outs are gentle
  (12f+), never snappy, and a line should not exit while the viewer is
  still mid-read. When a beat is tight, cut an element instead of
  speeding the animation.
- **Trailing sub-captions are optional, default OFF.** The small italic
  or kicker line that drops in at the end of a beat (the "sounds huge,
  right?" / "irrigation vs cooling, nationwide" garnish) is not needed on
  every beat and reads as clutter when the main graphic already says it.
  Use one only when it adds information the graphic does not carry.

- **Text-hold numbers (researched 2026-08-03).** Standalone on-screen
  text (labels, kickers, payoff lines) needs ~3.0s base + 0.5-0.7s per
  word of hold; sanity floor ~1s per 13 characters. Spoken-synced text
  may LAND exactly on its word but must persist >=1.5s after landing.
  When a line would appear near a beat's end, EXTEND the beat (chain it
  into the next with a butt cut, or hold past the spoken passage) —
  never let the read window shrink. The critical word should sit on a
  fully STILL frame for most of its hold (moving text reads 2-10x
  slower).
- **Final-state read-through (Payton feedback 2026-08-20).** After the normal
  frame QA, watch the finished composite at phone size and read every state in
  real time without pausing. The last accumulated state is the usual failure
  point: if a reasonable viewer cannot finish it before the cut, reveal it
  earlier, carry it across the handoff, or remove words. Do not accept a state
  merely because every individual reveal is transcript-synced.

- **Fast spoken lists accumulate.** When Payton names four or more items
  quickly, reveal each item on its spoken anchor but keep the earlier
  items visible so the audience can finish reading. Group related items
  or use a persistent checklist/grid; do not cycle one label out for the
  next every second.
- **One spoken thought owns the screen.** A visual state stays through the
  final word of the thought it explains. Do not introduce the next title,
  example, icon, or conclusion before its first matching spoken noun or verb.
  Derive both the reveal and replacement times from the verified word
  transcript of the locked edit. If a late item would have less than a useful read window, let it
  accumulate inside the current board or remove it. Never pre-roll the next
  idea to make the animation feel busier. This is stricter than scene-level
  timing: every internal phase must also follow the transcript.
- **No production chrome in the final.** Debug headers, option names, scene
  IDs, and decorative registration marks are not audience-facing graphics.
  Remove them before delivery. When a dense 1080x1920 board feels close to
  platform edges, an approved correction is one centered global scale wrapper
  around `(540, 960)` (the 2026-08-07 reaction used `scale(0.86)`), followed by
  full-frame QA. Keep the meaningful card system centered and comfortably out
  of the right-side controls and lower caption lane.
- **2026-08-07 final lock.** Payton approved the refined AI-more-than-coding
  Option A as the standing reference for dense reaction passages: evidence
  boards scaled to `0.86`, no production chrome or edge marks, exact internal
  word anchors, accumulated examples, and every visual state held through the
  full spoken thought. Its music stayed locked while its SFX was regenerated
  from the corrected phase times. Carry this process forward even when the
  next video's visual concept changes.
- **Connector hygiene.** Leaders and arrows must terminate in whitespace
  or at a card edge. They never pass through text, icons, cards, or one
  another. When three or more branches would make a crowded fan, replace
  the branches with a clean grid or checklist.
- **Marks belong to one target.** A strike, underline, or circle must be
  aligned to the exact label it marks. Never sweep one decorative
  diagonal through two separate labels; use one clean mark per target.



## OVER-FACE ANNOTATIONS AND BOARD FLOW (Payton verdicts, 2026-08-09 short6)

- Over-face annotation text sits BELOW the chin or near frame centre, never
  above the forehead or across the eyes. Over light clothing, a pale wall, or
  any mixed-value background, give the complete thought a dark pill backing
  (rgba(10,11,11,0.82-0.90), cardEdge border). Mint is an accent inside that
  card, never bare body copy over the live frame; a shadow alone is not enough.
- The DEFAULT graphics treatment is the opaque black board. Floating
  graphics over the talking head are the exception and must clearly earn it
  (approved case: official logo tiles popping on the spoken brand names).
  When unsure, board.
- No bare quick face pops between adjacent boards. If the next board's
  content starts within ~2-3s, HOLD the previous board settled (packets/idle
  motion keep it alive) and fade it out directly into the next sequence.
  Face returns are for the hook, real pivots, and the close — not gaps.
- This includes SUB-SECOND alpha leaks at butt cuts (round 3): even a
  ~0.3s half-transparent face bleed at a board-to-board cut reads to
  Payton as "I randomly pop up for no reason." Chained boards stay BLACK
  through the cut — opaque backdrop from frame 0 of the incoming scene,
  window-scanned alpha QA (see butt-cut mechanics above).
- Physical pours must read as the actual substance: fine granular stream
  (salt-style spec: small radius, every-frame spawn, tight spread sized to
  the spout, spawn mouth at the spout tip) with a visible rising fill.
  Chunky scattered tokens read as bouncing balls, not pouring.
- Annotation arrows still obey the arrow-earns-target law (the link-in-bio
  down-arrow pointed at nothing and was cut; the text pill alone was right).
