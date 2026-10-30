# Conversation reliability specification — implementation status

This is an implementation inventory, not a claim that all 100 requirements are complete. The priority is correct-speaker actions and graceful recovery. A running Windows laptop and measured live trials are needed for final acoustic acceptance. Engineering targets are not guarantees.

## This update

Bounded active ASR thread allocation (half logical CPUs, maximum four), exact low-risk spoken local-command fast lane; completed-turn handoff ownership; idle deadline grace; matched-user alternate echo-cancelled decode; explicit empty-capture recovery; cancelled-session restart ordering; narrow, one-use expected-answer continuation by the same saved speaker (12 seconds); microphone callback stall detection; bounded model output queue (64 chunks), cancellable reads and a 180-second total stream limit; bounded metadata-only capture traces and replay; p50/p90/p95/p99 timing aggregates; explicit 12-stage latency budgets in Settings; seeded generated-speech benchmark at clean, 20, 10, 5, 0 and -5 dB SNR.

## Critical boundaries

- Streaming preview is incremental local decoding, not a native token-streaming ASR service. Its 1.5-second preview interval does not meet a 150–300 ms first-partial goal.
- Voice interruptions retain full neural/saved-speaker/transcript/intent verification. Sound-only ducking is intentionally unavailable because it caused room-noise interruptions. No claim of sub-200 ms verified interruption is made. Stop in the UI remains immediate.
- English local models remain English. No automatic multilingual/code-switching model or contact-driven N-best recognizer is installed.
- Room/SNR labels are signal heuristics, not trained cafe/car/music classification. Scores are not calibrated correctness probabilities.
- No installed overlapping-speaker separator, continuous unknown-speaker diarization, direction finder, dynamic beam-steering array or camera attention. A synchronized calibrated delay-and-sum seam remains.
- Watchdog reports stalled input rather than silently changing microphones. No device reconnect, Bluetooth codec identification, network microphone jitter buffer or provider circuit-breaker/failover is claimed.
- Action operation IDs are process-local, not durable exactly-once transactions across crashes. Failed or uncertain actions are not automatically replayed. General undo needs action-specific implementations.
- The timing panel distinguishes unmeasured stages. Output latency is the driver estimate; physical audibility and total speech-end-to-ear timing require loopback measurement.
- Synthetic WER is separate from intent accuracy, executed-action accuracy, missed commands and false actions. Those rates require labeled real trials; no rates are invented.
- Only narrow expected answers bypass a repeated wake word, and only for the same confidently matched profile. Arbitrary background commands never gain this permission.

## Requirement-by-requirement inventory

“Integrated” means a working foundation exists, with scope limits in the notes above and architecture guides. “Partial” means only some requested mechanisms exist. “Unavailable” identifies substantial missing models, hardware/integrations or acceptance evidence.

