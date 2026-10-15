# Set up motion graphics

[JavaScript](#javascript-animation) · [Remotion](#remotion) · [HyperFrames](#hyperframes)

Your AI can build animated text, diagrams, callouts and explanations, then place
them in your video. Start with tools you already have. The assistant can handle
the technical setup after you choose what to add.

## Match a shown look

For the included Tech Motion, Gentlemen or layered Sketch examples, use [the matching source and render guide](<../../Payton Editing System/motion/flow/README.md>) and [example code](<../../Payton Editing System/motion/flow/src/Examples.tsx>). The starters below check each engine. Their neutral/cut-paper scenes are different examples.

## A simple choice during setup

The assistant should offer this early, without making it a requirement:

> Want motion graphics ready too? Your editor can already handle simple titles.
> The pack also supports Remotion, HyperFrames and a JavaScript drawing kit.
> The AI can check what you have and set up one suitable option.
> You can also leave this for the first video that needs it.

Recommend a route from the person's work and explain it in one sentence. Do not
make a beginner pick a programming language. If they already have a working
motion project, reuse its setup, design, assets and components. A new tool should
solve a need, not replace their work by default.

| Tool | Useful for | What the person keeps |
|---|---|---|
| Remotion | Reusable layouts and scenes built from React components. | Editable source, project settings and rendered video. |
| HyperFrames | HTML/CSS layouts and seekable animation, including explainers and overlays. | Editable HTML, local assets and rendered video. |
| JavaScript kit | Custom drawings, diagrams and procedural animation with seven included styles. | Editable scene code, drawing kits and rendered frames or video. |

The tools can work together. For example, a JavaScript diagram can use the
included Remotion adapter. A HyperFrames layer can be rendered and placed beside
it in the video editor. Each scene needs one clear owner and one known timeline.
Installing every tool does not automatically improve a graphic.

## What setup changes

The AI should inspect the chosen project and existing commands first. Node runs
JavaScript tools. Python runs some pack utilities. FFmpeg reads or encodes media.
A browser renderer turns animation code into frames. These are ordinary programs;
they do not give the AI new account permissions by themselves.

Before adding missing software, explain what it is for, where it will go, and
whether it needs a download, account, upload or payment. Group the necessary
changes into one understandable choice. Once the person approves that scope,
complete it without repeatedly asking for the same permission. Keep a separate
working project, exact dependency versions and an easy way to remove it.

Prefer project-local dependencies. Inspect official source and installation
scripts. Preserve existing package files, assistant skills and configuration.
Do not install a second global copy or overwrite a user's customized skill just
because a tutorial uses a one-line command. A new purchase, uploaded private
footage or broader permissions needs its own clear choice.

## Remotion

The full download includes an original starter in
[System 09](../../09%20Visual%20Storytelling%20and%20Motion%20System/INSTALL.md).
Copy `09 Visual Storytelling and Motion System/starter` into a separate
working folder. It uses Remotion **4.0.535**. Your AI can run these commands
from that copy:

```text
npm ci
npm test
npm run render
```

Open `out/neutral-motion.mp4`: the included scene is five seconds long and
silent. Use `npm run studio` for its editable browser preview. For a transparent
overlay, run `npm run render:overlay` and check `out/neutral-motion.mov` in
your editor. That route uses transparent source and ProRes 4444. Render only
the version you need. The render helper uses an installed Chrome/Chromium in a separate process when
available; otherwise a browser download may be required on first use. The AI should inspect the completed file and its reading time.

Check Node.js and the current operating-system requirements before installing.
As checked October 15, 2026, Remotion requires macOS 15 or newer on a Mac;
the official setup page lists the other platforms.

For a new project, follow the current [official setup](https://www.remotion.dev/docs/)
and [agent-skills instructions](https://www.remotion.dev/docs/ai/skills).
Choose only the relevant skill destinations and preserve existing copies.
Record and lock the versions used. Do not update a working project's dependency
versions in the middle of an edit without a reason and a regression check.

Remotion's [license](https://www.remotion.dev/license) permits free video creation
for eligible individuals and organizations, with a company license required
outside those terms. Check the user's situation. A ChatGPT or Claude subscription
does not purchase a separate company license or hosted rendering service.

## HyperFrames

The full download includes an original
[HyperFrames starter](../../09%20Visual%20Storytelling%20and%20Motion%20System/hyperframes-starter/README.md).
It pins HyperFrames **0.8.150**. The official CLI requires Node 22+ and FFmpeg.
Its local renderer uses a browser. The assistant should copy the starter into a
private project and install its locked packages after the setup choice.

Use `HYPERFRAMES_NO_TELEMETRY=1` for local commands without usage telemetry. The AI
should set it using the current shell's syntax. Then run:

```text
npm ci
npm run doctor
npm run check
npm run render
```

`doctor` reports prerequisites and optional tools. Its process can exit
successfully while its JSON says `ok: false`, including when optional voices,
transcription or Docker are absent. Read each finding: this local silent example
needs Node, FFmpeg/FFprobe and the browser, not every optional service. Resolve
missing requirements for the chosen render, then run `check` and inspect the
actual video for meaning, motion and readability.
Use `npm run render:overlay` when the receiving editor needs transparency.

Open `out/one-idea.mp4`: the supplied scene is five seconds long and silent.
Use `npm run preview` for the browser preview. The overlay command writes
`out/one-idea.mov`; check it over the actual footage in your editor.

For a fresh project, consult the [official quickstart](https://hyperframes.app/docs/1-startup/2-quickstart)
and [CLI guide](https://hyperframes.app/docs/5-packages/cli). The vendor offers
core skills and larger plugin bundles. Choose the relevant install, inspect its
destination and avoid overwriting another workflow. Record the installed skill
revision separately from the rendering version.

Local HyperFrames rendering is available under Apache 2.0 without a per-render
fee. Hosted rendering, generated media, voices and other services are separate
products. They are not needed for the supplied local example.

## JavaScript animation

Read the included [JavaScript skill](../skills/javascript-animation/SKILL.md).
It contains the builder, seven style kits and an optional pinned browser runtime.
Its [guide](../skills/javascript-animation/GUIDE.md) covers setup, checking,
storyboards and rendering. It needs Node.js 22+, FFmpeg for video, and a browser
runtime. From `AI Video Editing Pack/skills/javascript-animation`, your AI can
run the following. Replace `/path/to/private` with your actual working location
outside the pack; use a new output folder each time. Reuse an existing runtime
instead of running setup again.

```text
node tools/animate.mjs setup /path/to/private/motion-runtime
node tools/animate.mjs init /path/to/private/my-graphic --style cut-paper
node tools/animate.mjs build /path/to/private/my-graphic
node tools/animate.mjs check /path/to/private/my-graphic --runtime /path/to/private/motion-runtime --out /path/to/private/check-01
node tools/animate.mjs render /path/to/private/my-graphic --runtime /path/to/private/motion-runtime --out /path/to/private/render-01 --format mp4
```

Open `render-01/animation.mp4` and watch the entire animation. This command
does not add sound. Preserve the editable project and the runtime lockfile.

This route needs no new account or paid generation provider. The shipped examples
are opaque; an overlay requires a scene authored with transparent areas. Keep
the JavaScript source even when the editor receives a rendered file.

## One test before a full sequence

The assistant should make the first test part of the approved setup, using
synthetic material or authorized copies. No new recording is required.

1. Build a short scene with a title, one relationship or action, and enough time
   to read the final state. Use original text and the person's chosen visual style.
2. Check the opening, moving state, settled hold and ending. Seek forward and
   backward to catch state that depends on playback order.
3. Render to a new path. Inspect dimensions, frame rate, duration and whether
   audio or transparency is present as intended.
4. Import into the chosen editor. Check it over real footage, including faces,
   captions and screen demonstrations. Check alpha over light and dark areas.
5. Save the editable source, successful command and tool versions. Explain what
   works and any remaining app step in ordinary language.

If the test fails, fix the actual cause or choose a suitable route already
available. Do not tell the person to reinstall everything. A passing technical
check proves the tested operation; a useful graphic also needs a clear idea,
readable design, good timing and a checked final composite.
