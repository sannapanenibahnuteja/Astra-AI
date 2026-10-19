# Bob 0.11.1 — quiet-room interruption fix

- Fixes the next spoken sentence stopping merely because the sensitive capture detector noticed a possible sound. Only an actual unconsumed interruption stops sentence playback. Consuming the new request allows its answer to speak normally.
- Removes the quiet-sound shortcut through playback onset detection.
- Adds a separate interruption gate: strict, unboosted WebRTC speech evidence, an independent minimum signal floor, and sustained speech over roughly 240 ms with short consonant gaps allowed. Capture sensitivity while Bob is idle is preserved.
- Applies the same gate to playback ducking and early speaker checks. Short clicks, rustles and tiny signals cannot accumulate through speech-detector hangover to stop the reply.
- Incidental captures during playback that never qualify are not queued as commands. Final speaker verification cannot bypass a failed interruption gate. Existing saved-speaker filtering remains enabled according to your settings.
- Explicitly acknowledges consumed/discarded interruption turns so Bob does not remain silent on the next request.

## Try it

1. Close the old Bob and launch this release's `Bob.exe`, keeping `_internal` beside it. Existing profiles and microphone calibration are preserved.
2. Start voice conversation. Ask: **“Explain how a computer works in detail.”**
3. While Bob talks, make one small desk tap or keyboard click. He should continue, including his next sentence; no noise command should appear.
4. Speak normally: **“Actually, just give me the short version.”** Bob should interrupt after sustained speech (and saved-voice matching if enabled), then speak the shorter answer.
5. Try another normal command after interrupting. It must execute and its reply must be spoken.

The duration gate is a processing rule, not a guarantee of physical end-to-end latency. Sustained speech-like noise, loud speaker echo or overlapping voices can still be difficult. No live microphone accuracy claim is made from automated fixtures. See [the test report](TEST-REPORT-0.11.1.md).
