# Bob 0.10.27 verification

- 270 Python regression tests passed, including 19 day-planner checks: schedule math, buffer conflicts, multi-stop origins, midnight overflow, durable plans, missing-details refusal, selected-day context, single local request, loopback-only URL restrictions, no proxy, malformed/unknown/out-of-range estimates, failure clearing and manual mode without the model.
- Frontend production build and ESLint on changed JSX passed. Black day-planner preview visually inspected; no routing key/billing controls remain.
- Final packaged EXE: 88 UI contract checks passed, including planner add/reorder/remove/save/manual/local-result/read/link/refresh/delete controls. Integrations in this audit are simulated; it does not prove every real third-party app/provider action.
- Final packaged voice round trip and interruption-command dispatch passed with deterministic fixtures. Six navigation destinations and no horizontal overflow. This is not a real-microphone/background-noise accuracy test.
- Final packaged X-close verification stopped routine/reminder workers. Native screen fixture accessibility read/control and confirmation check passed. These tests use isolated profiles and a disposable window, not personal app content.
- Actual installed qwen3:8b local model returned a validated rough estimate between two public Bengaluru landmarks in approximately four seconds. This confirms local inference connectivity and output shape, not geographical accuracy or live traffic knowledge.
- No Google Routes calls, API keys or billing accounts were used. Local AI calculations never automatically send addresses to a routing provider. Google Maps route opening is simulated in the UI audit; standard URL construction is tested.

See TEST-RESULTS-0.10.27.json for flags, detailed UI checks and final EXE hash. No real carrier call, payment, calendar booking or personal route was executed for this release. Existing optional Twilio/Azure integrations retain provider charges if enabled.
