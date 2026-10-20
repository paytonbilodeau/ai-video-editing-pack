# Local JavaScript animation guide

This route builds one self-contained HTML Canvas animation from JavaScript.
It includes seven public style kits and their editable demos: cut-paper,
crosshatch, riso, sketchbook, math, isometric and pixel. Their upstream
[style descriptions](styles/README.md) describe the drawing hooks.

## Setup and first piece

Use Node.js 22 or newer. FFmpeg is needed for movie export, beat analysis and
media probing; PNG rendering only needs the local browser. The setup command
installs exactly the lockfile's Playwright and corresponding Chromium into a
new directory. It does not install system packages or use global Node modules.
On Linux, missing browser system libraries must be supplied by the machine's
administrator. `doctor` reports the actual browser and FFmpeg encoders.

Run these commands from this skill's directory; quote paths containing spaces:

```sh
node tools/animate.mjs setup /path/to/private-animation-runtime
node tools/animate.mjs doctor --runtime /path/to/private-animation-runtime
node tools/animate.mjs init /path/to/my-piece --style cut-paper
node tools/animate.mjs build /path/to/my-piece
node tools/animate.mjs check /path/to/my-piece --runtime /path/to/private-animation-runtime --out /path/to/check-01
node tools/animate.mjs storyboard /path/to/my-piece --runtime /path/to/private-animation-runtime --out /path/to/storyboard-01
node tools/animate.mjs render /path/to/my-piece --runtime /path/to/private-animation-runtime --out /path/to/render-01 --format mp4 --audio
```

Output directories must be new. Failed runs may leave partial output, which
must not be treated as a finished export. A successful report records technical
checks; it explicitly leaves visual and audio acceptance unverified. Build
updates the working piece's `index.html`, preserving authored `src/` files.
All projects, renders and dependencies belong outside the reference pack.

## Source and timing contract

`piece.json.format` and `window.TIMELINE` must agree on integer `width`,
`height`, `fps`, `frames` and numeric `duration`. Duration times fps must equal
frames. Limits are 4096 pixels per side, 120 fps and 36000 frames. Canvas `c`
must have the same dimensions. `window.renderFrame(seconds)` must redraw the
whole frame using only absolute time and seeded randomness. Never advance state
from earlier calls or use the clock. Match the declared duration to the actual
recording and edit. Shipped style code can quantize motion on twos.

The builder defaults to `src/head.html`, core, chosen style, scenes, bridges,
morph renderer, board and score. A `build` list can supply an authored renderer;
all parts stay inside the piece except explicit `kit/` files. Custom style
code lives in `piece/styles/<name>/kit.js`, referenced by `style` in metadata.
There is no parent-directory style discovery. Keep the required `const STYLE`
and frame/timeline contract even with an authored renderer.

Use local PNG, JPEG or WebP files in `assets/`; build embeds them and waits for
image decoding plus `document.fonts.ready`. The source itself cannot reference
external HTTP URLs or data URIs. Use installed or licensed local fonts and
record the environment. Repeat/out-of-order hashes are meaningful within the
same browser, OS and fonts; cross-platform pixel equality is not promised.
The installed browser version is pinned by the Playwright lockfile.

For a supplied voice recording, make a reviewed `voice.json` with a `lines`
array containing text, start/end times and optional word times. Build exposes
it as `VOICE`; cue scenes from those verified times. Use an existing local
transcription tool if authorized, or enter timings manually. No voice generation
or transcription model is installed by this skill. Preserve the original WAV
and mix it in the destination editor. The optional `--audio` export renders
the piece's synthesized score, not the supplied recording.

For a supplied music track:

```sh
node tools/animate.mjs beats /path/to/music.wav --out /path/to/my-piece/beats.json --bpm 120 --duration 30
```

The analyzer estimates phase around the supplied BPM. Listen against the track
and correct half/double-time mistakes before using it. Build exposes `BEATS`;
the source uses its BPM/offset to place cuts. This command does not mix the
track into the output. Add the exact same track segment in the editor. Maintain
rights and attribution for supplied audio.

## Reference matching and custom styles

