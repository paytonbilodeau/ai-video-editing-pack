# Start Here: AI Video Editing Pack

Give this pack to an AI assistant that can work with files on your computer,
such as Codex or Claude Code. It contains editing skills, guides and templates.
Your AI uses them with your video editor; opening the folder alone does not
edit a video.

## Get ready

1. [Download the ZIP](https://github.com/paytonbilodeau/ai-video-editing-pack/releases/latest/download/ai-video-editing-pack.zip).
   A ZIP is a compressed folder. Double-click it on a Mac; on Windows,
   right-click and choose **Extract All**. No GitHub account is needed.
2. Open your local AI assistant and give it the extracted folder. The
   [AI app guide](references/AI%20APP%20SETUP.md) explains plans, models and
   permission settings if you need help choosing.
3. Paste the message below. Your AI checks the setup and saves a private
   editing profile with your tools and preferences. No footage is needed yet.

```text
Set up this AI Video Editing Pack so you're ready to be my video editor.
Read SKILL.md and skills/vibe-editing-setup/SKILL.md, then follow their linked
guides. Check my existing AI app, editor and available connections. Ask only
for missing information that matters, and keep setup moving without requiring
a test clip or assigning exercises.

Create or reuse a private editing profile outside the pack. Save its location
in this assistant's supported project instructions so future edits can find
it. Use sensible starting preferences where I haven't chosen yet.

Keep originals untouched and work in editable copies. Ask before new installs,
paid services, uploads or broader access unless already authorized. Verify
what you can actually do and explain any remaining manual step plainly.

For future edits, complete the requested work and deliver the editable project,
export and short report. Don't pause for routine stage approvals unless I
request checkpoints. Setup alone is not a request to edit anything.
```

Setup is complete when your AI can explain the available editing route, find
your private profile, and tell you how to hand over a recording. If a connection
needs permission or an installation, it should name that one remaining step.
It must not call an untested connection working.

When you feel like editing, give it a recording and describe the result you
want. A short clip, a whole video or a quick experiment is your choice. You can
also ask for a preview before it continues. The default is a complete pass
within your brief, followed by files you can watch and adjust.

Keep original footage, projects and your profile outside the downloaded pack.
See [Safety and API Keys](references/SAFETY%20AND%20API%20KEYS.md) for connection
details and [the workflow](references/EDIT%20WORKFLOW.md) for how edits run.

## Optional private-folder setup

The paste message above needs no Python. If you want the included helper to
create worksheet copies, use Python 3.11 or newer and preview this command
from the extracted pack folder:

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
