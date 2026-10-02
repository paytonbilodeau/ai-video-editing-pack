# Pre-Edit Brief

## Source

- **Copied source file:** [named file inside the approved working folder]
- **Flattened SDR with one video and one audio track:** [yes or export a working copy]
- **New MP4 output:** [different filename]
- **New report:** [different .md filename]
- **Final editor or destination:** [tool or platform]

## Content

- **Language:** [language]
- **Recording type:** [talking head, tutorial, interview, or other]
- **Played media or music:** [yes or no, with ranges if known]
- **Sections to protect:** [ranges or description]

## Cut rules

- **Shorten quiet pauses:** [yes, or no with --keep-silence]
- **Silence threshold:** [-40 dB default]
- **Minimum detected silence:** [0.8 seconds default]
- **Speech padding per side:** [150 milliseconds default]
- **Exact approved cuts:** [original-source START-END ranges or none]
- **Exact restart marker:** [phrase or none; off by default]
- **Marker source:** [local Whisper, timed-word JSON, or none]
- **Full restart marker:** [phrase or none; separate confirmation required]
- **Remove unmarked retakes:** [no by default]
- **Remove fillers:** [no by default]

## Audio

- **Apply local speech cleanup:** [yes or no]
- **Practical starting target:** [-16 LUFS and -1.5 dBFS limiter ceiling]
- **Delivery specification needing a final meter:** [none or specification]

## Review boundary

- **Review every spoken-marker cut:** [yes]
- **Review every cut over 15 seconds:** [yes]
- **Review if total removal exceeds 45 percent:** [yes]
- **Stop condition:** [clipped speech, broken transcript, protected-range conflict, unexpected output, or other]

## Dry-run plan

[Exact command without --overwrite.]

## Render approval

- **Dry-run report reviewed:** [yes or no]
- **Generated plan reviewed:** [yes or no and plan filename]
- **Exact render command approved:** [same source and output with --from-plan PLAN]
