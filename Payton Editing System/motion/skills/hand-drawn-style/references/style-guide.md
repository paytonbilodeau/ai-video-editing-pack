# Payton Sketch — Compatibility Workflow Guide

This is a compatibility export for older callers. The canonical visual source is `payton-sketch-style-spec.md`; `SKILL.md` is the operating manual. When this guide disagrees with either file, the canonical spec wins.


---

## One-Sentence Style Definition

An authentic rough-but-coherent educational sketch frame with dry blue-gray or charcoal pencil lines, visible underdrawing and correction strokes, loose off-register fills, flat pale backgrounds, one strong accent color, simple character acting, sparse hand-lettered text, and storyboard-first composition.

Roughness is now a required style feature, not an optional imperfection. A smooth inked contour, polished face, perfect anatomy, or perfectly clipped fill fails even if the composition is good. Preserve coherent silhouettes while leaving about 5 to 15 percent of the searching drawing visible.

---

## What Changed From the Old Style

The old guide drifted toward clean whiteboard infographic. The reference sheet is actually rougher, simpler, more panel-based, and more like frames from an explainer animation.

### What the old guide allowed (and we are moving away from)

- Clean rounded cards
- Symmetrical 3-column diagrams
- Polished icon grids
- Large smiling presenter portraits
- Balanced multi-color palettes
- Corporate explainer infographic structure

### What the reference sheet actually emphasizes

- Single or stacked storyboard panels
- Cropped scenes and close-up moments
- Simple character acting
- Rough black or blue-gray line art
- Large pale gray or white negative space
- One accent color carrying the idea
- Speech bubbles, thought bubbles, rough labels, hand-written words
- Incomplete backgrounds that feel sketched, not designed

### The eight required changes

1. **Default away from infographic cards.** If the user gives a list or framework, do not automatically create three clean panels or cards. Turn the list into a scene, a rough two-panel storyboard, or physical objects.

2. **Use rough storyboard staging first.** The reference sheet looks like frames from a simple animated explainer. Camera close, background unfinished, characters mid-action.

3. **Use fewer colors.** Grayscale plus one accent is the default. One accent by default, with a tiny second accent only when needed.

4. **Make characters simpler and less polished.** Not clean mascot illustrations. Faces minimal. Bodies simple. Emotion from pose, gesture, and scene context.

5. **Use flat digital fills, not texture-heavy paper or charcoal.** Clean flat fills and line art. Hand-drawn, but not gritty charcoal. Paper grain can be subtle, never defining.

6. **Use text like the reference sheet uses text.** Big hand-drawn titles, speech bubbles, signs, labels, correction marks. Never a polished framework poster with many labels.

7. **Make the prompt explicitly say "not a clean infographic."** Most important negative constraint. Without it, the model over-organizes.

8. **Use this guide as the active style lock.** Do not force a full PDF re-analysis before every image. Re-check the reference sheet only for diagnostics or when an output drifts.

---

## The Six Reference Modes

Pick exactly one mode per image. Blend two only if the topic genuinely sits between them.

### Mode A — Rough storyboard scene

For personal stories, teaching moments, emotions, social posts.

One scene. Loose background. Character mid-action. One or two props. Maybe a speech bubble.

Use when the idea can be shown as a person doing or feeling something.

### Mode B — Two stacked animatic panels

For before/after, cause/effect, setup/payoff, "this leads to that."

Two wide panels stacked vertically. Top sets the problem. Bottom shows the turn, result, or explanation. Simple color accents.

Use when the idea has a clear contrast.

### Mode C — Close-up prop shot

For software workflows, checklists, phones, prompts, files, folders, dashboards, or one symbolic object.

One large prop fills the frame. Hand, screen, folder, sticky note, or document is oversized. UI text mostly scribbles. One readable phrase or label.

Use when a single object can carry the idea.

### Mode D — Rough UI moment

For AI tools, automations, courses, dashboards, app concepts.

Screen drawn like a sketch. Large interface blocks. Mostly scribbled text. One readable label. Character or hand nearby if needed.

Avoid glossy UI and perfect app mockups.

### Mode E — Physical metaphor scene

For abstract claims, frameworks, business ideas, productivity, learning, AI concepts.

The abstract idea becomes an object: messy desk, machine, conveyor belt, shelf, folder, map, cord, stamp, robot, sign. Characters interact with the object. Label only the key object.

Use when the idea would otherwise become a boring diagram.

### Mode F — Simple comic explainer card

For complex ideas that genuinely need labels.

Muted background block. Simple title. A few labeled objects. Rough arrows or circles. Still visibly hand-drawn.

Use sparingly. This is the closest the style gets to infographic.

---

## Non-Negotiable Style Rules

### Linework

Use:
- Rough black or blue-gray digital ink
- Imperfect joins
- Quick sketch strokes
- Slightly uneven contours
- Simple line-weight variation
- Sketchy motion marks and emphasis lines

Avoid:
- Clean vector outlines
- Perfect technical geometry
- Heavy charcoal texture
- Painterly crosshatching
- Glossy comic rendering

Prompt phrases to include:
- rough hand-drawn educational animatic
- loose black digital ink
- uneven storyboard linework
- imperfect sketch strokes
- unfinished explainer-video frame
- simple flat line art

### Color

**Default to luxury green `#0F583D` as the main accent.** Vary the accent by topic. Never default to navy or balanced rainbow palettes.

