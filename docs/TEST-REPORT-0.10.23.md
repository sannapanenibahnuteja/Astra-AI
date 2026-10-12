# Bob 0.10.23 interface verification — 12 October 2026

- Frontend production build and changed JSX lint passed.
- Visual browser review covered the futuristic welcome/composer and Settings surfaces at the normal laptop viewport.
- Compact responsive DOM check at 640×780: no horizontal overflow, 68-pixel icon sidebar and 30-pixel headline.
- Starter card interaction correctly populated **Open calculator** in the editable composer without executing it.
- Rendered animation checks confirmed **bob-orbit** with a 56-second duration and **bob-core-breath**. CSS includes background pause and reduced-motion disabling; no animation render loop or external graphics library was added.
- The saved screenshot is a browser design preview, not a live Windows task result.

This UI release does not retest real microphones, every Windows action, phone calls or hardware. Existing backend behavior remains unchanged.

Packaged Windows EXE build and isolated native UI fixture passed: voice event readiness, four navigation destinations, no horizontal overflow, simulated voice round trip and interruption command execution. Ollama status was connected; the fixture simulated speech and Calculator execution rather than testing model conversation.
