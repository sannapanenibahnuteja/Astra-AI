# Bob 0.11.8 candidate verification — 25 October 2026

**Status: automated checks passed; final live interruption acceptance is pending.**
This is not a claim that the reported microphone problem is resolved.
[Machine-readable evidence](TEST-RESULTS-0.11.8.json).

## Final source and packaged checks

- **496 Python tests passed** in 42.090 seconds. Added coverage includes neural
  evidence rejection, complete-request intent, focused duplicate-profile checks,
  active/missing model-switch protection, WASAPI same-device retry, recoverable
  driver dropouts, completed-utterance nomination and trusted pause learning after
  activation validation.
- Frontend production build passed; ESLint passed for both audio settings panels.
- PyInstaller built a runnable folder with Small English and the pinned optional
  Distil-Whisper Large v3 model. No personal voice profile or calibration is bundled.
- **164 packaged UI checks passed**, including both model selection values and
  restoration. Voice, links, app actions, phone and other UI integrations use
  isolated fixture implementations in these checks.
- Packaged startup and voice-turn handoff passed at 1366px without horizontal
  overflow. Window X stopped fixture schedulers and reminders.
- Packaged synthetic audio passed: 17.7dB seeded echo attenuation, real local
  neural rejection of generated noise/taps, and cancellation proof boundaries.
  The controlled acoustic onset is 120ms and acoustic gate 250ms. These are not
  end-to-end saved-voice interruption latency claims.
- Packaged generated-speech checks passed for both ASR models on three Windows
  voice phrases, with zero measured word errors on that small synthetic sample.
  The neural detector accepted all three. Generated double-talk through actual
  WebRTC DSP and capture produced a candidate accepted as neural speech.
  No microphone was used for these packaged tests.

## Live trials and unresolved acceptance

The user authorized and operated temporary checks on the laptop microphone and
speakers. No raw recordings, transcripts or private profile data were saved.

1. First trial: playback survived the noise stage, but deliberate interruption was
   not accepted. This was a failed acceptance test.
2. Diagnostic 2: duplex startup failed with a PortAudio host error. The test never
   reached voice verification. The implementation subsequently made WASAPI shared
   mode explicit and added a same-device buffer retry.
3. Diagnostic 3: duplex startup and playback worked, but the deliberate phrase
   still did not interrupt. The counters recorded no eligible authorization
   candidate. The implementation subsequently added completed-utterance acoustic
   evidence across gaps while preserving all final neural/speaker/intent checks.
4. Diagnostic 4: prepared for a user-started check with capture/rejection counters
   and signal-present flags. Its result is still needed. Until then, the final
   microphone behavior is **unverified**, not passed.

Earlier candidate diagnostics were discarded as final evidence after the
completed-utterance fix. A shadowed counter name in the diagnostic reporting code
was also corrected; final native evidence reports the actual 120ms controlled
onset rather than a generated tap offset.

## Performance and feature limits

The source CPU INT8 comparison took about 2.3–2.6s per generated clip for Small
and 10s for Large. The packaged comparison ran concurrently with other fixtures
and took longer; its exact results are in the JSON. Neither is a live-user or
overlapping-speaker accuracy benchmark. The faster model remains default.

The speaker and output-voice neural networks were not enlarged or retrained.
Local timing adaptation stores bounded per-profile pause statistics and cannot
weaken identity or interruption thresholds. Optional Windows/Azure output choices
remain; Azure cloud synthesis and real carrier calls were not tested here.
No real external messages were sent. Instagram/WhatsApp sending workflows were
not implemented by this voice upgrade.

[Changes and manual tests](RELEASE-0.11.8.md). Keep `_internal` with Bob.exe.
Treat this as a candidate until the outstanding live trial is reviewed.
