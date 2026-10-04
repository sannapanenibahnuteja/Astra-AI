# Bob 0.10 validation — 4 October 2026

- 94 Python regression tests passed, including opt-in call validation, mocked provider submission, no automatic redial, encrypted pairing, literal dictation routing, and monitor geometry.
- Production Vite build and standalone PyInstaller EXE build passed.
- Actual Notepad saved the exact string `Hello, Bob! Keep A+B = {value}.` in an owned disposable file. Run `scripts/verify-notepad.py` to repeat this check.
- Native fixture movement and literal typing passed. Windows exposed only one monitor during verification; physical movement between two displays remains unverified.
- Packaged EXE passed native focus, literal paste, accessible button invocation, maximize, and restore checks.
- Packaged UI passed startup, navigation, overflow and simulated wake/listen/reply checks. This simulates recognition and speech output; it is not a live microphone accuracy test.
- Carrier submission is covered with a mocked provider. No real call was placed. Account configuration, destination permissions, delivery and audio quality require testing with the user's provider account.
- Phone pairing persistence uses Windows user-bound DPAPI. Real phone lock-screen behavior and remote Tailscale connectivity were not exercised in this release check. Carrier calls are reminder announcements, not two-way AI calls; mobile browser microphone access requires an awake page.

The assistant supports validated actions exposed by its tools; arbitrary Windows/app control and flawless recognition are not guaranteed. Conversation style presets guide Ollama responses and do not replace the speech engine.
