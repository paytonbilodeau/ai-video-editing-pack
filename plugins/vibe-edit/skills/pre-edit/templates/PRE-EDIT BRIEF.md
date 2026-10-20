# Pre-Edit Brief

The assistant fills this from the request and existing profile. Ask only about missing choices.

## Working agreement

- **Working pace:** [careful, balanced or handle-it-for-me]
- **Authorized scope:** [user request reference and allowed actions]
- **Requested checkpoints:** [named stages or none]

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

## Plan review and render authority

- **Dry-run report reviewed:** [yes or no]
- **Generated plan reviewed:** [yes or no and plan filename]
- **Render authority:** [existing user request or requested checkpoint approval]
- **Exact render command:** [same source and output with --from-plan PLAN]
- **Reviewer:** [AI internal check or human review, with actual evidence]
