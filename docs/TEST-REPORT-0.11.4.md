# Bob 0.11.4 — appearance, discovery and fast command routing

22 October 2026. [Machine-readable evidence](TEST-RESULTS-0.11.4.json).

- **440 regressions passed**, 30.379 seconds, including **19 new appearance/app tests**. Every advertised action now has a validation fixture, including the appearance tool. The unique high-confidence typo test now expects automatic launch; ambiguity tests still reject the fast lane.
- Frontend production build passed. ESLint passed for the new appearance component/theme constants and changed orb component. This is not a claim that every legacy file is lint-clean.
- **150 packaged native UI checks passed**, including all appearance dropdowns, accent selection, optional surfaces, save/reset, palette open/close, restoring navigation/details and existing memory, routines, planner, profiles and settings controls. The same 150 source-native checks passed before packaging.
- Packaged startup, single-capture → interrupted request → execution handoff and X-button shutdown passed in isolated folders. Main UI had six navigation pages and no horizontal overflow. App/voice/phone integrations in UI tests are simulated.
- Packaged controlled native audio diagnostics passed, including seeded echo attenuation **17.7 dB**, all suppression levels, quiet/click rejection, explicit wake policy and the controlled 250 ms acoustic gate. This is not a live recognition or full interruption latency measurement.
- Visually inspected the actual local frontend at 1280 × 720, including the default black orb-centered workspace and the appearance drawer. This preview is not the desktop action bridge.
- One **live local qwen3:8b** evaluation with disposable data successfully mapped “Give the interface a mint accent. Leave every other preference alone.” to the requested accent only, completing in **4.14 seconds**. No actual app action or microphone was allowed in this test. The smaller UI-only schema prompt avoids loading the full Windows tool catalog. This is one observed run with model/cache conditions, not an instant-response guarantee or controlled comparative benchmark.

The first broad-tool live evaluation took 56.14 seconds and returned an invalid appearance payload; it was rejected before any change. The implementation was then changed to a compact schema-constrained UI-only model path, and the live test passed. General mixed UI/Windows tasks retain validated agent tools; both JSON-string and object appearance payloads are validated into the same bounded patch.

One concurrent regression run encountered Windows WinError 10053 in the existing loopback origin-rejection test. Its 11-test module passed separately, then the complete final 440-test run passed. No networking protection or test assertion was weakened.

Coverage includes independent saved appearance fields and boolean switches; natural phrasing, color aliases and clear typos; compound UI requests without partial application of mixed tasks; rejecting arbitrary CSS/code/invalid types; reset/persistence; no-model direct preferences and installed-app launches; compact model schema and contextual corrections; rejecting invalid generated patches; direct known website routing; EXE paths without shell arguments; bounded discovery excluding installers/helpers; ambiguous app names; and visible-window verification before a launch-success claim.

No real saved voice profiles, microphone calibration, personal memories, routines or phone settings were changed. No call was placed, recording captured or model weights trained. Appearance is shared per Windows Bob installation. Installed-app discovery does not scan all drives or guarantee every custom/UWP app. Unknown tasks still need supported tools; arbitrary execution, zero errors and universally instant responses are not promised. Physical microphone/speaker behavior and actual installed-app launches need live acceptance testing.

Launch `dist/release-0.11.4/Bob/Bob.exe` with `_internal` beside it. No compressed EXE/ZIP is required. [Changes and full new-feature test commands](RELEASE-0.11.4.md).
