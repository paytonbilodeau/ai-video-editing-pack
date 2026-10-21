# Vibe Edit

Turn Codex or Claude Code into your video editor. Vibe Edit is a plugin that carries Payton Bilodeau's editing system: how he briefs, cuts, fixes sound and color, adds captions and motion graphics, makes shorts and keeps his taste on file. Your own choices take priority from the first edit.

## Install

Paste one line into your local AI assistant, with this folder open or with the GitHub link:

```text
Read INSTALL.md and set up Vibe Edit for me.
```

The assistant adds the plugin, confirms the skills loaded, puts your editing profile outside the plugin and makes one disposable edit from the included practice clip. No footage of yours is needed for that.

If you would rather run the commands yourself: in Claude Code, `/plugin install vibe-edit --marketplace paytonbilodeau/ai-video-editing-pack`; in Codex, `codex plugin marketplace add paytonbilodeau/ai-video-editing-pack` then `codex plugin add vibe-edit@vibe-editors`. Every form, including installing from a downloaded folder, is in [INSTALL.md](INSTALL.md).

## Use

Ask for what you want in plain language: "edit this recording", "tighten the pacing", "add Tech Motion graphics", "make three shorts". The assistant picks the right skill. The twelve skills are setup, edit, pre-edit, style, remotion, hyperframes, javascript-animation, captions, shorts, editors, update and help.

## Learn

- [Eight illustrated lessons](lessons/visual/README.md): from setup to a checked export.
- [Twenty-two detailed lessons](lessons/README.md): the full guide behind the free email course.
- [Practice edit](practice/synthetic-lamp/README.md): a ten-second synthetic clip with a known right answer.
- Questions: the Vibe Editors community at https://www.skool.com/vibeeditors, or ask the `help` skill.

## Update

Claude Code: `/plugin marketplace update vibe-editors`. Codex: `codex plugin marketplace upgrade`. From a downloaded folder, paste the update line from the release post (version, link and hash) and the `update` skill downloads, checks and swaps the folder for you. Each change is offered, not imposed, and your profile, projects and footage are never inside the plugin, so updates never touch them. Details in the `update` skill.

[Changelog](CHANGELOG.md) · [License and use](LICENSE%20AND%20USE.md) · [Third-party notices](THIRD-PARTY.md) · [Optional asset bundle](ASSETS.md)
