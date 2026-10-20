---
name: style
description: Choose the look before the engine. Matches a request or profile to Tech Motion (also Tech Explainer, Digital Motion, Digital Explainer), Gentlemen, Sketch, Doodle Explainers, Editorial, Narrative Motion or Presenter Collage, plans the beats, and hands the render to remotion, hyperframes or javascript-animation. Use when the person names a look, asks which style fits, wants graphics or a color look built from references, or wants their own reusable motion style.
---

# Style

Pick the look, then the engine. Seven Payton-derived looks with recipes, beat-planning templates, their tools and rendered stills live here. The profile at `Vibe Edit Settings/EDITING PROFILE.md` (`Vibe Editor Settings/` on a 5.x install) wins over every default.

## Procedure

1. A look named in the profile or brief is the answer. Else read [MOTION OVERVIEW](<references/MOTION OVERVIEW.md>) and match by name: Tech Motion (Tech Explainer, Digital Motion, Digital Explainer); Gentlemen (The Gentlemen Style); Sketch (Payton's Sketch, hand-drawn, animatic: stills in `sketch`, motion in `sketch-motion`); Doodle Explainers (Little Guy Explainers); Editorial; Narrative Motion; Presenter Collage. Unsure: ask once.
2. Open the look's `GUIDE.md` and references first. Defaults: mint `#72DFA5`, dark green `#0F583D`, neutral base, bundled typography, calm holds. Change only what is asked. A new brand never needs Payton's portrait or private media.
3. Reference-led work follows [STYLE FROM REFERENCES](<references/STYLE FROM REFERENCES.md>) and [style-from-brief](references/style-from-brief.md): record each reference's permission and contribution, build an original variation, copy no frames, recipes, marks or unlicensed assets.
4. Plan beats with [SYSTEM](planning/SYSTEM.md) and its templates from the locked edit's word times: one idea per visual state, no quota. Validate with `node planning/tools/motion_plan.mjs PLAN.json`.
5. Pick the engine per scene from [MOTION AND LUTS](<references/MOTION AND LUTS.md>): native editor for titles or footage-linked masks; [remotion](../remotion/SKILL.md) for Tech Motion, Gentlemen and layered Sketch; [hyperframes](../hyperframes/SKILL.md) for HTML scenes; [javascript-animation](../javascript-animation/SKILL.md) for procedural drawings. Sketch stills and Doodle need an image-capable assistant. Offer [MOTION TOOL SETUP](<references/MOTION TOOL SETUP.md>) once.
6. Deliver the look and reason, beat map, engine handoff, and one short render checked over real footage in the receiving editor (entrance, hold, exit, captions, alpha, sound). Save preferences only when accepted.

## Files in this skill

| File | Use |
| --- | --- |
| [MOTION OVERVIEW](<references/MOTION OVERVIEW.md>) | Look table, palette, portrait regions |
| [style-from-brief](references/style-from-brief.md) | Route choice, sample-first review |
| [STYLE FROM REFERENCES](<references/STYLE FROM REFERENCES.md>) | The person's own reusable style |
| [MOTION AND LUTS](<references/MOTION AND LUTS.md>) | Routes, alpha, masks, LUTs |
| [MOTION TOOL SETUP](<references/MOTION TOOL SETUP.md>) | Engine choice and first test |
| [Tech Motion](references/tech-motion/GUIDE.md), [references](references/tech-motion/references/) | Flow grammar, manual, short finishing |
| [Gentlemen](references/gentlemen/GUIDE.md), [references](references/gentlemen/references/), [sound-sources](references/gentlemen/sound-sources/) | Marker handwriting, titles, CC0 sound |
| [Sketch](references/sketch/GUIDE.md), [references](references/sketch/references/) | Sketch specification and prompts |
| [Sketch motion](references/sketch-motion/GUIDE.md), [references](references/sketch-motion/references/) | Animating approved Sketch frames |
| [Doodle](references/doodle/GUIDE.md), [references](references/doodle/references/), [examples](references/doodle/assets/examples/), [LICENSE](references/doodle/LICENSE), [NOTICE](references/doodle/NOTICE.md), [openai.yaml](references/doodle/agents/openai.yaml) | Xiaohei illustrations, MIT upstream |
| [Editorial](references/editorial/GUIDE.md) | Warm paper, serif, fine diagrams |
| [Narrative Motion](references/narrative-motion/GUIDE.md), [references](references/narrative-motion/references/) | Persistent stage, retained objects |
| [Presenter Collage](references/presenter-collage/GUIDE.md) | Inserts around a talking head |
| [SYSTEM](planning/SYSTEM.md), [templates](planning/templates/), [examples](planning/examples/) | Beat planning templates and example |
| [motion_plan.mjs](planning/tools/motion_plan.mjs), [tests](planning/tools/tests/) | Beat-map validator |
| [tools README](tools/README.md), [OPTIONAL PROVIDERS](<tools/OPTIONAL PROVIDERS.md>), [optional](tools/optional/) | Tool index; paid adapters stay off |
| [sound](tools/gentlemen_selected_sound.py), [marker](tools/gentlemen_marker_options.py), [squeak](tools/gentlemen_squeak_options.py), [nib](tools/gentlemen_fine_nib_options.py), [reference](tools/gentlemen_reference_options.py), [compile_font](tools/gentlemen_compile_font.py), [track](tools/gentlemen_track.py) | Gentlemen sound, font, tracking |
| [flow_sfx.py](tools/flow_sfx.py) | Procedural UI cues |
| [hook_rule.py](tools/hook_rule.py) | Hook-card duration rule |
| [mask_graphics.py](tools/mask_graphics.py), [person_segment.swift](tools/person_segment.swift), [vision_segment.swift](tools/vision_segment.swift) | Person mask behind graphics |
| [overlay_visuals.py](tools/overlay_visuals.py) | Timed illustrations over video |
| [layered_fcpxml.py](tools/layered_fcpxml.py) | Layered FCPXML interchange |
| [native_fusion_fixture.py](tools/native_fusion_fixture.py) | Scratch Fusion comp exercise |
| [README](examples/rendered/README.md), [stills](examples/rendered/) | Stills; videos in the [asset bundle](../../ASSETS.md) |

## Scope and honesty

A chosen look is a starting point, not a promised result. Say which routes were rendered and checked this session and which are only documented. Nothing here uploads, spends, publishes or changes a permission without the person's choice. Original media and approved cuts stay untouched; graphics go on duplicates with new output names.
