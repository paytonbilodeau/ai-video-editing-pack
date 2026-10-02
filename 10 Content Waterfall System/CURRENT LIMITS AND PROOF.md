# Content Waterfall Current Limits and Proof

## What is proven locally

- Strict schema, ID, range, duration, claim-reference, approval, and relative-path validation.
- Exact word timing is preserved and rebased for clip captions instead of estimated from segment length.
- Extraction writes into a new output directory, refuses replacement, verifies the source hash before and after, and records relative output labels.
- A synthetic end-to-end fixture creates neutral media, extracts one short, probes duration, creates captions, and verifies source immutability.

## What is not yet proven

The optional approved-source audio record is a manual workflow policy. The included tools do not enforce its approval scope or perform full decode, complete-word, measured-alignment or audio-payload comparisons. Record those checks separately; neither user acceptance nor a waveform is a claim that the assistant listened.

The complete system has not processed and passed human review on one real recording of at least 30 minutes. Selection quality, real transcript quality, real crop quality, full output usefulness, operating-system coverage, and actual time or cost improvement remain unproven.

## Next production proof gate

1. Use one rights-cleared recording of at least 30 minutes.
2. Create the real transcript, claim ledger, and strict content map.
3. Obtain separate human approval of the whole map.
4. Render at least one mid-length clip and two shorts.
5. Create exact captions and at least one email and two text drafts.
6. Review A/V sync, crop, readability, source fidelity, privacy, and rights.
7. Verify the source hash stayed unchanged and receipts contain no absolute paths.
8. Record setup, run, review, rework, disk use, and actual cost without making a broader savings claim.
9. Save the receipts and update this file only after the evidence is reviewed.

The system is ready for careful public use now, but these unproven points remain limits until the evidence above exists.
