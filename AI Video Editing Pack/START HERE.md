# Start Here: AI Video Editing Pack

**For the complete personal system, [start at the full download’s setup](<../START HERE.md>).** This folder keeps the independent core workflow and optional plugin route available.

**[8-step visual walkthrough](../Kit%20Email%20Workflow/visual-guide/README.md)**

In Codex, start a **Local** task in a dedicated editing folder. Select the
extracted **Vibe Editors** folder or give its exact location, then ask the AI
to list a few files it can read. Use the [AI app setup guide](references/AI%20APP%20SETUP.md)
for the Claude Code route. Paste the message below. No footage is needed yet.
The full download includes the editing skills, pre-edit and waterfall tools,
motion resources and 22 lessons. You can start immediately.

```text
Set up this Vibe Editors folder so you can be my video editor. Read its START HERE guide and follow the setup skill. Ask how hands-on I want to be: careful, balanced, or handle it for me. Reuse my existing tools, permissions, skills and preferences. Keep my originals and projects safe, and keep my private editing profile outside the pack. Explain any new access, upload, installation or cost before using it unless already authorized. Offer useful optional tools, then set up what fits. List a few files you can read in this pack, show where my private editing profile is saved, and separate editor actions you tested from actions that still need me. Tell me the simplest next step. No footage is needed for setup.
```

The AI should inspect first, recommend a setup, explain meaningful choices,
and carry out the work you authorize. Keep the editor and workflow you already
use when they fit. Your working pace can change at any time.

[Setup flow](references/SETUP%20FLOW.md) explains the interview and optional
installs. [AI App Setup](references/AI%20APP%20SETUP.md) explains app choice and
permissions. Your profile, footage and projects belong outside the pack so
future updates preserve your work.

When ready, hand over a recording and describe the result. Ask for a complete
edit, one specific improvement or a preview. The AI checks the actual route
and tells you which steps it can perform and which need your action. Use the
[8-step visual walkthrough](../Kit%20Email%20Workflow/visual-guide/README.md)
when you want to know what to do next and what can wait.

If you installed only the native plugin, use the
[complete ZIP](https://github.com/paytonbilodeau/ai-video-editing-pack/releases/latest/download/ai-video-editing-pack.zip)
for its supporting tools and teaching guide. Native plugin installation alone
may cache only the core skill folder. Don't delete a working plugin or project
just to add the complete download.

## Need one specific step?

- [Make your first edit](../Kit%20Email%20Workflow/visual-guide/README.md).
- [Choose a motion tool and run its starter](references/MOTION%20TOOL%20SETUP.md).
- [Update without losing your preferences](references/UPDATING.md).

## Optional private-folder setup

The paste message above needs no Python. If you want the included helper to
create worksheet copies, use Python 3.11 or newer and preview this command
from the `AI Video Editing Pack` folder inside the extracted `Vibe Editors`
folder. Your assistant can run it for you:

```sh
python3 tools/setup_project.py --project "/path/to/my-video-project" --profile-dir "/path/to/my-private-editing-profile"
```

The helper previews every file it would create. If both private destinations
are right, repeat the command with `--apply`. It copies three project
worksheets into the project folder and `EDITING PROFILE.md` into the separate,
durable profile folder. Record that profile path in `PROJECT INTAKE.md` and
reuse it for later projects. The helper refuses to overwrite edited files.
If that profile already exists, it reuses the file unchanged while creating
the new project's worksheets.
On Windows, use `py -3.11` in place of `python3`.

You can do the same manually: make two private folders outside this pack,
copy `PROJECT INTAKE.md`, `EDIT PLAN AND REVIEW.md`, and
`DELIVERY AND LEARNING.md` from `templates/` into the project folder, copy
[EDITING PROFILE.md](templates/EDITING%20PROFILE.md) into the durable profile
folder if it is new, and record both locations in the intake. Reuse an
existing private profile as it is. If you also want a portable
skill copy, add `--skills-dir "/path/to/my-assistant-skills"` to the preview
and apply commands. Check your AI app's current folder rules first. Copying
files does not activate a native plugin.

For the recommended local Codex route and its permission choices, read the
dated [AI app setup guide](references/AI%20APP%20SETUP.md).
