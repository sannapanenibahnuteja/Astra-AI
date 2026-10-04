# Bob 0.10.5 — Full-duplex desktop voice

Changes from 0.10.4:

- Added a local WebRTC AEC3 audio engine. During a desktop voice conversation,
  microphone capture and Bob's speaker playback run simultaneously on WASAPI.
- Rendered Windows speech to PCM instead of allowing a separate process to play
  it. Azure speech uses the same playback path. The exact played samples feed
  the echo canceller, then noise suppression runs before speech recognition.
- Detect sustained user speech, stop playback, cancel pending spoken generation
  and keep 300 ms of pre-roll. Already completed Windows actions are not undone;
  an in-flight native action may finish before cancellation takes effect.
- Keep active voice conversations open during silence; close the audio device
  when the user ends the conversation. Whisper runs only on captured utterances.
- Added bounded audio queues, audio synchronization checks and a safe fallback
  when the device or AEC library cannot initialize.
- Packaged the WebRTC native extension in the Windows EXE.

Testing:

1. Quit the previous Bob from the tray and run the 0.10.5 EXE.
2. Use a real microphone and choose your speakers in Windows Sound settings.
3. Start voice conversation once. Speak without waiting for a beep.
4. Ask: “Tell me a long story.” Listen silently; Bob should not interrupt himself.
5. While Bob speaks, say: “Actually, open Calculator.” Check that his voice stops
   and the complete request appears in the transcript.
6. While a response is being prepared, say: “Never mind, what time is it?”
7. Stay quiet for 15 seconds, then ask another question; the session remains open.
8. Say: “Stop listening.” Check the microphone is released.
9. Repeat at different volumes, and restart the session after changing devices.

Limits: the reference covers Bob's audio, not music/video from other apps.
AEC reduces echoes; it cannot guarantee perfect recognition on every device or
in a loud room. The phone webpage and iPhone locked-screen restrictions are
unchanged. Speech is synthesized per reply; streaming TTS is separate work.

Dependency: pywebrtc-audio 0.2.0, WebRTC AEC3 (Apache/BSD notices packaged with it).

Validation: 107 unit tests passed; frontend build, packaged UI voice round trip,
native Windows automation fixture and ZIP integrity passed. Packaged AEC reduced
simulated delayed noise echo by 23.9 dB and opened the Realtek WASAPI capture and
playback stream. Generated speech echo caused no false interruption; an added
independent speech request was detected and captured. The live microphone sample
was effectively silent, so real simultaneous user speech still needs the manual
test above. These checks do not establish performance on every audio device.
