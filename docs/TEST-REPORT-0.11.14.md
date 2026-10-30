# Bob 0.11.14 verification — 30 October 2026

[Machine-readable results](TEST-RESULTS-0.11.14.json).

- **557 Python regressions passed** in 41.005 seconds, including the authenticated mobile gateway and host/origin rejection tests.
- **11 client startup checks passed**: successful pairing, blocked storage, failed Remember preference, blocked history, missing token, manual same-origin pairing, foreign-origin link rejection, expired credentials, stalled fetch without AbortController, non-JSON gateway response and unpair cleanup. The test uses a JavaScript VM with fake DOM/storage/network, not real Safari. A follow-up passed after making the fake browser storage properties enumerable/configurable.
- Frontend production build passed.
- **190 packaged UI checks passed**. Native startup/voice handoff fixture and queued interruption fixture passed with no horizontal overflow at 1366px. Native X-close stopped fixture reminders/schedulers.
- The user's already-running phone gateway returned authenticated state successfully both locally and through the configured private HTTPS endpoint. Only response status/shape were reported. The private pairing URL, token, credentials, reply contents and reminder contents were not printed or changed.

No actual iPhone browser interaction, microphone recording, provider call or voice-accuracy test occurred. A real Safari retry after launching the new EXE is still required. The old running EXE cannot acquire a frozen HTML update merely by refreshing its phone page; quit it and launch 0.11.14 before reopening the complete pairing link. No private pairing rotation or account setup is required by this code change.
