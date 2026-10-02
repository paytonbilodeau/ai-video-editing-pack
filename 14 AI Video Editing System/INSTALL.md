# Setup and First Test

Use a working copy of the library and an empty project folder under `_MY WORK`.
Keep the user's original media outside test outputs. These instructions install
nothing automatically. A file-aware coding assistant can carry out approved
steps; a chat assistant can guide the person performing them.

## 1. Check what is already available

From this system folder, using Python 3.11 or newer:

```text
python3 -B tools/setup_doctor.py --workspace "../_MY WORK"
```

On Windows, use `py -3.11` instead of `python3`. Create the named workspace first.
For the optional HTML/React motion route, add `--motion`. The checker looks at
the supplied directory, asks named installed tools for their versions, and
checks standard Resolve MCP locations. It does not read media, connect to
Resolve, install anything or change settings. Tool presence is not connection
or license proof. Missing prerequisites produce a nonzero exit and useful notes.

Python is for the included checker. FFmpeg and ffprobe support media inspection
and technical verification. System 05's `INSTALL.md` covers their platform
installation. Node.js 22 or newer satisfies the documented Hyperframes baseline;
check the chosen Remotion version's requirements too. Use official installers
or an already trusted package manager after reviewing the proposed install.

## 2. Connect the editor

Follow `guides/RESOLVE AND MCP.md` for the installed edition and platform.
The documented native automation path here was checked on Resolve Studio 21.1
on macOS. Windows and Linux need their own connection and sample-render checks.
Keep the free editor or an existing editor if it fits manual finishing; do not
promise the Studio integration is available in every edition.

Record the exact version, license route, chosen connector and read-only result
in `templates/TOOL SETUP.md`. Confirm a disposable project can import a copied
clip, make one reversible timeline change and export before attempting a full
recording. A listed MCP server alone does not pass this test.

## 3. Add motion only if the clip needs it

Follow `guides/MOTION TOOL SETUP.md`. You can use native Resolve titles first,
the neutral Remotion starter in System 09, or a small Hyperframes project.
The guide has copyable commands and a test prompt. Pin the working versions
and keep package lockfiles. Do not install both frameworks merely because they
are listed here. Local rendering and optional hosted generation have different
costs and data flows; verify those before choosing a provider.

## 4. Run the small edit

Complete the project brief. Make a clean 20 to 60 second cut from a copy,
review its joins, then add one approved visual. Save a clean master, decorated
master and editable project if all three are useful. Reopen the project,
decode the outputs and have someone watch and listen to the exact export.
Use `examples/EXAMPLE EDITING RUN.md` as a fictional filled-in reference.

## 5. Test the included checker

```text
python3 -B -m unittest discover -s tests -p "test_*.py" -v
```

These offline tests simulate missing and present tools, unsupported Node,
unavailable directories and version-call failures. They do not test Resolve,
render a video or establish a human's operating-system setup.
