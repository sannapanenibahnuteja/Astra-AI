# Bob 0.11.6 — protect pending generation and use microphone calibration

The reported symptom was “[Response stopped.]” while the reply was still generating. This release adds a second check at the generation-cancellation boundary, beyond the completed-voice checks added in 0.11.5.

## Cancellation now requires response-scoped proof

A completed eligible turn must match the selected/current saved speaker and contain a confident explicit interruption phrase. It then creates a short-lived, opaque, one-use permit tied to that response. The audio callback must deliver the matching permit before generation can be canceled. Bare onset callbacks, JSON/boolean claims of verification, reused permits, changed speakers and proof from an older response are rejected. A genuine verified interruption still works while waiting for model output, even before the first token arrives. Native actions already executing remain protected; the next captured request can wait for them.

If the final callback refuses the permit or fails, playback is retained and the candidate is not queued. Manual Stop remains functional and invalidates outstanding proof. Existing wake words, completed-transcript checks, no acoustic ducking, saved-voice controls and command execution validation remain.

## Device-specific calibration

The user-authorized laptop-microphone calibration was completed using separate ambient and reading stages. Only microphone level measurements were saved, never raw audio or a voiceprint. A validated device gain was saved locally; no Windows system volume or identity threshold was changed. The distributable and Git history do not contain the user’s microphone measurements. The initial beep-timed attempt lacked enough clear speech and did not alter calibration. The subsequent user-started timed window passed.

The interruption gate now derives an additional post-gain floor from a matching device's measured voice and room levels. A different device or invalid/missing calibration uses the existing fallback. This affects interruption eligibility only: ordinary speech capture is not made less sensitive. This is level calibration, not proof of speaker identity, speech-recognition training or a guarantee of transcription accuracy. Other installations retain their own device calibration.

## Use and test

1. Close the older Bob. Launch `dist/release-0.11.6/Bob/Bob.exe` with `_internal` beside it. Restart is required to load the newly saved calibration.
2. To use voice interruption, enable **Recognize my voice**, select yourself under **Focused listening**, and enable **Allow verified voice interruptions**. These remain separate from microphone calibration.
3. Say “Hey Bob, explain how a CPU works in detail.” While Bob is thinking before the first words, tap keys or make a desk click. The pending response should continue rather than becoming “[Response stopped.]”. Repeat while text is streaming and while audio is playing.
4. Say “Hey Bob, please stop talking” and finish the phrase. The saved voice and final words must be verified before stopping. Endpoint/ASR delay still applies.
5. Say “Hey Bob, open calculator” during another reply. The old reply should stop after proof, and the new request should remain available for validated execution.
6. Press Stop during generation: it must still stop. Start a new request; any delayed proof from the stopped response must not cancel it.
7. Check Settings → Microphone calibration: the saved device calibration should be available after restart. Recalibrate if you change input devices or placement substantially. No need to overwrite saved voice profiles merely to change gain.

No noise detector can read private intent or guarantee zero recognition errors. This release removes unproved cancellation routes and applies measured device levels. [Verification and scope](TEST-REPORT-0.11.6.md).
