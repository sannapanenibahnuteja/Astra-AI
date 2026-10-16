# Bob 0.10.32 verification

- 312 Python regression tests cover saved-speaker filtering, unknown/other-user rejection, no transcription for ignored speakers, verified-only interruption, stale-turn rejection, failed verifier rejection, output/microphone metering and minimum enrollment data.
- Frontend production build and ESLint for changed components passed.
- Browser preview visually checked against the supplied reference: scattered colored particle sphere on black. Procedural canvas, no copied raster assets.
- Final packaged UI checks and generated-speech speaker-model diagnostics are recorded in the test ledger. UI model/audio inputs are synthetic. Generated-speech diagnostics use the real local model and encrypted temporary profiles, not microphone recordings.

The initial canvas check ran before first paint; it now waits for visible particles. The initial generated enrollment passages were too short for the stronger four-second usable-speech minimum; diagnostic passages and user suggestions were lengthened, without weakening the minimum.

Limits: tests do not prove recognition accuracy for this user's voice or separation of simultaneous speakers in their room. Recognition-enabled interruption verification needs about 1.6 seconds of voiced audio plus inference time; short acknowledgements may be ignored. Wake words remain Windows grammar-based. A person with access to the PC or paired remote controls is not blocked by biometric authentication. No real user profile, settings, microphone or paused automation was modified.

Real-model synthetic stress check: held-out enrolled speech matched with added broadband noise at 10 dB SNR; a different unregistered Windows synthetic voice was rejected. This does not establish live-user or overlapping-speech accuracy. The enrolled-speaker gate also runs before the bounded pending-command queue so background voices cannot occupy its slots.

The new settings persistence audit initially queried its fixture database before the save committed; it now waits for the expected persisted value. No production setting failure was found in that check.
