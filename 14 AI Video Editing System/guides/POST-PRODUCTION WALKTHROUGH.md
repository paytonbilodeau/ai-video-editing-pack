# Post-Production Walkthrough: One Clip to a Finished Edit

This walkthrough describes the AI's work after a video is supplied. Use a
short clip or a full recording as you prefer. Setup itself needs no footage.
The default is a complete requested edit with internal checks, an editable
project, export and report. Pause between stages only when checkpoints were
requested or a real blocker needs the person's decision.
The [fictional example](../examples/EXAMPLE%20EDITING%20RUN.md) shows what a filled-in run looks like.

## 1. Set up only the route you need

Fill in the [project brief](../templates/PROJECT%20BRIEF.md) with the exact source,
audience, output shape, protected words or demonstrations, and the editing stage
you want. Follow [INSTALL](../INSTALL.md) and save the read-only setup checker
result in the [tool setup record](../templates/TOOL%20SETUP.md). These files are
instructions, templates and a prerequisite checker, not a one-click editor.

If you want the assistant to control DaVinci Resolve, follow the
[Resolve and MCP guide](RESOLVE%20AND%20MCP.md). First prove a read-only
connection to your installed edition. Then use copied media in a disposable
project to prove import, one reversible timeline change, save, export and reopen.
The documented native route was inspected on Resolve Studio 21.1 for macOS;
your editor, edition and computer need their own test. If the connection is
unavailable, you can make the same edit manually with the brief and review
records. A listed tool or passing setup checker does not mean the assistant
has edited a frame.

## 2. Find the story and make the clean cut

Transcribe the source, then play the opening, ending, failed takes and doubtful
words. Pick the best *complete* take for each thought. Remove the agreed mistakes
and dead time, while keeping full words, useful breaths and the time needed to
see a demonstration. Save a version before fine trimming. Review every join in
the rebuilt timeline, including the outgoing word and the incoming one together.
Use [CUT REVIEW](../templates/CUT%20REVIEW.md) to record the exact source and
timeline version, decisions and unresolved ranges. A transcript or silence
detector can point you to a possible cut; playback decides whether it works.

## 3. Finish sound and picture before graphics

Listen to the entire clean cut. Check that dialogue is centered as intended,
clear across recording changes and in sync. Compare any noise or echo treatment
with the original at similar listening volume. Match exposure, white balance
and skin between shots before adding a shared look. Keep these changes editable.
Export a clean review copy with the cuts, sound, color and original recorded
visuals. Check that exact file and record any unresolved issues. Save this timeline
version before adding any requested graphics.

## 4. Add graphics when the brief calls for them

Use an authorized reference and the [style brief](../templates/STYLE%20BRIEF.md)
to describe what you observed, what you want to make, and when it should appear.
Put requested titles or annotations on separate tracks. Skip this stage
when the recording already explains the point and no graphics are requested. Check that it becomes
readable when its spoken point arrives, stays long enough to read, and never
covers the action the viewer needs to see. Native Resolve titles are enough for
this first test. If the shot needs more, follow [motion tool setup](MOTION%20TOOL%20SETUP.md)
for **one** chosen Remotion or Hyperframes route and test its render in the editor.
Review the actual composite, including sound, over the moving footage.

## 5. Deliver the exact reviewed version

Complete [FINISH AND DELIVERY](../templates/FINISH%20AND%20DELIVERY.md). Save the
editable project and a decorated export. Keep a clean master too when later
reframing or derivatives need the final cuts without added graphics; it still
contains the original recorded visuals. Reopen the project and confirm media is
online. Check that exports decode, picture and sound stay in sync, and the ending
is complete. A technical pass is separate from watching and listening to the
whole final export. Record which file a person reviewed and what remains open.
Use the final export's timing for subtitles, chapters or packaging.

## 6. Keep the corrections that worked

If someone adjusts the cut, save the returned project before comparing it with
your previous version. Record the actual changed source ranges and the reason in
[CUT REVIEW](../templates/CUT%20REVIEW.md); a later clip moving because of a cut
is not another edit. Put an accepted, narrow rule and its example in the
[learning log](../templates/LEARNING%20LOG.md), alongside the style brief and
working assets. Test it on another suitable clip before treating it as reusable.
This is a durable instruction, reference and feedback loop, not model training.

Once source timing is settled, use [the content waterfall](../../10%20Content%20Waterfall%20System/START%20HERE.md)
if you want shorts or other derivatives. Exporting a finished video does not
publish it.
