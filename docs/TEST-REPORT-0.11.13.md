# Bob 0.11.13 verification — 30 October 2026

[Machine-readable evidence](TEST-RESULTS-0.11.13.json).

- **556 Python regressions passed** in 44.828 seconds. Includes individual-monitor identity, single-screen write isolation, no-change readback rejection, disconnected/expired reference checks, missing model target rejection, explicit numeric entity preservation, capture/stream races and exact local-control fast paths. Contract fixtures now supply the required brightness display field; negative assertions still ensure missing targets fail closed.
- Frontend production build and audio-panel ESLint passed.
- **190 final packaged UI fixture checks passed**, including rapid cancelled-session restart and visible empty-capture recovery without action dispatch. Voice round-trip/queued interruption fixture passed; no horizontal overflow at 1366px. X-close stopped fixture schedulers/reminders.
- Packaged native synthetic audio checks passed, including actual neural noise/tap rejection, cancellation-permit guards and seeded AEC attenuation of 17.7 dB. Controlled onset/gate timings are not live end-to-end interruption latency.
- **Live physical monitor checks passed**: laptop 40→41→40 and external 50→51→50. Exact changed readback was verified; each other screen stayed unchanged. Both original values were restored. No user action was sent to any other app or network provider.
- **24 local qwen3:8b interpretation-only cases passed**: eight casual requests plus sixteen seeded held-out corpus variations. Checked exact action, target percentage and display after validation/entity preservation. No proposed action was executed by this evaluation. An initial seven-action test omitted screen targets, and one held-out case substituted monitor 2 for first monitor; both issues were fixed and rerun. These tests do not establish accuracy for all possible conversation.
- **1,012 labeled synthetic examples** generated and their expected plans validated. They are reusable evaluation/preparation data, not a fine-tuned model and not 1,012 model-inference passes.
- A generated Windows-speech alternate-audio recovery test passed using actual local ASR, with simulated speaker identity and no microphone.
- Seeded 18-trial speech/noise benchmark: median ASR decoding 3469→2500 ms; p95 5562→4391 ms after bounded active CPU allocation. Total word errors remained 38/108 across the mixed clean-to-minus-five-dB trials. Strong noise degraded accuracy. This remains above the sub-second target; it is neither a live accent test nor executed-action accuracy.

No live microphone, overlapping-speaker acceptance, phone call, message send or fine-tuning was performed. Saved voice profiles, calibration, memories, phone credentials and paused routines were preserved. The 100-point reliability inventory explicitly records unavailable models/hardware features and unmeasured stages.

Earlier staging checks identified and corrected the capture restart race, new frame metadata fixture expectations and the exact-local-command policy contract. No assertion was disabled to obtain the final pass. Asyncio/WMI/localhost checks require ordinary Windows access; restricted sandbox runs cannot initialize some native components.
