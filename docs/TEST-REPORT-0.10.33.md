# Bob 0.10.33 verification

- 316 Python regression tests passed in 26.116 seconds. Capture tests verify a six-second pause does not end enrollment, explicit Finish preserves captured audio, Cancel skips enrollment, capture remains bounded at 60 seconds, and Finish has no effect outside enrollment.
- Frontend production build and ESLint on changed components passed.
- Final packaged EXE: 108 native UI checks passed, including three Finish sample submissions and cancellation preserving the sample count. These use simulated integrations.
- Packaged voice round trip and interruption-command execution passed with injected audio. No layout overflow.
- Packaged title-bar shutdown passed; scheduler and reminder workers stopped.
- Real packaged speaker model matched generated speech and a different phrase, restored encrypted profiles, and deleted the temporary profile. This uses synthetic speech, not a live-user accuracy evaluation.
- Idle three-second sample: 3.1% of one CPU core, 522.4 MB summed working set including seven child processes and shared pages, excluding Ollama. This is a short observation, not a performance guarantee.

The first regression run exposed two older tests that assumed enrollment used conversational duplex capture. They were updated to verify the still-supported identity-test duplex path; the new enrollment capture has separate pause/Finish/Cancel tests. Final suite passed.

Existing voice profiles and the user's paused routine were not modified. Live microphone enrollment with the user's own voice still needs their verification. Speaker identification is approximate and does not separate simultaneous speakers or provide authentication.
