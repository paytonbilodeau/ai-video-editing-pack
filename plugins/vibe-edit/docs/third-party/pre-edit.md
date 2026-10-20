# Third-Party and Dependency Notes

The included Python files use the Python standard library. They do not contain copied FFmpeg, Whisper, or PyTorch source code.

## Core local dependency

### FFmpeg and ffprobe

- Purpose: inspect media, detect quiet pauses, render cuts, encode MP4, and process audio.
- Project: [ffmpeg.org](https://ffmpeg.org/)
- License: FFmpeg builds may be LGPL or GPL depending on how that build was compiled. Review the license information supplied with the installed build and the [FFmpeg legal page](https://ffmpeg.org/legal.html).
- Data path: local process. The included tool does not upload the media.

### x264 through FFmpeg

- Purpose: the renderer requests FFmpeg's `libx264` encoder for H.264 video.
- Project: [VideoLAN x264](https://images.videolan.org/developers/x264.html)
- License: x264 requires use under the GNU GPL or a commercial x264 license. FFmpeg documents that enabling GPL components such as `libx264` makes that FFmpeg build GPL. Review the license supplied with the installed build and get legal advice for a commercial distribution decision.
- Distribution boundary: this library calls an FFmpeg binary the user installs. It does not contain, link, or redistribute FFmpeg or x264 binaries or source.

## Optional spoken-marker dependencies

### OpenAI Whisper

- Purpose: create local word timestamps for exact spoken-marker detection.
- Project: [github.com/openai/whisper](https://github.com/openai/whisper)
- License: review the project's included MIT license and the terms accompanying the selected model.
- Data path: the selected model downloads on first use; transcription runs locally through the installed package.

### PyTorch

- Purpose: local runtime used by OpenAI Whisper.
- Project: [pytorch.org](https://pytorch.org/)
- License: review the project's BSD-style license and bundled third-party notices.

The marker dependencies are large and optional. Do not install them or download a model without the computer owner's approval. A timed-word JSON file can be used instead.

## Not included

- no paid audio service;
- no cloud transcription API;
- no API key or account connection;
- no `torch.hub` download or unreviewed remote code loader;
- no hardware-only encoder requirement;
- no editor plug-in, LUT, Final Cut XML, or proprietary project format.

Check the licenses and terms that apply to the user's source media, fonts, music, clips, final editor, and distribution destination. This file describes dependencies; it is not legal advice.
