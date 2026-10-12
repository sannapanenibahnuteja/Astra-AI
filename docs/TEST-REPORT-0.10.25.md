# Bob 0.10.25 verification — 12 October 2026

- Frontend production build and lint for the three changed JSX files passed.
- Three native clipboard unit tests passed: Unicode content, lock release after write failure, and invalid input rejection. Clipboard calls were mocked to preserve the real clipboard.
- Source interaction audit passed 67 checks before the native clipboard route was added. It extends the previous controls audit with edit-memory, all eight capability examples, core voice toggle and status shortcuts focused on their actual controls.
- Browser keyboard test: Enter on a capability card prepared the request and focused Message Bob. Clicking Choose AI model focused Model. Visual review covered the welcome and capability cards.
- No external graphics library or animation render loop was added. Motion uses CSS transforms/opacity and reduced-motion/background rules.

UI audits simulate voice, phone, external app, picker and clipboard integrations, while memory/settings use the isolated local store. They verify wiring/state behavior rather than actual carrier delivery, real microphone quality, or every Windows app. No real call or personal data mutation was performed. These changes add interaction routes, not new Windows automation capabilities.

The initial packaged audit tried revoking pairing while its preceding operation was still busy. The control correctly rejected it. The diagnostic was corrected to wait for enabled controls; the final packaged audit passed 68 checks. The EXE build and native voice/interruption fixture passed, with four navigation destinations and no horizontal overflow. Speech, Calculator and clipboard execution were simulated in the UI fixture.
