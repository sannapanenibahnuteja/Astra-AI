# Bob 0.11.0 — verification report

Tested on this Windows workspace on 19 October 2026. Machine-readable evidence: [TEST-RESULTS-0.11.0.json](TEST-RESULTS-0.11.0.json).

## Passed

| Check | Result |
|---|---|
| Full Python regression suite | **371 passed**, 30.857 s in normal Windows context. Includes existing Windows/browser/media/phone contracts and 28 new audio/policy tests. |
| Frontend | Vite production build passed. ESLint passed for the new audio panel and changed conversation controls. |
| Packaged EXE UI | **120 checks passed**: navigation, settings, voice enrollment controls, noise level, autonomy, diagnostics reset, public mode, memory, routines and day-planner controls. External integrations and microphone speech are simulated in this UI audit. |
| Packaged startup / reply handoff | Correct Bob assets, no horizontal overflow at 1366 px, voice-ready handler, simulated voice round trip and interruption command executed. |
| Packaged native close | Window X request exits and stops scheduler/reminder workers in an isolated fixture. |
| Packaged native DSP | 10 ms / 48 kHz frames; seeded echo reduction **17.7 dB**; native AEC frame p95 **0.259 ms**, max **0.480 ms** during this run. All suppression levels accepted finite aligned frames. |
| Controlled detector | 120 ms sustained onset during established playback; 450 ms quiet endpoint for a short turn. Uses controlled VAD input; not an acoustic accuracy measurement. |
| Packaged speaker model | Varied generated phrases matched, similarity 0.970 at threshold 0.650; encrypted reload matched; fixture profile deleted. No real user profile was modified. |
| Separate speaker/transcription paths | Generated held-out voice matched both (0.936 / 0.916). Unregistered generated voice rejected. Echo-only speaker path reduced simulated echo 20.4 dB. Added 10 dB broadband-noise fixture matched. Very short ambiguous speech remained rejected. |
| Idle UI fixture | 0.0% CPU over a 3-second sample after hiding/suspending renderer; 513.3 MB summed working sets across 7 processes. Includes possible shared-page double counting, excludes Ollama and active speech models. This is not a promise of real voice-session resource use. |

## New regression coverage

Exact ducked playback/AEC reference; ramped playback gain; anti-alias resampling; calibrated channel alignment; noise-estimate initialization; optional source consent/hysteresis; invalid extractor output; unknown-speaker ASR rejection; final-recognition priority; latest-only preview queue; stale preview cancellation; speaker-focus changes during inference; semantic pause bounds; activation and independent speaker proof; ordinal context isolation; interrupted-answer context; public/silent speech policy; derived pause statistics; action success/failure/cancellation replay protection; autonomy and frozen IDs; unverified launch failures; capability-honest diagnostics; and cancellation before native execution.

Existing command regressions passed, including scoped tab/window references, pending confirmation/correction, repeat actions, voice model intent, enrollment, reminders, UI controls, and profile memory. A passing contract test does not mean every external application or hardware variant was exercised live.

## Limits and remaining acceptance tests

- Your microphone was **not recorded** for these tests. Existing saved voices and microphone calibration were preserved. Repeat the guide’s live-voice test table using your usual laptop microphone.
- DSP timings exclude speaker matching, Whisper, model generation, synthesis and physical output latency. Sub-300 ms verified cancellation is **not** established; fast temporary duck and slower identity confirmation are distinct.
- Simulated/generated speech is not a measured false-activation rate, missed-activation rate, accent score, or proof of noisy-room/overlap accuracy.
- No target-separation model, continuous diarization, automatic microphone switching, camera attention or multi-device fusion was installed. Optional array processing needs synchronized exposed channels and calibrated delays.
- Phone integration contracts were regression-tested; no paid carrier call was placed in this release run. Existing Twilio settings were not changed.
- Action IDs are process-local. They do not provide crash-proof exactly-once delivery across external services. Failed actions require a deliberate new request.
- The attachment’s camera section and earlier VAD request ended mid-sentence. Camera remains disabled; no assumptions were made about missing camera permissions or behavior.

Launchable output: `dist/release-0.11.0/Bob/Bob.exe`, with `_internal` beside it. No release archive is required.
