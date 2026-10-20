# Example: Synthetic Video Pre-Edit Report

This filled example came from the included six-second synthetic fixture. It contains no client media or transcript.

- Tool version: 1.0.0
- Source file: `source.mp4`
- Planned output file: `output.mp4`
- Approved plan file: `output_plan.json`
- Render state: rendered; video stream, audio stream, and duration verified

## Duration

- Source: 0:06.000
- Planned output: 0:03.600
- Removed: 0:02.400 (40.0%)

## Settings

- silence threshold: -40 dB
- minimum silence: 0.8 seconds
- speech padding: 150 ms per side
- silence cuts enabled: True
- user-approved exact ranges: 0
- local audio enhancement: True
- spoken-marker language: en
- dry run: False

## Cuts

| Start | End | Duration | Reason | Review |
|---:|---:|---:|---|---|
| 0:01.650 | 0:02.850 | 0:01.200 | detected silence | standard |
| 0:04.650 | 0:05.850 | 0:01.200 | detected silence | standard |

## Protected ranges

No protected ranges were supplied.

## Spoken marker analysis

- enabled: False
- restart phrase: cut cut
- restart markers found: 0
- restart markers skipped for protected conflict: 0
- full restart markers found: 0
- transcript fallback: none

## Local audio

- applied: True
- target_lufs: -16.0
- limiter_ceiling_dbfs: -1.5
- true_peak_compliance: not certified; review or meter for delivery
- measured_before_lufs: -23.76
- requested_gain_db: 7.76
- applied_gain_db: 7.76
- gain_was_limited: False
- measured_after_lufs: -15.8
- method: high-pass, light EQ, compression, fixed measured gain, ceiling limiter

## Verification

- scope: `video stream, audio stream, and duration`
- has_video: True
- has_audio: True
- subtitle_streams: `0`
- chapters: `0`
- duration_seconds: 3.626
- expected_duration_seconds: 3.6
- duration_matches: True

## Warnings and review

- Container and stream metadata are not preserved; the encoder may add new technical tags.
- All timestamps refer to the original source.
- Review every spoken-marker cut and every long cut before replacing a manual edit.
- Keep the source file until the new output passes the review checklist.

The source SHA-256 was identical before and after the smoke render. This example validates the maintained macOS test fixture, not an individual user's computer or footage.
