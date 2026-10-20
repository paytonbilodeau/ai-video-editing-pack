# One disposable test, then your own edit

The `tools/fixtures` JSON files are synthetic contract examples. The ready fixture includes a fictional listening record to exercise schema logic; it is not evidence that anyone heard a real video. The not-ready fixture should fail because its hook/order, defect and review claims do not support completion.

Run the unit suite for exact-source occupancy, source transcript preservation, audio restoration, final-timeline timing and API boundary checks. A successful suite establishes those contracts only. It does not create a native project, train a model or establish your editor's compatibility.

For a real route test, use a copy of a short recording you may edit. Ask for two editable spans that preserve a full sentence and one useful click/action. Save, reopen, export and inspect the actual result. Check source hashes, exact expected frames, linked audio, original preservation and the complete word/action. Record what was tested and any manual step. Stop after that operation is established; no need to benchmark every optional tool before the first edit.

## Recreate the disposable media test

From the editing folder, run `python3 examples/make_fixture.py YOUR_NEW_TEST_FOLDER` with your installed FFmpeg. It refuses an existing folder. This creates a three-second synthetic picture, tone and click, plus original and attenuated WAVs, a protected-range manifest and illustrative word cues. These cues are authored test data, not measured human speech.

Use the clip for a local import/save/reopen/export test or the included tools. The ranges protect the click from frame30 to45 at30fps. Compare exact decoded protected WAV samples before lossy encoding; compare final encoded timing and levels separately. Delete only this disposable folder when no longer needed. No app settings, provider accounts or personal files are changed by the generator.
