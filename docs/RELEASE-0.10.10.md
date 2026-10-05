# Bob 0.10.10 — Optional voice recognition

Changes from 0.10.9:

- Settings has an optional **Recognize my voice** switch, off by default.
- Enroll three spoken samples under your name. Matching uses a bundled local
  speaker-embedding model, distinct from Whisper transcription.
- Desktop voice requests show a likely matching name or an uncertain identity.
  Matched names are available to Bob's conversational model for that turn.
- Profiles contain Windows user-encrypted embedding features, not recordings.
  Delete removes the profile and unfinished enrollment samples.
- Matching uses one CPU thread, loads only when needed and unloads after sixty
  seconds idle. Turning the switch off stops matching and retains the profile.

## Setup and test

1. Quit the old Bob from the tray and run this version's Bob.exe.
2. Stop an active voice conversation before enrollment. Open Settings and find
   **Recognize my voice** near Phone & reminders.
3. Enter your preferred name. Click **Record sample**, read the displayed sentence
   naturally for five to ten seconds, then pause. Repeat for all three samples.
   You do not need to enable matching to enroll.
4. Turn on **Recognize my voice · optional**, then click **Save settings**.
5. Start a voice conversation. Say a full sentence such as “Bob, could you tell
   me what the time is and help me plan my afternoon?” Look for “Voice recognized
   as [your name]”. Bob may use your name naturally; he does not repeat a greeting
   on every request. Routine direct commands still use their brief normal replies.
6. Try several sentences and, with their agreement, another person's voice.
   Check that they appear uncertain rather than as you. If results are unreliable,
   delete and enroll again in a quiet room using your usual microphone.
7. Turn the switch off and save: matching stops. Turn it back on to reuse the
   profile. **Delete voice profile / restart enrollment** erases it.

Recognition is approximate, not a login, owner-only command filter, or liveness
check. Recordings and similar voices can match. Short phrases, overlapping voices
and noise may be uncertain; commands still undergo existing transcription review
and action confirmations. Wake-word standby itself is not restricted to your
voice. This release identifies desktop captured speech, not phone carrier calls
or typed mobile messages. Your live recognition accuracy requires testing after
enrollment; automated tests cannot establish that Bob recognizes your voice.

Implementation follows the [official sherpa-onnx speaker identification API](https://github.com/k2-fsa/sherpa-onnx/blob/master/python-api-examples/speaker-identification.py).
The bundled model is `3dspeaker_speech_eres2net_sv_en_voxceleb_16k.onnx` from the
[official model release](https://github.com/k2-fsa/sherpa-onnx/releases/tag/speaker-recongition-models).
Model download SHA-256 is pinned in `scripts/download-speaker-model.py`.
