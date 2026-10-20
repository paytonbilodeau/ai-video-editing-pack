# Keep the cut editable

Use the existing editor and project when they fit. For Resolve, save a named project, preserve sources and create separate Assembly, Dialogue, Clean Review, Visuals and Final timelines as needed. Duplicate before a meaningful change, not before every harmless read. Keep linked picture/dialogue, original source handles, native grades, crops, fades and named visual/audio tracks.

## Native Resolve route

Payton's working route uses Blackmagic's installed native MCP or bundled ResolvePython with Studio. Verify product/version and the specific API in the installed SDK. Connection, licensed access, a successful setter, saved state and a successful render are different checks. On supported macOS installations the bundled interpreter is inside the Resolve application; use the customer's installed path. Do not install a third-party bridge or expose Network scripting just to copy a tutorial. Local scripting and existing safe-action settings are sufficient for the intended route when supported.

`resolve_control.py doctor` is read-only. Its `smoke-test` creates a new project and a bounded ≤60-second 4K sample; it is a connection/render test, not an edit. Save open work before switching projects and preserve failed receipts. Use it for a new or changed operation, not as a compulsory benchmark every session.

## Assemble and read back

Set timeline and playback FPS before assembly, preserving rational source rates. Playback rate may remain different even when timeline/export rates are right; check again after reopening. When the installed API exposes a setting read-only, use the native UI and verify, rather than inventing a setter.

Import actual media and check source path, FPS, duration and channels. On the tested Resolve route, plain-path movie imports worked; image-sequence dictionaries have different uses. A nonempty list is not source verification.

For repeated ranges from the same source, the tested reliable route appends one span per call with explicit record frame. Verify each clip's source range, output start, duration and linked audio, then total occupancy. The tested append path used half-open source ends, while render mark-out was inclusive. Test the actual API path; do not reuse one convention indiscriminately.

Keep a source/output map with source hashes, half-open source/output ranges, speed, track, crop and grade identity. Validate retiming and nonzero source timecode before interpreting offsets. Rounded native source getters have differed by one frame in real imports. Do not “repair” approved sync merely to make those getters agree.

## Preserve native state

Export DRP/DRT with the review, retain referenced media and reopen/import the deliverable in a disposable project when verifying a new handoff route. A DRP alone does not embed every source file. An XML import may omit caption styling, effects, crop or motion; inspect those properties after import.

Track-level disabling has not always provided reliable evidence on inactive timelines. Select the intended timeline, read the state, then inspect each actual audio item for replacement mixes. Ensure original/backup dialogue is not playing with its replacement. Check linked picture remains enabled. Native fades can read correctly and disappear after reload; save/reopen and render a representative seam before calling persistence verified.

The saved keyboard/layout/export files are optional conveniences. Importing them changes the user's settings and requires their choice. Preserve existing controls. The keyboard's serialized Ctrl values represent the tested Mac Command mapping; verify actual shortcuts on another platform. The export presets keep a historical 30 fps test state and an empty target directory: explicitly set current source FPS, output location and filename before every job.

Render only the new job ID owned by this task. Do not clear other jobs. Refuse an existing output file independently of an API overwrite flag. Recheck the actual saved frame count and format rather than trusting “Complete.”

The portable layout has its former machine-specific media folder removed from the serialized layout. Its layout settings are preserved, but this sanitized copy needs an import/readback check on the destination build. Save your current layout first. Select your own media location; importing a layout must not be treated as permission to replace your workspace preferences.
