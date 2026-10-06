# Changelog

## 4.3.0 - 2026-10-06

- Add the portable JavaScript animation skill alongside Remotion, Hyperframes and native editor routes. Include seven MIT-attributed public styles, demos and a pinned upstream source.
- Add isolated lockfile-pinned Playwright setup, contained builds, deterministic frame checks, local beat analysis, storyboards and reference comparison. Keep supplied voice timing local and provider-independent.
- Add a frame-acknowledged Remotion adapter and PNG/H.264/ProRes handoff. Alpha export preserves authored transparency and rejects an opaque source; H.264 does not preserve alpha.
- Include runtime sources, regression tests and notices in the standalone ZIP. Bump the native plugin manifests to 1.2.0.
- Patch the motion starter's transitive `source-map-js` to 1.2.2 and `postcss-selector-parser` to 7.1.6 to resolve their reported denial-of-service advisories without changing the pinned Remotion version.

## 4.2.0 - 2026-10-03

- Setup ends ready without a required recording or practice assignment.
- Full requested edits are the default; checkpoints and sample previews are optional.
- Private taste profiles start during setup and are reused through project instructions.
- Revised all 22 email templates for clear, practical advice without daily homework.
- Refreshed app, plan, model and permission guidance; updated the editing-brief illustration.
- Warn on unusual probed frame rates and document the observed Resolve EDL import mismatch.


## 4.1.0 - 2026-10-03

Make the pack work the same way on all four editors. Add a per-editor playbook for DaVinci Resolve Studio 21.1, Premiere Pro 26.5, Final Cut Pro 12.4 and CapCut 9.5 desktop: current version facts, every control route (vendor connector, unofficial bridge, file import, computer use), the scripting or interchange surface, default shortcuts, the talking-head workflow in order, a smoke test and a short learning path. Rewrite EDITOR CONNECTIONS around a truthful capability matrix and the interchange formats each editor reads.

Add `tools/cut_list_to_timeline.py`, which turns one reviewed cut list into FCPXML (Final Cut and Resolve), Final Cut Pro 7 XML (Premiere and Resolve), a CMX3600 EDL and a cut sheet for CapCut, with frame-exact rational timing, linked audio, markers and a summary; 16 offline tests plus a DTD validation test; FCPXML output validated against Apple's shipped FCPXML 1.11 DTD. Add EDITING CRAFT NUMBERS (takes, restarts, pauses, breaths, word-edge handles, non-speech sounds, pacing, punch-in scales, captions, graphic timing, QC, shorts), SOUND AND COLOR NUMBERS (dialogue chain with starting values, loudness targets, per-microphone moves, tool names in each editor, color order, scope targets, LUT practice, monitoring) and LEARNING PATH (current courses by editor and level). Refresh MOTION AND LUTS for Remotion 4.0.5xx and HyperFrames 0.8.x, alpha hand-off commands and the behind-the-person method per editor. Link the new references from the umbrella skill, START HERE, the workflow and the cuts, platform, setup, audio, color, motion and waterfall skills. Plugin version is 1.0.8. Email lessons, setup and download URLs and the human review gates are unchanged.

## 4.0.5 - 2026-10-02

Clarify all 22 email lesson templates and the greeting-free confirmation email, with definitions beside new terms, concrete exercises, shorter prompt blocks and result checks. Explain the first download in three steps and preserve the immediate-first-lesson/daily cadence. Describe optional final audio processing and derivative handling without repeating enhancement.

Add a short beginner entry path to START HERE. Point the optional pre-edit tool at the tested 4.0.4 supporting release, including its updated dependency requirements, instead of 4.0.2. Plugin version is 1.0.7. Existing setup/download URLs, skill behavior and human review gates are preserved.

## 4.0.4 - 2026-10-02

Add automated repository and editing-tool checks, dependency update pull requests, and private vulnerability reporting guidance. Update vulnerable optional PyTorch and motion-starter dependencies. Create fallback media outputs with owner-only permissions, including when the system has a permissive umask. The standalone pack and all 22 lessons are unchanged.

## 4.0.3 - 2026-10-02

Clarify the optional external audio finish: complete the visual edit first, use the agreed microphone preset once, retain the untreated master, and build derivatives without processing enhanced audio again. Plugin version is 1.0.6. All 22 lesson resources and stable setup and download paths are preserved.

## 4.0.2 - 2026-10-02

Updated the source-credit label to AI Video Editing Pack and refreshed the versioned setup references. The native plugin is version 1.0.5. Editing behavior is unchanged.

## 4.0.1 - 2026-10-02

Renamed this repository to AI Video Editing Pack and made its scope explicit: the editing pack, supporting tools and Kit email workflow. Today in AI, AI Mentorship and Echo Improvement each have their own repositories. Updated setup, download and plugin-install links to the new address; existing links continue through the GitHub rename redirect. The plugin is version 1.0.4. Editing behavior is unchanged.

## 4.0.0 - 2026-10-02

Reorganized the public release around AI Video Editing Pack, Today in AI, AI Mentorship and Echo Improvement, in that order. The broader personal library is no longer part of this public repository or its history. Existing main-branch editing paths and the latest-pack download URL are preserved.

Added a reusable Kit confirmation-and-sequence workflow with 22 lesson templates. The editing pack is version 1.0.3; its references now point at this maintained public release instead of the retired library tags. The supporting pre-edit, motion and repurposing tools remain included.

This release retains Alec Stephens's setup-cache and table fixes, the API-key safety guide, current FFmpeg compatibility, export-sidecar protection and standalone-pack regression tests from library release 3.12.3. Thanks to Alec for the original contribution.
