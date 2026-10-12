# Bob 0.10.30

Fixes from 0.10.29:
- Timed routines are no longer blocked by passive voice listening.
- Due tasks persist in a queue when Bob is responding, transcribing or using the action lock. They execute afterward, once, without losing the scheduled minute.
- Startup/wake delays under 30 minutes catch up. Persisted queued runs can resume for up to 24 hours; old unqueued runs are not replayed.
- Editing a schedule re-arms its due time. Paused/manual routines do not run automatically.
- Automations results update every five seconds while the page is visible; scheduler polling stays at ten seconds.
- Recognized user identity is placed early in the local model prompt, with only that profile's memory. Memory relevance now handles punctuation in names and relationship questions.

Test an enabled routine at a local PC time one minute ahead, with step “set volume to 20 percent”. Keep Bob open and listening. Allow ten seconds after the scheduled time, then check volume/result. If busy, it shows Queued and runs afterward. Disable/delete the test routine. Keep Bob and PC running; X quits Bob, so routines cannot run afterward.

Enrol each user in Settings → Recognize my voice. Save different preferences per profile, then ask “What is my favorite drink?” and verify responses follow the recognized user. Voice identification is approximate, not authentication; uncertain speakers do not receive another user's memory.
