# The Gentlemen Style visual specification

Commissioned by Payton on September 8, 2026. The Netflix series is the visual reference. His adaptation uses AI Mentorship mint. The phone photos are the primary evidence for the on-screen graphics; social posts and font-identification pages are secondary leads.

**Visual approval, September 9:** Payton approved the palette, selected fonts, title cards and handwriting treatment. Keep them stable. His refinements are plain serif fill with a slight drop shadow only, one clean cross-out, and a replacement dry-erase sound. The sonic choice is now approved: use the September 9 selected 85% Feather squeak / 15% Thin nib blend in `sound.md`. The original noise-based Foley is not approved.

## What makes it work

For still images, use the customer's own authorized identity reference when the task calls for it. Keep the graphic treatment unchanged.

The graphic explains a concrete thing already happening in the scene. A price appears when someone names it. The previous offer stays visible with a strike through it when the deal changes. An arrow lands on an actual object. The note uses empty space in the shot and remains still while the viewer reads. The restrained handwriting and the cinematic scene carry the effect; there is little decorative motion.

Separate four jobs: handwriting explains, block titles establish a chapter or location, serif dialogue translates or captions a spoken phrase, and geometric marks identify a surface or object. Each has its own typography and timing.

## Typography

| Treatment | Implemented font | Evidence and limits |
| --- | --- | --- |
| Marker | Reenie Beanie, regular | Strong visual match against the distinctive M, tilted t crossbar, open pound sign, upright irregular spacing, Harmony and Marco's protection. The original studio font credit is unconfirmed. |
| Main titles and locations | Archivo Black, regular, typically 1.16–1.32 horizontal scale | A free approximation of the wide, heavy source titles. Some source glyph structures, particularly E and G, differ. It is not an identified original. |
| Episode/chapter kicker | Cinzel, medium, wide tracking | Free approximation of the small classical serif caps above the large title. |
| Translation subtitles and optional captions | Bevan, regular, horizontal scale .90 | Free close alternative with heavy slab serifs and round dots. Exact source face remains unresolved. |

All four shipped fonts come from Google Fonts' own repository with SIL Open Font License files. Do not take a site's “free download” label as proof it distributes the original font. The study tested Caveat, Kalam, Nothing You Could Do, Ultra, Alfa Slab One, Patua One, Rokkitt, Roboto Serif, Rockwell variants, Superclarendon and Bernard MT Condensed. The installed Microsoft fonts were specimen comparisons only and are not bundled.

The wide title font is still an open identification question. A social discussion proposes Titling Gothic FB Wide Bold as a close candidate but does not establish the exact original. A page claiming CG Gothic No1 conflicts with the condensed proportions in Monotype's own specimen. Do not repeat that claim as fact. Production artwork credits, film-title credits, poster fonts and Netflix's normal UI subtitle preferences are not interchangeable with the series' burned-in graphics.

## Colour and finish

| Role | Value | Use |
| --- | --- | --- |
| Mint ink | #72DFA5 | Writing, arrows, prices, titles and special subtitles |
| Old Money | #0F583D | Background depth and supporting atmosphere |
| Deep backdrop | #071B12 to #0B1711 | A full-screen text plate when footage is not needed |
| Tiny top edge | #BAFFD8 | A restrained one-pixel title highlight, not a second prominent accent |

The phone photos show vivid warm yellow marker strokes and warmer peach-gold titles. These are observations of a photographed display. White balance, display brightness, perspective and reflections prevent an exact source colour measurement. Mint comes from the actual brand palette, not a sampled phone pixel.

Marker lettering is opaque, fine, smooth and irregular in shape. Keep the original variable letter widths and small height variations. The font already supplies the human variation, so do not add continuous jitter or random rotation to every glyph. Use no glow. On footage, a soft dark shadow around 1–2 pixels can separate the strokes. A broad, faint, feathered shade behind a busy area is preferable to a panel with visible boundaries.

Titles have a very shallow raised edge: a one-pixel light top edge, a small dark lower edge and a short shadow. They are not extruded metal, inflated objects or luminous neon. Keep the title itself steady. A brief fade or direct cut fits the source better than springy letters.

Serif subtitles and captions are different: plain mint fill with a slight dark drop shadow behind the text. No outline, pale rim, top-edge highlight or bevel. The original subtitle implementation's stroke and light edge were removed at Payton's request. Title edges remain approved.

