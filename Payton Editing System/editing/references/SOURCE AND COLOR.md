# Qualify the source before changing its picture

Record actual dimensions, rational FPS, codec, bit depth, primaries, transfer, range, rotation and channel layout. Inspect camera settings when metadata is missing or contradictory. A camera brand, flat-looking image or filename does not establish its log curve. A stereo container does not establish two healthy dialogue channels.

Keep camera log, HDR phone footage, SDR screen recordings, browser graphics and already graded footage distinct. Preserve a correct existing project configuration. Use one coherent color-management path or explicitly controlled transforms; document input, working and output space. A LUT must receive the space it expects. Do not apply the same conversion twice or use a Mac gamma tag merely because one player looks different.

Correct exposure, white balance and shot matching before the creative look. Use waveform for clipping, RGB parade for imbalance and vectorscope for hue/saturation; compare actual frames and movement. Preserve natural skin, highlights, texture and legible interfaces. Grade the camera region separately from a demonstrated screen when possible. Neutral RGB equality applies to a known neutral object, not every surface.

For multiple rooms/setups, establish a representative balanced frame per setup, then inspect every transition in sequence. A single attractive still or copied LUT does not prove shot matching. Keep intentional scene differences.

## Optional warm filmic branch

Payton has accepted a warm rendering with a slightly lifted face, soft local shaping and restrained halation/glow on suitable camera footage. Match that intent to the new source; do not copy static face-mask coordinates as though they track a new person. Fit and track broad feathered windows where needed, checking movement, hands, hair and glasses for halos or drift. Add no grain merely because the word “filmic” appears.

A specific accepted experiment used JP 2499 and shot-fitted DCTL shaping, but its camera-input/output contract was not technically certified. Aesthetic approval is not a universal camera profile. The separately licensed or vendor-supplied transform must be obtained by the user and its actual expectations verified. Native curves and Film Look Creator can interpret the look; label that honestly rather than claiming exact reproduction of another film stock or plugin.

For DJI D-Log versus D-Log 2, choose the exact camera/model's official transform. These are different signals. A documented ACES route needs the correct log/gamut-to-AP0 conversion and intended working/output rendering; a model-specific log-to-Rec.709 LUT is a different, already display-rendered path. Do not feed that output back into a scene-referred chain as though it were raw log. Refresh the manufacturer's current instructions for the actual model.

## Cross-editor and overlay checks

When moving a graded image to CapCut or another editor, preserve source FPS and use a suitable high-quality intermediate. Check actual import, gamma/range, color and alpha against the source, including soft edges and brand colors. Avoid extra lossy round trips. Resolve color management also affects Fusion and imported PNG/video layers; a successful import is not proof of one correct transform.

The optional CapCut AI-enhancement route is a separate chosen step, not merely selecting 4K output. Verify the installed control and the finished file. Keep interpolation and Smart HDR separate decisions. For source-rate 60-family footage, do not pass through a 30 fps project then export 60. Actual enhancement must be compared for skin, hair, hands, fabric, highlights, gradients and text artifacts. An ordinary upscale does not prove an AI-enhancement step occurred or that detail improved.

Primary product references: [Blackmagic color tools](https://www.blackmagicdesign.com/products/davinciresolve/color), [DJI model-specific LUT guidance](https://repair.dji.com/help/content?customId=01700007105&lang=en&paperDocType=ARTICLE&re=US&spaceId=17), [CapCut export guidance](https://www.capcut.com/help/export-videos-in-capcut). Their current versions must be checked for a customer's actual setup.

## Included finishing code

[Payton Warm Finishing](../presets/Payton%20Warm%20Finishing%20-%20Shot-Fitted%20Reference.dctl) contains the actual owned finishing transform from a reviewed vertical recording. It adds gentle display-code contrast, 1.025× saturation, broad static edge shaping, a 3.5% midtone face-region gain, restrained background darkening, highlight diffusion and warm spill. The face gain is code-value gain, not exposure stops. Its exact numerical behavior is retained.

This is an optional shot-fitted reference after a suitable display rendering, not a camera input transform or a replacement for exposure and white balance. The original separately licensed JP2499 rendering is not included. Its original direct-input experiment did not independently establish the correct input transform. Use a rendering whose input assumptions are known, then compare the finishing effect on actual footage.

The mask centers and radii are normalized image coordinates in `finish_pixel`. Adapt them for the subject's framing and movement; they do not detect or track a face. Check the whole shot for drifting light patches, clipped channels, halos and changed screen content. Disable the effect if the actual result is worse. Native import/render of this portable DCTL is not yet verified; mathematical/static checks do not prove the look.
