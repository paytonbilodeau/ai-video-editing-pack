# Update without losing your choices

Download the exact release available to you and keep it separate from the current installation. Ask the assistant:

> Compare this new release with my installed base and customized working copy. Preserve my editing profile, originals, project files and custom changes. Prepare the update with the included bootstrap, explain any conflicting change, and test the candidate before replacing the active pack. Keep a recoverable backup and verify the result.

The assistant uses three versions:

| Version | Purpose |
|---|---|
| Original supplied base | Shows what the previous release contained. Its hashes are retained in `.vibe-editor/bases/`. |
| Your working copy | Contains your changes and additions. Your active profile stays outside it. |
| New supplied release | Contains the reviewed upstream improvements. |

An unchanged working file can receive its upstream update. A custom file stays as it is when upstream did not change it. If both changed the same file, the tool saves all three versions and holds that conflict for review. It does not guess which preference should win.

## Assistant commands

Run from the current release's reviewed bootstrap. Substitute actual paths; do not paste the labels unchanged.

```sh
python3 "NEW BUNDLE/Payton Editing System/setup/bootstrap.py" plan-update --source "NEW BUNDLE" --workspace "YOUR EDITING WORKSPACE" --output "NEW REVIEW FOLDER"
```

Stop active edits, renders and dependency installations before promoting an update. Read `comparison.json`, inspect the candidate and run the relevant tests. Keep the active pack unchanged until this review is complete. If there are conflicts, edit the candidate to the accepted result and save a resolution file containing every conflict path, its decision and the exact reviewed file hash. Example:

```json
{
  "some/module.md": {
    "decision": "merged",
    "sha256": "SHA256_OF_THE_REVIEWED_CANDIDATE_FILE"
  }
}
```

Decisions are `keep-custom`, `take-upstream`, `merged` or `delete`. A deletion uses `"sha256": null`; the corresponding candidate file must be absent. This file records a considered decision, not permission to discard an unexplained customization. No resolution file is needed when there are no conflicts.

```sh
python3 "NEW BUNDLE/Payton Editing System/setup/bootstrap.py" apply-update --source "NEW BUNDLE" --workspace "YOUR EDITING WORKSPACE" --plan "NEW REVIEW FOLDER" --resolutions "REVIEWED RESOLUTIONS.json"
```

Omit `--resolutions` when there are no conflicts. Promotion rechecks the old base, the current working bytes, new release hashes and reviewed candidate. A changed input stops the update. Existing runtime folders such as node_modules and virtual environments, and local account configuration such as .env, are kept separately from the distributable comparison. Their contents are not written into the comparison report or candidate. Promotion copies them locally without following their symlinks and leaves the complete previous copy in the backup. Do not run dependency installs or edit those files during this copy. This can require space for another installed runtime.

It preserves the old working copy and state under `.vibe-editor/backups/`, keeps the customer profile untouched, and records the new base separately.

After promotion, repeat the relevant short test and verify the active profile and skill paths. If a new bridge conflicts with an existing skill, the existing file is preserved and reported. The update receipt alone does not prove the editor, renderer or profile choices still behave correctly.

## Restore

The update receipt names the exact backup. Close work using the pack, preserve the failed/current candidate in a separate folder, and restore the backed-up `Vibe Editor Pack` and `state.json` together. The customer profile is outside both and should remain unchanged. Review any newly added skill bridges separately; do not delete user-created skills. Reopen the project and run the short affected test before calling the restore successful.