## Scale and placement

The implementation uses a 1920 × 1080 baseline at 30 fps. Scale coordinates and strokes with the canvas when producing 4K. The photos contain a monitor, window borders and sometimes letterboxing; none is part of the style. Deliver the requested 16:9 or 9:16 composition without importing those borders.

| Element | Useful starting range at 1080p landscape |
| --- | --- |
| Handwritten explanation | 100–125 em pixels, typically 35–75 visible pixels depending on the letter |
| Price or one-word emphasis | 150–200 em pixels |
| Handwritten line spacing | 95–120 composition pixels |
| Arrow/underline | 2.5–4 pixels, rounded ends |
| Main block title | 105–145 pixels, slightly extended horizontally |
| Location caps | 50–70 pixels, placed on a shared baseline |
| Chapter kicker | 22–28 pixels, 6–8 pixels of tracking |
| Serif subtitle | 45–55 pixels, centered near 78–84% of height |
| Outer safe space | Start with 5–7% of width; increase around controls and the speaker |

The font's em is not its visible height. Reenie Beanie has small lowercase bodies and tall strokes and descenders. Its nominal 110-pixel size is not comparable to a 110-pixel sans-serif title. Use the actual rendered bounds and `inkWidth()` when fitting a phrase.

On 9:16, recompose around the face. A close landscape crop leaves little side space. Use fewer words at approximately 125–175 em pixels, keep them below the chin, and check the shirt region throughout the cue. The supplied portrait example uses baselines at 1370, 1470 and 1570 on a 1080 × 1920 canvas. These coordinates are specific to that close crop, not a universal social safe zone.

## Writing and sound

Use a central stroke mask over the original filled font outline. A stroke around the glyph contour draws both sides of the letter and looks like outlined typography. A rectangular wipe exposes everything at one x coordinate and looks like a reveal effect. The mask method exposes the shape under a travelling pen while preserving the final font exactly.

The compiler rasterizes the font, extracts central routes, simplifies those routes and retains the original vector glyph. It prefers continuous motion through intersections, begins selected glyphs from the left, and defers dots. These are inferred pen routes. Inspect large or slow phrases because the font contains overlaps that can produce an unusual branch order. Hand-author a route override for a hero word if the automatic route still looks wrong.

In the renderer, each stroke gets a start and end from its length, a slight pen-lift interval and the phrase's total duration. Use short word groups, usually a few tenths of a second to about 1.5 seconds. A larger explanatory phrase can take 1.5–2 seconds. These are tested production choices; still photos cannot reveal the show's exact easing or write speed.

Begin with the spoken noun or number. For a long phrase, start on the lead-in so the key word arrives with the voice. Hold through the explanation. Let changed values coexist long enough to compare. Write a strike after the correction is said. End with a quick restrained fade or a scene cut. Never erase a value before the audience sees what changed.

The first sample Foley used filtered noise with a faint resonance. Although it was gated by pen events, Payton heard it as paper scribbling and rejected its material character. The replacement target is a smooth dry-erase marker on whiteboard or glass: restrained contact, occasional soft rubbery squeak, no rough paper hiss, no repetitive chatter. Use recorded contact textures, match audible contact to the actual rendered writing, and leave clear silence during holds. Do not pretend a filtered whiteboard recording was recorded on glass; label glass-like interpretations honestly. Normalize audition options comparably and include previews both in isolation and below speech. Keep the chosen WAV independent. No sound is needed merely because an established annotation follows an object.

A cross-out is one deliberate line across the old term, followed by a pause. Do not replace it with repeated back-and-forth scribbles. Continue refining inferred pen routes and tracking from observed failures while preserving the approved visual style.

Approved sound after the final blend: Payton locked 85% Feather squeak and 15% Thin nib as the main sound for now, with future user-requested changes allowed. Retain the delicate paper-like writing and soft thin-marker squeak, match the quiet production level, and rebuild the sound against each scene's actual pen motion. See [the current sound workflow](sound.md).


## What the photos cannot establish

The stills do not prove exact stroke order, writing duration, easing, how much of the effect was hand-animated, the original sound source, font licenses or production font credits. The movement system is a tested reconstruction based on the stills and Payton's description. The title and subtitle substitutions remain labelled. A future direct production credit or original project file should update the typography choice without replacing the rest of the system.
