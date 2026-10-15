# Use the system in your AI app

Open a local working folder in the app you already use. Keep the complete downloaded bundle available until setup finishes. Paste the [setup message](<START HERE.md>); the assistant can run the commands below.

The local bootstrap needs Python 3.11 or later. It copies the reviewed bundle and creates skill instructions. It does not install video editors or graphics engines, change app permissions, connect accounts or subscribe to a service.

## Codex

Select the local project folder. Setup creates project skills in `.agents/skills/` with unique `vibe-` names, each pointing to the complete copied module. Ask Codex to use `vibe-editor-setup` if that name is in the supplied manifest; otherwise ask it to read the setup file directly. Confirm the actual skill path and customer profile in its readback. Existing personal or project skills remain intact.

## Claude Code

Start Claude Code in the local project folder. Setup creates project skills in `.claude/skills/`. Use the supplied `vibe-` skill name or ask Claude to read the setup file directly. Confirm which file loaded: an existing personal skill can have priority over a project skill with the same name. Keep your current permissions and connections.

These locations are documented by [OpenAI](https://learn.chatgpt.com/docs/build-skills) and [Claude Code](https://code.claude.com/docs/en/skills), checked October 15, 2026. Loading instructions does not establish access to a native editor.

## Local command

Replace both quoted placeholders with real folder paths. The first command only shows the plan. Run the second after checking the destination. `--app claude` or `--app both` selects the other integration.

```sh
python3 "FULL BUNDLE/Payton Editing System/setup/bootstrap.py" install --source "FULL BUNDLE" --workspace "YOUR EDITING WORKSPACE" --app codex
python3 "FULL BUNDLE/Payton Editing System/setup/bootstrap.py" install --source "FULL BUNDLE" --workspace "YOUR EDITING WORKSPACE" --app codex --apply
```

An existing profile can be selected with `--profile "preferences/EDITING PROFILE.md"`, relative to the workspace. The default is `Vibe Editor Settings/EDITING PROFILE.md`. Never put secrets in that profile.

If the app cannot read local files, attach the relevant instruction and template files and ask for a manual plan. That can help with a brief or review, but it does not install this system or operate your editor. Return to the local route for the tested editing workflow.
