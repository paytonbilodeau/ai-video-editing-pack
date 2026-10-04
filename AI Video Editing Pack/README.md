# Free AI Video Editing Pack

This portable set of skills helps a file-aware AI assistant and a human editor
finish recorded video together. It covers the setup interview, an editable
first cut, sound and color, useful motion, review, export, and learning from
corrections. It does not install an editor plugin or grant an assistant control
of your tools.

**Start with [START HERE.md](START%20HERE.md)** or give your assistant its
[stable public URL](https://github.com/paytonbilodeau/ai-video-editing-pack/blob/main/AI%20Video%20Editing%20Pack/START%20HERE.md).
Its copyable message also works with an assistant that can read this folder.
A browser-only chat can help plan and
review, but cannot inspect local files, operate your editor, or verify an
export. The [provider check](references/PROVIDER%20CHECK.md) helps you confirm
what your particular assistant and editor can do today.

## Get a working copy

Download the [standalone pack ZIP](https://github.com/paytonbilodeau/ai-video-editing-pack/releases/latest/download/ai-video-editing-pack.zip),
the [free repository ZIP](https://github.com/paytonbilodeau/ai-video-editing-pack/archive/refs/heads/main.zip),
or clone the repository. Extract it, keep one clean reference copy, and put footage, references,
account information and working projects in a separate private folder.

The folder includes a portable [OpenAI Agent Plugins manifest](plugin.json)
and a [Claude Code manifest](.claude-plugin/plugin.json). Current
[OpenAI packaging guidance](https://developers.openai.com/plugins/build/plugins)
and [Claude plugin guidance](https://code.claude.com/docs/en/plugins) describe
how their hosts discover `skills/` modules. Installing a plugin does not grant
editor or computer access; verify the host's current permission and connection
steps. The copyable setup message in START HERE works without native plugin
installation.

To install the native plugin through Codex, add this repository's marketplace:

```sh
codex plugin marketplace add paytonbilodeau/ai-video-editing-pack --ref main
```

Refresh ChatGPT desktop, then install **ai-video-editing-pack** from the
**payton-ai-tools** marketplace in the Plugins Directory. Follow the
[current OpenAI install guide](https://developers.openai.com/plugins/build/plugins)
if those controls have changed.

In Claude Code, use:

```text
/plugin marketplace add paytonbilodeau/ai-video-editing-pack
/plugin install ai-video-editing-pack@payton-ai-tools
```

The [Claude install guide](https://code.claude.com/docs/en/plugins/install)
also covers Desktop Code's **+ → Plugins → Add plugin** route. These installs
add the pack's skills; editor control still needs the separate connection
and permission checks below. If an installer is unavailable, use the stable
START HERE URL or standalone ZIP.

For a concrete local starting route, use the dated
[AI app setup guide](references/AI%20APP%20SETUP.md); it covers Codex Local,
computer access, permission choices and a Claude alternative. Verify the
current UI and plan before changing any setting.

You can use the [main skill](SKILL.md) to route the work or use one focused
skill at a time:

| Step | Skill |
|---|---|
| Start the full workflow | [Vibe editing setup](skills/vibe-editing-setup/SKILL.md) |
| Interview and project setup | [Intake](skills/intake/SKILL.md) |
| Check current app and editor capabilities | [Platform refresh](skills/platform-refresh/SKILL.md) |
| Set up a local AI app and computer access | [AI app setup guide](references/AI%20APP%20SETUP.md) |
| Protect keys and choose trusted connections | [Safety and API Keys](references/SAFETY%20AND%20API%20KEYS.md) |
| Inspect footage and verify source claims | [Source research](skills/source-research/SKILL.md) |
| Optional local automatic first pass | [Pre-edit](skills/pre-edit/SKILL.md) |
| Select takes and make clean cuts | [Cuts and pacing](skills/cuts-pacing/SKILL.md) |
| Repair and balance sound | [Audio](skills/audio/SKILL.md) |
| Correct picture and assess LUTs | [Color](skills/color/SKILL.md) |
| Create useful graphics and motion | [Style and motion](skills/style-motion/SKILL.md) |
| Review, export and learn from corrections | [Review and delivery](skills/review-delivery/SKILL.md) |
| Make approved derivatives | [Waterfall](skills/waterfall/SKILL.md) |

Reference files the skills lean on:

| Reference | Use it for |
|---|---|
| [Editor connections](references/EDITOR%20CONNECTIONS.md) | What an assistant can script, import, drive by computer use or must leave to you, per editor, with the interchange formats each one reads |
| Editor playbooks: [Resolve](references/EDITOR%20PLAYBOOK%20RESOLVE.md), [Premiere](references/EDITOR%20PLAYBOOK%20PREMIERE.md), [Final Cut](references/EDITOR%20PLAYBOOK%20FINAL%20CUT.md), [CapCut](references/EDITOR%20PLAYBOOK%20CAPCUT.md) | Current version facts, control routes, shortcuts, the talking-head workflow in order, a smoke test and a learning path for each editor |
| [Cut list export](references/CUT%20LIST%20EXPORT.md) | Turn one reviewed cut list into FCPXML, Premiere XML, EDL and a cut sheet with `tools/cut_list_to_timeline.py` |
| [Editing craft numbers](references/EDITING%20CRAFT%20NUMBERS.md) | Measurable defaults for takes, pauses, breaths, word edges, non-speech sounds, pacing, punch-ins, captions, graphics timing, QC and shorts |
| [Sound and color numbers](references/SOUND%20AND%20COLOR%20NUMBERS.md) | The dialogue chain with starting values, loudness targets, per-microphone moves, tool names per editor, color order, scope targets and LUT practice |
| [Learning path](references/LEARNING%20PATH.md) | Current courses by editor and level, and the craft sources behind the numbers |

The [editing workflow](references/EDIT%20WORKFLOW.md) gives the stage order and
acceptance checks. [Project intake](templates/PROJECT%20INTAKE.md),
[edit plan and review](templates/EDIT%20PLAN%20AND%20REVIEW.md), and
[delivery and learning](templates/DELIVERY%20AND%20LEARNING.md) are copyable
working records. The [editing profile](templates/EDITING%20PROFILE.md) keeps
accepted rules privately across projects. Setup needs no footage; begin editing whenever you have a video you want to use. Keep the
original media and any approved edit recoverable. A setup check, transcript,
or AI summary is not proof that an edit works.

Keep Final Cut, Premiere, CapCut, or another editor you already use when it
fits the job. If choosing from scratch, DaVinci Resolve is the recommended
starting editor, subject to a current edition and setup check. Native editor
titles are enough for a
first graphic; Remotion and Hyperframes are optional routes for a specific
need. No new installation, paid service, model download, wider access, or
upload of private footage is part of setup by default. Check your assistant's
current skill instructions before installing these files. This pack makes no
universal plugin compatibility claim.

For deeper examples and optional utilities, see the original free systems:
[05 Video Pre-Edit](https://github.com/paytonbilodeau/ai-video-editing-pack/tree/main/05%20Video%20Pre-Edit%20System),
[09 Visual Storytelling and Motion](https://github.com/paytonbilodeau/ai-video-editing-pack/tree/main/09%20Visual%20Storytelling%20and%20Motion%20System),
[10 Content Waterfall](https://github.com/paytonbilodeau/ai-video-editing-pack/tree/main/10%20Content%20Waterfall%20System),
and [14 AI Video Editing](https://github.com/paytonbilodeau/ai-video-editing-pack/tree/main/14%20AI%20Video%20Editing%20System).
These are optional references, not duplicate files in this pack.

Updates do not overwrite customized projects. Check the pack and build a
deterministic standalone ZIP with `python3 tools/build_pack.py --check` and
`python3 tools/build_pack.py --output /path/to/AI-Video-Editing-Pack.zip`.
The optional Python 3.11+ helper previews private worksheets and a durable
cross-project profile. [START HERE](START%20HERE.md) has the exact command and
manual copy route. The prompt and manual route do not need Python.
For maintainers: after changing this pack, test it, rebuild a versioned
release ZIP, update the native plugin/catalog version if required, and check
the public release asset. A changed repository folder does not update a
previously published ZIP.
