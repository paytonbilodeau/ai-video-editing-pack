# Vibe Edit

**Turn Codex or Claude Code into your video editor.** Vibe Edit is a free plugin with Payton Bilodeau's editing system inside: briefs, cuts, sound, color, captions, motion graphics in six looks, shorts, and a private taste profile that updates never touch. Formerly the AI Video Editing Pack.

## Install

Paste one line into your local AI assistant:

```text
Read https://raw.githubusercontent.com/paytonbilodeau/ai-video-editing-pack/main/plugins/vibe-edit/INSTALL.md and set up Vibe Edit for me.
```

Or run the commands yourself.

Claude Code:

```sh
claude plugin marketplace add paytonbilodeau/ai-video-editing-pack
claude plugin install vibe-edit@vibe-editors
```

Codex:

```sh
codex plugin marketplace add paytonbilodeau/ai-video-editing-pack
codex plugin add vibe-edit@vibe-editors
```

Then reload the plugins (Claude Code: `/reload-plugins`; Codex: start a new session) and say:

```text
Set up Vibe Edit as my video editor and run the practice edit.
```

No footage of yours is needed for that. Setup checks the tools you already have, keeps your editing profile outside the plugin and makes one disposable edit from the included practice clip.

## Learn

- [Plugin overview](<plugins/vibe-edit/README.md>) and [INSTALL](<plugins/vibe-edit/INSTALL.md>)
- [Eight illustrated lessons](<plugins/vibe-edit/lessons/visual/README.md>)
- [Twenty-two detailed lessons](<plugins/vibe-edit/lessons/README.md>), also delivered as the free email course at https://vibeeditors.com
- [Vibe Editors community](https://www.skool.com/vibeeditors): questions, feedback on your videos, and each new version one week early

## Update

Claude Code: `/plugin marketplace update vibe-editors`. Codex: `codex plugin marketplace upgrade`. [Changelog](<plugins/vibe-edit/CHANGELOG.md>).

[License and use](<plugins/vibe-edit/LICENSE AND USE.md>) · [Third-party notices](<plugins/vibe-edit/THIRD-PARTY.md>) · [Optional asset bundle](<plugins/vibe-edit/ASSETS.md>)
