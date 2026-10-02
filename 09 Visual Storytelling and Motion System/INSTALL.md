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
6. Render to a new output path. Do not overwrite source assets.

The first render may download a separate Chrome Headless Shell binary and therefore needs network access and additional disk space. Review the displayed download before continuing. Later renders may reuse a local cache.

The package pins exact versions for repeatability. A pinned version is not a claim that it is the newest. Review current official release, security, and license information before updating it.

For transparent overlays, use a codec and pixel format that support alpha, confirm alpha with a media probe, and remove audio. Keep a standard opaque fallback when the final editor does not support alpha.

The included standard render command is muted. A verified release test produced one five-second video stream and no audio stream. This proves the neutral fixture on the tested release environment, not every user operating system or editor.
