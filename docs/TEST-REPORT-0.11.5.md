# Bob 0.11.5 — completed interruption and shared-path efficiency

22 October 2026. [Machine-readable evidence](TEST-RESULTS-0.11.5.json).

- **451 regressions passed**, 28.720 seconds. Includes ten completed-interruption regressions and one cosmetic-save/capture-preservation regression. Existing validation fixtures still cover every advertised tool action; this does not mean every real Windows integration was exercised against personal apps.
- Frontend production build and changed audio-panel ESLint passed.
- **150 packaged native UI checks passed**: current interruption enable/disable preference, appearance fields/reset, existing navigation, profiles, memory, routines, planner and settings controls. Voice and integrations are simulated for these UI checks.
- Packaged startup had the expected UI, six navigation pages, wake handler and no horizontal overflow. Single-capture → interrupted new request → fixture command handoff passed. Native close stopped the isolated schedulers.
- Packaged native audio diagnostics passed: **17.7 dB** seeded echo attenuation, all three suppression levels, quiet/click rejection, wake policy, and new proof that partial results cannot authorize reply stops and setting combinations cannot enable sound-only interruption. The controlled acoustic gate is 250 ms; full saved-voice/endpoint/ASR verification takes additional time.

New checks cover all eight combinations of legacy wake/verification/duck switches retaining authorization with ducking disabled; disabled voice interruptions avoiding decoding; partial hallucinated controls not reaching identity/ASR or cancellation; positive partial callbacks not stopping output; direct onset callbacks unable to bypass completed proof; weak acoustic candidates not being queued; weak individual words rejecting an otherwise high-average-confidence transcript; explicit interruption phrases still being required when idle wake mode is off; completed verified requests canceling once and preserving the command; preview inference not competing with active replies; and cosmetic updates not reconfiguring audio or advancing capture serials.

One initial full run exposed a missing optional attribute on an older test fixture built without the normal constructor. The boundary now reads it safely; real Bob always installs authorization. The subsequent final full suite passed. No noise guard or fixture assertion was weakened.

Efficiency changes remove speculative interruption inference passes, pause provisional captions during replies, keep final inference available, preserve accepted final transcripts, avoid stale/duplicate queued commands and keep appearance-only saves out of voice reconfiguration. The UI reuses appearance state across audio-status renders. No global speedup percentage or perfect accuracy is claimed.

The running build and a small set of audio flags were inspected read-only. No raw recordings, speaker vectors or conversations were copied. No live microphone recording/test, paid phone call, voice re-enrollment, calibration replacement, routine run or real profile change was performed. The reported quiet-room case still needs live acceptance testing with the user's microphone and speakers. Voice identity/intent are approximate; real audio/device failures must be distinguished from a verified interruption.

Launch `dist/release-0.11.5/Bob/Bob.exe` with `_internal` beside it; no ZIP is required. [Changes, setup and quiet-room test steps](RELEASE-0.11.5.md).
