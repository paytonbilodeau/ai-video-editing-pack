# Find music and sound that you can actually use

Keep supplied or already approved music and the style's cleared sound palette.
For new effects, ambience or music, start with [Openverse](https://openverse.org).
Search for the sound's job: a soft interface click, an airy transition or a
restrained underscore. Audition candidates under the real dialogue.

Openverse indexes other providers. Its search metadata is a lead, not proof of
ownership or permission. Visit the matching source page and check the exact
track's terms. Prefer verified CC0. CC BY can work when the required credit
appears in the final description or credits. Keep title, creator, source URL,
license version/link, existing notices and changes such as trimming or looping.
Exclude NC and ND from the usual commercial-video search. Assess ShareAlike
obligations before using it, or choose a simpler candidate.

The optional API search uses no bundled credential:

```sh
curl --fail --silent --show-error --get \
  --data-urlencode 'q=soft whoosh' \
  --data-urlencode 'license=cc0' \
  --data-urlencode 'page_size=5' \
  --output openverse-search.json 'https://api.openverse.org/v1/audio/'
```

Use a fresh output path. Read the response before choosing a provider URL.
Check rate-limit headers and honor Retry-After; do not bulk-download or work
around limits. If the API is unavailable, use the website or a cleared local
asset. Do not silently switch to paid or generated audio. Any tool distributing
Openverse-powered search must identify that use and state it is not endorsed
or certified by Openverse.

Record source URL, retrieval date, license evidence, local hash and whether the
file is a preview or original. A WAV converted from MP3 does not restore detail.
Probe and decode the file, then listen for artifacts and fit under speech.
Freeze selected audio locally before rendering. Missing or conflicting source
terms leave an asset unselected; an API response alone does not clear it.

Place the audible attack at the actual visual action, preserve clean tails,
keep music below intelligible dialogue and leave quiet space. This guide does
not authorize a sound pass during cuts-only work or alter approved audio.

Sources: [license verification](https://docs.openverse.org/api/reference/made_with_ov.html),
[API terms](https://docs.openverse.org/terms_of_service.html),
[CC BY](https://creativecommons.org/licenses/by/4.0/),
[music and video](https://creativecommons.org/legalmusicforvideos/).