| # | Requirement | Status |
|---|---|---|
| 1 | Build a latency budget | Partial; targets or extensions pending |
| 2 | Parallelize the pipeline aggressively | Partial; targets or extensions pending |
| 3 | Separate prediction from commitment | Integrated foundation |
| 4 | Prewarm everything possible | Partial; targets or extensions pending |
| 5 | Local fast-path engine | Integrated foundation |
| 6 | Instant stop must bypass the normal stack | Partial; targets or extensions pending |
| 7 | Multi-stage ASR | Partial; targets or extensions pending |
| 8 | N-best transcript reasoning | Unavailable / not validated |
| 9 | Phonetic personal lexicon | Partial; targets or extensions pending |
| 10 | Accent adaptation | Unavailable / not validated |
| 11 | Code-switching support | Unavailable / not validated |
| 12 | Dynamic ASR model selection | Partial; targets or extensions pending |
| 13 | Real-time audio quality score | Partial; targets or extensions pending |
| 14 | Detect impossible audio early | Partial; targets or extensions pending |
| 15 | Microphone health monitoring | Unavailable / not validated |
| 16 | Bluetooth-aware handling | Unavailable / not validated |
| 17 | Jitter buffers | Unavailable / not validated |
| 18 | Predictive audio buffering | Integrated foundation |
| 19 | Post-speech audio tail | Integrated foundation |
| 20 | Acoustic scene memory | Integrated foundation |
| 21 | Noise fingerprinting | Unavailable / not validated |
| 22 | Dynamic beam steering | Unavailable / not validated |
| 23 | Multi-beam tracking | Unavailable / not validated |
| 24 | Target-speaker persistence | Integrated foundation |
| 25 | Overlap detection | Unavailable / not validated |
| 26 | Echo-path adaptation | Integrated foundation |
| 27 | Double-talk detection | Integrated foundation |
| 28 | TTS ducking before cancellation | Unavailable / not validated |
| 29 | Speech-state prediction | Partial; targets or extensions pending |
| 30 | User-specific endpoint model | Partial; targets or extensions pending |
| 31 | Prosody-aware endpointing | Unavailable / not validated |
| 32 | Incremental semantic parser | Partial; targets or extensions pending |
| 33 | Incremental context resolver | Partial; targets or extensions pending |
| 34 | Cache recent tool results | Integrated foundation |
| 35 | Prefetch likely context | Partial; targets or extensions pending |
| 36 | Intent-router fast path | Integrated foundation |
| 37 | Response-first-token optimization | Integrated foundation |
| 38 | Separate spoken answer generation from deep reasoning | Partial; targets or extensions pending |
| 39 | Short-first spoken response | Partial; targets or extensions pending |
| 40 | Pre-generated conversational micro-responses | Partial; targets or extensions pending |
| 41 | Silence is a feature | Integrated foundation |
| 42 | Adaptive TTS chunk size | Partial; targets or extensions pending |
| 43 | TTS prebuffer tuning | Integrated foundation |
| 44 | Sentence-aware TTS | Integrated foundation |
| 45 | Speculative TTS carefully | Partial; targets or extensions pending |
| 46 | TTS pronunciation dictionary | Unavailable / not validated |
| 47 | Audio-device output latency measurement | Partial; targets or extensions pending |
| 48 | Prevent assistant self-triggering | Partial; targets or extensions pending |
| 49 | Wake-word false-positive suppression | Partial; targets or extensions pending |
| 50 | Wake-word false-negative recovery | Integrated foundation |
| 51 | Multi-turn predictive context | Integrated foundation |
| 52 | Expected-answer grammar | Integrated foundation |
| 53 | Context-dependent ASR biasing | Partial; targets or extensions pending |
| 54 | Confidence fusion | Unavailable / not validated |
| 55 | Confidence calibration | Unavailable / not validated |
| 56 | Reliability tiers | Integrated foundation |
| 57 | Never guess important entities | Integrated foundation |
| 58 | Automatic repair before asking the user | Partial; targets or extensions pending |
| 59 | Minimal repair prompts | Partial; targets or extensions pending |
| 60 | Repeat-with-context behavior | Partial; targets or extensions pending |
| 61 | Frustration-resistant behavior | Partial; targets or extensions pending |
| 62 | Conversation watchdog | Integrated foundation |
| 63 | Hard timeouts | Integrated foundation |
| 64 | Circuit breakers | Unavailable / not validated |
| 65 | Provider abstraction | Unavailable / not validated |
| 66 | Health checks | Partial; targets or extensions pending |
| 67 | Offline degraded mode | Integrated foundation |
| 68 | Fast reconnection | Unavailable / not validated |
| 69 | Idempotency everywhere | Partial; targets or extensions pending |
| 70 | Conversation transaction model | Integrated foundation |
| 71 | Per-action rollback where possible | Unavailable / not validated |
| 72 | Realtime priority scheduling | Integrated foundation |
| 73 | Separate realtime thread/process | Integrated foundation |
| 74 | Avoid garbage-collection spikes | Partial; targets or extensions pending |
| 75 | Backpressure | Integrated foundation |
| 76 | Resource-aware inference | Unavailable / not validated |
| 77 | Adaptive processing ladder | Partial; targets or extensions pending |
| 78 | GPU acceleration | Unavailable / not validated |
| 79 | Warm-model cache | Integrated foundation |
| 80 | Fast resume | Partial; targets or extensions pending |
| 81 | Priority interrupt channel | Partial; targets or extensions pending |
| 82 | Conversation-state snapshots | Unavailable / not validated |
| 83 | Deterministic state transitions | Integrated foundation |
| 84 | Race-condition tests | Integrated foundation |
| 85 | Stress-test audio | Partial; targets or extensions pending |
| 86 | Add synthetic noise testing | Partial; targets or extensions pending |
| 87 | Real-room tests | Unavailable / not validated |
| 88 | Measure word-error rate selectively | Partial; targets or extensions pending |
| 89 | End-to-end command accuracy | Partial; targets or extensions pending |
| 90 | False-action rate | Unavailable / not validated |
| 91 | Missed-command rate | Unavailable / not validated |
| 92 | Barge-in success rate | Unavailable / not validated |
| 93 | Turn-cutoff rate | Unavailable / not validated |
| 94 | Dead-air metric | Integrated foundation |
| 95 | Tail-latency optimization | Integrated foundation |
| 96 | Reliability SLOs | Unavailable / not validated |
| 97 | Automatic performance regression tests | Partial; targets or extensions pending |
| 98 | Record structured traces | Integrated foundation |
| 99 | Replay system | Integrated foundation |
| 100 | Reliability-first final principle | Partial; targets or extensions pending |

## Reproduce checks

Run `venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py"` for deterministic guards/recovery/replay. Some existing device tests need normal Windows WMI and localhost access.
Run `venv/Scripts/python.exe scripts/benchmark-conversation-audio.py --output .cache/conversation-snr-benchmark.json`. It renders public canned phrases locally, mixes fixed seeded noise/hum, decodes with the installed model and writes only aggregate trial metadata/WER. It does not use the microphone, execute commands or upload audio.
Use Settings → Conversational audio → Latency targets and measured tail latency to see observed stages. Missing observations remain “not measured.” Reset diagnostics clears session aggregates; traces stay bounded in RAM and are never saved automatically.
Run live acceptance in the actual room: quiet baseline, fan, taps/coughs, another speaker taking turns, then deliberate overlap. Record command/action outcomes and interruption latency with ground truth. This update has not completed those live trials.
