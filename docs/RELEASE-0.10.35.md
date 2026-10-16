# Bob 0.10.35

- Fixes manual voice enrollment still waiting for a command-volume threshold. After the cue, recording now captures continuously until Finish sample or the 60-second limit. Quiet words and mid-sentence pauses are preserved. Empty takes reach an explicit audio-quality error instead of being silently discarded.
- Enrollment, voice-match tests and conversation now use the same Windows WASAPI default microphone. The selected input is shown during recording.
- Adds Settings → Calibrate my microphone: measure three seconds of room noise, then ten seconds of normal speech. A device-specific bounded input gain is saved and used for enrollment and conversation. Audio remains in memory and is discarded. Silence, clipping and insufficient clear speech cannot replace a good calibration.
- Adds microphone meters during enrollment and calibration, with separate preparing/recording/processing states. A cancelled take keeps earlier accepted samples.
- Speaker-feature preparation now analyzes active speech rather than initial silence and skips long empty gaps before selecting its bounded model input. Four seconds of usable speech and three consistent samples are still required.
- The standalone calibration helper offers optional natural pauses (650 ms setting with adaptive timing) and changes that preference only if selected. Existing interruption, context and speaker restrictions are preserved.

## Set up and test

1. Close old Bob. Launch this Bob.exe with _internal beside it. Stop voice conversation.
2. Settings → Calibrate my microphone → Measure room noise. Stay quiet for three seconds.
3. Click Record my normal voice. Speak at your normal distance for ten seconds. Check the calibrated confirmation; levels are saved automatically for that input.
4. Under Recognize my voice, enter your name, Record sample, wait for Listening, read naturally, then Finish sample. The meter should move as you speak. Repeat three varied takes. The wording is optional; there is no transcript-matching test.
5. If an existing profile fails Test voice match, delete only that person's voice profile and enroll it again after calibration. Existing memories and conversations remain.
6. Test a full spoken request and interruption during a reply. For natural breathing room choose the natural speaking-pause setting in Voice & personality. Brief or overlapping speech can still be uncertain with saved-voice-only listening.
7. Change your Windows default microphone: the old device calibration must not be applied to it. Repeat calibration for the new microphone.

Calibration does not guarantee recognition in every room or separate simultaneous speakers. It does not change Windows microphone volume or save raw recordings. Quality checks and saved-voice-only permissions remain active. User calibration and live-user enrollment still require the user's participation.
