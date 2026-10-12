# Install and Test

Planning needs only a current Node.js installation. Rendering also needs the third-party packages declared in `starter/package.json`.

## Planning test

From this system folder:

```bash
node --test tests/*.test.mjs
node tools/motion_plan.mjs examples/example-beat-map.json
```

## Optional Remotion starter

1. Read `THIRD-PARTY.md` and confirm your Remotion license eligibility.
2. Make a working copy of `starter` under `_MY WORK`.
3. From that copy, run `npm ci`.
4. Run `npm test`.
5. Run `npm run studio` and inspect the neutral composition.
6. Run `npm run render` for a muted MP4 or `npm run render:overlay` for a transparent ProRes 4444 MOV. Inspect the result and keep its editable source.

The included render helper uses an installed Chrome/Chromium in a separate rendering process when one is found. Otherwise Remotion may download Chrome Headless Shell on first use. It does not open your personal browser profile. The assistant can set `REMOTION_BROWSER_EXECUTABLE` for a custom installed location. Explain any required download before continuing.

The package pins exact versions for repeatability. A pinned version is not a claim that it is the newest. Review current official release, security, and license information before updating it.

For transparent overlays, use a codec and pixel format that support alpha, confirm alpha with a media probe, and remove audio. Keep a standard opaque fallback when the final editor does not support alpha.

The included standard render command is muted. A verified release test produced one five-second video stream and no audio stream. This proves the neutral fixture on the tested release environment, not every user operating system or editor.

## Optional HyperFrames starter

Copy `hyperframes-starter` into a private working project. Its README explains
the Node 22+, FFmpeg and browser requirements, telemetry choice, locked install,
checks, and opaque/transparent renders. Use the same beat map and review process
for either runtime. Do not install both merely to finish one graphic.

## JavaScript route

The pack's [JavaScript animation skill](../AI%20Video%20Editing%20Pack/skills/javascript-animation/SKILL.md)
provides a third route, including a Remotion adapter. It can share rendered
layers with these starters. Preserve the source and match frame rates.
