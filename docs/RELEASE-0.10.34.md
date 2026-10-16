# Bob 0.10.34

- Whisper speech filtering is tuned for short commands. If it produces no words, Bob retries once without that second filter only when the audio contains sustained speech-like sound. Silence and broadband hiss do not trigger the retry. Decoder confidence and no-speech rejection remain active.
- Saved-voice matching no longer silently drops a capture when its verification finishes after the receive timeout. Matching work is bounded to prevent a background-voice backlog.
- A completed captured utterance reuses its successful voice match instead of running that same check again before transcription. This cache applies only to the exact audio object and current profile settings; unknown speakers still cannot issue voice commands.
- The UI shows checking/transcribing stages and explains rejected saved-voice matches. Test voice match now captures independently of the saved-voice filter so a failing profile can be diagnosed.
- Keeps manual Finish sample enrollment from 0.10.33.

## Quick test

1. Close old Bob. Launch this Bob.exe with _internal beside it.
2. Settings → Recognize my voice → Test voice match. Say a full sentence; check the result. Saved-voice-only mode still needs a confident match.
3. Start voice conversation and say “Bob, please open calculator for me.” Watch Capturing → Checking your saved voice → Transcribing, then the request and reply.
4. Say “What time is it?” and another longer request at your normal volume. If voice matching rejects a capture, Bob now explains this beside the voice controls instead of silently waiting.
5. Speak while Bob replies to interrupt. Then try an unenrolled person's voice: it must not execute a request while saved-voice listening is enabled.
6. Silence should not produce commands. Uncertain decoded words still appear for review rather than being executed automatically.

These fixes do not guarantee matches in loud noise or for very short utterances. No saved profile, recognition preference, or paused routine was changed. Enrollment samples are acoustic examples, not a dictation test; they are not transcribed into chat.
