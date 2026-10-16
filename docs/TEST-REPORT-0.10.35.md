# Bob 0.10.35 verification

- 333 Python regression tests passed in 27.621 seconds. Enrollment tests cover voice below the former onset threshold, continuous capture, explicit Finish/Cancel, bounded time, empty-audio quality rejection and long reading pauses. Calibration tests cover device binding, bounded gain, noise/voice stages, invalid levels, noise/clipping rejection and cancellation preserving previous settings.
- Frontend production build and ESLint passed for changed components.
- Final packaged EXE passed 112 native UI checks, including guided calibration saving, enrollment controls and rejection notices. These integrations are simulated in the UI audit.
- Packaged voice loop and interruption-command execution passed with injected audio, without layout overflow.
- Packaged close-window shutdown passed; scheduler/reminder workers stopped.
- Real packaged speaker model matched generated speech and a different phrase, restored encrypted temporary profiles and deleted them. Similarity 0.970 against a 0.650 threshold is a synthetic result, not a probability or a live-user accuracy score.
- Real-model generated-speech stress check matched clean speech and speech with added broadband noise at 10 dB SNR, and rejected an unregistered synthetic voice.

A separate requested interactive calibration completed for this user's current laptop microphone and was verified against the saved settings. Only device identifiers and scalar input levels were saved locally; no microphone audio was saved or committed. The user selected natural pauses in that helper. Existing real voice profiles and paused automations were preserved.

One targeted test run without the Windows user encryption environment could not call CryptProtectData; the final full regression run in the normal Windows context passed. An initial speaker diagnostic invocation lacked its module path, then the sandbox could not enumerate Windows voices; rerunning with the correct path and Windows voice access passed.

Limits: these checks do not prove flawless recognition in the user's room or separation of overlapping speakers. Live enrollment and Test voice match with the newly calibrated microphone still need user verification. Saved-voice-only restrictions and four-second/three-sample enrollment quality requirements remain active. Humanlike conversation remains dependent on microphone placement, acoustic conditions and local model latency.
