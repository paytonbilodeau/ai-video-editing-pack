# Set Up Your AI App for Local Video Editing

**Verified September 28, 2026.** AI apps change quickly. Open the linked official setup page before you grant access, and confirm that the feature is available on your current plan, operating system, region, and workspace.

## Recommended setup: ChatGPT desktop with Codex Local

Payton's setup is **ChatGPT desktop → Codex → Local → a dedicated video project folder**. This gives the assistant a real working folder, local tools, and an optional way to operate approved desktop apps. A normal browser chat can help plan an edit, but it cannot reach into your computer or control DaVinci Resolve by itself.

Use a capable model with enough reasoning time for source review and revision comparison. Check the current model choices in your app instead of relying on a model name printed in an old guide.

### 1. Start a local Codex task

1. Install the [ChatGPT desktop app](https://learn.chatgpt.com/docs/app). OpenAI currently documents desktop apps for macOS, Windows, and Linux.
2. Choose **Codex**.
3. Start a new task, choose **Local**, and select the folder for this video project. OpenAI also offers Worktree and Cloud environments, but Local is the direct route for files on this computer ([Codex environments](https://learn.chatgpt.com/docs/environments/modes)).
4. Keep original footage outside the pack. Work from copies inside a dedicated project folder.

### 2. Choose a permission mode

Open **Settings → General → Permissions**, then choose the mode in the task menu ([OpenAI permission modes](https://learn.chatgpt.com/docs/permission-modes)).

| Mode | What it allows | When to use it |
|---|---|---|
| **Full access** | Codex can edit files outside the project and use the network without asking. | Payton prefers this for his own trusted editing workflow because it avoids repeated stops. Use it only when you understand the wider access, have recoverable files, and have named the exact project and task. |
| **Approve for me** | Codex stays inside the workspace boundary. Auto-review checks requests that go beyond it. | The supported step down from Full access. This is a sensible starting point when you want fewer prompts without giving unrestricted access. Auto-review can still make mistakes. |
| **Ask for approval** | Codex stays inside the workspace boundary and asks you before going beyond it. | Use this when you want to review wider file or network access yourself. OpenAI recommends starting here for most work. |

Full access is Payton's personal choice, not a requirement for this pack. Changing a permission mode also does not install an editor connection or approve a desktop app.

### 3. Add Computer Use for visual editor actions

Open **Plugins → Computer Use → Install plugin**. Enable the Computer Use server and skill if those switches appear, then add Computer Use to a Work or Codex task ([official setup](https://learn.chatgpt.com/docs/computer-use)).

On macOS, approve these prompts when you want local GUI control:

- **Screen Recording** lets the app see the interface.
- **Accessibility** lets it click, type, and navigate.

OpenAI's current setup does not list Full Disk Access as a standard requirement. Do not grant it in advance. If a current official prompt asks for it, read the reason and decide then.

Approve DaVinci Resolve or another editor when Computer Use asks for that app. Editor approval is separate from the file and shell permission mode. OpenAI does not specifically promise Resolve support, so prove it on a copied 20 to 60 second clip before using it on valuable work.

### 4. Use the native editor connection and the GUI together

Use a vendor-native MCP, API, or scripting route for structured operations it officially supports. Use Computer Use for visible controls that the structured connection does not cover. These routes complement each other:

- A native connection is usually better for exact project status, timeline data, and repeatable commands.
- Computer Use can handle visible dialogs and controls, but layouts and pop-ups can change what it sees.
- A person still watches and listens to the saved export before calling the edit finished.

For the current Resolve, Final Cut, Premiere, and CapCut routes, use [Editor Connections](EDITOR%20CONNECTIONS.md). This pack does not bundle an MCP server or change editor settings automatically.

### 5. Keep the computer available

For a long local task on macOS, turn on **Settings → General → Prevent sleep while running** ([OpenAI long-running work](https://learn.chatgpt.com/docs/long-running-work)). Local scheduled work also needs the computer on and the ChatGPT desktop app running ([OpenAI automations](https://learn.chatgpt.com/docs/automations)).

OpenAI currently supports background Computer Use tasks on macOS. On Windows, keep the target app visible on the active desktop ([local Work security](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-local-security)).

### 6. Add Chrome only when the task needs your signed-in browser

Use the built-in browser for isolated web research. Use the Chrome extension only when the task needs a site where you are already signed in.

1. Open **Settings → Computer Use → More browsers**.
2. Choose Chrome and follow the install link.
3. Confirm **Manage** in the extension flow.
4. Start a new Work or Codex task and mention **`@Chrome`**. Use **`@Computer`** for approved desktop apps.

OpenAI currently documents Chrome, Edge, Brave, Opera, and Vivaldi support. Availability can vary by rollout and workspace settings ([browser extension setup](https://learn.chatgpt.com/docs/chrome-extension)).

## Claude is a credible alternative

Claude Cowork can work with connected local files and, where available, use approved desktop apps through Computer Use. Claude Code Desktop works with local project files and commands; it needs a separately verified editor connection for editor actions. The exact Claude UI is moving: some Pro and Max accounts now use a combined Chat and Cowork experience, while other accounts still show a Cowork switcher ([Anthropic's current rollout note](https://support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude)). Follow the labels you actually see.

### Cowork

1. Install [Claude Desktop](https://support.claude.com/en/articles/10065433-install-claude-desktop).
2. Connect only the folder needed for the project.
3. Open **Settings → General → Enable computer use**.
4. Approve the editor when Claude requests it. On macOS, Computer Use needs Accessibility and Screen Recording.
5. Use **Manual** when you want to approve actions yourself, or **Auto** when you want Claude's safety review. Older interfaces may show **Skip**; do not use Skip as the default on a personal editing computer.

Cowork is currently documented on paid plans, while native Computer Use is currently limited to Pro and Max on macOS and Windows. Computer Use needs the desktop app open and the computer awake. Check the [current Cowork setup](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork) and [Computer Use availability](https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork) before teaching or buying around it.

### Claude Code Desktop

Claude Code is the closer alternative to Codex for local project files, commands, and technical workflows. Current permission choices include **Manual**, **Accept edits**, **Plan**, **Auto**, and **Bypass permissions** ([Claude Code Desktop](https://code.claude.com/docs/en/desktop)).

Do not recommend **Bypass permissions** on a normal personal Mac. Anthropic says to reserve it for isolated containers or virtual machines because it skips permission prompts, including protected paths ([Claude Code permissions](https://code.claude.com/docs/en/permissions)). Manual or Auto is the better fit for an editing computer.

Claude in Chrome uses your signed-in personal browser. Set it up at **Settings → Connectors → Claude in Chrome → Configure**, then enable it for the conversation ([Claude in Chrome](https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome)).

## Prove the setup before the real edit

Use a disposable project and a copied short clip:

1. Confirm the assistant can name the selected folder and editor without changing either.
2. Import the copied clip.
3. Make one reversible change.
4. Save, close, reopen, and export a short review file.
5. Watch and listen to the export yourself.

Record the result as **documented**, **directly tested**, or **unavailable**. If the editor connection fails, use the pack's manual workflow. The editing method still works when a person performs the named steps.

Current OpenAI plan coverage is listed on the [ChatGPT plans page](https://learn.chatgpt.com/docs/pricing). Current Claude Code plan coverage is listed for [Pro and Max](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan) and [Team and Enterprise](https://support.claude.com/en/articles/11845131-use-claude-code-with-your-team-or-enterprise-plan). Treat those pages, not this dated snapshot, as the final word on availability.
