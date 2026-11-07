# Bob 0.11.16 verification — 7 November 2026

[Machine-readable results](TEST-RESULTS-0.11.16.json).

- 589 Python regression tests passed, including persistent numbered choices, isolated chats, no replay of previous approval, exact volume and display controls, and direct 16 kHz capture handoff. The frontend production build passed.
- The actual packaged EXE passed simulated wake-to-reply and queued interruption execution, native shutdown, and simulated duplex audio checks. The packaged settings fixture passed 211 UI checks on retry after an initial settings assertion failure. These fixtures do not exercise every external service or the live microphone.
- The generated-audio benchmark exercised the final duplex input path with three English clips. All three decoded without a review flag. Two literal word differences were the expected transcription normalization from “twenty percent” to “20%”. The cold decode took 4,334 ms; the two subsequent samples took 2,335 and 2,338 ms. The microphone was not recorded.
- From a text transcript, the local time reply was visible and complete in 75 ms in this sample. A separate real Ollama explanation showed text at 5,172 ms and completed at 9,628 ms. Those timings exclude recording, speech decoding and playback, and do not guarantee latency for other requests. Reproduce with `scripts/benchmark-voice-turn.py`.

The EXE launches with `_internal` beside it. No ZIP was created. No live speaker match, noisy-room microphone accuracy or perceived voice naturalness was verified.

EXE SHA256: `cc7d7a495b7a7f30bf353395a283bbad0555b18d6bc5d2a385ee07ff49a6e951`.