Measure the reference's frame shape, margins, object proportions, palette,
line thickness, typography and motion before coding. For a video, inspect
representative frames and record shot/transition times using the existing
editor or FFmpeg. Use only references the user is authorized to supply.

```sh
node tools/animate.mjs compare /path/to/my-piece --runtime /path/to/private-animation-runtime --out /path/to/comparison-01 --reference /path/to/reference.png --frame 24
```

The side-by-side image has a ten-percent width grid. Compare proportions and
visual character, not only pixel difference. Revise the kit in the private
piece, render representative frames, then review motion. The comparison is an
aid to human review; it does not assign a style-match score. `storyboard` uses
the piece's `TIMELINE.board` and `renderBoard` implementation; the shipped demos
include it. A custom renderer can implement the same hook or supply its own
review sheet. Keep the accepted style and demo together in the project.

## Remotion

Copy [AnimationFrame.tsx](adapters/AnimationFrame.tsx) into a Remotion project.
Put built `index.html` in that project's `public/animation/` directory and use
`<AnimationFrame src={staticFile('animation/index.html')} />`. Use the piece's
width and height for the composition. The host fps may differ: the bridge maps
host frame/fps to the nearest native frame and clamps the rounding at the last
native frame. Keep host duration within the source duration. Serve the HTML from the
same origin. Built HTML includes a content security policy that blocks network
connections and external assets while allowing its inline code and embedded
images. Inspect the source before execution; the policy is not a hostile-code
sandbox. The included frame bridge awaits images and fonts, renders the
requested absolute frame, and acknowledges that exact request before Remotion
continues. Errors cancel rendering. There is no autonomous playback clock.

The adapter uses the public Remotion React APIs and is source code, not a new
Remotion installation. Add exported `audio.wav` separately with `Audio` if
needed. Match both timelines at frame zero. Test a short actual Remotion export
with repeat and out-of-order frames on the user's installed version before
accepting a handoff. Source-level or handshake tests alone do not prove an
export. If that environment cannot embed an iframe, use the PNG sequence with
`Img` indexed by `useCurrentFrame()`; preserve the piece's native fps or resample
time explicitly.

## Transparency and editor / Hyperframes handoff

The seven shipped demos paint opaque backgrounds. `--alpha` does not remove
them. An overlay needs an authored renderer/style that clears the canvas each
frame and avoids full-frame opaque paper, backdrop and post-processing fills.
Do not strip paper from a style whose texture or blend modes depend on it.
Render actual transparent pixels and check edges over both light and dark
footage. PNG captures preserve the canvas alpha channel. The tool rejects an
all-opaque source when alpha is requested and an entirely invisible render.

```sh
node tools/animate.mjs render /path/to/overlay --runtime /path/to/private-animation-runtime --out /path/to/overlay-png-01 --format png --alpha
node tools/animate.mjs render /path/to/overlay --runtime /path/to/private-animation-runtime --out /path/to/overlay-prores-01 --format prores --alpha
```

ProRes export uses `prores_ks`, profile 4 (4444), `yuva444p10le` and 16-bit alpha.
Verify the encoded file's decoded alpha, edges and duration on the destination
system. MP4/H.264 uses `yuv420p` and does not preserve alpha; the CLI rejects
`--format mp4 --alpha`. MP4 also requires even width and height; the CLI
rejects odd dimensions before rendering frames.

In Resolve, Premiere or Final Cut, import the sequence at its recorded fps or
use the ProRes movie. Check the application's alpha interpretation and composite
over actual footage. CapCut support varies by platform and version; test the
import and use an opaque rendered clip if its alpha route fails. In Hyperframes,
use a supported alpha movie or frame-indexed PNGs tied to composition time.
H.264 is suitable for an opaque scene, not a transparent overlay. A generated
asset, an import and a verified composite are three separate states.

## Verification

Run offline tests from this directory:

```sh
node --test tests/animation.test.mjs
```

Set `ANIMATION_RUNTIME` to the installed local runtime to run the browser
regressions as well. They cover dimensions, frame seeking, nondeterministic
sources, real PNG transparency and paths with spaces. The repository validator
runs this suite; CI installs an isolated runtime and enables browser tests.
Neither a passing test suite nor successful encoding replaces watching the
actual deliverable.
