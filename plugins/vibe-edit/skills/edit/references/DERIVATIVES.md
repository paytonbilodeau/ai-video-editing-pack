# Turn the approved recording into useful clips

Do this only when derivatives are part of the request. Begin with the approved clean picture/dialogue master. Use the pre-Auphonic version for a new unprocessed edit, then the chosen final audio route once. A verified already-finished-audio reuse branch is available in [protected audio](PROTECTED%20AUDIO%20AND%20REUSE.md); never enhance it twice.

Read the complete transcript and inspect the source around each candidate. Select a complete promise, necessary condition, explanation and payoff for the actual audience. Consider hook strength, self-containment, quotability and audience fit. These are editorial judgments, not measured predictions of views. Choose only as many strong clips as the source and brief support. A longer complete explanation is more useful than an arbitrary short duration that removes its condition.

A planning-only request produces the proposed source ranges, exact opening words, title, rationale and layout. A request to select and edit already authorizes that work; do not add a repeated approval question. Publication retains its separate authorization.

## Keep one content map

Use the customer's exact source file and source-relative times. A contiguous extraction row for `extract_short_clips.py` is:

```json
[
  {"start": 12.2, "end": 42.8, "title": "An accurate title from the recording", "hook": "The exact opening words", "caption": "A concise title-style post caption"}
]
```

The numbers above illustrate the schema and must be replaced by reviewed timings. For landscape extraction, the same rows can include a unique plain `id`, or live under a `mids` array. Disjoint approved ranges require the editable cut-list exporter or a reviewed native assembly; a single bounding range could restore rejected speech.

`waterfall_validate.py` checks a complete content map against the actual source. Its inherited general mode applies the original long-form/chapters/mids/shorts contract; `--mode more` supports the frame-based `clips[]` contract without the generic five-minute landscape minimum. Read `--help` and the returned issues. Those mode names describe schemas, not access to Payton's accounts, and validation is not creative approval or publication.

## Use only the needed tool

```sh
python3 tools/extract_mid_clips.py project/approved-master.mp4 project/new-landscape-clips --manifest project/mids.json --software
python3 tools/extract_short_clips.py project/approved-master.mp4 project/new-portrait-clips --manifest project/shorts.json --static-crop
python3 tools/waterfall_transcribe.py --emit-clip-vtt project/content-map.json project/transcript
```

The static short route is a **center crop**. Use it only after confirming the complete shot fits. Use Resolve or the motion component's source-specific renderer for an off-center speaker, screen demonstration or paired comparison. Tracking remains conditional and needs its own full movement review. A 4K file made from a small source does not restore detail.

The transcript command creates a rebased VTT plus a real `*.words.json` for each reviewed contiguous clip. It preserves source word timings, refuses a cut through a timed word and refuses existing sidecars. Supply that word JSON to the strict RSVP renderer; a sentence VTT is not equivalent to measured word timing. Word data still needs checking against actual speech. The optional local transcription route may download its model if absent, so use an existing route or make that download an explicit setup choice.

For a discovery clip, start with a short truthful text hook and no sales CTA unless the brief chooses otherwise. Keep the hook only while it provides useful context and does not hide the demonstration. Posting copy is a concise title line; captions inside the video carry the spoken words. A supposed universal retention trick or numerical virality score is not evidence.

Render one clip at a time. Inspect the full movement and final word, then check dimensions, source FPS, decode, encoded sound and exact source ranges. For a styling-only revision, verify the entire unchanged audio payload against the independent same-length approved clip. State remaining manual steps for the actual editor.

Optional written derivatives reuse the same verified recording: one useful point per post, a carousel with one idea per slide, or an email connecting the actual experience to one practical action. Do not invent personal stories, results or quotes. Choose platform limits and publication cadence from the customer's current brief; Payton's private accounts, schedules and distribution automations are not inherited.
