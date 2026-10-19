# Bob 0.11.2 — saved voice and deliberate interruption

**Default:** Settings → Conversational audio → **Only interrupt for my voice and clear intent** is on. Enable **Recognize my voice** and select your own saved profile under **Focused listening**. Keep your existing enrollment; no new recording is required.

While a reply is active, sound alone no longer stops or lowers it. An interruption must pass sustained-speech checks, match the selected saved profile (or the recognized person Bob is replying to when all-saved mode is selected), and produce confident, directed words. Unknown/other saved voices and gibberish do not stop the reply. Recognition is approximate; it cannot read your thoughts or provide secure authentication.

Try: **“Bob, stop”**, **“Shorter”**, **“Actually, open calculator”**, **“Bob, what does that mean?”**, or **“No, I meant Friday.”** Unaddressed narration, filler, a name alone and uncertain words are ignored during replies. New commands are still interpreted and validated through the existing agent after capture; interruption detection never executes actions itself.

Pure reply controls such as “Bob, stop” are consumed locally after verification. They cannot be reinterpreted by the LLM as stopping a browser, media player or other app. Compound requests still reach normal validation.

No saved/matched identity or unavailable local transcription means **no voice interruption** in this mode. The Stop button always remains available. Select your specific voice rather than all saved voices for consistent primary-user focus.

The microphone stays active. Speaker verification runs before interruption ASR, so other people do not consume a decode. Early previews are bounded and cannot replace the final request. An accepted completed transcript is reused when its speaker proof remains valid, avoiding duplicate transcription. Stale results cannot cancel or queue into a newer turn.

Strict verification adds model/identity delay; the earlier 250 ms acoustic gate is not the full verification time. This conservative mode prioritizes avoiding unwanted cuts. Turning the setting off explicitly restores the earlier acoustic interruption behavior. In strict mode, the separate playback-lowering option is not used before authorization.

Very short words may not contain enough voice for reliable matching. Prefer **“Bob, please stop talking”** or **“Bob, could you give me the short version?”** if a one-word interruption is ignored. Matching thresholds are not weakened to accept noise.

## Quick test

1. Close old Bob; launch this release's `Bob.exe` with `_internal` beside it.
2. Settings → Recognize my voice → enable and select your saved name under Focused listening. Keep the new clear-intent option enabled, Save settings, then restart voice conversation.
3. Ask Bob to explain something in detail. Make a desk click, say “um, blah blah,” or let another person speak: the reply should continue.
4. Say **“Bob, stop”** in your normal voice. Then ask another question: Bob should speak the new answer.
5. During the next reply say **“Actually, open calculator.”** It should stop after verified recognition and process that new request.

See [test evidence](TEST-REPORT-0.11.2.md). Automated fixtures are not a guarantee of every real-room/overlapping-speech result.
