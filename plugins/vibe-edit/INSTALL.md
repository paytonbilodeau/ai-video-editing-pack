# Install Vibe Edit

This page is written for the AI assistant. If you are a person reading it, give it to your assistant with one line:

```text
Read INSTALL.md and set up Vibe Edit for me.
```

Vibe Edit is a plugin: a folder of skills that turns a local AI assistant into a video editor. It is also called Vibe Editing, the Vibe Editors pack and, by its older name, the AI Video Editing Pack. One install, then the person asks for edits in plain language.

## What the assistant does

Work through these steps in order. Run the commands yourself where the app allows it. Ask the person only when a step needs their click or a choice only they can make. Finish with the verification in step 5; a command that printed "installed" is not a working setup.

### 1. Find out where you are running

Decide which of these is true from the environment you can observe, not from a guess:

| Situation | How to tell |
| --- | --- |
| Claude Code | The `claude` command is available, or the session is a Claude Code session |
| Codex (ChatGPT desktop app or Codex CLI) | The `codex` command is available, or the session is a Codex session |
| Another local agent that reads skills (Cursor, Gemini CLI, OpenCode and similar) | Neither command above, but you can read and write local files |
| A chat-only app (ChatGPT on the web, Claude.ai, a phone app) | You cannot read the person's local files or run commands |

Also find the source: either this file is inside a downloaded folder, or you were given a GitHub link. The downloaded folder has `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json` two levels above this file. Read the `name` field in the matching file; that is the marketplace name used below. The public GitHub marketplace is named `vibe-editors`. A community early-release folder is named `vibe-editors-early`.

### 2. Install the plugin

**Claude Code.** From a shell, or by asking the person to type the slash form inside their session:

```sh
claude plugin marketplace add paytonbilodeau/ai-video-editing-pack
claude plugin install vibe-edit@vibe-editors
```

On Claude Code 2.1.275 or later the two steps collapse into one, inside a session: `/plugin install vibe-edit --marketplace paytonbilodeau/ai-video-editing-pack`.

From a downloaded folder, replace the first command with the folder path (the folder that contains `.claude-plugin`), and use the marketplace name you read from it:

```sh
claude plugin marketplace add "/path/to/the downloaded folder"
claude plugin install vibe-edit@vibe-editors-early
```

Then ask the person to run `/reload-plugins` in their session, or to restart Claude Code. New skills appear only after that. Before installing from a folder, remove any copy installed from the other marketplace, so the person never has two copies with the same skills: `claude plugin uninstall vibe-edit@vibe-editors` or `claude plugin uninstall vibe-edit@vibe-editors-early`.

**Codex.** The same two steps:

```sh
codex plugin marketplace add paytonbilodeau/ai-video-editing-pack
codex plugin add vibe-edit@vibe-editors
```

From a downloaded folder:

```sh
codex plugin marketplace add "/path/to/the downloaded folder"
codex plugin add vibe-edit@vibe-editors-early
```

Then ask the person to start a new Codex session; bundled skills load at session start. If the `codex plugin add` command is unavailable in their version, open the Plugins tab in the ChatGPT desktop app (or type `/plugins` in the Codex CLI), choose the marketplace and install Vibe Edit there. That is one click for the person; show them where it is.

**Another local agent.** Keep this whole `vibe-edit` folder in a permanent place, such as the person's editing workspace. Point the agent's skills directory at `vibe-edit/skills`: on the Agent Skills standard that means a link from the project's `.agents/skills/<name>` to each `vibe-edit/skills/<name>` folder, or whatever that agent documents for adding a skills directory. Do not copy individual skills out of the folder; they reference each other and the `lessons`, `practice` and `licenses` folders by relative path.

**Chat-only app.** Say in one sentence that this app cannot operate a video editor or read local files, then give the person the two Claude Code or Codex commands above to paste into a local app. Stop there; do not pretend to install.

### 3. Confirm the skills loaded

List the installed plugin and its skills:

```sh
claude plugin list
```

or in Codex, start a new session and check that the Vibe Edit skills are offered. Expect these twelve skills: setup, edit, pre-edit, style, remotion, hyperframes, javascript-animation, captions, shorts, editors, update, help. In Claude Code they are invoked as `/vibe-edit:setup` and so on. If fewer appear, the install is incomplete; read the app's plugin error list and fix that before continuing.

### 4. Run the setup skill

Once the skills are loaded, run setup. The person can type the one-line prompt, or you can start it:

```text
Set up Vibe Edit as my video editor and run the practice edit.
```

The setup skill checks the tools already on the computer, puts the person's editing profile outside the plugin so updates never touch it, finds a working route to their video editor, and makes one disposable edit from the included practice clip. Nothing in this folder needs the person's own footage for that.

### 5. Verify before saying "ready"

Report, in the person's words, not in file paths:

- Which app and which editor are connected, and which route works (native control, timeline file, or screen control).
- Where their editing profile lives, and that it is outside the plugin.
- That the practice edit produced a saved project and an exported video, and what you watched and checked.
- Any step that still needs their hand, named exactly.

## What this install never does

It does not connect paid services, upload footage, publish anything, change app permissions or security settings, or install a video editor. It does not put secrets anywhere. If a later step would need any of those, say so and wait for the person's choice.

## Updating later

Updates arrive through the same marketplace. In Claude Code the person runs `/plugin marketplace update vibe-editors` (or turns on auto-update for that marketplace under `/plugin`); in Codex, `codex plugin marketplace upgrade`, then reinstall from the Plugins tab if the app asks. A downloaded folder (the community early release or the public zip) updates when the person pastes the line from the release post, "Update Vibe Edit to <version> from <link> with hash <sha256> and keep my profile": the `update` skill downloads the new zip, checks its SHA-256, swaps the folder in place and offers each change. Their profile and projects stay where they are. The `update` skill explains the details and the move from a 5.x install.
