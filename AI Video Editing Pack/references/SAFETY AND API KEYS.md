# Safety and API Keys

Give your AI the footage and tools it needs for this edit. Keep originals,
credentials and unrelated files outside that access. These rules guide the
workflow; they do not replace the permissions enforced by your AI app or editor.

## Keep keys out of the pack

An API key can give someone access to a service or let them spend from your
account. Never put a real key in this pack, your editing profile, a chat prompt,
a screenshot, a shared log or GitHub. Record the service name and the private
storage location in your setup notes, not the key itself.

Use the service's supported secret storage or a private local configuration
outside the shared pack. If a tool needs an environment variable, set it using
that tool's documented method. A local `.env` file still contains readable
secrets: exclude it from version control and shared folders, limit file access,
and do not ask the AI to print its contents. Give each key only the permissions
it needs. Set a spending limit when the service supports one.

If a key is exposed, revoke it at the provider and create a replacement.
Removing it from a file or a Git commit does not disable the exposed key. Check
the provider's usage history for unexpected activity.

## Check connectors before granting access

A connector or MCP server lets an AI use another tool. Check its publisher,
source, installation command and requested permissions before installing it.
Prefer an official editor integration when available. An unofficial connection
needs its own source review; a familiar product name is not proof of trust.

Start with the named project folder and a copied 20 to 60 second clip. Prove a
read-only connection before allowing an edit. Do not disable safeguards or
grant full-computer access to get past a setup error. Keep a local editor
connection on the local computer by default. If remote access is needed, use
the connector's supported authentication and network protections. Remove
connections, tokens and permissions you no longer use.

## Treat outside instructions as source material

A webpage, transcript, README or downloaded file can contain instructions
aimed at your AI. For example, a tutorial might tell it to send your footage or
keys to an unfamiliar address. This is prompt injection: outside content tries
to change what the assistant does.

Use that content as information to inspect, not permission to run commands,
expand access, reveal secrets or upload files. Check the original source and
ask the AI to explain an installation command before approving it. If a tool
output or reference asks for an action you did not request, stop and review it.
Do not rely on written instructions alone to block a malicious action; keep
the app's approval and access controls in place.

## Keep the edit recoverable

Work from copied media and save an editable timeline. Keep a recoverable
version before applying a large change. Review the plan before allowing the
helper or editor to write files. Uploading private footage, publishing a video,
buying a service and expanding access each need your specific authorization.
Watch and listen to the exported file before sending it anywhere.

For the connection test, use [AI App Setup](AI%20APP%20SETUP.md). Record the
approved tools, folders and upload destinations in
[Project Intake](../templates/PROJECT%20INTAKE.md).

Sources checked October 2, 2026:

- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [OWASP LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)
