# Build the stage and its timing

At 1920×1080, useful starting values are a 140px content margin, 90–140px serif
heading, 44–70px card label and 26–32px functional text. Paper #F7F8F2, ink
#192B23 and green #0F583D are editable house defaults. Recompose portrait.

For each semantic cue, record the exact source hash, phrase, start/end, retained
objects, what changes and why. Preparatory movement may begin before a word;
the new meaning should arrive at its actual cue. Do not use one timer for every
scene. A fixed numerical hold is not a universal reading-time rule.

The included `flow/src/narrative/primitives.tsx` supplies clamped time functions,
cards, reveals, paths and directional planes. Internal reveals can start around
0.35–0.50 seconds with 18–28px travel. Wipes can start around one-third second.
Couple blur to moving content only and return to zero at rest. Keep the canvas
and presenter stable. A 2–4% push is optional when it directs attention.

Connectors and labels share an object coordinate system. Attach an underline to
the actual text width with descender clearance. Clear old text before new text
occupies the same ink area. Do not keep a temporary clipping mask over settled
italics. Keep real video frame-aware and mute it unless its audio is authorized.

Use the existing Flow/Remotion engine and local fonts. Copy the example to a new
project; keep other compositions unchanged. No timers, unseeded randomness or
live asset downloads during rendering. Test repeated and out-of-order frames.

[Frame-driven animation](https://www.remotion.dev/docs/animating-properties)
and [easing](https://www.remotion.dev/docs/easing) document the renderer approach.
