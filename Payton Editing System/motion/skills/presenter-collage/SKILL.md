---
name: presenter-collage
description: Meaningful inserts and real-foreground composites around a talking head.
---

# Presenter Collage

This portable treatment keeps the actual source room and customer identity. Use the editing module for source-aligned masks and native checks; source creator media is not included.

## Decide the job, then the depth

Add these fields to the existing semantic beat sheet, rather than creating a competing timeline:

`spoken cue | viewer question | asset/source | job | depth | bounds | protected regions | visible change | settled hold | exit | sound cue | review frames`

| Job | Depth/layout | Behavior |
| --- | --- | --- |
| Deliver a hook, opinion, pivot or CTA | Clean face, optionally a small side annotation | Let performance carry the line. Keep eyes and mouth clear. |
| Identify a named tool/person/object | Side or rear insert | Enter on the relevant noun; show enough identity to recognize it. |
| Explain a relationship | Rear diagram if room permits, otherwise full-screen Tech Motion | Reuse objects and transform their relationships. Keep essential labels outside the subject silhouette. |
| Establish a source or demonstrate real behavior | Deliberate foreground evidence or full-screen proof | Preserve aspect ratio, source context and a readable crop. Face covering is a chosen cutaway, never an accidental overlay collision. |
| Land an emotional comparison | Brief reaction insert | Choose for the spoken meaning, allow recognition, then clear. A meme is not factual evidence. |
| Return from proof to an invitation | Face foreground; proof may move behind on a deliberate shot cut | Keep the proof recognizable across the handoff and give the person visual priority. |

There is no quota for memes, inserts or movement. Use clean face beats when they serve the argument. When applying this requested treatment, a rear insert is a deliberate exception to Flow's default opaque board. The existing hook/pivot/close face rule stays active. Do not let generic lane quotas force an unnecessary physics beat into a small talking-head passage.

## Reserve room before building

Inspect the actual head, hands, microphone, props, eyeline and crop over the whole interval. Draw separate hook, caption and platform-caution regions first. Large headroom in these references is part of why the treatment works. A persistent top hook consumes some of the same space.

Reserve the actual customer-owned hook and caption regions. Confirm who owns each text layer before adding another.

The study's debug layout at 1080×1920 reserves x80–900/y120–400 for the hook and x80–900/y1220–1500 for captions, with right x930–1080 and bottom 420 pixels treated cautiously. These are provisional composition guides, not current platform specifications or universal positions. Scale proportionally for the working raster, then verify the actual destination preview. A face, prop or hand can require a different arrangement.

If critical words intersect the subject or a protected area: move the message, simplify the graphic, use a smaller side symbol, or defer to the full-screen section. Do not solve a collision by shrinking readable text below the established floor. A decorative border may pass behind hair; the key claim may not.

Recheck placement at **every source cut or framing change inside an insert**.
The study's second prototype kept a panel fixed through a closer shot and the
head hid a central label. A working matte did not make that layout acceptable.
Split the insert into shot-specific placements or exit it before the cut;
inspect the first new frame and the following motion before accepting the repair.

## Composite with real foreground coverage

Reuse `resolve-edit/references/motion-and-editorial-craft.md` and its approved matte route. Bottom-to-top stack:

1. The unaltered source frame, including its room.
2. Rear insert, with only its intended motion.
3. Time-aligned foreground subject, including any required hands, microphone and held objects.
4. Deliberate foreground evidence or annotation, when that beat calls for it.
5. User-owned text regions remain reserved.

The equivalent masked-insert alpha is `insertAlpha * (1 - foregroundMatte)`. Soft alpha is multiplication, not subtraction. Keep the full source behind it and one dialogue audio path. Base and foreground must share source time, retime, crop, stabilization and transform. If any upstream edit changes, regenerate or realign the matte.

`motion/tools/vision_segment.swift` uses **foreground instance segmentation with all detected instances**, not a person-only guarantee. It can include props, furniture or other foreground objects. Check what was selected before trusting its output. A separately detected laptop can be useful or an unwanted occluder. A person-only matte can conversely miss a held notebook. Choose the intended objects explicitly in the actual production route.

Use real per-frame masks or verified tracking for motion. A still mask pasted over a moving shot is not sufficient. Check hair, shoulder gaps, fingers, motion blur, the microphone, held props and partial exits. Inspect delivery-size frames and temporal behavior. Reject holes, halo, edge chatter and wrong depth. If the matte is poor, use a native tracked/rotoscoped repair or a layout with no overlap; do not hide the problem under more effects.

