# One-second portrait-layout test

This is a **synthetic layout fixture, with synthetic tone**, not spoken footage or a transcript. `source.mp4` ships in the optional asset bundle (ASSETS.md at the plugin root). Copy this entire project to a new folder, install the Flow runtime from the remotion skill, then run the shorts skill's `tools/render_short.py` with `/absolute/path/to/new-project demo`. The shorts, edit and remotion skills stay together inside the installed plugin.

The actual production compositor reads these three JSON files. For your own source, use its exact frame rate, measured crops, source frame ranges, reviewed hook and timed phrase captions. The frame source is full landscape; the central608px crop becomes2160×3840. The example carries one second of synthetic tone so the audio path can be checked. It is not a recommended production composition.

This route re-encodes the source audio excerpt to AAC without an enhancement chain, then copies that audio into the final. A matching extracted-audio check is not proof that AAC matches source PCM exactly. The final review still needs actual words, display boundaries and listening.
