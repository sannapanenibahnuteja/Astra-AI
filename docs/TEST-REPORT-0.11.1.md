# Bob 0.11.1 — quiet-room interruption verification

19 October 2026. Evidence: [TEST-RESULTS-0.11.1.json](TEST-RESULTS-0.11.1.json).

- **384 regression tests passed**, 33.144 seconds. Includes 13 new noise/interruption tests and all existing command, conversation, profile, audio and integration contracts.
- **Frontend production build passed.**
- **Packaged EXE: 120 UI checks passed**, native close stopped reminder/scheduler workers, correct assets rendered without horizontal overflow, and simulated interruption → new command → reply handoff passed. UI integration speech is simulated.
- **Packaged native audio checks passed:** tiny input falsely labeled as speech was rejected; a short loud click followed by VAD hangover was rejected; sustained soft-speech labels with consonant gaps qualified at **250 ms** in the controlled fixture. This is gate timing, not measured physical/biometric interruption latency.
- Native echo reduction remained **17.7 dB** in the seeded echo fixture; all three suppression levels processed finite aligned frames. Native AEC frame p95 was **0.314 ms**, excluding ASR, speaker matching, synthesis and playback latency.

New regression coverage includes tiny continuous false-VAD input, brief clicks with hangover, repeated keyboard bursts, soft sustained speech, echo settling, room-relative signal thresholds, unchanged quiet capture when idle, zero noise duck/cancel/queued commands during playback, confirmed speech interrupting once, final matching respecting a failed gate, continuing the next TTS sentence through provisional noise, speaking the new response after consuming an interruption, stopping an old response for an unconsumed genuine interruption, and resetting the state when explicitly discarded.

The speaker-path mock fixture now supplies the noise-floor value required by the independent gate; existing channel alignment checks still pass.

No live user microphone recording, profile re-enrollment, calibration change, paid call or real routine modification was performed. Synthetic/controlled tests cannot establish flawless real-room recognition, background-speaker rejection or an exact physical latency. Follow the five-step test in [Release notes](RELEASE-0.11.1.md) with your usual microphone.

Launchable build: `dist/release-0.11.1/Bob/Bob.exe`. Keep `_internal` beside it; no release ZIP is required.
