# Bob 0.10.16 — Less waiting before speech

## Changes from 0.10.15

- Windows speech reuses one renderer across sentences instead of starting PowerShell and the speech engine again for each sentence. Selecting Windows speech, or Automatic without configured Azure, prepares that renderer when a desktop voice conversation starts.
- The renderer exits after 60 seconds of inactivity and is terminated when you stop voice mode or interrupt active rendering. If it is idle while audio plays, interruption stops playback and retains the renderer for your replacement request. It does not record audio. The existing echo cancellation and action verification remain active.
- Private phone webpage replies also reuse Windows speech; carrier calls still use Twilio's separate voice. Azure neural voices retain their existing explicitly configured path.
- Streaming waits for an actual sentence boundary instead of treating the end of each model token chunk as a sentence. Decimal values and titles such as “Dr.” are kept together.
- The fast portable folder and lighter chat prompts from 0.10.15 remain included. There is no artificial instant acknowledgement or unverified claim that an action succeeded.

## Install and test

1. Quit the old Bob from the tray. Extract the whole new ZIP into a fresh folder and run **Bob.exe**. Keep **_internal** beside it.
2. Select **Windows** or **Automatic** in Settings → Voice & personality, then save. Start a voice conversation.
3. Say “Hello Bob”, then “What are black holes?” Compare the pause before Bob's speech and the gaps between sentences. The first cold speech-engine/model load can still take longer.
4. Interrupt with “Actually, open calculator”. Speech must stop and the replacement request must execute.
5. Say “Shorter”. The answer should adjust without repeating actions.
6. To hear cleaner punctuation, ask Bob to explain the number 3.14, or use Read aloud on text containing “Dr. Smith”.

## Measured limits

Rendering the same short greeting in memory took 3.3 seconds for the first renderer request and 0.08–0.10 seconds for subsequent requests on this PC. This excludes speaker playback, recognition, model generation and network delay. Preparing the renderer during the voice session removes that cold setup from subsequent sentences, but cannot guarantee instantaneous replies.

The prior release's startup smoke test improved from 36.8 to 4.5 seconds, and its warm-model greeting first text improved from 1.65 to 0.48 seconds in the controlled comparison. Complex actions and longer histories can take more time. Background renderer memory is released on idle; no model, context, memory or voice-accuracy settings are silently reduced.

185 regression tests passed, followed by the additional repeated-warmup timer check. The production frontend build passed. A live native speech-path check produced valid WAV audio before mock playback in 0.60 seconds after preparation and 0.10 seconds on the next reply; interrupting mock playback retained the idle renderer. No microphone was recorded during those checks.
