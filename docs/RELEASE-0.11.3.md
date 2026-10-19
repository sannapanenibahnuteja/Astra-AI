# Bob 0.11.3 — complete speech and explicit wake phrases

Spoken prose no longer silently stops after a few sentences, 200 words or 5,000 characters. Streaming sentence playback drains through the final words. Long read-aloud requests are split into bounded synthesis requests without dropping the remainder. Explicit cancellation still stops pending playback. Public mode still says only “The details are on screen”; meeting/text-only modes stay silent, and fenced code is summarized.

**New default:** Settings → Conversational audio → **Require Hey Bob for each voice request**. Say **“Hey Bob”**, **“Okay Bob”** or **“OK Bob”** before each new request and interruption. The prefix is removed once; the remaining request is preserved. A wake phrase alone arms one next request for eight seconds; an explicit Voice-button activation also arms one request. A slow transcription does not expire a command authorized when capture began. New unrelated speech after that one request requires another wake phrase.

During replies, wake phrases still require sustained speech, a saved-voice match to the selected/current user and confident local recognition. Bare “actually”, “shorter”, clicks, other voices and uncertain words cannot authorize interruption. **“Bob, please stop talking”** remains an addressed reply-stop shortcut. **“Stop listening”**, **“Stop voice”** and **“Go to sleep”** are explicit end-session phrases. A pure reply-stop never becomes a media/app action.

Enable **Recognize my voice**, select your own profile under **Focused listening**, and Save settings. Without matching identity Bob keeps speaking; use the Stop button. Wake-only mode keeps verified interruption protection even if the older intent switch is off. Turning off both guards explicitly restores acoustic interruption behavior. Auto-listening at startup is disabled in wake-only mode; native wake listening remains available when Wake words is enabled.

## Test the update

1. Close the older Bob. Launch `dist/release-0.11.3/Bob/Bob.exe` with `_internal` beside it. No ZIP or installation is required.
2. Settings: enable Read replies, Wake words, Require Hey Bob, and Recognize my voice. Select yourself under Focused listening, Save settings, then restart the voice session. Existing enrollment remains.
3. Say “Hey Bob”, wait for the cue, then “Explain the water cycle in detail.” Or in an active session say “Hey Bob, explain the water cycle in detail.” Check the spoken answer reaches the last sentence shown.
4. In a voice session, say “open calculator” without a wake prefix after a completed request. It should be ignored. Then say “Hey Bob, open calculator.” The normal agent should process it.
5. During a detailed reply, make a desk click or say “actually” alone: playback should continue. Say “Hey Bob, please stop talking” in your normal enrolled voice: playback should stop after identity and transcript verification.
6. During another reply say “Hey Bob, open calculator.” The verified request should interrupt and enter the normal action pipeline. Tool execution remains validated separately.
7. Say “Hey Bob” alone. Finish speaking, then say the next request within eight seconds. It should be accepted once. Say “Stop listening” to end the session.
8. Use Read aloud on a long answer: the last words should be heard. Stop cancels remaining chunks. Public and meeting modes retain privacy behavior.
9. Toggle Require Hey Bob off/on and save; restart voice conversation. Its saved setting should persist after reopening.

Wake detection and voice matching are approximate; they cannot infer private intent, guarantee recognition in overlapping speech, or authenticate securely. Clear longer phrases usually match more reliably than a single short word. Local ASR/speaker checks add latency. Automated fixtures do not replace live testing with your laptop microphone. See [test evidence](TEST-REPORT-0.11.3.md).
