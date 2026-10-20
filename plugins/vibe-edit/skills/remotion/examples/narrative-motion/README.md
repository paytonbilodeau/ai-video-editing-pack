# Try Narrative Motion

Watch [the eight-second example](../../../../ASSETS.md#preview-mp4). The same note moves and becomes
a short summary. Its timing is invented for this silent fixture; it is not
measured narration or a real publication.

Open `flow/src/narrative/Example.tsx` for the editable scene and
`flow/src/narrative/primitives.tsx` for the reusable code. From a separate copy
of the motion `flow` folder, use its existing dependency setup, then run:

```sh
npx remotion render src/index.ts NarrativeMotion narrative-motion.mp4 --codec h264
```

Change the two note phrases while keeping their meaning connected. Check the
middle of the move, the replacement text and the final reading hold. A longer
phrase may need a different composition. For a real edit, replace the invented
times with that edit's actual phrase cues and review it with audio.

The example proves only its recorded render and deterministic frame checks.
It contains no reference footage, account data or third-party screenshots.
