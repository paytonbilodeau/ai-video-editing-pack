# One-image prompt

Replace the fields with verified content. Call native Codex image generation separately for each image.

```text
Create one standalone 16:9 landscape annotated illustration at the highest useful native quality. All visible labels must be English.

Pure white background. Thin black hand-drawn pen lines with slight natural wobble. A sparse, clean, absurd physical scene with abundant empty white space. Main subject occupies roughly 40-60% of the canvas; at least 35% blank white space.

Include Xiaohei: a small solid-black creature with white dot eyes, tiny thin legs, slightly uneven outline, and a blank serious expression. Xiaohei must perform the core action, not stand beside it. Deadpan, slightly strange, never cute.

Core idea: {one verified idea}
Structure, for composition only, not visible text: {structure}
Physical scene: {objects, character action, and how that action creates the result}
Exact short handwritten labels: {three to five labels, no more than eight}

Black for objects and character. Orange for the main movement. Red for a key problem or result. Blue for secondary notes or feedback. Use colors sparingly.

No title, corner heading, category name, extra words, formal flowchart, slide grid, realistic software interface, commercial vector style, cute mascot, shadows, gradients, paper texture, beige background, or dense explanatory text. Invent the scene for this idea; do not copy the bundled example compositions.
```

If a different language is requested, replace both language requirements and the exact label list consistently.

For a local edit, inspect the target first and tell the native tool:

```text
Edit the provided image. Replace only the label "{incorrect text}" with "{exact corrected text}" in matching handwritten strokes and color. Preserve all other characters, objects, labels, composition, aspect ratio, white space, and image quality. Add nothing else.
```

For an unwanted title, remove only the named title and its underline, restoring pure white background. For a decorative character, regenerate with the same meaning but give Xiaohei the action that makes the result happen.
