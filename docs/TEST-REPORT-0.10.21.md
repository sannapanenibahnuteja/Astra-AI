# Bob 0.10.21 test report — 12 October 2026

This release changes endpoint timing and local speech-model readiness. It retains the previous command-execution and interruption fixes.

## Evidence

- **231 automated tests passed**, no failures or skipped tests. [Per-check ledger](TEST-RESULTS-0.10.21.json).
- New tests verify exact short/medium/long endpoints, a breathing pause continuing the same turn, fixed mode preservation, model reuse, stale idle timer protection, session-end release timing, shutdown and recovery from preload failure.
- Generated speech through WebRTC echo cancellation: Bob-only echo caused no interruption; simulated user speech at gains 0.5 and 0.1 produced “Actually, open calculator” with accepted transcripts and correct action plans. Both turns completed. This does not execute Calculator or measure a real room.
- Local generated-audio measurement: background preparation 2.177 seconds, subsequent transcription 3.571 seconds, the same loaded model reused. This is one source-run measurement on this machine during a build, not a general latency benchmark or an instant-response guarantee.
- Frontend production build and ConversationControls lint passed.
- Final EXE UI fixture passed voice round trip, interrupted Calculator request, four navigation destinations and no horizontal overflow. Speech and Calculator execution were simulated; Ollama was offline in this isolated fixture.
- Final EXE confirmation diagnostic actually closed its owned disposable Windows fixture after approval, with speech-onset callbacks injected before processing and during execution. No microphone used.
- Packaged Whisper correctly transcribed generated Calculator, time, memory and web-search requests and rejected silence. Generated “stop listening” was marked for review; generated wake phrases were misheard as “bulb” by Whisper. Standby wake detection uses a different Windows recognizer; that recognizer was not retested here.
- The first full packaged speech run timed out at 100 seconds. A single-recording diagnostic succeeded, then a fresh isolated full retry completed within the 30-second sampling window with all eight results. The initial timeout's cause was not established; this is a remaining performance uncertainty, not evidence that every run is fast.

## Limits

Natural mode uses detected speech duration, not semantic prediction of when a person has finished. A pause longer than the configured deadline can still split a thought. Patient and Thinking remain available.

Recognition remains English and completed-turn Whisper. No new real microphone, user's voice identity, phone call, carrier, locked iPhone or every third-party app test was performed. Historical broader live action checks are described in the previous release reports. Automated command contracts are not proof that every action works on every device.

[Changes and test guide](RELEASE-0.10.21.md). [Full voice explanation](VOICE-PIPELINE.md).
