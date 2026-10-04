# Set Up Your AI App for Video Editing

**Checked October 3, 2026.** Use a local assistant such as Codex or Claude Code
with a folder on your computer. It can read the pack, work with files and run
editing tools. A normal browser chat can discuss an edit, but that alone does
not connect it to your local video editor.

Start with the subscription and editor you already have. Give the assistant
the pack and its [setup message](../START%20HERE.md). It should inspect the
available tools, save your private editing profile and explain any missing
connection. You do not need a recording ready, and there is no practice clip
to complete before you can use it.

## Which plan and model?

A plan pays for access and usage. A model does the reasoning. Neither one,
by itself, gives the AI control of your editor.

At this check, OpenAI lists **Plus at US$20/month** and **Pro from US$100/month**.
Start with an eligible plan you already pay for. Consider a higher allowance
when real editing work repeatedly hits your limits, or when a model or feature
you need is unavailable. Check the [current plans](https://learn.chatgpt.com/docs/pricing)
before paying: access, limits and regional prices can change. A ChatGPT
subscription does not include separate API usage for another tool.

For editing, the difficult part is often judgment: choosing the complete take,
keeping a useful pause, comparing references and diagnosing a bad transition.
Payton prefers **GPT-6 Astra with High reasoning** for that work. This is a
workflow preference, not a measured claim that it wins every video-editing task.

**GPT-6.1 Sol** is a capable everyday option designed to offer much of Astra's
capability at lower usage cost. **Luna** suits narrower tasks with clear checks,
such as renaming files or formatting notes. A higher reasoning setting gives a
model more time to work through a problem; it does not add an editor connection
or guarantee better taste. There is no need to choose Max or Ultra for every
task. See [OpenAI's model guide](https://learn.chatgpt.com/docs/models) and the
choices available in your own app.

Claude Code is another local route. Anthropic currently includes it in paid
Claude plans, with usage shared across Claude and Claude Code; API billing is
separate. Use an available model suited to complex reasoning for editorial
decisions and a lighter one for routine work. Check [Claude's current plans](https://claude.com/pricing)
and [Claude Code Desktop](https://code.claude.com/docs/en/desktop) before choosing.

## Codex: connect the working folder

In the [desktop app](https://learn.chatgpt.com/docs/app), open Codex, start a
**Local** task and choose a dedicated editing folder. Local means the work
runs on this computer. Keep original footage recoverable and projects outside
the downloaded pack, so replacing the pack cannot replace your work.

Give the AI the extracted pack and setup message. It should create or reuse
your private editing profile, then save a pointer in the project's instructions.
Later edits in that workspace can read it. A new app or unrelated chat may
need the folder supplied again.

## Permissions: what each setting actually does

Choose a mode in the task's permission menu. Settings may first need enabling
under **Settings → General → Permissions**. Follow the current labels in your
app and [OpenAI's permission guide](https://learn.chatgpt.com/docs/permission-modes).

| Mode | What changes | Why choose it? |
|---|---|---|
| **Ask for approval** | Requests beyond the workspace boundary go to you. | Useful while getting familiar with a workflow. |
| **Approve for me** | Automatic review evaluates requests beyond the same boundary. | Fewer interruptions, with review that can still make mistakes. |
| **Full access** | File and command access extends beyond the project, including network access, without those approval prompts. | Payton uses it for his established workflow. It reduces stops but also gives mistakes more room to cause damage. |

Full access is optional. It does not install a connector, authorize publishing
or make downloaded instructions trustworthy. Keep the task specific and
originals recoverable whichever mode you choose.

## Let the AI operate the editor

File access and editor control are different. The assistant should check the
[connection matrix](EDITOR%20CONNECTIONS.md) and your editor's playbook, then use
the route that actually works on your installed version. A native connection
can handle supported operations precisely. Computer Use can operate visible
controls. A timeline-file route may require you to import a file yourself.

For Codex Computer Use, follow the [official setup](https://learn.chatgpt.com/docs/computer-use).
On macOS, **Screen Recording** allows the app to see the interface and
**Accessibility** allows clicking and typing. These are separate from Codex's
file permissions. Approve the particular editor when asked. A remembered or
“always allow” choice, where offered, avoids repeated prompts for that app;
choose it only for an app and access you intend to keep available.

**Full Disk Access** is a macOS permission for protected data. It is not the
same as Codex's Full access, and OpenAI does not list it as a standard Computer
Use requirement. Enable it only when a current, specific setup requirement
explains why it is needed. More switches turned on does not mean a better edit.

Claude Code Desktop has its own modes, including Manual, Accept edits, Plan
and Auto. Anthropic reserves Bypass permissions for isolated environments
such as containers or virtual machines; it is not the equivalent recommendation
for a normal personal editing computer. Follow its [desktop guide](https://code.claude.com/docs/en/desktop)
and verify the actual editor connection separately.

## What “ready” means

The AI can find your profile, name its available editing route and explain
how to hand it a recording. If it needs to test an import or export, it can
use a harmless disposable fixture within your authorized setup. It should
report whether a capability is documented, directly tested or unavailable.
It must not claim it edited or watched a file when it could not.

For long local work, keep the computer awake and the app running. Codex offers
**Prevent sleep while running** in General settings; see the
[long-running work guide](https://learn.chatgpt.com/docs/long-running-work).
Then use your own clips at your own pace. Ask for a complete edit, a small
experiment or a preview first. The pack defaults to completing the work you
request and returning the editable project, export and a short report.
