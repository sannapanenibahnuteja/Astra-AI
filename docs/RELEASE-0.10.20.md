# Bob 0.10.20 — spoken confirmations

Changes from 0.10.19:

- Speech onset can interrupt active model generation or an active spoken response. It no longer cancels a newly accepted request during command preparation.
- Native action execution is protected from acoustic onset callbacks so its verified result is retained. The Stop button still cancels; voice playback and model answers remain interruptible.
- Reply audio tracks whether it is currently speaking, instead of treating earlier speech as an active response.
- Added regressions for “Close Microsoft Edge” → “Yes”, callbacks before processing, callbacks during execution, manual stop and active-answer interruption.
- Added a packaged confirmation diagnostic that injects speech-onset callbacks and verifies actual closure of a dedicated disposable window.

## Run and retest

Quit the previous Bob using its tray menu, then run `dist/release-0.10.20/Bob/Bob.exe`. Keep `_internal` beside it.

1. Open a disposable Edge window. Say “Close Microsoft Edge.”
2. When Bob asks, say “Yes.” A verified closure result or an actionable error should appear; an idle speech callback must not silently stop it.
3. If several Edge windows match, use their exact titles or say “close all those” after Bob lists them. Whole browser-window closure closes their tabs too; save important work first.
4. Ask Bob to explain something, then interrupt with “Actually, open calculator.” Reply interruption should still work.

[Test report](TEST-REPORT-0.10.20.md). Voice identity uncertainty is separate from command cancellation; this release does not claim a new live voice-biometric accuracy fix.
