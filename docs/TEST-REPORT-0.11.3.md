# Bob 0.11.3 — complete speech and wake-phrase activation

19 October 2026. [Machine-readable results](TEST-RESULTS-0.11.3.json).

- **421 Python regressions passed**, 29.738 seconds. Includes **16 new tests** for wake activation, interruption policy and complete spoken output. The final punctuation-tolerant wake parser then passed **37 targeted wake/interruption tests**.
- Frontend production build and changed audio-panel ESLint passed.
- Final launchable Windows EXE built successfully. **126 packaged native UI checks passed**, including wake-phrase off/on persistence, existing interruption preferences, settings, profiles, memory, routines and planner controls.
- Packaged single-capture → interruption → new request round trip passed using the current “Hey Bob, open calculator” fixture. The first capture models the explicitly armed manual activation. Actual microphone, TTS output, model replies and the app action are simulated in this handoff test.
- Packaged native close-button test passed and stopped fixture schedulers. Startup showed the correct assets, wake handler, navigation and no horizontal overflow.
- Packaged native DSP test passed: seeded echo attenuation **17.7 dB**, all three suppression levels, quiet noise/click rejection, controlled 250 ms acoustic interruption gate, and explicit wake policy. This is not end-to-end speaker/ASR latency or real-room recognition accuracy.

New coverage: no new agent request from untriggered ordinary speech; wake-prefix removal preserving the payload; standalone wake phrase arming one request; expiration; slow final decoding retaining capture-start permission; uncertain wake rejection; explicit session stops; bare “actually”/“shorter” rejection in wake-only mode; addressed reply-stop compatibility; no app-action reinterpretation of reply-stop; explicit policy opt-out; strict authorization remaining active with wake-only mode; prose longer than 5,000 characters and 200 words surviving; streamed sentence/tail delivery exactly once; bounded renderer chunks preserving all words; complete render/play dispatch; and cancellation preventing subsequent chunks. Public/text-only privacy behavior remains covered by the regression suite.

The first packaged handoff run used the old test fixture’s untriggered “Actually…” phrase and failed under the intentional new default. The fixture was updated to model explicit activation and use “Hey Bob”; the final packaged run passed. No guard was bypassed in production code to make that fixture pass.

No live user recording, microphone recalibration, profile replacement, paid call or real routine change was performed. Voice identification and intent remain approximate; use a longer clear phrase such as “Hey Bob, please stop talking.” Background overlap and physical audio playback require acceptance testing with the normal microphone/speakers. Public mode stays generic, meeting/text-only modes stay silent, and code blocks stay summarized.

Launch `dist/release-0.11.3/Bob/Bob.exe` with `_internal` beside it. No ZIP is needed. [Changes and manual test steps](RELEASE-0.11.3.md).
