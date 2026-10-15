---
name: pan-3d-transition
description: Create 3D pan/swivel transition effects for videos using Remotion. Use when user asks to add 3D transitions, create swivel effects, or add video transitions.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# 3D Pan Transition

## Goal
Create 3D rotating "swivel" transition effects for videos using Remotion rendering.

## Scripts
- `../../tools/insert_3d_transition.py` - Insert transition into video

## Usage

```bash
python3 ../../tools/insert_3d_transition.py input.mp4 output.mp4 \
  --insert-at 3 \
  --duration 5 \
  --teaser-start 60 \
  --bg-image Drop/bg.png
```

## Parameters
| Argument | Default | Description |
|----------|---------|-------------|
| `--insert-at` | 3 | Where to insert (seconds) |
| `--duration` | 5 | Transition duration |
| `--teaser-start` | 60 | Where to sample content from |
| `--bg-image` | none | Background image |

## How It Works
1. Extracts frames from later in video
2. Creates 3D rotating animation via Remotion
3. Splits video: intro, transition, main
4. Concatenates with audio preserved

## Dependencies
```bash
cd motion/flow && npm ci
```

## Output
Video with swivel teaser inserted at specified position.


Customer scope: read `motion/START HERE.md` first. Use your own working copy, existing customer profile and authorized tools. Current task permissions control spending, downloads and publication.

Run in a fresh full motion working copy. The historical stream-copy insertion route is optional and does not guarantee frame-exact boundaries or unchanged audio timing. Use the native editor for a critical cut; verify full output timing/audio after any use. The standalone pan effect preserves the source frame rate in the portable adaptation.