Default formula:
- Background: off-white, pale gray, or muted blue-gray
- Ink: black, charcoal, or blue-gray
- Accent: one color, picked from the table in SKILL.md (luxury green by default)
- Optional micro-accent: red circle, yellow spark, or orange mark

Use large white or gray areas. Do not color every object.

Avoid:
- Full rainbow palettes
- Realistic skin rendering
- Shiny gradients
- Complex lighting
- Polished advertising colors

### Characters

Readable but simple.

Use:
- Line eyes or dot eyes
- Minimal nose
- Simple mouth
- Expressive eyebrows only when useful
- Simplified hands
- Casual proportions
- Clear posture

Avoid:
- Highly rendered faces
- Perfect anatomy
- Mascot-style polish
- Exaggerated 3D cartoon emotion

### Customer character

Use the supplied customer character sheet and the canonical specification.

## What Never To Generate

- Photorealism
- 3D render
- Pixar-style character
- Clean vector art
- Corporate infographic style
- Glossy UI mockup
- Polished dashboard product shot
- Dense poster text
- Realistic shading
- Airbrushed gradients
- Painterly rendering
- Anime polish
- Perfect icon-grid layout
- Symmetrical 3-card framework unless explicitly requested

---

## Aspect Ratio Composition Notes

### 5:2
Use for X Article header images.
- Generate a 16:9 4K master, then crop to exact 5:2
- Keep every essential subject, face, symbol, and headline inside the middle 70 percent of the source height
- Use the outer top and bottom strips only for blank background or disposable sketch residue
- Inspect the final crop instead of trusting an automatic center crop

### 2:1
Use for thumbnails and banners.
- One dominant center-safe subject
- Keep bottom-left clear when requested (talking-head overlay)
- Avoid tiny details
- Text should be large and short

### 16:9
Use for standard video thumbnails and LinkedIn Article cover images. LinkedIn recommends 1920 x 1080.
- One main subject on a third or center
- Leave room for short text
- Use one focal scene, not many panels

### 4:3
Use for educational post visuals.
- Works well for one storyboard scene or a two-level composition
- Keep text large
- Avoid too many small labels

### 1:1
Use for iconic social visuals.
- One dominant centered metaphor
- Minimal background
- No tiny UI details

### 4:5
Use for feed graphics.
- Stack headline, scene, and payoff vertically
- One large character or prop
- Use one or two panels

### 9:16
Use for shorts and stories.
- Vertical scene
- Main subject in the middle
- Payoff or bubble above
- Large text only

---

## Prompt Formula

```
Create a [ASPECT RATIO] image in the reference-sheet hand-drawn educational animatic style.
Core read: [2 SECOND READ].
Show [MAIN SUBJECT] [ACTION] in a rough storyboard scene.
Use [FOCAL OBJECT / METAPHOR] as the main visual anchor.
Composition: [REFERENCE MODE + PLACEMENT].
Text: [SHORT HAND-LETTERED PHRASE OR NONE].
Style: rough black and blue-gray digital ink, loose uneven linework, imperfect sketch strokes,
simple flat fills, pale gray/off-white background, ONE muted accent color, simple expressive
characters, sparse hand-lettered text, unfinished explainer-video storyboard frame.
Avoid clean 3-card infographic layouts, polished vector icons, glossy UI, photorealism, 3D,
dense labels, realistic lighting, and over-rendered faces.
```

---

## Strong Style Lock (When the Model Drifts)

```
Rough hand-drawn educational animatic storyboard frame, like an unfinished explainer-video
still. Loose black digital ink and blue-gray sketch lines, uneven contours, imperfect joins,
quick motion marks, simple flat color blocks, mostly grayscale with ONE accent color, pale
gray/off-white background, simple characters with minimal faces, sparse hand-lettered text
only. Not a clean infographic, not a vector illustration, not glossy, not 3D, not
photorealistic, no dense text, no polished card layout.
```

---

## Negative Prompt Bank

- no clean infographic
- no 3-card framework layout
- no perfect rounded cards
- no corporate vector art
- no glossy UI
- no photorealism
- no 3D render
- no Pixar-style character
- no full-color advertising poster
- no realistic lighting
- no smooth gradients
- no airbrushed shading
- no dense labels
- no perfect typography
- no polished icon grid
- no over-rendered faces
- no navy / blue-gray default colorway

---

## Troubleshooting Quick Reference

| Problem | Add to the prompt |
|---|---|
| Too clean | "Make it rougher and more like a storyboard sketch, uneven digital ink, imperfect line joins, simple flat fills, unfinished background, no clean infographic." |
| Looks like a corporate infographic | "Turn the framework into a physical scene with characters and props, not a diagram. Use one rough storyboard panel or two stacked panels." |
| Too many colors | "Mostly grayscale and off-white with ONE accent color only. Leave large areas uncolored." |
| Defaulted to navy / blue-gray | "Replace the navy/blue-gray colorway. Use luxury green #0F583D as the main accent. Off-white background. Black linework. Leave large areas uncolored." |
| Too much text | "One short hand-lettered phrase only. All other text as scribbles, lines, or boxes." |
| Too polished or realistic | "Flat digital storyboard drawing, minimal shading, no realistic lighting, no painterly rendering, no 3D." |
| Customer likeness looks wrong | "the customer as a simple line-art creator using their authorized character sheet: distinctive hair silhouette, chosen clothing, minimal face, active inside the scene." |

---

## Final Principle

The style works when the image feels like a clear storyboard frame from a smart explainer animation: rough, simple, scene-based, emotionally readable, and restrained. It fails when it becomes a polished infographic with perfect cards and too many labels.
