# Bob 0.10.7 — Adaptive interruption detection

Changes from 0.10.6:

- Replaced 180 ms of uninterrupted loud speech with a rolling speech window.
  Consonant gaps and quiet speech can now trigger an interruption.
- Lowered the fixed energy floor and added bounded gain for speech detection and
  transcription. Echo cancellation still uses original microphone/reference levels.
- A 550 ms quiet gap ends recording, plus the voice detector's own hangover.
- Learn background residual levels during a turn's quiet ending so the same
  background sound does not immediately create another command.
- Expose recording state, captured duration, completed turns, interruption count
  and input/clean audio levels. Logs record speech onset, utterance completion and
  transcription confidence without saving audio or logging transcript text.

Test:

1. Quit the older Bob from the tray. Start this release's Bob.exe.
2. Start a voice conversation and check “Echo cancellation active.”
3. Ask “Tell me a long story.” Halfway through, say “Actually, open Calculator.”
4. Pause for about a second. Bob should finish capture, transcribe and execute.
5. Try again in a quieter normal voice. Do not whisper or shout.
6. Say “Stop listening” to end the active conversation.

The status distinguishes “Ready for your next request” from capturing a command.
An open voice conversation waits between requests by design. Uncertain transcripts
still need review. These changes address identified detection weaknesses; real
room/accent/device quality must be checked with your voice. Other apps' audio is
not part of Bob's echo reference.

Validation: 111 tests and the frontend build passed. The generated-speech check
in scripts/verify-interruption.py models actual speaker cutoff, delayed echo,
VAD, capture ending, Whisper transcription and action parsing. Normal and quieter
speech both produced a reliable “open calculator” action plan; Bob-only echo
caused no interruption. This is a simulation, not a live user-voice guarantee.
