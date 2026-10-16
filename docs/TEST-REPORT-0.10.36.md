# Bob 0.10.36 verification

- 343 Python regression tests passed in 26.656 seconds. Checks cover short speech reaching identification with the higher short-utterance similarity cutoff, rejection of very brief audio, unchanged four-second enrollment requirements, synchronized speaker/transcription channels, identical echo reference/delay, and routing each channel to its correct consumer.
- A matched full request now interrupts even if its early partial check missed. Tests verify only one interruption for a turn and rejection of late results from older turns.
- Re-recording tests verify encrypted old data is untouched until all three replacement samples are accepted; cancellation and invalid takes preserve it. Completion retains profile ID, personality, memory and conversation association after encrypted reload.
- Frontend production build and ESLint passed.
- Final rebuilt EXE passed 114 native UI checks, including starting/cancelling re-recording. UI integrations are simulated. Packaged voice loop and interruption-command execution passed with injected audio; native title-bar close stopped scheduler/reminder workers.
- Real packaged speaker model matched generated phrases and restored encrypted temporary profiles. The separate speaker channel matched a held-out generated voice and rejected an unregistered generated voice. Simulated playback echo was reduced by 20.4 dB on that channel.
- A very short generated sample reached the real extractor but remained below the stricter short-speech similarity cutoff. This is an expected uncertain result, not a claim that every short request now matches.

The user completed the requested live full-sentence check: both raw and existing noise-suppressed microphone audio matched the saved profile without changing it. The result argues against forcing enrollment again or assuming noise suppression alone caused the reported failure. Code inspection found the hard one-second voiced-audio rejection and the partial-check/full-check interruption issue; both are addressed. A separate speaker channel is retained to reduce processing differences, with echo cancellation on both paths.

Limits: the live full-sentence result does not establish live-user short-command or overlapping-speaker accuracy. Similarity thresholds and ambiguity checks remain active. No live audio or per-user profile scores are committed. Existing real profiles, memories, calibration, recognition preferences and paused routines were preserved. One automatic approval-review attempt timed out; the permitted retry ran successfully.
