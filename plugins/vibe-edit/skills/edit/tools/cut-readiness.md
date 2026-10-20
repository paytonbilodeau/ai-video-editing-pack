# Cut-readiness evidence check

`cut_readiness.py` checks a JSON evidence manifest before a cut is described as ready. Use it inside the Resolve cut-review procedure. It does not connect to Resolve, change a timeline, listen to media, or alter the edit.

## Run

```bash
python3 cut_readiness.py fixtures/ready-retime-stale-marker.json --output result.json
python3 -m unittest discover -s tests -v
```

Exit code `0` means the manifest's `release_claim.ready: true` is supported by the declared structural evidence, an encoded-render true-peak measurement, and a declared human listening record. Exit code `1` means the claim is absent, pending, malformed, or blocked. The helper cannot verify that listening actually occurred.

## Manifest contract

- `source_id`: schema v1 requires exactly one explicit source. Every clip must carry that same `source_id`; multi-source timelines fail closed because frame numbers can collide.
- `timeline.clips[]`: `source_id`, `timeline_start_frame`, `duration_frames`, `left_offset`, and `speed_percentage` are required. Exact half-open source occupancy is `round(left_offset × speed_factor)` through that start plus `round(duration_frames × speed_factor)`. Optional reported source starts and ends are diagnostic only.
- `required_hook.expected_start_frame`: exact timeline frame where the hook must begin. An intact hook displaced after other footage fails.
- `required_hook.ordered_blocks[]`: every declared half-open source span must be fully occupied and appear in the declared timeline order. Split fragments inside each block must also preserve source order without duplication.
- `known_speech_defects[]`: each defect is `resolved` or `unresolved`. A source-removal resolution needs an absent source core and evidence references. A ready claim fails if any defect is unresolved.
- `diagnostic_markers[]`: retained marker objects are history only. They never establish current source occupancy or defect state.
- `dead_air_review`: supplies project-specific detector thresholds, context evidence, and every reviewed candidate. `intra_clip` and `between_clips` candidates follow the same rule: each needs `retain` or `repair`, a concrete reason, and evidence references. A planned repair cannot support a ready claim.
- `review_audio`: finite `gain_db`, `measured_true_peak_dbtp`, `peak_ceiling_dbtp`, evidence references, and `measurement_stage`. The ceiling must be at or below 0 dBTP, and measured true peak must be at or below that ceiling; the result reports `headroom_db = peak_ceiling_dbtp - measured_true_peak_dbtp`. `source_prediction` can record pending work; only `encoded_render` supports final readiness. Gain has no fixed target, and the helper imposes no LUFS target.
- `perceptual_review`: only `human_listening` or `continuous_av_review` with a nonempty reviewer and evidence references can support `status: passed`. These values must document an actual heard and seen review. A playback command, waveform, ASR, still frames, and structural checks cannot substitute for review.

The helper contains no built-in silence length, trim count, pacing target, defect quota, gain target, or loudness target. The manifest owns thresholds and context. The checker tests whether those inputs and their dispositions are present and internally consistent. It does not require a before/after improvement metric, since that would reward changes for their own sake.

## Fixtures and limits

`ready-retime-stale-marker.json` proves that a 200% clip's exact `[140, 150)` occupancy wins over a rounded reported `[140, 149)` span, that a stale marker at source frame 151 does not imply retained speech, and that a quiet source can safely carry a measured +12 dB gain when its encoded true peak remains below the declared ceiling. `not-ready-unfamiliar.json` combines a reordered hook, unresolved speech, unexplained intra-clip dead air, source-prediction-only audio, and waveform/ASR-only acceptance. `split-hook-reversed.json` covers a single hook block whose two source halves are both present but reversed.

This is a schema and consistency checker. It does not detect silence, judge whether a reason is editorially wise, authenticate evidence references, inspect media, or establish perceptual quality.
