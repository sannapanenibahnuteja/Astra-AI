# Bob 0.11.11 — automatic room sensitivity

Listening now adapts to measured room noise. Both room preferences start cautiously. After two seconds of non-speech quiet, capture becomes more tolerant of soft speech; the Quiet room preference needs one second. Eight noisy non-speech frames (80 ms) restore Balanced detection. Playback and detected speech cannot establish quiet. Clipping or invalid measurements restore caution. These are lightweight heuristics, not a trained room or voice classifier.

Capture VAD, soft-speech energy floor and completed-interruption neural evidence use a consistent policy for each utterance. Noise changes cannot relax an utterance partway through. Saved-voice thresholds, confidence requirements, wake/intent rules and response cancellation permits are unchanged. Background speakers still require identity and intended-command checks; this is approximate identification, not a guarantee of separating overlapping voices.

## Try it

1. Quit older Bob; launch `dist/release-0.11.11/Bob/Bob.exe`, keeping `_internal` beside it.
2. Start a voice conversation. Stay quiet for two seconds (one with Quiet room selected), then speak normally: “Hey Bob, open Calculator.”
3. During a reply, tap the table or cough. The reply should continue. Deliberately say “Hey Bob, please stop talking” to test the saved-voice interruption path.
4. Try the same request with a fan running. Sustained non-speech noise restores Balanced capture; voice checks remain.

No microphone audio was collected for this update. Real room, voice and speaker behavior still require live acceptance testing. No new model, cloud service or background inference was added. Existing local preferences and private data are preserved.
