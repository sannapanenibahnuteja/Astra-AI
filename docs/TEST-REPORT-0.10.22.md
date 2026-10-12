# Bob 0.10.22 UI verification — 12 October 2026

- Frontend production build passed; lint passed for both changed JSX files.
- Browser visual review covered Assistant, Memory and Settings; Capabilities navigation and catalog were inspected through the rendered DOM.
- Reviewed 1280×720 laptop, 640×780 compact and 1600×1000 wide layouts. The compact view has no document horizontal overflow; New conversation and all navigation destinations remain accessible. All four welcome cards and the composer fit the laptop view.
- The status side panel hides in narrower windows; the new Voice control remains beside the composer.
- The preview screenshot is a browser design preview, not a live Windows action result.

Packaged Windows EXE build passed. Its isolated native UI fixture passed: correct Bob assets, voice event readiness, four navigation destinations, no horizontal overflow at 1366 pixels, simulated voice round trip and interrupted Calculator command execution. Speech and Calculator execution were simulated; Ollama was offline in this fixture. Backend commands and calling services are unchanged; this interface release does not retest every physical device, real microphone, carrier call or third-party app.
