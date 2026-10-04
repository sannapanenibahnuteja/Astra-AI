# Bob 0.10.6 — Finish commands and execute interruptions

Changes from 0.10.5:

- Added WebRTC's dedicated voice activity detector after echo cancellation.
  Background residual audio no longer relies only on a spectral probability to
  decide when speech ends. A 650 ms pause ends an utterance (plus VAD hangover).
- Added a relative speech-energy threshold so quiet background residuals cannot
  keep a captured command open indefinitely after a louder spoken request.
- Preserve and consume queued interruptions even when the microphone was started
  in single-command mode. Do not close the session before the new turn is handled.
- Ignore redundant wake/start events during an active conversation instead of
  closing its microphone and losing buffered audio.
- Recognize conversational prefixes such as “Actually, open Calculator” through
  the direct command path. Dictation payloads retain their literal wording.
- Added a packaged UI regression that interrupts a single spoken response,
  submits the next request and verifies its action result with a safe fixture.

Test this version:

1. Quit the older Bob from the tray and run this version's Bob.exe.
2. Start voice conversation. Check “Echo cancellation active.”
3. Say “Open Calculator” and pause. Bob should transcribe and execute after the
   short pause, rather than stay stuck capturing the same utterance.
4. Say “Tell me a long story.” While Bob is talking, say “Actually, open Notepad.”
   He should stop speaking, capture your full request, open Notepad and reply.
5. Try the same interruption after starting with the single-command mic button.
6. Say “Stop listening” when finished.

During a conversation, listening resumes after each reply so you can follow up.
That is different from a command stuck in recording. Check the transcript and
“Transcribing”/“Thinking” indicators. Low-confidence recognition still asks for
review rather than automatically executing unclear speech.

Live microphone/speaker quality still requires testing on your actual setup.
The audio reference covers Bob's speech, not other apps' media playback.

Validation: 110 unit tests and the frontend build passed. The frontend regression
used simulated speech and a safe action fixture to verify an interrupted reply
leads to the next command's result. Generated-speech AEC/VAD checks detected the
independent interruption and completed its recording; Bob-only echoes caused no
false interruption. These are deterministic checks, not a guarantee of recognition
quality on every physical microphone.
