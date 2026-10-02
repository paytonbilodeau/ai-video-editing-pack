# Tools, Licenses and Sources

The library includes original instructions and a small Python setup checker.
It does not bundle editor binaries, MCP vendor code, fonts, media, AI models,
framework packages or a private production style.

| Tool | Role and setup boundary | Primary source |
|---|---|---|
| DaVinci Resolve / Studio | Editing, Fusion, audio, color and export; verify edition and native integration before buying or updating | [Blackmagic support](https://www.blackmagicdesign.com/support/family/davinci-resolve-and-fusion) |
| Native Resolve MCP and scripting | Inspect the documentation installed with the same editor; a supported client and local permissions are separate requirements | [Resolve 21.1 manual](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_21.1_Reference_Manual.pdf) |
| Python | Runs the included read-only setup checker; version 3.11+ | [Python downloads](https://www.python.org/downloads/) |
| FFmpeg and ffprobe | Local media inspection, decode and fixture rendering; license depends on build and redistribution | [FFmpeg](https://ffmpeg.org/download.html) |
| Node.js | Optional motion runtime; use a supported version meeting the chosen framework requirements | [Node.js](https://nodejs.org/en/download) |
| Remotion | React motion rendering; use System 09's pinned starter and check license eligibility | [Remotion docs](https://www.remotion.dev/docs/) and [license](https://www.remotion.dev/license) |
| Hyperframes | HTML motion and local rendering; Apache-2.0 project, optional services separate | [Official repository](https://github.com/heygen-com/hyperframes) |
| Local transcription or audio service | Use the user's approved route; inspect model downloads, data handling and any service cost first | System 05's `THIRD-PARTY.md` |

Setup sources were checked September 14, 2026. Preserve the license notices of
any tools or assets you install. Recheck current documentation after updates.
An AI subscription does not automatically pay for optional APIs, hosted renders,
font licenses or a commercial editor. An open-source tool can still consume
local compute, disk and setup time.
