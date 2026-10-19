# Bob 0.11.2 — owner voice and deliberate interruption

19 October 2026. Machine-readable evidence: [TEST-RESULTS-0.11.2.json](TEST-RESULTS-0.11.2.json).

- **405 Python regressions passed**, 31.223 seconds. Includes **21 new interruption-intent/ownership tests**.
- Frontend production build and ESLint for the changed audio-settings panel passed.
- **123 packaged native UI checks passed**, including strict-interruption preference off/on and persistence, along with existing settings, profiles, memory, routines and planner controls. Audit waits for saves to finish. Functional state updates prevent rapid audio-setting edits overwriting one another.
- Packaged native audio checks cover directed control acceptance, high-confidence gibberish/undirected narration rejection, uncertain-word rejection, tiny noise/click rejection, native echo cancellation and suppression. These are controlled fixtures, not live speaker-intent accuracy measurements.
- Packaged startup, simulated interruption → new request handoff and native X-button shutdown are checked in isolated data folders. UI speech and integrations are simulated.

New regression coverage: other enrolled/unknown speaker rejection before interruption ASR; no proof when identity is disabled or owner absent; own-voice gibberish rejection; confident directed requests and corrections; polite phrasing; no active-profile mutation; stale inference and mid-inference focus changes; model-lock contention; no acoustic-only cancellation/ducking in strict mode; reply-start capture timing; idle voice matches not creating an unproved reply stop; accepted interruption delivery/acknowledgement; reusable final transcription proof; and pure “Bob, stop” being consumed as a reply control instead of an app/media request.

The default guard requires enabled saved-voice recognition and a selected/current recognized profile. Without identity proof or confident local recognition, it keeps the reply playing. A user may explicitly opt out in Settings. The Stop button remains available.

Identity matching and directed-word detection remain approximate. Clear intent is inferred conservatively from recognized words and cues; Bob cannot know private mental intent. The 250 ms controlled acoustic gate is not a guarantee of full voice/ASR verification latency. Bare short words may not contain enough speaker information; prefer “Bob, please stop talking.” Overlapping speech and strong echo still need live acceptance testing with the normal microphone.

No live user recording, profile replacement, microphone recalibration, paid call or real routine change was performed. Existing memory scopes and action validation remain. Launch `dist/release-0.11.2/Bob/Bob.exe` with `_internal` beside it; no ZIP is needed.
