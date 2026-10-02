# Content Map Approval Record

- **Map label and hash:** [value]
- **Source label and hash:** [value]
- **Reviewer:** [person]
- **Reviewed:** [YYYY-MM-DD]
- **Approved output IDs:** [IDs]
- **Rejected output IDs and reasons:** [IDs and reasons]
- **Claim corrections:** [changes or none]
- **Privacy and rights check:** [pass or fail]
- **Extraction approval:** [approved or not approved]

Approval covers only the named map and output IDs. A changed map needs a new review.

## Optional approved-source audio acceptance

Use this only when the user has approved the finished main and authorized continued work on that basis. These are manual review notes, not new required JSON fields; existing approved maps and completed records remain compatible.

- **Approved main label and SHA-256:** [value]
- **User approval and scope:** [instruction reference and authorized downstream work]
- **Audio-presence evidence:** [audio stream, visible waveform or decoded audio; receipt reference]
- **Listening actually performed:** [yes with reviewer and evidence, or no]
- **Processed master and derivative receipts:** [each output ID/hash; full audio/video decode, audio presence, expected duration/frame count, measured alignment and complete-word boundary evidence, or pending]
- **Audio preservation for picture-only revisions:** [independent same-length reference and copied payload comparison when applicable, or justified not applicable]

This records acceptance of the source. It does not approve an unnamed output, excuse a failed technical check, certify unheard sound quality, or authorize publication.
