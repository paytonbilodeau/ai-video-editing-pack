# Set Up One Motion Tool

Use Resolve/Fusion for native compositing and footage interaction. Choose
Remotion for React components that derive their appearance from frame numbers,
or Hyperframes for HTML scenes with seekable animation. Both can supply assets
to a Resolve timeline; neither replaces the review of that final composite.

## Remotion: use the library's existing neutral starter

Read System 09's `INSTALL.md` and `THIRD-PARTY.md`. Copy its `starter` directory
into a new working project. From that copy:

```text
npm ci
npm test
npm run studio
npm run render
```

The included script renders `NeutralMotion` to `out/neutral-motion.mp4`, muted.
Inspect that small render before changing its content. Keep the lockfile and
exact dependency versions together. These are pinned working versions, not a
claim to be the newest. For a fresh project outside this starter, use Remotion's
[current project guide](https://www.remotion.dev/docs/).

Browser installation may be an additional download. The Remotion
[license](https://www.remotion.dev/license) has eligibility conditions; do not
describe it as free for every business. Confirm your intended use before setup.

For an overlay, first make a five-second test with transparent corners and a
soft edge. Follow the [transparent-video guide](https://www.remotion.dev/docs/transparent-videos)
for a supported alpha codec and pixel format. Import into Resolve and check
over dark, light and actual footage. Keep a muted graphic and a separate sound
stem when that helps prevent duplicated dialogue. Ordinary H.264 output does
not preserve alpha. Keep an opaque alternative where the editor cannot use
the chosen alpha format.

## Hyperframes: create a small local project

The official CLI documents Node.js 22+ and FFmpeg. Check the current
[repository](https://github.com/heygen-com/hyperframes) and
[CLI guide](https://hyperframes.heygen.com/packages/cli) before installation.
The following commands can download and execute packages, install skills,
create files and start a local preview. Run them only after approving setup:

```text
npx hyperframes init motion-test
cd motion-test
npx hyperframes --version
npx hyperframes preview
npx hyperframes render
```

Choose a plain example when prompted. For an agent-led setup, the official
[quickstart](https://github.com/heygen-com/hyperframes/blob/main/docs/quickstart.mdx)
uses `npx hyperframes skills update` to install the core skills. Review the
destination and changes before applying it to an existing skill library.
Record the resolved CLI version and pin it in the working project's package
scripts after the first passing render. Later runs must use that pin, not
silently float to a new version. Inspect the installed command's help when
flags differ from an older tutorial.

Local Hyperframes rendering does not use HeyGen generation credits. Optional
hosted rendering, avatars, voices and generated assets have separate terms and
costs. Do not enable them as part of a local test by accident.

## Ask for a neutral test

```text
Make a five-second original explanation using a plain background, the words
"One clear idea", one arrow and a readable hold. Use the motion tool we chose.
Use local supplied assets and no generated voice, music or paid service. Keep
the project editable. Show the start, settled state and end, then render it.
Inspect the encoded clip and test it over my copied footage in Resolve. Record
the command and versions that worked before expanding the scene.
```

## Production lessons to apply after the test

- Keep narration time, frame rate and composition duration explicit. An animation
  must finish its information change and leave reading time before its exit.
- For frame-driven work, derive animation from the composition clock. Avoid
  uncontrolled wall-clock timers, random state or render-time network assets.
- In Hyperframes, verify frame zero and repeated direct seeks. Essential hidden
  initial states belong in static CSS too. A paused animation can otherwise
  expose a layer before the first seek. CSS stacking owns layer order.
- Keep text and its background in one transform group when they should move
  together. Use internal transforms only for independent content movement.
- Check sound in the encoded result, not only the preview. Keep a single intended
  dialogue path and review effects underneath speech at normal volume.
- A partial render failure does not invalidate every finished part. Reuse a part
  only when its source, timing and dependencies still match, then inspect joins.

Use System 09's beat map, asset ledger and render plan to scale beyond the test.
Do not copy a private creator preset or bundle third-party reference assets.
