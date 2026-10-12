# Bob 0.10.30 verification

- 303 Python tests passed. Scheduler tests cover passive listening, busy-response deferral past the due minute, transcribing, persisted queue across restart, native action-lock contention, delayed polling, midnight recovery, disabled routines, expiry and once-only execution. A real worker-thread test triggers on the system clock during listening without calling tick manually; its action is simulated, and no Windows settings are changed.
- Recognized-profile prompt tests demonstrate Alice's prompt contains only Alice's drink preference and Ben's only Ben's, plus their corresponding names. Relationship relevance includes punctuation in “Who is Maya?”
- Frontend production build and ESLint for changed components passed.
- Final packaged UI controls, voice-loop/interruptions and shutdown diagnostics are recorded in the release ledger. UI external integrations and voice input/model replies are simulated.

Scope: these tests verify scheduler timing and data routing, not flawless voice biometrics or every third-party application/hardware control. No user enrollment was overwritten. No carrier calls were placed. Schedules use the PC's local clock, need Bob/PC running, and poll every ten seconds. Startup/wake delays under 30 minutes catch up; already queued runs expire after 24 hours. Routines do not run with Bob closed.
