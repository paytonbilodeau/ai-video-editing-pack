## Picking the Moments (short-clip selection rules)

- **Density:** roughly one clip per 9 to 12 seconds of video. A 60s short
  gets 5 to 7 clips; a ~90s video gets 8 to 9; a 2-minute video gets 10 to
  13. Aim for about half the runtime covered by animation, but never inflate
  a clip after its action has landed or accept a weak visual to reach the
  target. The ceiling is the on-camera anchors: hook, punchline, and at least
  a couple of breathing gaps must survive.
- **Anchor to concrete language.** Cut to animation on the concrete nouns,
  metaphors, and lists ("stacking days", "throw it at the wall", "lift
  something heavy") — never on abstract connective tissue.
- **Hook and punchline stay on camera.** Never cover the first ~3 seconds or
  the closing line. The viewer bonds with the presenter at the start and the
  payoff lands face-on.
- **Land the FIRST clip early, around the 5-second mark** (roughly 3 to 7s in,
  a beat before or after 5s is fine). Do not wait past ~8s for the first visual.
  Getting a clip in this early is a retention hook: it signals to the scroller
  "this is produced, not just another talking head" at the exact moment they
  decide whether to keep watching. Still leave the literal hook words on the
  face for the first ~3s; the first cutaway lands on the first concrete anchor
  after that. This applies to every video regardless of length. (Payton
  feedback, 2026-07-09.)
- **Time the readable state to the phrase.** An entrance may start slightly
  before its word when the viewer needs time to find it. The older 0.3 to 0.8s
  lead is a starting example, not a rule for every cue. Do not reveal a result
  before the sentence establishes the question, or keep drawing after it is needed.
- **Breathing room:** leave at least 2 to 3 seconds of talking head between
  clips, and protect a few longer face stretches across the video (hook,
  punchline, one reflective beat). At the new density the animations do more
  of the carrying, but the face gaps are what make the cutaways land.
- **Clip length by content:**
  - 1 to 3s — one simple symbol action (checkmark draws, block lands, bubble
    sends).
  - 3 to 5s — the workhorse for one clear scene and one action.
  - 5 to 5.5s — only when the narration and action clearly sustain the full
    window.
  - 5.5 to 6s — exceptional. Use only when trimming earlier would cut off the
    meaning. If the action settles early, shorten the delivered clip even
    though the paid source generation is longer.
  - Longer than 6s → split into two beats or reconsider.
- **Continuous mode** (one long animation) only when Payton asks for it or
  the body is one sustained explanation under ~35s where cutting back to
  camera would break the spell.


## Storyboard Rules

- **One idea, one scene, ONE primary action per beat.** Never split a
  sentence across beats.
- **Literal clarity before clever metaphor.** Start with the concrete nouns
  and verbs in the exact spoken anchor. Use an abstract metaphor only when a
  viewer can decode it in about one second. A visual that needs an explanation
  is a failed visual, even if it is attractive.
- **Exact-sentence match.** Before generating, state internally: (1) the
  exact phrase being illustrated, (2) the exact object or person viewers will
  see, (3) the exact action that matches the spoken verb, and (4) how the beat
  supports the video's main claim. If any answer is vague, redesign the beat.
- **Silent-frame test.** Place the transcript anchor beside the proposed
  keyframe. The connection should feel obvious immediately, not merely
  defensible after analysis. Reject locks, targets, gates, machines, or other
  stock metaphors when they do not map cleanly to the specific sentence.
- **Scene selection:** use the six reference modes and metaphor library from
  the `hand-drawn-style` skill, with `payton-sketch-style-spec.md` as the
  visual source of truth. Physical metaphors animate best.
- **Variability (mandatory):** characters in at most about one beat in three,
  and only when human presence adds meaning; the rest are object-only scenes,
  prop close-ups, machines, environments. Never the same reference mode twice
  in a row. Vary framing (wide, close-up, top-down) and where the accent
  lands. Payton avatar only for first-person content.
- **Visual continuity:** carry one anchor across clips (the accent green, a
  recurring prop). Same DNA, different expression, every clip.
- **Logos** must come from current official assets supplied as keyframe references. Generate each exact mark once as an integrated part of a static surface away from the mover. Never rely on model memory, use a flat after-generation overlay, or let the video model add or redraw a logo. If accuracy is uncertain, correct the keyframe or stop; never omit a required mark.


## The Text Law (symbols first)

Documented failure from live testing 2026-07-07: a label on a moving folder
warped into garbage glyphs mid-motion, while static title text survived.
That run establishes a risk, not a universal limit of every model or of local
compositing. The following conservative rules apply to generated physical
motion; local transforms may move approved text/marks intact when appropriate:

1. **Default is NO TEXT.** Carry meaning with symbols: accurate logos, icons,
   arrows, checkmarks, X marks, trays, folders, flames, sprouts.
2. **Allowed exceptions, sparingly:** a bare numeral ("3", "80%"), a single
   brand wordmark as part of an accurate logo, or ONE label of one to two
   words when the idea genuinely cannot be drawn.
3. **Placement law:** any text or logo lives in a static safe zone (top or
   bottom band) with all motion elsewhere. Text NEVER sits on or near a mover.
4. The keyframe prompt says "No words, no letters" for symbol-only frames,
   and the motion prompt always forbids letters appearing.


## The Motion Laws (from live critique 2026-07-08)

1. **END COMPOSED.** The clip's final frame must still be a complete,
   composed image with the mover settled IN frame. Every motion prompt ends
   the action with "...then settles and holds." Never let the subject exit
   the frame (documented failure: an arrow flew fully out of frame, leaving
   two seconds of empty background).
2. **FRONT-LOAD THE ACTION.** Clips are trimmed from the HEAD of the
   generated video (Grok minimum is 6s; a 2.5s beat keeps only the first
   2.5s). The primary action must begin immediately and read within the
   beat's trimmed length. No slow wind-ups.
3. **MOTION MARKS ARE STEERING, AND THEY LEAK.** Marks in the keyframe act as
   implied-motion cues the model follows — draw them ONLY behind the one
   mover, pointing where it travels. But they remain briefly visible in the
   video before the model absorbs them (documented leak: a guide arrow
   visible beside the sprout for the first beats). So keep marks TINY (short
   dashes, not bold arrows), and when a beat is trimmed very short (1 to 3s),
   consider omitting marks entirely and steering with the motion prompt alone.
4. **One primary action + at most one tiny secondary life.** Locked camera by
   default; use a small purposeful move only within the canonical style rule.

---


## Keyframe Prompt Template (per beat)

```
Create a 9:16 vertical image in the hand-drawn educational animatic storyboard style.

CORE READ (one sentence):
[what the viewer must instantly understand]

REFERENCE MODE:
[one of: rough storyboard scene / two stacked animatic panels / close-up prop shot / rough UI moment / physical metaphor scene / simple comic explainer card]

SCENE:
[Focal object, the single action frozen mid-moment, positioning. Tiny motion marks only behind the one mover, pointing where it will travel (or none for very short beats). Compose for vertical 9:16, focal subject in the middle 60 percent, safe margins top and bottom. State "no people" for object-only beats.]

TEXT:
[Default: "NO TEXT. No words, no letters, no numbers anywhere." Exceptions per the Text Law, always in a static zone away from the mover.]

SKETCH STYLE LOCK:
One clear visual thesis staged as a physical relationship. Authentic rough-but-coherent explainer sketch made with dry blue-gray or charcoal pencil strokes, pale visible underdrawing, occasional doubled and corrected contours, open imperfect joins, simplified slightly awkward anatomy, and loose lightly off-register flat fills. Keep the focal silhouette unmistakable and leave 70 to 80 percent off-white or pale cool negative space. Mostly grayscale structure with one green-led accent, Old Money Green #0F583D by default on light backgrounds. One dominant action. Original scene, not an infographic, clean inked cartoon, polished mascot, anime frame, or imitation.

COLOR PALETTE:
- Background: off-white or pale gray
- Linework: black or blue-gray
- Main accent: [luxury green #0F583D default; vary by topic]

CHARACTERS:
[Usually "None." Generic simple character or Payton in at most one beat in three. Payton: fit male, simple line-art face, dirty-blonde or tan wavy short-to-medium hockey-flow hair at or barely above the tops of the ears and swept back slightly sideways; not past the earlobes and not touching the neck, jawline, or shoulders; not shoulder-length, long, freely flowing, or feminine. Blue shirt or green brand accent.]

LOGOS AND BRANDS:
[If none: "NONE."] [If required: "Use the attached current official [BRAND] logo asset as a required structural reference. Render that recognizable mark once into [SPECIFIC STATIC SURFACE] in the SAME rough Sketch linework, materials and palette as the scene. Preserve exact geometry, proportions, component count, spacing and wordmark spelling. Keep it away from the mover. Do not distort, duplicate, invent its structure or add it later as a flat overlay."]

AVOID:
Words and letters (unless the Text Law exception applies), clean infographic cards, glossy UI, 3D, photorealism, borders.
```


## Motion Prompt Template (per beat)

The frame already defines the look; every word of the prompt describes
MOTION — one action, immediately, ending settled — plus a preservation and
ban block. Fill and send as `motion_prompt`:

```
[ONE primary action starting immediately, in plain motion verbs, e.g. "The green block drops straight down and lands squarely on top of the stack."] [It/he] then settles and holds, staying fully in frame. [Optional tiny secondary life: "The gear bobs gently in place."] Preserve the approved keyframe's composition, subject identity, the chosen character's silhouette, rough searching linework, visible underdrawing, loose off-register fills, negative space, and exact palette. Do not clean, smooth, ink, or polish the sketch. The locked camera remains still. Add no new objects, characters, words, logos, colors, effects, or scenery. Do not morph faces or props. Keep a subtle handmade line-boil with coherent silhouettes. End composed and fully readable as the same Sketch frame.
```

The template above uses the default locked shot. For a small camera move justified
by the meaning, replace its camera sentence with that one explicit path; preserve
composition, identity and reading time. Do not add camera movement merely to
make a settled scene look busy.

Motion verbs that work: slides, drops, lands, pops out, stacks, sorts, draws
itself (arrows, checkmarks), fills up, lights up, hands over, skids to a
stop, nods, points, flips, flows, opens, stamps, snaps together, unfurls,
flickers, bubbles. Avoid unmotivated camera moves, particle effects, explosions,
transformations, fast whip motion, anything that carries the subject out of
frame.

---


## storyboard.json Schema

Short clips (the default — one segment per clip, one beat per segment):
```json
{
  "title": "anti-optimization-extras",
  "segments": [
    {"name": "maxing-trend", "start_at": 11.3, "beats": [
      {"slug": "01_maxing-trend", "line": "...", "seconds": 2.5,
       "keyframe_prompt": "...", "motion_prompt": "...", "source_image": null}
    ]},
    {"name": "cliff-stop", "start_at": 57.4, "beats": [ ... ]}
  ]
}
```

Continuous (single file, on request):
```json
{
  "title": "why-ai-needs-context",
  "intro_seconds": 4.5,
  "outro_seconds": 3.0,
  "beats": [ ... ]
}
```

`seconds` = how long the clip should run in the final edit (CAN be under 6;
generation clamps up to Grok's 6s minimum and assembly trims back to
`seconds` from the head of the clip). `start_at` = seconds into the FINAL
video where the clip begins. Establish the entrance and readable state from
actual word timing; a provisional estimate must be replaced before final sync. `source_image` (optional)
routes an authorized hosted image URL through the paid Images 2.5 Flare
image-to-image adapter. The documented adapter requires hosted references rather
than local base64 inputs. Preserve every required identity/logo reference: use
an authorized hosted asset or the native generation route with the local input.
Set `source_image` to `null` only when no reference is required, never to bypass
an input-format failure.

---


## Keyframe QC Gate (check before animating)

For every PNG: does it obviously illustrate the exact transcript anchor
without needing a verbal explanation? Does the visible action match the
spoken verb? Does it support the video's main claim rather than merely match
the topic? Is it on-style (rough ink, pale background, one accent)? Symbols
only, no stray words (unless a Text Law exception was intended, spelled
right)? Did every required logo come from a current official reference, appear exactly once, preserve its exact recognizable geometry and match the scene's rendering style, feel integrated, and stay in a static zone? Motion marks tiny, only behind the intended
mover, pointing the right way (or absent on very short beats)? Text/logo in
a static zone away from the mover? Composition varied from the previous
beat? Correct the failed still using the chosen authorized route before motion.


## Motion QC (check after animating, before delivering)

Apply the complete-clip/composite review in the current workflow above. The
frame extraction below is an additional diagnostic, not a substitute for that
review. Respect the required reading hold before shortening a settled scene.

Extract the actual final decoded frame by zero-based index (decoded frame count
minus one), plus consecutive frames around suspect movement or joins. Seeking
0.3 seconds before EOF is a near-end sample, not the final-frame check.
Verify: mover settled IN frame; no letters appeared; no mark leak lingering
past the first moments on longer beats; style still flat 2D ink. If only motion
fails, preserve the approved still and version the motion retry. If the still
itself is wrong, intentionally replace and re-review it. Trim excess idle tail
only after retaining the reading interval needed for the resolved idea.

---


## Troubleshooting

For the optional paid adapter, distinguish recovery from replacement.
`--animate-only --resume` can continue existing work; inspect its manifest/job
state first. `--force` deletes the beat's PNG, MP4 and manifest entry. It is
reserved for intentional full-beat/keyframe replacement, with recoverable backups.
For a completed but weak motion clip, retain the accepted image and create a
versioned animation-only attempt that reuses it, using the adapter's inspected
capabilities. Do not invent a force-video flag or delete the original asset to
make a retry run. Confirm that the planned attempt will not regenerate the still
or duplicate an uncertain paid job before executing it.

- **Whole batch fails at once:** transient Kie outage. Wait 60s, `--resume`.
- **Repeated provider 500s:** inspect the saved job states and whether failures
  affect other authorized beats before blaming the source image. Preserve the
  approved still and successful clips. Reconcile uncertain jobs before retries;
  use bounded backoff or an authorized fallback that reuses accepted assets.
  Do not insert a placeholder video into the completed-asset cache to make the
  adapter skip a failed beat. Missing output remains pending until real output
  is received and checked.
- **"download failed":** the paid result URL is already in manifest.json.
  Rerun `--resume`; it redownloads for free, never regenerates.
- **A video task returns 500:** rerun `--animate-only --resume` first. Do not
  add `--force` unless you intend to replace the approved still too; `--force`
  clears the beat's cached still and hosted keyframe URL before retrying.
- **Reference image says "File type not supported":** `source_image` is a
  local path or data URI. Replace it with a direct public HTTPS image URL after an authorized upload. Never drop a required official reference to bypass this check.
- **Network blips or timeouts mid-run:** the script retries GET polls and
  backs off on downloads automatically; if it still dies, `--resume` continues
  from the last paid step. POSTs are never auto-retried (double-charge risk).
- **Long unattended runs:** wrap the animate call in a retry loop (60s
  backoff, ~5 attempts) run in the background; every attempt uses `--resume`
  so completed beats are never re-paid.
- **Model ID rejected:** candidates are tried in order; if all fail, check
  kie.ai/market for the current ID and update the TIERS dict.
- **Text or logo warps:** the mover was carrying text or the logo, or motion got too big.
  Move the exact logo or text to a static keyframe surface away from the mover, shrink to one small action, and `--force`. Never patch a warped mark with a flat overlay.
- **Wrong thing moves:** motion marks in the keyframe point at the wrong
  object. Fix the marks, `--force` the frame, re-animate.
- **Subject leaves the frame / clip ends empty:** add "then settles and holds,
  staying fully in frame" and retry only the motion while preserving the still.
- **Guide arrow visible in the video:** mark leak. Shrink or remove marks in
  the keyframe, add "the small guide marks fade away as the motion begins".
- **Style drifts 3D/realistic:** strengthen the preservation instructions, shrink
  the motion and version the motion-only retry with the approved still.
- **Beat feels static:** a readable hold is often correct. Add one small secondary
  action only if it serves the meaning. A camera move needs the separate
  justification allowed by the canonical spec, not a desire to fill stillness.
- **Timing off:** edit `seconds` or `start_at`, rerun `--assemble-only`. Free.

---
