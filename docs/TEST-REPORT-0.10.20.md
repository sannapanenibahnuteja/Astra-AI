# Bob 0.10.20 test report — 10 October 2026

This focused release fixes accepted voice commands being cancelled by unrelated speech-onset callbacks. It retains 0.10.19's command repairs and Edge fixes.

## Current-release evidence

- **226 automated tests passed**, including command fixtures for every one of the 84 advertised actions and six new voice-confirmation regressions. No skipped tests. [Per-check ledger](TEST-RESULTS-0.10.20.json).
- Exact “Close Microsoft Edge” → “Yes” tested with simulated native execution and injected speech onset before generation; the approved action executes once, records one step and returns its result without `[Response stopped.]`.
- Injected onset during native execution cannot cancel away its verified result. Active model generation and spoken responses remain interruptible. Manual Stop remains effective.
- Real disposable Windows fixture passed the new confirmation diagnostic from source and the **final EXE**. A spoken approval survived injected callbacks before generation and during execution; the real test window disappeared and the result was retained. Speech capture and output were simulated; no microphone used.
- Final EXE frontend fixture passed: voice round trip, interrupted Calculator request, four navigation destinations and no horizontal overflow. Input speech and calculator execution were simulated.
- Frontend production build and desktop UI lint passed.

## Meaning and limits

The onset callback used to cancel any active spoken request. It now only cancels model generation or current spoken output, and is ignored while native execution is underway. Short native actions finish and report their outcome; this is not a guarantee of immediate voice cancellation inside a blocking native action. The Stop button retains its existing cancellation behavior.

This test establishes the cancellation fix, not perfect speech recognition or voice identity accuracy. A “Voice identity uncertain” status does not prevent command processing. Several matching Edge windows still require a specific selection; whole-window closure can encounter a save dialog and must report an error rather than invent success.

The broader live checks and phone/microphone limitations from the previous release are documented in [0.10.19 verification](https://github.com/sannapanenibahnuteja/Astra-AI/blob/main/docs/TEST-REPORT-0.10.19.md); they are historical evidence, not newly repeated live checks for every capability. Carrier calls, physical iPhone access, arbitrary app controls and real-user speaker accuracy were not tested live in this focused release.

## Repeat

- `venv\Scripts\python.exe scripts\verify-release-tests.py` — full regression suite.
- `venv\Scripts\python.exe scripts\verify-voice-confirmation.py --exe dist\release-0.10.20\Bob\Bob.exe` — native confirmation diagnostic. Creates and closes only its own test window.
- `Bob.exe --ui-test --data-dir .cache\isolated-ui` — frontend interruption fixture; microphone input and calculator execution simulated.

[Changes and user retest steps](RELEASE-0.10.20.md).
