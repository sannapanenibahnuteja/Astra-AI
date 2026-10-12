# Bob 0.10.27 — free local day planning

Changes from 0.10.26:
- Day planner with editable dates, starting address/time, UTC offset, arrival buffer and up to eight ordered appointments or flexible stops. Save/reopen/delete, reorder or sort timed appointments.
- One local Ollama request estimates all drives, with structured JSON validation and a 60-second timeout. No Google Routes account, key or billed calls. Remote model URLs are refused for planning; no background model polling.
- Clear rough-estimate labels: the model has no maps, measured distances or live traffic. Unknown/invalid legs report failure instead of claiming completion or silently using manual values.
- Manual drive-time planning works without a model. Leave/arrival/start/finish timeline, travel totals, timing conflicts and next-day overflow. Appointments are never silently rescheduled.
- Free Google Maps route links for checking real destinations and current traffic; spoken first-departure briefing.
- Five planning tools for conversational creation and follow-ups: “Show my day tomorrow”, “Plan my day tomorrow”, “When should I leave?”, “Open the route to stop two”. Selected-day context carries forward.

See DAY-PLANNER.md for setup and tests. This is driving only; no automatic calendar sync, GPS, shortest-route optimization or proactive traffic monitoring. Optional carrier calls/cloud voices still have their existing provider costs when enabled. This release removes billing from day planning, not from telephone providers.
