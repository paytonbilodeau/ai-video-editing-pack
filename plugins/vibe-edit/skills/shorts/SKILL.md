---
name: shorts
description: Cuts dedicated shorts from a long recording and runs the wider waterfall of derivatives (long cutdowns, mid-length clips, shorts, captions and text drafts) from an approved edit, with every output traced to source time ranges and supported claims. Use when the person asks for shorts, clips, a content map, a waterfall or other derivatives from a finished video; publishing stays a separate action.
---

# Shorts

Makes derivatives from an approved recording. Two jobs: a dedicated short cut from a long edit (one complete idea, exact camera-cut coverage, single-line captions), and the wider waterfall of long cutdowns, mid-length clips, shorts, captions and text drafts. Every output stays traceable to source time ranges and supported claims. Read `Vibe Edit Settings/EDITING PROFILE.md` in the person's workspace first; the current brief overrides it. A brief asking for a main video and shorts authorizes both; a shorts-only brief stays shorts-only.

## Procedure

1. **Confirm the source.** Use the approved clean master; record label, hash, duration and rational frame rate. If the long edit carries aspect-specific graphics, use the clean companion in [WATERFALL SYSTEM](<references/WATERFALL SYSTEM.md>). Never modify the original.
2. **Get word timing.** Reuse a timed transcript or run [waterfall_transcribe.py](../edit/tools/waterfall_transcribe.py). Normalize supplied timing with [transcript_adapter.py](tools/transcript_adapter.py); it does not transcribe.
3. **Choose complete ideas.** Read the whole transcript. Pick openings that stand alone and endings that pay them off, qualifications included; let the source set the count. Record opening words, closing words, payoff and claim IDs in the content map. Craft: [DERIVATIVES](../edit/references/DERIVATIVES.md).
4. **Validate before extracting.** `content_waterfall.py validate`, or [waterfall_validate.py](../edit/tools/waterfall_validate.py) for the frame-based `clips[]` contract. Record the request's authority once in the approval record; set `approved` only for outputs inside it.
5. **Extract.** `content_waterfall.py extract --confirm EXTRACT` writes approved clips to a new folder with a static crop. Face-centred 9:16: [extract_short_clips.py](../edit/tools/extract_short_clips.py). 16:9 mids: [extract_mid_clips.py](../edit/tools/extract_mid_clips.py). Reviewed portrait layout: [render_short.py](tools/render_short.py).
6. **Captions and finishing.** Dedicated short: [dedicated short finishing](../style/references/tech-motion/references/dedicated-short-finishing.md) gives integer camera-cut coverage, an opaque first graphic frame and measured single-line captions. Caption ownership and renderers: [captions](../captions/SKILL.md). `content_waterfall.py captions` rebases word timing into one VTT per clip.
7. **Review every export with sound.** Dimensions, frame rate, full decode, crop through the largest movement, caption readability, complete first and last words, claim fidelity. Text derivatives cite ledger claim IDs. Record in [DELIVERY AND LEARNING](<../edit/templates/core/DELIVERY AND LEARNING.md>).
8. **Learn after the person publishes.** Fill the performance ledger and ten-run tracker, then the winner review and next capture brief. Never rewrite source facts to fit a past winner.

## Files in this skill

| File | Use |
| --- | --- |
| [core-waterfall.md](references/core-waterfall.md) | Core rules, safe zones |
| [WATERFALL SYSTEM.md](<references/WATERFALL SYSTEM.md>) | Full process, ranges, audio policy, claims rule |
| [AUDIENCE BRIEF.md](<templates/AUDIENCE BRIEF.md>) | Audience, formats, boundaries |
| [VOICE GUIDE.md](<templates/VOICE GUIDE.md>) | Voice to preserve |
| [CLAIM LEDGER.md](<templates/CLAIM LEDGER.md>) | One ID per claim |
| [CONTENT MAP.md](<templates/CONTENT MAP.md>) | Planned outputs; mirrors the JSON |
| [APPROVAL RECORD.md](<templates/APPROVAL RECORD.md>) | Authority, pace, approved IDs |
| [PERFORMANCE LEDGER.md](<templates/PERFORMANCE LEDGER.md>) | Results after publication |
| [TEN-RUN CONTENT TRACKER.md](<templates/TEN-RUN CONTENT TRACKER.md>) | Time and counts per run |
| [WINNER REVIEW.md](<templates/WINNER REVIEW.md>) | Pattern review after ten runs |
| [NEXT CAPTURE BRIEF.md](<templates/NEXT CAPTURE BRIEF.md>) | Next recording improvements |
| [content_waterfall.py](tools/content_waterfall.py) | `validate`, `captions`, `extract`; hash check, new folder only |
| [transcript_adapter.py](tools/transcript_adapter.py) | Normalizes supplied word timing |
| [render_short.py](tools/render_short.py) | Portrait render from the three JSON plans; put `../edit/tools` on `PYTHONPATH` for `video_render_check` |
| [test_content_waterfall.py](tools/tests/test_content_waterfall.py) | Synthetic end-to-end test |
| [test_transcript_adapter.py](tools/tests/test_transcript_adapter.py) | Adapter tests |
| [EXAMPLE WATERFALL RUN.md](<examples/EXAMPLE WATERFALL RUN.md>) | What the example proves and does not |
| [example-content-map.json](examples/example-content-map.json) | Valid map: one claim, one short, one email |
| [example-transcript.json](examples/example-transcript.json) | Word-timed sample |
| [portrait-short/README.md](examples/portrait-short/README.md) | Synthetic layout fixture; `source.mp4` is in the [asset bundle](../../ASSETS.md) |
| [portrait-short/content-map.json](examples/portrait-short/content-map.json) | Frame-based `clips[]` map |
| [portrait-short/shorts/layouts.json](examples/portrait-short/shorts/layouts.json) | Crops, segments, hook, captions |
| [portrait-short/shorts/caption-plan.json](examples/portrait-short/shorts/caption-plan.json) | Timed caption cues |

## Scope and honesty

Publishing is a separate action that never happens automatically; the exported files end this skill. No promises about views, reach or time saved. Preserve source meaning, visible demonstrations and every qualification; a clip may not add a fact, number, quote or implication the source lacks. Original media and the approved master stay untouched; every output goes to a new folder.
