# Bob 0.10.29 verification

- 294 Python regression tests, including all 91 advertised tool-action validation contracts, profile isolation, natural memory, location validation/refresh, automation schedule and once-only approval execution.
- Frontend production build and ESLint for the changed components passed.
- Packaged native UI audit: 93 checks passed, including location buttons and recognized/uncertain avatar changes. External integrations in this audit are simulated.
- Packaged voice round trip, interruption command execution, six-page navigation and layout overflow checks passed using injected audio/fixture results.
- Packaged X-button shutdown stops routine and reminder workers.
- Real local qwen3:8b checks: volume reduction, compound YouTube/volume, close all YouTube, negation, optional voice-identification question, and daily routine creation. Dry runs only; no native actions executed. New voice-identification and routine checks took about 2.7 and 3.4 seconds with a warm local model; cold responses can take longer.
- Real Windows location: a fresh position was available on this PC, accuracy approximately 241 metres. Coordinates were not printed, persisted in the test report, or sent to external services.
- Real native confirmation fixture: passed: approval executed, speech onset did not cancel execution, and the owned disposable test window closed. No microphone was used.

The first local-model routine prompt returned a duplicate create action; existing duplicate-action validation would reject it before execution. The protocol was clarified and the repeated dry run returned exactly one routine action. Model replies claiming success before execution are discarded; the routine is saved only after one user approval.

Limitations: these checks do not establish faultless biometric identity, noise rejection for every microphone, or operation of every arbitrary website/app. Live user voice enrollment was not overwritten or tested. No carrier call was placed in this upgrade. Scheduled routines require Bob/PC running and idle during the scheduled minute; no event triggers, catch-up scheduling, or arbitrary unattended sensitive actions. Natural memory deliberately extracts only clear supported personal statements; it is not comprehensive semantic extraction. Voice profiles are personalization, not a security boundary. Local route times are not live traffic.

The initial final UI voice check timed out on local-model startup. The UI test flag now injects fixed model replies to check the voice lifecycle deterministically; actual model understanding is covered by the separate six dry runs. A Windows loopback remote-access fixture also encountered a transient connection abort; the full suite was rerun.
