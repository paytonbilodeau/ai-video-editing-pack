# Upstream and modifications

Source: [cth9191/animate](https://github.com/cth9191/animate), commit
[`7e5eb56feb2dd573f890e1b7b34748af43d58263`](https://github.com/cth9191/animate/tree/7e5eb56feb2dd573f890e1b7b34748af43d58263),
retrieved October 6, 2026. Upstream is MIT licensed; its copyright and grant are
preserved verbatim in [LICENSE.upstream](LICENSE.upstream).

The five `kit/` modules, seven public `styles/` folders and `templates/` derive
from that source. The dark isometric demo was omitted because it reads sibling
source paths. The default isometric demo remains included. The style index was
adapted to the packaged commands. `tools/beats.mjs` preserves the upstream
analysis with bounded inputs, local-file checks and failure propagation.

The builder was adapted to constrain reads, reject escaping symlinks, validate
metadata, escape injected JSON, await local assets, and carry a content security
policy into the built HTML. The new CLI uses an
isolated lockfile-pinned Playwright runtime, fail-closed technical checks,
PNG/H.264/ProRes export and a Remotion frame handshake. Upstream's global-package
fallback, remote capture, paid voice generation, broad file search and optional
account/provider integrations are not included. The guide provides local
voice-timing and reference-review routes. Review outputs distinguish technical
checks from visual and listening acceptance.

Playwright is pinned in `package-lock.json`; its Apache-2.0 license and bundled
third-party notices are installed with the runtime. Chromium is downloaded by
Playwright setup with its own notices. FFmpeg is separately installed by the
user and retains the license of that installation. Remotion is optional and
has separate licensing; the adapter does not grant a Remotion license.
