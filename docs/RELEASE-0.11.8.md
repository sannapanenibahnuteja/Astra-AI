# Bob 0.11.8 — neural speech checks and a larger recognition option

## Changes from 0.11.7

- A completed interruption candidate must pass an independent local Silero neural
  speech check before voice matching and transcription. Missing or failed neural
  inference retains playback. This runs on the verification worker, never the
  real-time capture callback.
- During a reply, a wake phrase by itself no longer stops it. Use a complete
  addressed request such as “Hey Bob, open calculator” or “Hey Bob, please stop
  talking.” Wake-only activation while idle still arms the next request.
- Completed speech can reach final verification using sustained evidence across
  an utterance, rather than requiring dense speech in one short window. This
  helps quiet words and consonant gaps. It nominates a candidate only; it does
  not bypass neural speech, saved-speaker, transcript or response-permit checks.
- Interruption transcription does not use vocabulary/hotword hints, which could
  bias an unclear sound toward an expected word. Normal command hints remain.
- Explicitly focused profiles are verified directly. Duplicate enrollments no
  longer have to compete to win automatic identification for this binary check.
  Automatic profile switching still requires a clear inter-profile margin. Voice
  matching remains approximate personalization, never authentication.
- Pause learning now occurs only after activation/attention checks on accepted,
  confident text from a matched speaker. Rejected chatter, noise and uncertain
  transcripts cannot update it. Existing on/off and forget controls remain.
- Settings → Conversational audio offers Small English and the bundled larger
  Distil-Whisper Large v3 model. Change models only after ending the voice session
  and response, then Save settings. Missing models cannot be selected; switching
  clears the previous loaded model. Runtime never downloads a model automatically.
- A generated-speech diagnostic compares both models without opening the
  microphone, making calls or running commands.
- Duplex startup explicitly requests WASAPI shared mode and retries the same
  endpoints with a more tolerant buffer if low-latency startup fails. It does not
  silently switch to another microphone. A recoverable single driver dropout no
  longer aborts playback; repeated failures remain visible audio errors.

## Try it

1. Quit the previous Bob and launch `dist/release-0.11.8/Bob/Bob.exe`. Keep
   `_internal` beside it; no ZIP extraction is required.
2. In Settings, enable saved voice recognition, choose your profile under focused
   listening, and enable verified voice interruptions. Save settings.
3. Ask “Hey Bob, explain how computers work.” During generation and playback,
   tap the table or cough. The reply should continue. Report any actual cutoff;
   this guide does not certify zero errors in every room.
4. During a reply say the whole phrase “Hey Bob, please stop talking.” Bob waits
   for completed, verified speech; it does not stop on the first sound.
5. Interrupt with “Hey Bob, open calculator.” Verify the actual window opens.
   Noise rejection, speaker matching, endpointing and command execution are
   different stages; a successful transcript is not action success.
6. End the conversation before choosing the larger model in Conversational
   audio. Save, restart the conversation, and compare your normal requests.
   Small remains the faster default; choose it again if Large is too slow.
7. Turn off Learn my speaking pauses, or use Forget learned speaking pauses, to
   control local adaptation. No neural weights or identity thresholds self-train.

## Model and performance limits

The larger model has 756 million parameters and is English-only. It is a pinned
upstream model, not a model newly trained on the owner's conversations. See the
[official model card](https://huggingface.co/distil-whisper/distil-large-v3) and
[converted model](https://huggingface.co/Systran/faster-distil-whisper-large-v3).
The conversion revision is `c3058b475261292e64a0412df1d2681c06260fab`.

In a development CPU INT8 comparison with two threads, three generated Windows
speech clips were transcribed correctly by both models. Small took about
2.3–2.6 seconds per clip; Large took about 10 seconds. Large is not a guaranteed
speed or accuracy improvement on this laptop. These clean generated phrases do
not measure the user's accent, overlapping speakers, live background noise or
end-to-end voice-command latency. The app still uses CPU INT8 for recognition;
GPU acceleration was not added in this release.

Bob already uses neural transcription and speaker models. This release adds a
separate neural speech gate and an optional larger ASR model; it does not enlarge
the speaker model, retrain a personal voice, or change the chosen Windows/Azure
output voice. Natural conversation adapts through accepted local pause statistics
and existing user-controlled preferences/memory, not uncontrolled self-training.
