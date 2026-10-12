# Bob 0.10.29

Changes from 0.10.28:
- Optional Windows location for a dynamic starting point. Named destinations work without a street address. Location is refreshed on calculation or first-route requests; saved plans retain a marker, not coordinates. No continuous tracking or paid routing service.
- Recognized users show their name and initials in the sidebar. Uncertain matches display a neutral identity instead of pretending to recognize someone.
- Bob's model receives accurate information about optional voice identification, enrollment and the current match state.
- Ordinary spoken app launches and selected Edge tab closes execute without an extra approval prompt. Sensitive actions and potentially destructive window closes still require confirmation. Low-confidence transcription still needs review.
- Separate memories and conversations for enrolled voice profiles. Unknown speakers get a separate conversation and cannot read or write the previous speaker's personal memory through conversation commands.
- Automatic local memory of explicit preferences, routines, preferred names and relationships. Controlled in Settings; facts remain editable and deletable in Memory. No added model request for learning these statements.

## Try it
1. Run Bob.exe with its `_internal` folder beside it. Start Ollama.
2. In Settings enable Recognize my voice and enroll each person with a distinct name. Save settings. Speak a full sentence; a clear match changes the sidebar initials/name. A short/noisy sample may remain uncertain.
3. Say “My favorite food is dosa”, “I usually exercise in the morning”, or “Alex is my brother.” Check your profile in Memory. Have another enrolled user say “My favorite food is pasta”; each profile should retain its own preference. Say “What do you remember about my favorite food?”
4. Turn off Remember personal facts from conversations and repeat a new preference: it should not be saved automatically. Explicit “remember that…” remains available. Delete a saved fact in Memory.
5. Ask “Can you recognize me by my voice?” Bob should describe optional identification and its current state, not deny the feature or claim a text message identifies you.
6. Say “Open YouTube”, then “Close all YouTube tabs.” Selected tab closes should execute once without repeated yes/no prompts. Generic app/window closes may have unsaved work and still ask once.
7. In Day planner enable Allow current PC location for trip planning. Open Windows location permissions and allow Location services/desktop app access. Refresh current location, then select Start from my current location. Add a destination such as “Museum, Bengaluru”, save, and calculate. Refresh/calculation obtains a fresh position; accuracy depends on Windows and available sensors.

Voice recognition cannot be guaranteed faultless and is not authentication. Personalization and profile separation do not secure data against someone with access to this PC. Natural memory extraction deliberately saves only clear supported statements; it does not infer every fact from arbitrary conversation. Local driving estimates are rough guesses, not live traffic. Opening a Google Maps route sends its origin and destination to Google.

## Voice automations

Say “Set up a daily routine called Morning at 8 AM: open YouTube and set volume to 35 percent.” Confirm the complete routine once, inspect it in Automations, and keep Bob running and idle at that time. The scheduler runs once that day. Up to twelve explicit steps; daily schedules support opening/search/folders, sound, brightness and media transport. Manual routines can use other supported steps with their normal confirmations. Disable/delete the routine after testing. Conditional/event triggers and runs with Bob closed are not supported.
