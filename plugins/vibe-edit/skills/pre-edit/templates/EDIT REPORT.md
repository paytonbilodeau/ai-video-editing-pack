# Video Pre-Edit Report

- **Tool version:** [version]
- **Reported:** [UTC time]
- **Source file:** [basename only]
- **Planned output file:** [basename only]
- **Approved plan file:** [basename created by or consumed for this run]
- **Render state:** [dry-run plan only or rendered with video, audio, and duration verified]

## Duration

- **Source:** [time from original]
- **Planned output:** [time]
- **Removed:** [time and percent]

## Settings

- **Silence threshold:** [dB]
- **Minimum silence:** [seconds]
- **Speech padding:** [milliseconds per side]
- **Silence cuts enabled:** [true or false]
- **User-approved exact ranges:** [count]
- **Local audio enhancement:** [true or false]
- **Spoken-marker language:** [language]

## Cuts

| Start | End | Duration | Reason | Review |
|---:|---:|---:|---|---|
| [original-source time] | [time] | [time] | [detected silence, spoken marker, or user-approved range] | [standard or check] |

## Protected ranges

| Start | End | Reason |
|---:|---:|---|
| [original-source time] | [time] | [user-protected; no cuts allowed] |

## Spoken marker analysis

- **Enabled:** [true or false]
- **Restart markers found:** [count]
- **Restart markers skipped for protected conflict:** [count]
- **Full restart markers found:** [count]
- **Transcript fallback:** [none or reason marker cuts were disabled]

## Local audio

[Applied filters, fixed gain, limiter ceiling, after-measurement, or none.]

## Verification

- **Scope:** [video stream, audio stream, and duration]
- **Video present:** [true or false]
- **Audio present:** [true or false]
- **Subtitle streams:** [zero]
- **Chapters:** [zero]
- **Rendered duration:** [seconds]
- **Expected duration:** [seconds]
- **Duration matches:** [true or false]

## Warnings and review

[Long cut, high removal, transcript fallback, stripped source metadata, or no other threshold crossed.]

- All timestamps refer to the original source.
- Review every spoken-marker cut and every long cut.
- Keep the source until the review checklist passes.
