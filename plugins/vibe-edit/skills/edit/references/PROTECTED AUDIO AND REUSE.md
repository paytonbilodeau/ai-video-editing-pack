# Protected demonstration sound and finished-audio reuse

A played example may deliberately contain original, loud, quiet, muted or comparison states. Mark the exact half-open frame ranges on the locked output timeline before processing. A visible demo under normal narration is not automatically exempt from narration treatment.

For the chosen single-provider route, process normal narration once, then restore only manifest-listed PCM from the locked pre-provider master with `protect_demo_audio.py`. It requires matching rate/channels and aligned duration, uses integer frame boundaries at rational FPS and places fades outside protected intervals. It verifies identical decoded float32 samples inside the protected spans. Keep both original and processed sources.

That exact PCM claim applies before lossy delivery encoding. After AAC remux, verify timing, channel behavior, protected-level relationships and correlation as appropriate; do not demand identical lossy bytes or claim PCM identity there. Normal narration outside the protected/fade spans must still come from the processed result. Do not send the restored program through the provider again.

If comparable listening level is explicitly wanted, adjust a separate audition copy or documented bounded gain without erasing the intended loud/quiet/muted difference. Distinguish exact restoration from intentionally changed gain. A test teaching a volume change must preserve that contrast, including short previews.

## Reuse before rerunning

For a picture-only change, compare source/finished audio identity, duration, start time and payload; copy compatible accepted audio and verify the result. For derivatives, use an exact reuse map only when the audio segments' lineage proves a single prior pass and the new boundaries remain valid. Rebuild from unprocessed sources when speech/timing or treatment requires a new pass. A filename saying “final” or “quiet” is not lineage evidence.

Keep graphics and their sounds on separate named tracks. A clean master removes added overlays and their dedicated sound effects while preserving source footage, recorded demonstrations, dialogue, grade and timing. Its mix can differ from the decorated master; different AAC hashes alone do not prove speech changed.
