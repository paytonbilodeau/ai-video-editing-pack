# Third-Party Notes

## Remotion

The optional starter uses Remotion `4.0.535`. Remotion is source-available software with its own license eligibility rules. It is not included as source or binaries in this library. The user installs it and confirms current eligibility at:

- https://www.remotion.dev/docs/license/faq
- https://github.com/remotion-dev/remotion/blob/main/LICENSE.md

Do not resell Remotion itself, copy its source into a template package, or use this starter to avoid the license that applies to your organization or product.

## React and Node.js

The starter uses React `18.3.1`, React DOM `18.3.1`, TypeScript `5.5.4`, and the user's Node.js runtime. These packages are installed separately from their official registries and keep their own licenses.

## Browser used for rendering

Remotion may download Chrome Headless Shell on the first render. That browser binary is not included in this library. Its version, size, download source, and terms are controlled by the third-party render tool and can change. The user reviews the download and keeps enough disk space before rendering.

## Assets

No font, logo, footage, music, model weight, generated asset, or third-party template is bundled. Supply assets you are allowed to use and record their rights in `ASSET LEDGER.md`.

Third-party terms and security information can change. Recheck official sources before a release or dependency update.

## Additional optional runtime

The original `hyperframes-starter` source is supplied with this system. It
downloads HyperFrames 0.8.150 (Apache-2.0) and GSAP 3.15.0 through its package
lock when installed. Their code is not vendored here. Read the current
[HyperFrames license](https://github.com/heygen-com/hyperframes/blob/main/LICENSE)
and [GSAP licensing terms](https://gsap.com/community/standard-license/) before use.
The separate Remotion starter now pins Remotion 4.0.535; its license eligibility
continues to apply. Hosted services and generated assets remain separate choices.
