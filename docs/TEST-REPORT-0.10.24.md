# Bob 0.10.24 verification — 12 October 2026

## Checked

- Frontend production build and lint for all four changed JSX files passed without warnings.
- Five voice-choice regression tests passed, including explicit playback while automatic replies are disabled. An initial sandbox run could not create SQLite temporary files; the normal permission run passed.
- Source native button audit: 43 checks passed. It clicks navigation, all starter cards, send, Read aloud (including injected failure recovery), New conversation/delete, mic, Voice/end, memory save/delete, app filtering/launch, footer Settings, Refresh, voice preview/refresh/setup, project picker, Save settings, data folder, phone enable/new link/revoke/setup, three enrollment samples, speaker test/personality/delete and the black canvas.
- Browser visual review and computed styles confirmed RGB(0,0,0) with no background image. Existing core motion remains.

## Test scope

The button audit uses an isolated data folder and simulated voice, links, app launch, project picker, profiles and phone integrations. Memory and settings writes use the real local store in that folder. It checks UI-to-API wiring and state recovery, not physical microphone quality, network reachability, carrier delivery or every external app. No real phone call was placed. Only fixture conversations/memories were deleted.

The new diagnostic requires a fresh empty data folder and rejects existing folders to protect personal data. Historical live Windows/voice/action evidence remains in prior reports. A working button cannot guarantee that an unconfigured external provider or inaccessible Windows control will succeed.

Final packaged EXE passed the same 43-control audit and the existing native voice round-trip/interruption fixture. Four navigation destinations were present and there was no horizontal overflow. Speech and Calculator execution in that fixture were simulated. The EXE build completed successfully.
