#!/usr/bin/env bash
# Frame-INDEXED contact sheet for Flow QA.
#
# Why not `fps=1/N,tile=...`: that resamples on timestamps and the cells do
# not land on the frames you think they do. Chasing a "missing" beat through
# a mislabelled tile wastes a render cycle. This selects explicit frame
# numbers and burns the index into each cell, so what you see is checkable
# against the scene code and the word transcript.
#
# Usage:
#   scripts/qa-contact-sheet.sh <video> <out.png> <cols> <frame> [frame ...]
#
# Example:
#   scripts/qa-contact-sheet.sh out/bench0808/C.mp4 /tmp/qa-C.png 7 \
#     0 60 120 180 240 300 360

set -euo pipefail

VIDEO="$1"; OUT="$2"; COLS="$3"; shift 3
FRAMES=("$@")

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

i=0
for f in "${FRAMES[@]}"; do
  ffmpeg -hide_banner -loglevel error \
    -i "$VIDEO" \
    -vf "select='eq(n\,${f})',scale=240:-2,drawtext=text='f${f}':x=7:y=7:fontsize=21:fontcolor=yellow:box=1:boxcolor=black@0.75:boxborderw=4" \
    -frames:v 1 "$TMP/$(printf '%03d' "$i").png" -y
  i=$((i + 1))
done

ROWS=$(( (${#FRAMES[@]} + COLS - 1) / COLS ))
ffmpeg -hide_banner -loglevel error \
  -pattern_type glob -i "$TMP/*.png" \
  -vf "tile=${COLS}x${ROWS}:padding=4:color=0x202020" \
  -frames:v 1 "$OUT" -y

echo "wrote $OUT (${#FRAMES[@]} frames, ${COLS}x${ROWS})"
