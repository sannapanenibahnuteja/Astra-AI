# Bob 0.11.6 — response-scoped cancellation and microphone calibration

[Machine-readable results](TEST-RESULTS-0.11.6.json).

- **465 regressions passed**, 28.542 seconds, including **14 new tests** for response-bound permits, callback failure, replay/stale response rejection, and calibrated interruption floors.
- Frontend production build passed. The UI retains the previous release's controls and layout; only its build version changed.
- **150 packaged native UI checks passed**, plus startup with the correct UI/wake handler, no horizontal overflow, single-capture → interrupted request → fixture execution handoff, and X-button shutdown stopping fixture schedulers.
- Packaged native audio diagnostics passed: **17.7 dB** seeded echo attenuation, all suppression levels, quiet/click rejection, completed/explicit interruption checks, and new checks rejecting raw generation callbacks and publicly supplied verification values. A synthetic device calibration exercises the additional floor. These diagnostics do not record a microphone.
- **Live user-authorized microphone-level calibration passed** in a separate timed window: ambient measurement followed by a reading stage. A valid device profile was saved locally; raw audio was discarded. The first beep-timed attempt lacked sufficient clear speech and made no calibration change. No personal measurements or recordings are included in the distributable or this Git evidence.

New regression coverage: raw callbacks cannot cancel before the first token or during generation; direct barge-in without proof cannot stop TTS; a genuine completed speaker/intent result cancels generation and preserves the next turn; a permit is consumed once; old-response proof and response changes during decode are rejected; finishing an older job does not clear a newer context; callback refusal/failure retains playback and drops the candidate; manual Stop clears pending proof; external JSON/boolean/string values cannot forge a permit; post-gain calibration applies only to the matching device; missing/invalid calibration falls back; and the calibrated interruption floor does not reduce ordinary capture sensitivity.

Existing confirmation/streaming fixtures were updated to model an already verified permit at their injection point rather than assuming an unproved callback should cancel. Their original pending-action and streaming assertions remain. Separate end-to-end unit tests exercise the actual opaque permit issuance/delivery/consumption path. One initial full run identified the old bare-callback fixture expectation; after updating that fixture, the complete final suite passed.

Calibration changed input-level configuration only. It did not register a voice, change speaker thresholds, alter Windows system microphone volume or validate transcription/identity accuracy. Restart Bob to load it. No paid call, personal routine execution, real app control or raw-recording save was performed. UI integrations and most action execution in regression tests are simulated. The reported quiet-room interruption case still needs a live acceptance test after restart; the microphone level test is not an end-to-end noise/intent accuracy trial.

The cancellation boundary now consumes short-lived response-scoped proof; a genuine verified interruption can stop a waiting model even before text appears. Unverified callbacks do not have that authority. The microphone remains active, and existing completed-turn, saved-speaker, explicit-phrase and word-confidence gates remain. Matching is approximate; this does not claim access to private mental intent or perfect recognition.

Launch `dist/release-0.11.6/Bob/Bob.exe` with `_internal` beside it; no ZIP is required. [Setup and pending-generation test](RELEASE-0.11.6.md).
