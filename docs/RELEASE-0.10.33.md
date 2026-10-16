# Bob 0.10.33

- Enrollment now waits for **Finish sample**, with up to 60 seconds per recording. Mid-sentence pauses no longer end your sample.
- Added a recording timer and **Cancel recording**. Cancel discards the current take and preserves earlier accepted samples.
- Enrollment uses a dedicated capture path instead of conversational endpointing or saved-speaker filtering. This also lets a new person enroll when saved-voice-only mode is enabled.
- Normal commands, interruption timing, and sample quality requirements remain unchanged.

## Test it

1. Close old Bob, launch this Bob.exe with _internal beside it.
2. Stop voice conversation. Settings → Recognize my voice → enter your name → Record sample.
3. Wait for Listening. Read slowly, pause for several seconds halfway through, and finish reading. Bob should keep recording.
4. Click Finish sample. After processing, the sample count increases if the audio meets quality requirements. Repeat for three varied samples.
5. Start another sample and click Cancel recording: the sample count must not increase. Quiet/short takes still require another attempt.
6. Test voice match, then save recognition settings. Ordinary commands still use normal fast endpointing.

The example text is optional. Speak naturally for at least four seconds of clear speech per take; aim for eight to twelve seconds. Recording ends at 60 seconds, or 30 seconds if speech never starts. Speaker identification remains approximate; live microphone testing with your voice is still needed.
