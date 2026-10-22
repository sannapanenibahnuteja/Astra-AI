# Bob 0.11.5 — completed-phrase interruption protection

The microphone stays active, but sound onset, provisional words and voice identity alone cannot stop or lower a reply. Interruption now commits only after a completed turn passes the sustained-speech gate, matches the selected/current saved user, and contains a confident explicit phrase. Low-confidence individual words cannot be hidden by a high average transcript score. Accepted commands retain their completed transcript and are delivered once to the existing action pipeline.

**Settings → Conversational audio → Allow verified voice interruptions:** on permits this completed verification; off disables voice interruptions entirely. Every setting combination keeps authorization installed. Turning off wake-only idle conversation mode never enables unaddressed or noise-only reply interruption. The legacy acoustic-duck preference cannot weaken this policy. The Stop button remains available.

**Enable Recognize my voice and select yourself under Focused listening.** If recognition is off, Bob does not accept voice interruptions. The UI now says so explicitly. Existing saved recordings are preserved; no re-enrollment or automatic microphone/profile changes were performed.

## Efficiency and reliability

- Removed up to three speculative speaker/ASR interruption passes per candidate while replies play. Only completed eligible turns reach the interruption decoder.
- Provisional captions pause during active replies so preview Whisper work does not compete with playback/final recognition. The microphone remains active; captions resume during normal listening.
- Pure appearance edits no longer rebuild voice policy, close a speaker model or invalidate an in-flight capture. The UI also reuses its appearance object between audio-status updates.
- A stale/duplicate interruption that fails its final commit is not queued as a later command. Strict authorization cannot be bypassed through an onset callback.
- Existing direct app/site launches, constrained UI interpretation, contextual agent/tool validation, complete spoken replies and profile-scoped memory remain. This is a focused audio/shared-path optimization, not a claim that every possible feature or environment is perfect.

## Test it

1. Close old Bob; launch `dist/release-0.11.5/Bob/Bob.exe` with `_internal` beside it.
2. Settings → Recognize my voice: enable, select your saved profile under Focused listening, Save. Enable **Allow verified voice interruptions**. Restart the voice session after changing audio settings.
3. Say “Hey Bob, explain how a CPU works in detail.” Make a desk click, tap keys, cough or say gibberish. These should not authorize stopping or lowering the reply.
4. Say “actually” or “shorter” without addressing Bob: the reply should continue, even if idle wake-only mode is off.
5. Say **“Hey Bob, please stop talking.”** Finish the phrase. Bob should stop only after the completed words and saved voice are verified. There is endpoint/recognition delay; a noise-only 250 ms gate is not the complete latency.
6. During another answer say **“Hey Bob, open calculator.”** After verification, check the real app window and reported result. Native failures must still be reported honestly.
7. Turn **Allow verified voice interruptions** off: all voice interruptions should be ignored; Stop still works. Turn it back on to restore verified interruptions.
8. With saved-voice recognition off, check the visible warning. Noise cannot gain permission through missing identity.
9. While capturing a request, change only an appearance preference with the palette. Cosmetic saves should not reset the voice engine/capture.

Voice and intent matching are approximate; Bob cannot read private intent or guarantee perfect noisy-room recognition. Longer clear phrases help. All tests use controlled fixtures unless explicitly listed otherwise. A real audio stream/device failure is separate from a verified interruption and should be surfaced as an audio error. [Evidence](TEST-REPORT-0.11.5.md).
