# The actual HTML/GSAP route

This runtime pins HyperFrames 0.8.150, the version used for the retained templates. Use Node 22+, npm and FFmpeg. Work in a new copy of this skill folder (or of one template or the starter), because the workflow guides and helper scripts are adjacent and the plugin folder is replaced on every update. The project can use your existing Chrome; follow the CLI's current browser instruction if none is available. Do not install a new provider or buy credits during setup.

From the copied folder:

```sh
npm ci --ignore-scripts --no-audit --no-fund
node run.mjs check --dir templates/motion-wide --strict
node run.mjs render --dir templates/motion-wide --output wide.mp4
```

Use new output names. Open the movie and verify the exact final frame. The 12-second wide and portrait templates retain the actual word/line/media reveal mechanism. Their input is clearly labeled synthetic practice. To test portrait, substitute `motion-portrait`. Customize the local HTML words, CSS palette, explicit geometry and GSAP timing. Match source media times, root duration and timeline duration.

`gentlemen-hybrid` contains a synthetic base, the real Remotion handwriting alpha export and its actual selected marker WAV. It demonstrates combining those layers in HTML; its `assets/overlay.mov` ships in the [asset bundle](../../ASSETS.md). `alpha-proof` is a short transparency fixture. ProRes alpha may require the renderer's media conversion and native-editor checking; a browser preview alone cannot certify it.

The wrapper uses the pinned local CLI and disables telemetry/automatic skill setup. It never installs automatically. All 23 installed upstream HyperFrames workflow/domain skills are included under `workflows/`, one folder each with its GUIDE.md. The embedded-captions compilers, themes, matting and layout helpers live in the sibling captions skill at `../captions/embedded/`. Read [the portable contract](workflows/hyperframes/references/portable-contract.md) before any route. Its customer permissions/profile rules govern older upstream examples.

The embedded-caption helpers accept `HYPERFRAMES_ROOT` pointing to this installed runtime. The portable adaptation also finds this folder and supports its npm CLI path, puppeteer-core and sharp. Browser-dependent helpers require your actual Chrome path; unsupported systems must supply one deliberately. Matte/transcription/voice/generation routes may download models or call providers. They are optional, not setup prerequisites. Inspect their exact command and current model/license terms first. [Optional providers](../style/tools/OPTIONAL%20PROVIDERS.md) explains the boundary.

Historical compile/QA helper scripts can regenerate their named working files. Run them only in a disposable copy with original source/media elsewhere. No helper has permission to kill unrelated browser processes, publish a project or claim a timed-out output finished.

Official references: [HyperFrames](https://hyperframes.heygen.com/), [source and license](https://github.com/heygen-com/hyperframes), [GSAP license](https://gsap.com/community/standard-license/). The bundle's original procedural sound/texture replacements are disclosed in [THIRD-PARTY](../../THIRD-PARTY.md).