No alpha-overlay import or Resolve Magic Mask capability is proven by the study's local prototype. Those remain separate native-editor checks. Flattened reference-video compression also limits edge diagnosis.

## Six reusable editorial recipes

**Continuous explanation.** Establish the same objects, show the confusing state, perform one visible operation, arrange the result, then label it. The system-diagram reference clears its old connections before drawing the ordered ones. Keep the final relationship long enough to read. Use Remotion/JavaScript/Hyperframes deterministically through the existing route.

**Role swap.** Set up two meaningful words or objects, then exchange their roles on the actual verbal reversal. A stationary board and a brief crossing path preserve comparison. Emphasis color can follow role; object identity and spelling must stay stable. Timing is in seconds and spoken cues, not copied source frame counts.

**Source → crop → highlight.** Show enough authentic context to identify the source. Reframe the relevant excerpt, then reveal one aligned highlight. Keep prior highlights during a fast spoken list. Parent screenshot, crop and marks under the same transform so a zoom cannot make the underline drift. Never invent a screenshot, silently change text or imply a mismatched before/after is controlled evidence.

**Directional screen handoff.** Preserve the cause: select/copy, move to the target, paste/submit, show the result. A short sideways move can connect screens while the person stays sharp. Blur the moving panel only, then settle before reading. Default to a cut when motion adds no explanation.

**Semantic reaction.** Pick an image whose action or emotion maps to the sentence. One useful joke can be enough. Avoid a stock reaction simply because a long stretch lacks motion. Do not ridicule a person or audience the script is trying to help. Meme rights and appropriateness are checked at asset selection.

**Proof-to-person handoff.** After evidence has been given sufficient time, cut to the speaker with the proof behind or beside him. Keep the essential result visible and move nonessential detail behind the silhouette. Do not switch depth every few frames just to signal editing effort.

The disappearance effect is an optional advanced gag: a clean/reconstructed plate, foreground fade and independent particles. The reference does not prove a particular particle engine or AI-video method. Keep it out of a serious hook unless the sentence earns it and the source supports a clean result.

## Impact and return-to-speaker recipes, October 8

Use these optional mechanics from the public Zane Hoyer study, source `TXpXlFdI1B0`. The full transcript and 175 visual samples were reviewed. Exact source settings and continuous audiovisual coverage are not claimed. The silent JavaScript practice passed timing/seek checks; natural-subject masks and native Fusion replication require their own scene review.

**Event-timed impact (source 02:24–06:28).** A drop/landing or camera jolt needs a semantic reason. Obtain a clean plate and a verified moving foreground matte before separating a person from the room. Align subject and camera movement on one contact frame. Strength stays exactly zero before contact, starts on the first output frame on/after contact, decays briefly and returns to zero. Inspect the frame immediately before, at and after impact: spline smoothing can start the shake too early. Check the largest translations and rotations for exposed edges; use the smallest sufficient overscan. A calm passage keeps this effect disabled. The practice checks only translation overscan, not arbitrary rotation.

**Group, read, return focus (source 06:32–13:32).** Keep each collage's image, cutout, arrow, short labels and shadow under one parent transform. Local movements may have a small settle, followed by a stable reading hold. When the spoken focus returns to the presenter, a restrained camera move and blur on the now-secondary collage can share one progress function and exact start/end. Keep the presenter sharp. Don't blur text still needed to understand the point; remove or defer the treatment instead. Review the entire move against face, hand, hook and caption regions. The source insert is foreground evidence; behind-head placement separately requires the approved matte stack.

**Reveal a relationship (source 16:30–17:40).** Use a drawn path to connect, trace or encompass something meaningful. In Fusion, an open Polygon with controlled Border Width and animated Length can drive a colored Background. In Remotion/JavaScript, use a deterministic stroke reveal. Place rear/front sections on the correct sides of the object, maintain path continuity and hold the completed relationship. An orbit or line with no explanatory job is optional decoration to remove first.

Use existing native Text+, shapes, transforms, masks and controlled shadows before adding paid presets. A free approximation is not the original plugin. Preserve authentic assets, approved grade/typography, clear readable labels, protected caption/hook space and the one-pass audio contract. The current system avoids duplicate summaries and busy motion; these recipes do not restore either. Cue any SFX by its actual audible transient on the corresponding event, then listen with narration. No source sound mix was verified in this study.
