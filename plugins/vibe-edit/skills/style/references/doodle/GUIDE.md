---
name: ian-xiaohei-illustrations
description: Doodle Explainers, also called Little Guy Explainers, little black guy illustrations, small black guy illustrations, black character explainers, or black cat explainers. Explain a project, skill, plugin, process, workflow, article, or concept through sparse hand-drawn annotated illustrations with Ian's Xiaohei characters. Use for visual explainers, illustration shot lists, and edits to these images. English labels and native Codex image generation are the defaults; use a diagram tool instead when exact editable architecture is required.
---

# Doodle Explainers

Use **Doodle Explainers** as the user-facing name. Recognize **Little Guy Explainers**, **little black guy**, **small black guy**, **black character illustrations**, **black cat explainers**, and the original **Ian Xiaohei Illustrations** as requests for this same skill. Keep `ian-xiaohei-illustrations` as the technical ID and directory for compatibility with existing links and prompts.

Turn a verified idea into a memorable physical scene that a nontechnical reader can understand quickly. Preserve Ian's original visual language: 16:9, pure white, thin black hand-drawn lines, sparse red/orange/blue annotations, and a deadpan black character doing the work. This is a distinct style, not Sketch.

## Codex defaults

- Use native Codex image generation (`image_gen`) for generation and edits. No Claude Code, Higgsfield MCP, API key, CLI image runner, or metered fallback is required or installed.
- Use English for labels, shot lists, and prompts unless the user requests another language. This overrides the Chinese defaults in the preserved upstream source and example images.
- For a request to plan, return the shot list and stop before generation. For a request to generate, plan briefly and generate without an extra approval pause. Respect the requested number; when unspecified choose only the useful images, usually one for a concept and four to eight for a substantial article.
- Use automatically when an annotated visual explanation materially helps a requested deliverable. Do not generate decorative images for routine answers.

## Understand what actually happens

Read the supplied document or relevant project files before inventing a scene. For a build or workflow, identify its trigger, inputs, key transformations, human decisions, and output. Ground each in the source. Read only relevant files; avoid secrets. Do not imply a proposed integration is implemented or an unverified output is live. Keep hypothetical details explicitly hypothetical.

Select the moments where a picture explains a causal action, judgment, contrast, state, or metaphor. Do not illustrate every paragraph or compress the whole system into one crowded image.

## Plan the illustrations

For each shot, state its placement or use, core meaning, structure, Xiaohei's action, main objects, and exact short English labels. Choose one structure from [composition-patterns.md](references/composition-patterns.md). Invent a fresh physical metaphor from the actual subject; reference images are calibration, not templates to copy.

Read [style-dna.md](references/style-dna.md) and [xiaohei-ip.md](references/xiaohei-ip.md) before the first generation. Read [prompt-template.md](references/prompt-template.md) to construct the prompt. Consult `assets/examples/` only when visual calibration is useful, not by default.

## Generate or edit

Generate each illustration separately with native `image_gen`. One image communicates one core idea. Use the precise label list, abundant whitespace, and Xiaohei as an essential participant. Avoid formal flowcharts, dense slides, realistic software UI, and corner titles naming the structure.

When a real brand mark is needed, follow the portable logo and asset rules in the style skill's `MOTION OVERVIEW.md`: use the current official structure and render it with the same linework and materials. Do not invent a logo. Omit unnecessary logos.

For edits, inspect the target image first and use native editing. Preserve unrelated composition and labels. Never cover spelling errors with flat text overlays. If native generation is unavailable, deliver the plan and prompts with a clear limitation; do not silently switch providers.

## Inspect and deliver

Use [qa-checklist.md](references/qa-checklist.md). Inspect full and phone size for correct text, causal meaning, character action, white background, restrained color, and clutter. Repair concrete defects with native editing or regeneration, normally within two focused rounds; disclose unresolved defects.

Keep the original lossless output. Save final maximum-quality PNGs in the user-requested location; otherwise use `assets/<subject-slug>-illustrations/` or `assets/<subject-slug>-illustrations/` in another project. Name them `01-topic-name.png`, `02-topic-name.png`; never overwrite existing assets without authorization. Keep prompts and QA receipts in the task's `output/` folder, not in Drop. Verify file existence, PNG type, and actual 16:9 dimensions; report a mismatch rather than stretching or claiming compliance.

Report the number generated, purpose, clickable paths, and remaining limitations. A saved prompt or shot list is not a generated image.

## Source

Adapted from Ian's MIT-licensed [ian-xiaohei-illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations), commit `91b560849e8f883922cc2fa8a358a668caa94105`. Retain `LICENSE` and `NOTICE.md`. See [source.md](references/source.md) for adaptation provenance.
