# Bob 0.11.11 verification — 29 October 2026

[Machine-readable results](TEST-RESULTS-0.11.11.json).

- 525 Python regressions passed in 30.832 seconds, including six new adaptive-room tests.
- Frontend production build and audio-panel ESLint passed.
- 187 packaged UI fixture checks passed. Voice handoff/queued interruption fixture passed; no horizontal overflow at 1366px. X-button shutdown stopped fixture reminders/schedulers.
- Packaged synthetic audio checks passed: seeded AEC attenuation 17.7 dB, generated noise/taps rejected, cancellation proof guards retained. These are controlled fixtures, not live recognition accuracy or end-to-end response latency.

New coverage verifies sustained quiet is required, Quiet preference still requires measured evidence, sustained noise restores caution, single taps do not change policy, playback/speech cannot establish quiet, clipping/invalid data restore caution, and softer capture still requires sustained speech. No identity or transcript thresholds were lowered.

The first sandboxed full-suite attempt encountered WMI/localhost permission failures. Rerunning with the required native access passed the entire suite; no assertions were removed or skipped. No actual microphone, private profile, call, financial record or saved routine was used or changed. Live deliberate interruption acceptance remains unresolved and must be verified using the user's normal microphone and speakers.
