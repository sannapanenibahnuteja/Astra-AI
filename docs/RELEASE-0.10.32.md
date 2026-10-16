# Bob 0.10.32

- Replaced the old letter/rings with a three-dimensional colorful particle sphere on black, inspired by the supplied reference. Gentle rotation, smoothed microphone/speech-volume movement, no flashing or large jumps. It remains visible beside the conversation; rendering pauses when hidden or outside the viewport and honors reduced motion.
- Actual playback amplitude is exposed separately from microphone volume. The orb responds to each source during its corresponding turn. No extra microphone or cloud service is used.
- With Recognize my voice enabled, only enrolled voices may issue desktop voice commands or interrupt. Uncertain/unknown voices are discarded before Whisper transcription and do not reach chat. Choose Saved voices only for all enrolled users, or focus on one user.
- Speaker verification runs off the audio-processing thread before canceling Bob's reply. It does not switch the active profile while checking background speech. Verified full utterances still select the correct profile and memory.
- New enrollment requires three varied samples with at least four seconds of usable speech each. Aim for eight to twelve seconds per sample. Captured usable speech is shown; clipping, silence, broadband noise and inconsistent samples are rejected. Existing encrypted profiles remain available.

## Try it

1. Close the old EXE and launch this release with `_internal` beside it.
2. Settings → Recognize my voice: enroll each person separately in a quiet room. Speak naturally using varied sentences for eight to twelve seconds per sample; exact wording does not matter. Watch the captured-speech total. Existing users can test their saved profile before deciding whether to re-enroll.
3. Enable recognition, select Saved voices only (or your specific profile), and Save settings. With recognition off, ordinary voice input remains available; with it on and no enrolled profiles, no spoken commands are accepted.
4. Start voice mode and say “Bob, please open calculator for me.” A matched saved speaker should execute it and select their profile. Have an unenrolled person say the same request: it should be ignored. If focused on one person, other enrolled people should also be ignored.
5. While Bob speaks, use a full sentence to redirect it. Recognition-enabled interruptions wait for roughly 1.6 seconds of voiced speech plus verification time. Very short words may be ignored. For a pending approval, use “Yes please go ahead and do it”.
6. Observe the orb while speaking and listening to a reply: its motion follows volume softly. Minimize Bob: animation stops. Windows reduced-motion preference gives a still sphere.

Speaker identification is approximate, not authentication. This does not isolate overlapping speakers from a single microphone, guarantee matches in loud noise, or block other speakers from triggering the Windows wake-word listener. A close microphone/headset and quiet enrollment improve the odds. Recordings/TV/replayed voices can fool biometric matching. Desktop microphone commands are gated; paired phone text/call access keeps its existing access controls.
