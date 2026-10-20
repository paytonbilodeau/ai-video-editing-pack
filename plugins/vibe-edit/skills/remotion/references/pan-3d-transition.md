# 3D pan transition

An optional swivel teaser: frames from later in the video rotate in 3D at high speed, then the video continues. It renders through Flow in Remotion.

## Scripts

- [`../tools/pan_3d_transition.py`](../tools/pan_3d_transition.py) renders the transition clip from a source video.
- [`../tools/insert_3d_transition.py`](../tools/insert_3d_transition.py) renders it and inserts it into a copy of the video.

Both find Flow at `../flow` relative to the tools folder and write temporary frames and a dynamic composition inside that `flow/` folder, then call its installed `node_modules/.bin/remotion`. To keep those writes out of the plugin, copy the whole `remotion` skill folder (`tools/` beside `flow/`) into the person's workspace and run from there.

## Usage

```bash
python3 tools/insert_3d_transition.py input.mp4 new-output.mp4 \
  --insert-at 3 \
  --duration 5 \
  --teaser-start 60 \
  --bg-image /path/to/bg.png
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--insert-at` | 3 | Where to insert (seconds) |
| `--duration` | 5 | Transition duration |
| `--teaser-start` | 60 | Where to sample content from |
| `--bg-image` | none | Background image |

`pan_3d_transition.py` alone takes `input.mp4 output.mp4` plus `--start`, `--source-duration`, `--output-duration`, swivel, tilt, perspective, speed, easing and background options; run it with `--help`.

## How it works

1. Extracts frames from later in the video.
2. Renders a 3D rotating composition with Remotion.
3. Splits the video into intro, transition and main.
4. Concatenates them with audio preserved.

## Dependencies

Node 22 or newer, FFmpeg, and Flow's pinned dependencies installed in the `flow/` folder beside `tools/`:

```bash
cd flow && npm ci --ignore-scripts --no-audit --no-fund
```

Remotion's license applies; see [THIRD-PARTY](../../../THIRD-PARTY.md).

## Scope

Read [MOTION OVERVIEW](<../../style/references/MOTION OVERVIEW.md>) first. Use the person's own project, profile and authorized tools. Current task permissions control spending, downloads and publication.

The historical stream-copy insertion route is optional and does not guarantee frame-exact boundaries or unchanged audio timing. Use the native editor for a critical cut; verify full output timing and audio after any use. The standalone pan effect preserves the source frame rate in the portable adaptation. Write to a new output name and keep the original video.
