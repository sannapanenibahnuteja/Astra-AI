# Bob 0.11.7 verification — 24 October 2026

[Machine-readable evidence](TEST-RESULTS-0.11.7.json).

- **470 Python regression tests passed** in 34.356 seconds, including five new
  readiness tests covering failed prerequisites, isolated probe failures,
  fixed-field support output, no private-error leakage and one call per probe.
- Frontend production build passed. ESLint passed for the new WelcomePanel.
- PyInstaller built a new runnable Windows folder containing Bob.exe and its
  `_internal` runtime/model assets.
- **160 packaged UI checks passed**, including ten new checks for initial setup
  status, refresh, summary copy, Settings navigation, and four request cards that
  prepare text without calling `start_chat`. These use isolated fixture data and
  simulated integrations.
- Packaged startup/voice handoff fixture passed: seven navigation destinations,
  no horizontal overflow at 1366px, voice round trip and interrupted-command
  handoff. X-button shutdown stopped fixture schedulers and reminders.
- Synthetic native audio diagnostics passed, including 17.7dB seeded echo
  attenuation and cancellation guards. No microphone was recorded.

The packaged readiness UI uses synthetic probe results for deterministic tests.
Its real probes query Ollama, model files and device availability; they do not
capture audio, load AI models or confirm acoustic/synthesis quality. No real
Windows application workflow, provider call, purchase or customer hardware trial
was performed in this upgrade. Existing personal settings and calibration were
not changed. These results do not establish sale readiness, flawless speaker
recognition or universal PC control.

Documentation adds a customer acceptance plan and corrects the architecture
guide. Payment/activation, code signing, installer/update delivery, full commercial
dependency review and live acceptance remain open work. See
[customer release plan](CUSTOMER-RELEASE.md) and [new feature test steps](RELEASE-0.11.7.md).
