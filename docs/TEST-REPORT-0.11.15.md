# Bob 0.11.15 verification — 7 November 2026

[Machine-readable results](TEST-RESULTS-0.11.15.json).

- Complete regression suite: all 585 tests passed after final application and diagnostic changes. These include profile isolation, deleted-memory invalidation, offline retrieval, shortcut conflicts, fresh action verification, failed-action exclusion, cancelled speech decoding, clipping/recovery, web evidence-only answers and escaped SSML.
- Frontend production build and changed-component ESLint passed.
- Actual local Ollama embedding model returned 768-dimensional vectors. With temporary synthetic facts, a dinner question ranked dietary preference 0.5694 above an unrelated sport 0.4325. Another profile returned no facts. No personal memories were inspected by this test.
- Actual public web search returned five usable source entries. Live search is not proof that every source or current-fact answer is correct.
- Actual Windows speech rendering: the same synthetic sentence rendered as Neutral 5.538 seconds, Calm 6.173 seconds, Bright 4.982 seconds. SSML application was confirmed for Calm and Bright. No microphone was recorded and no listening-quality claim follows from duration alone.
- Small English ASR: 18 generated-speech trials with seeded broadband noise and hum; 35 word errors across 108 reference words. Median decoding 1,859 ms, p95 4,172 ms. Across three clean trials, two word errors across 18 words. This is a limited synthetic test, not real-user accuracy or physical barge-in latency acceptance.

Final packaged EXE checks passed:

- 211 native UI contracts, including the learning switches, voice expression choices and both clear controls. Integrations are simulated; this is UI behavior verification.
- Wake/listen/reply simulated voice round trip and queued interruption command execution passed; no layout overflow.
- Native close test passed and stopped the reminder/automation schedulers.
- Native DSP simulation passed: 10 ms at 48 kHz; seeded echo reduction 17.7 dB, p95 DSP processing 0.256 ms, controlled VAD onset 120 ms. Simulated explicit interruption gating passed; unproved callbacks, random generated noise and forged permits were rejected. This is not actual end-to-end microphone latency.
- A three-second hidden-window idle sample measured 1.5% of one CPU core and 488.4 MB summed working set across Bob and its children. Shared pages may be counted repeatedly; Ollama is excluded. This short fixture sample does not measure always-on live recognition resource use.

Launchable folder: `dist/release-0.11.15/Bob`, with required `_internal` beside `Bob.exe`. No ZIP was created.

EXE SHA256: `00ac1fc2132c81e38a3414dfcbb6d91fce6252a32e04a5974476b03c2280ebdc`.

The requested internet, learned-intent, neural-memory and Auto expressive-voice settings were enabled in the existing user data. Other settings, credentials, profiles, memories and routine enable/paused states were preserved. Restart into the new EXE to load all new code.

No live microphone recording, overlapping-speaker separation acceptance, real iPhone interaction, provider phone call or subjective voice-naturalness assessment occurred. The user's real microphone interruption test remains required. Existing AEC, saved-user verification and explicit interruption authorization were preserved; this release must not be represented as perfect recognition or sentient emotion.
