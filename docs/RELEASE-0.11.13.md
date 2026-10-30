# Bob 0.11.13 — individual monitors and natural intent

This release includes the unreleased 0.11.12 capture/reliability work plus the individual-monitor fix.

- Brightness controls are bound to Windows display interface identities and the same monitor inventory used for window movement. Reversed brightness-library enumeration cannot swap screen numbers. Unknown individual screens never fall back to a different screen.
- Brightness plans from Ollama must include an explicit display field. The initial local model check omitted it for seven action requests, which previously defaulted to all screens. Schema and instruction examples now preserve the named display. A further held-out failure showed stale model context substituting monitor 2 for an explicit first-monitor request; a narrow literal-entity guard now preserves one unambiguous monitor number, without interpreting negated or multi-target instructions.
- Laptop/external, numeric, primary/secondary and spatial selectors are supported. Previous/other references require a recently verified physical screen (five minutes); stale, disconnected or ambiguous choices ask for a screen.
- Readback now also rejects a one-point requested change when the monitor reports no actual movement. Partial failures report what changed and what failed.
- Eight conversational model interpretation cases, a generated corpus of 1,012 labeled variants, and negative examples are supplied. These are evaluation data and prompting improvements, NOT a claim that the model weights were fine-tuned or that every possible utterance is supported.
- Capture handoff and cancelled-session restart races, explicit empty-transcript recovery, matched-user alternate echo-cancelled decoding, local command fast paths, bounded streaming/timeouts, latency diagnostics and the microphone-stall watchdog are included.

## Test files

- [Individual monitor requests](test-commands/Monitor-Test-Commands.txt)
- [Voice and broader commands](test-commands/Voice-and-Commands-Test.txt)
- [Results checklist](test-commands/Test-Checklist.csv)
- [Reliability inventory and limits](CONVERSATION-RELIABILITY.md)

Quit older Bob and launch `dist/release-0.11.13/Bob/Bob.exe`; keep `_internal` beside it. Start with “Hey Bob, what is the current brightness of each screen?” Then ask naturally to change only the external screen and verify the laptop stays unchanged.

Live hardware verification used one-point changes on both connected screens, checked exact changed values and that the other screen stayed unchanged, and restored the originals. No live microphone test, message send, carrier call, fine-tuning or private profile modification was performed.
