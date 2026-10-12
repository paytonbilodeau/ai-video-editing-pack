# A first HyperFrames graphic

This five-second example reveals an idea, its connection, and a clear visual.
It gives your AI a small editable project to test before building a longer scene.
The source contains no paid assets, fonts, voices or cloud service calls.

Ask the AI to copy this folder into a new private working project, check Node 22+
and FFmpeg, then offer the package install if it is not already authorized.
After `npm ci`, the AI can run `npm run check`, `npm run render`, or
`npm run render:overlay`. The last command sets the `transparent` variable in the source and produces ProRes 4444. Set `HYPERFRAMES_NO_TELEMETRY=1` for local
commands without usage telemetry. `npm run doctor` prints a JSON report; inspect
its `ok` field and the individual checks, not just the process exit code.

The package lock fixes the dependency versions for this example. The install
may download renderer dependencies. Keep the final source and its lockfile.
Inspect the encoded video and test its overlay in your own editor. The renderer
being installed does not prove that every chosen effect or codec imports there.

HyperFrames and GSAP remain third-party dependencies downloaded from their
published packages. Their source is not bundled in this folder. Consult their
current licenses before your use. See the parent system's `THIRD-PARTY.md`.
