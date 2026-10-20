# Payton's Sketch Image Style Specification

This is the canonical visual language for Sketch still images and generated animation. The model or production tool can change. The visual language does not.

The canonical name is **Payton's Sketch image style**. Also accept Sketch, sketch style, paint and sketch, paint sketch style, paint sketch, paint sketches, Payton Sketch, Payton's sketch, and hand-drawn image style. All names invoke this exact system. Keep `hand-drawn-style` as the technical skill ID for compatibility.

## Identity

Sketch turns one useful idea into one instantly readable hand-drawn scene. It combines the clarity of an explainer animatic with the authentic roughness of a real working sketch, a calm teaching voice, green-led palette, and personal character silhouette.

The result should feel drawn by a thoughtful human visual storyteller, not arranged by an infographic template and not copied from another creator.

## Two-second read

Before prompting, write one private sentence that completes this thought:

`The viewer should instantly understand that ...`

Build the frame around one physical relationship that proves that sentence. One metaphor, one dominant action, and one focal object are the default. A scene can include supporting props, but it must not carry a second thesis.

## Visual DNA

- **Line hierarchy:** loose dry charcoal or blue-gray digital-pencil strokes. Main contours are darker but still wobbly and sometimes doubled. Secondary props use lighter searching lines. Background suggestions are pale and incomplete.
- **Authentic roughness:** keep about 5 to 15 percent visible underdrawing. Allow small correction strokes, abandoned construction arcs, open joins, slight overlaps, uneven pressure, and repeated attempts at a contour. Roughness comes from the drawing decisions, not a paper-grain filter.
- **Coherence floor:** every important silhouette, hand interaction, prop, and facial beat must still read instantly. Rough does not mean malformed, muddy, or random.
- **Shapes:** compact slightly awkward cartoon anatomy, oversized heads, minimal dot-or-line faces, simplified hands, angular readable hair, reduced props, and strong pose silhouettes. Avoid polished jawlines, handsome hero rendering, perfect anatomy, and uniform character proportions.
- **Fills:** light flat color washes with a little streak, edge wobble, or off-register overlap. Do not perfectly clip every fill to a smooth ink outline.
- **Background:** 70 to 80 percent flat off-white or a very pale cool field with no photoreal paper vignette. Suggest the place with three to seven incomplete marks, then stop.
- **Color:** grayscale and pale blue-gray structure plus one main accent. Old Money Green `#0F583D` is the light-background default. Mint `#72DFA5` is the dark-background accent. A tiny warm micro-accent may mark friction, insight, or motion.
- **Light:** flat fills and simple tonal separation. No cinematic rendering, glossy highlights, gradients, or realistic shadows.
- **Emotion:** one readable beat at a time through posture, eyeline, brows, mouth, and distance. Even difficult scenes should feel recoverable rather than panicked.
- **Text:** usually none. When needed, use one integrated hand-lettered phrase of two to five words on a sign, note, label, or speech bubble. Do not turn the frame into a poster.

## Character identity

Use the customer as the recurring person only when the task calls for their first-person teaching, workflow or story and they supply an authorized reference. Keep a short character sheet in their working project: head and hair silhouette, simple face, clothing and one accent. For other ideas, use a generic person or no person. Never insert Payton's likeness as the customer's identity. Keep the compact, slightly awkward anatomy and unpolished drawing; changing identity does not require smoothing the style.

## Composition grammar

Choose the smallest format that carries the idea:

1. A medium character scene with one action.
2. A close-up of one symbolic prop or hand interaction.
3. A wide scale-contrast metaphor.
4. Two rough panels for cause and effect.
5. A hand-lettered title or principle card used as punctuation.
6. A simplified UI or diagram only when the idea genuinely depends on it.

Across a sequence, alternate character scene, prop close-up, title or label beat, and physical metaphor. Do not repeat the same desk, presenter pose, camera distance, or machine metaphor.

## Palette

On light fields:

- Background: warm off-white or pale blue-gray.
- Linework: charcoal, black, or muted blue-gray.
- Main accent: Old Money Green `#0F583D` by default.
- Highlight: Mint `#72DFA5` in small amounts.
- Optional micro-accent: mustard, muted coral, or burnt orange only when the story needs it.

On dark fields:

