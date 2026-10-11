# Bob 0.10.21 — natural speech pacing

Changes from 0.10.20:

- Natural mode ends short replies after 450 ms of silence, ordinary requests after 650 ms, and longer speech after 950 ms. Resuming before the deadline keeps the same turn.
- Whisper prepares in the background at conversation start, reuses its model between turns, and releases idle memory after three minutes in a session or one minute outside it.
- Old idle timers cannot unload a newly reused model. Shutdown releases prepared weights; preload failures allow normal capture to retry.
- Quick, Patient, Thinking and enrollment pause settings retain their existing behavior. Noise and interruption protection remain in place.
- Added focused timing, pause-continuation and model lifecycle regressions, plus a plain-language voice pipeline diagram.

Run `dist/release-0.10.21/Bob/Bob.exe` directly, keeping `_internal` beside it. Quit the old Bob first.

[How it works and voice test steps](VOICE-PIPELINE.md). [Test report](TEST-REPORT-0.10.21.md).

This is adaptive timing and reduced loading overhead, not word-by-word streaming transcription or a claim of perfect microphone accuracy.
