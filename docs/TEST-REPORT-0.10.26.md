# Bob 0.10.26 verification — 12 October 2026

- 251 regression tests passed. Added 16 tests covering daily routine persistence/restarts, pause/busy/missed times, safe schedule validation, partial failure, voice routine lookup/ambiguity, optional scoped setup, stale/ambiguous screen references and cleanup despite a failed service.
- Frontend production build passed. Lint passed for all four changed desktop JSX files. Whole-repository lint reports existing issues in legacy chat/task components, rendering engine and wake-listener files; these were not concealed or changed in this release.
- The final packaged EXE passed 78 native UI control checks: previous controls plus onboarding review/skip, selected memory only, routine template/add/remove/save/edit/daily time/refresh/run/delete. App launches, speech, phone and link integrations are simulated in this audit.
- Packaged voice-to-chat and interruption execution fixture passed; five navigation entries and no horizontal overflow at the native test viewport. This is simulated voice input, not validation of every microphone/noise/accent.
- Packaged WM_CLOSE test passed. The process exited normally, scheduler/reminder stop flags were set, and native cleanup ran. The test window is a fresh isolated profile; no running personal instance was closed.
- Source and packaged screen tests read the dedicated Windows verification app's accessibility tree, resolved its observed Record control, required confirmation in the resulting plan and invoked that control. The fixture output file proved the actual app received it. No personal screens were read. No image-only vision capability is claimed.
- Browser visual inspection confirmed the black routine builder and editable template. Preview screenshot: .cache/bob-routines-0.10.26.png.

The first regression run caught an unregistered capability fixture and absent new release notes. Both were corrected before the final 251-test pass. The UI audit intentionally injects a speech error to verify recovery; that expected exception is not a release failure.

Daily routines use deterministic command planning, validate all steps before acting and never use a language model to invent unattended operations. Actual daily hardware changes, carrier calls, home automation, cloud services, all Windows apps and every possible user utterance were not exhaustively tested in this release. Existing integration guides document their requirements.

Launch dist/release-0.10.26/Bob/Bob.exe directly, keeping _internal beside it. No ZIP was created.
