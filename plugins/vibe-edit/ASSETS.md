# Optional asset bundle

The plugin stays small so it installs quickly. Large example renders, a 24 MB template overlay, extra practice audio and texture masks live in a separate download:

- Public: the `vibe-edit-assets-6.0.0.zip` file attached to the matching GitHub release at https://github.com/paytonbilodeau/ai-video-editing-pack/releases
- Vibe Editors members: the same file in the community classroom resource for this version

Nothing in the first setup or an ordinary edit needs it. A skill tells you when it does.

## Where to put it

Unzip it into a folder named `Vibe Edit Assets` beside the person's editing projects, not inside the plugin (the plugin folder is replaced on every update). Record that folder as `assets_path` in `Vibe Edit Settings/SETUP STATUS.json`. Skills refer to files inside it by the same relative paths listed below.

## What is in it

| Path inside the bundle | Used by |
| --- | --- |
| `examples/rendered/*.mp4` | style: rendered reference videos for Tech Motion, Gentlemen, Sketch, Editorial, JavaScript, HyperFrames, the portrait layout and the pan effect |
| `examples/narrative-motion/preview.mp4`, `examples/dedicated-short/preview.mp4` | remotion: previews of the two editable examples |
| `examples/portrait-short/source.mp4` | shorts: source clip for the portrait short example |
| `hyperframes/templates/gentlemen-hybrid/assets/overlay.mov` | hyperframes: the Gentlemen hybrid template overlay |
| `hyperframes-workflows/music-to-video/references/templates/**/assets/**` | hyperframes: texture masks for the music-to-video templates |
| `practice/synthetic-lamp/*.wav`, `practice/synthetic-lamp/assets/*`, `build.py`, `scenes.ffconcat` | practice: the hum-filter listening exercise and the kit that rebuilds the practice videos |

Every file keeps the license stated in `THIRD-PARTY.md` and `licenses/`.