- Background: near-black or very dark green.
- Linework and subject: off-white and pale gray.
- Main accent: Mint `#72DFA5`.
- Depth: Old Money Green `#0F583D`.

Use one accent family per frame. Leave most objects uncolored. Never default to a balanced multi-color palette.

## Static generation lock

Use this block inside every still-image prompt:

```text
SKETCH STYLE LOCK:
One clear visual thesis staged as a physical relationship. Authentic rough-but-coherent explainer sketch drawn with loose dry blue-gray or charcoal digital-pencil strokes. Contours visibly search for the shape: slightly wobbly lines, occasional doubled strokes, open imperfect joins, pale construction marks, and small corrections. Keep roughly 5 to 15 percent visible underdrawing. Important silhouettes stay simple and unmistakable. Characters have compact slightly awkward cartoon anatomy, minimal dot-or-line faces, simplified hands, and no polished jaw or realistic facial rendering. Flat color washes are loose, lightly streaked, and sometimes a little off-register rather than perfectly clipped. Backgrounds are only a few pale incomplete marks with 70 to 80 percent blank off-white or pale cool field and no paper vignette. Mostly grayscale structure with one green-led accent, Old Money Green #0F583D by default on light backgrounds, plus only a tiny warm micro-accent if needed. One dominant action. Little or no text; any text is short and genuinely hand-lettered. Original scene and metaphor. Not an infographic, clean inked cartoon, polished digital illustration, vector mascot, anime frame, photoreal image, glossy UI, or imitation of another creator.
```

## Motion preservation lock

Generate or approve the still keyframe first. The video model is an animator, not a second art director.

Use this block inside every generated-video prompt:

```text
SKETCH MOTION LOCK:
Preserve the approved keyframe's composition, subject identity, the chosen character's silhouette, rough searching linework, visible underdrawing, loose off-register fills, negative space, exact palette, exact words, and exact official logos. Do not clean up, smooth, ink, polish, or redraw the sketch during motion. Animate one primary action immediately. At most one tiny secondary action may add life. Keep the camera locked unless a small intentional camera move is required by the meaning. Add no new objects, characters, words, logos, colors, effects, or scenery. Do not morph faces, props, letters, or marks. Keep every logo and word in a static zone away from the mover. Keep a subtle handmade line-boil, with the same coherent silhouettes in every frame. End with the subject settled, fully in frame, and the final composition still readable as a complete sketch.
```

For a sequence, reuse the same character sheet, palette statement, line hierarchy, and approved first frame. Change only the scene, action, and framing needed for the next idea.

## Logos and exact words

Acquire the current official logo asset from an authoritative source and provide it to the native image generator as a required visual reference. Generate the full still, exact mark, and short final words together so perspective, lighting, texture, spacing, occlusion, and softness belong to the same scene. The mark keeps its exact recognizable structure, proportions, spacing, and wordmark while adopting the scene's own pencil strokes, fills, texture, and palette treatment. It appears once on a believable static surface away from the planned mover. Never reserve a blank plate for later compositing or repair the result with a flat overlay. If the still fails, use a targeted native image edit or regenerate it. The video model receives only the approved keyframe and may not add, redraw, move, or alter any logo or word.

## Originality boundary

The August 2026 study of older Improvement Pill videos informed broad explainer principles: single-metaphor clarity, sparse settings, expressive posing, alternating scene types, controlled imperfection, and selective color. Do not copy its recurring characters, pill identity, exact frames, compositions, scenes, lettering, timing sequences, or palette. Do not name the reference creator inside generation prompts. The chosen avatar, stable silhouette and green-led palette, original metaphors, calmer emotional tone, and unified still-and-motion grammar are the owned system.

## QA rubric

A final passes only when all answers are yes:

1. Can a phone-size viewer understand the thesis in about two seconds?
2. Is there one dominant metaphor, action, and focal object?
3. Does the subject silhouette read without labels?
4. Is most of the frame quiet negative space?
5. Does the linework visibly show underdrawing, searching or corrected contours, open joins, and uneven pressure without losing coherent shapes? Smooth finished ink fails.
6. Is there one accent family rather than a rainbow palette?
7. If a recurring person appears, is their chosen silhouette stable?
8. Is text absent or short, integrated, and necessary?
9. Is the scene original rather than a recognizable recreation?
10. In motion, did every object, word, logo, face, line, and color stay stable until the composed ending?
