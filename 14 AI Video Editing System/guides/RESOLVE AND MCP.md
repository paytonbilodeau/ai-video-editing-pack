# Connect DaVinci Resolve to Your Assistant

MCP is a way for the assistant to discover and call an application's tools.
Resolve still performs the editing and rendering. The assistant must understand
the installed tool descriptions and inspect the result of each operation.

## Choose the supported route

1. Open Resolve and check its edition and version in About. Install or update
   only from [Blackmagic Design](https://www.blackmagicdesign.com/support/family/davinci-resolve-and-fusion)
   when an approved task actually needs it. The person handles any purchase,
   account entry and activation.
2. Check the installed manual and Developer/Scripting documentation. In the
   inspected Studio 21.1 distribution, Preferences > System > General exposes
   External scripting and Automatic scripted actions. Use Local and Allow safe
   for the corresponding local workflow. Do not enable network scripting or
   arbitrary execution just to avoid understanding a failed call.
3. Prefer the bundled native MCP for a supported installation. If the assistant
   supports MCP bundle import, use the vendor's `DaVinciResolve.mcpb`. Otherwise
   inspect its current manifest and the assistant's current local-server setup
   instructions. Preserve unrelated MCP configuration and back it up first.
4. Restart or refresh the assistant's MCP tools if its interface requires it.
   Ask for Resolve status. Confirm it identifies the running installation.
   Then test a read-only request before touching any active project.

The macOS Studio 21.1 bundle contains `ResolveMCP` in the application's
`Contents/Applications` directory. Its bundled wrapper starts that binary with
`BMD_IS_MCPB=1`. For an MCP client using a command/args/env object, this is the
macOS server object to adapt after checking the installed path:

```json
{
  "command": "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/ResolveMCP",
  "args": [],
  "env": {"BMD_IS_MCPB": "1"}
}
```

This is a server object, not a complete configuration for every client. A client
using TOML needs its equivalent fields. Do not paste it over an entire config.
On Windows, inspect the actual installation for `ResolveMCP.exe`; an installer
can use a non-default drive. On Linux, inspect the installed vendor bundle and
manual instead of assuming the macOS path applies. The setup checker accepts
`--resolve-mcp "path/to/ResolveMCP"` to check a known custom location, but does
not execute that binary or prove connectivity.

## Prove a connection and one edit

```text
Use the installed Resolve tools to report the application version and whether
it is running. Do not modify the current project. Search the installed scripting
API for the operations needed to create a test project, import a clip, assemble
a timeline and export it. Show the exact small test and output location first.
Once that test is authorized, use copied media in a disposable project, save it,
export a short clip and reopen the project. Report the actual tools used and
which checks passed. Do not substitute a tool-list response for an exported test.
```

The inspected native server exposes status, API search/documentation and safe
script execution. Discover their actual names and schemas in the current client.
A UI feature may have no corresponding script setter. Use supported native UI
controls for that step or describe the limit; do not invent an API call.

## When it does not connect

| Symptom | Next useful check |
|---|---|
| Server listed, app not available | Finish opening and activating the right edition; retry status |
| Executable missing | Inspect the actual install and version; do not replace a working bridge blindly |
| Client has no local MCP support | Use supported computer use or perform the editor steps manually |
| Script rejected | Read the error and current SDK; keep the safe route, narrow the action |
| Project or timeline unexpected | Stop mutations, select the intended project and read its state again |
| Feature missing from scripting | Check installed documentation and native UI before promising automation |

The Studio 21.1 scripting notes also describe a bundled `ResolvePython` runtime
that can import `DaVinciResolveScript` without custom environment variables.
It is for Resolve scripts, not a replacement for a general Python environment
with pip packages. Use it only when the documented native MCP route is
insufficient and the operation is authorized.

## Sources and scope

Checked September 14, 2026 against the installed vendor Studio 21.1 bundle,
its MCP manifest/wrapper and Scripting README (dated August 31, 2026), plus
a live read-only native status call on macOS. The library does not redistribute
that vendor code. Read the current [official manual](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_21.1_Reference_Manual.pdf)
and installed Developer documentation for your release. Installation paths and
client interfaces can change. This check did not perform a new production edit.
