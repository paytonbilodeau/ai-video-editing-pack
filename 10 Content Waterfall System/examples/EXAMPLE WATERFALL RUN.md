# Example Waterfall Run: Controlled Fixture

The supplied example uses a neutral 24-second transcript about review receipts. It contains one source claim and two planned outputs: one 21-second short and one email draft.

## What the example proves

- `example-content-map.json` passes strict structural validation.
- The short range is within the 20 to 90 second default.
- Both outputs cite the same source claim.
- The example transcript stores real word start and end fields rather than estimated segment timing.

## What it does not prove

There is no matching real recording in the public library. The zero-filled source hash is an example value, so extraction should refuse it against any actual file. The example does not prove selection quality, crop quality, platform performance, or time saved.

Use the tests to create a temporary neutral video and prove the full local extraction path.
