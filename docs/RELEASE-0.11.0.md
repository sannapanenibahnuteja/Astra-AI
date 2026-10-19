# Bob 0.11.0 — conversational audio and policy

Changes from 0.10.36:

- Keeps the existing WASAPI/WebRTC, saved voices, local Whisper, Ollama, Windows tools and streaming TTS. No framework rewrite or cloud audio requirement.
- Adds bounded, disposable incremental Whisper previews and provisional captions. Unknown speakers are filtered before preview inference when saved-voice filtering is on. Final recognition has priority; previews cannot execute tools or change profiles.
- Ducks playback on sustained speech while checking a saved voice. Exact attenuated playback is the AEC reference. Early identity checks can retry at bounded speech intervals; only a verified speaker cancels a reply when filtering is enabled. Rejected speakers restore normal playback.
- Adds heuristic noise/SNR/clipping diagnostics, configurable light/moderate/stronger WebRTC suppression, optional calibrated delay-and-sum array processing, and replaceable stage interfaces.
- Extends turn timing for incomplete provisional phrases and learns bounded, derived mid-sentence pause statistics per matched profile. Explicit Patient/Thinking pauses remain authoritative. The recording hard limit remains 20 seconds.
- Adds activated-session attention states and an optional group attention filter. This is an extra heuristic, not a probability of identity, gaze tracking or overlapping-voice separation.
- Adds compact per-conversation context, observed numbered-choice resolution, interrupted-answer context, and correction context. Existing frozen confirmation and native repeat/context resolution remain in use.
- Adds focus, driving, meeting, silent, public, private and bedtime conversation modes. Public mode keeps spoken details generic; meeting/silent use text. Voice replies have sentence/word budgets and adjusted pace for selected modes. Full visual replies remain available.
- Adds explicit action autonomy levels, process-local action IDs/states, and replay protection for each approved operation. Sensitive native confirmations remain. Failed or unverified launches do not become successful action-ledger entries. Automatic retries do not replay consequential actions.
- Adds recovery metadata and bounded session diagnostics: observed ASR/model/TTS-dispatch timings, repetitions, failures and verified interruptions. No fabricated accuracy rates; reset controls are available.
- Adds Settings → Conversational audio, live diagnostics, reset diagnostics, and forget learned pauses. Native UI checks cover the new controls.

Launch `Bob/Bob.exe` directly with `_internal` beside it. No archive is needed. Keep existing profiles; do not re-enroll solely for this upgrade. Your real paused routines are not enabled or modified by this release.

Read [the audio guide and tests](CONVERSATIONAL-AUDIO-GUIDE.md) and [architecture](AUDIO-ARCHITECTURE.md). See the accompanying test report for actual validation and its limits. The release does not claim flawless recognition, guaranteed sub-300 ms identity verification, continuous diarization, multi-device audio fusion, automatic microphone switching, camera attention or an installed target-speaker separation model.
