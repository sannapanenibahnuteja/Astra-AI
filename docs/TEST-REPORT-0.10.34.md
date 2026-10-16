# Bob 0.10.34 verification

- 324 Python tests passed in 26.480 seconds. New regressions cover empty-VAD recovery, no retry for silence/hiss/cancellation, confidence review on retries, exact-audio match reuse, unchanged speaker-focus checks, waiting for pending verification, visible rejection reasons and bounded matching work.
- Frontend build and ESLint passed.
- Final packaged EXE: 109 native UI checks passed, including the rejection notice and manual enrollment Finish/Cancel controls. Integrations in this audit are simulated.
- Final packaged voice interaction and interruption-command execution passed with injected audio; no horizontal overflow.
- Final packaged title-bar close test passed; scheduler and reminder workers stopped.
- Real local Whisper decoded ten generated samples (five phrases at normal and quiet gain). Silence and broadband hiss returned no words. One quiet sample remained marked for user review; confidence requirements were not weakened.
- Final packaged Whisper decoded all seven generated speech WAV files; silence returned no text. No microphone or Windows actions were used.

The first regression run exposed a pending-verification field missing from an old test mock and a retry trying to decode an empty test input. The mock now has the real field; the optional retry handles absent audio. The final full suite passed.

Limits: synthetic fixtures do not establish live-user or noisy-room accuracy. Speaker matching remains approximate and gates desktop voice commands when enabled. The isolated UI snapshot reported Ollama offline; its replies were simulated. Local Whisper transcription works independently of Ollama. No live-user profile, recognition preference, or real paused routine was changed.
