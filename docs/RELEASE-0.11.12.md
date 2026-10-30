# Bob 0.11.12 — captured speech handoff and recovery

Unreleased staging notes. These changes are delivered together in Bob 0.11.13.

- Idle timeout now measures actual idle time. Active capture, endpoint publication and saved-voice verification keep ownership of the pending turn. This prevents a timeout racing the completed-turn handoff and starting another listen with different wake permission.
- If suppressed speech decodes to no words, an already matched user can get one additional decode using the synchronized echo-cancelled, unsuppressed voice track. It uses the same local model and final confidence/wake checks, never an unverified raw microphone stream. Ordinary successful recognition takes no extra pass. The fallback is bounded and may add delay only when the first path fails.
- An empty decode now produces an explicit repeat-request message in hands-free mode. It cannot silently submit an empty command. Uncertain text awaiting confirmation survives an idle gap. Hands-free listening avoids a brief idle-state flicker between captures.
- Dynamic quiet/noise sensitivity from 0.11.11 remains. Saved-voice thresholds and deliberate interruption guards are unchanged.
- Reliability layer: a stalled microphone callback now reports an input failure; model streaming uses a 64-chunk bound, cancellable waits and a 180-second total request limit. No failed external action is retried automatically.
- Settings shows 12 latency targets with measured p50/p95/p99 or “not measured.” Capture state traces remain metadata-only and RAM-bounded; replay validates ordering without executing anything.
- After a narrow question, the same confidently recognized user can answer with a time, day, option or yes/no without repeating Hey Bob, once within 12 seconds. Unrelated speech keeps the wake requirement.
- [All 100 requested reliability requirements and their current status](CONVERSATION-RELIABILITY.md). This is a tested foundation update, not completion of every model/hardware-dependent feature.

- Exact common spoken requests (volume, mute, time, window/monitor lists, brightness and basic media controls) now have a deterministic local fast lane. Negative, compound and ambiguous requests keep the reasoning/validation path.
- Active local ASR uses at most four threads and half the logical CPUs. A repeatable 18-trial synthetic benchmark improved median decoding from 3.47 to 2.50 seconds with unchanged total word errors. This remains above the instant-response target.

## Try it

1. Quit older Bob and launch `dist/release-0.11.12/Bob/Bob.exe`, keeping `_internal` beside it.
2. Start Voice, wait ten seconds, then say “Hey Bob, open Calculator.” Check the complete request appears and Calculator actually opens.
3. Say “Hey Bob,” pause briefly, then say “open Notepad.” Try both normal and softer speech.
4. If Bob cannot decode a capture, it should explicitly ask you to repeat instead of silently displaying ready. Repeat the complete request including Hey Bob.
5. If uncertain words appear for confirmation, wait a few seconds and say “yes”; silence must not erase those words. Cancel instead if they are wrong.
6. Taps/coughs should not interrupt a reply. Use “Hey Bob, please stop talking” in your saved voice to test deliberate interruption.

The supplied video was inspected. Its missed intervals did not contain usable microphone speech in the recording audio, so it cannot establish live ASR accuracy. Tests cover the identified handoff/recovery paths; live microphone acceptance remains necessary. No new microphone recording, cloud request, call, profile edit or private data change was made.
