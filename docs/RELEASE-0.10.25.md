# Bob 0.10.25 — interactive workspace and motion

The black workspace now connects its useful status surfaces to actions. Connection badges, model labels, resource badges and voice metrics open and focus the relevant settings. The Bob logo returns to Assistant. The YOU avatar opens voice profiles; local memory shortcuts open Memory.

Click Bob’s core to start voice mode and click again to end it. Capability cards put an editable example into the composer without executing it. Click a saved memory to edit its fields and Save memory to apply. Messages have Copy buttons using the native Unicode clipboard in the EXE.

Buttons have hover, press and expanding glow feedback. Cards and panels enter smoothly; the voice status icon moves during listening/speaking and the composer accent reflects the current state. Reduced-motion preferences disable the effects, and hidden-window motion pauses. Text headings and decorative grid-free space remain readable content rather than misleading controls.

## Test the new interactions

1. Quit the previous Bob through the tray and launch this folder's Bob.exe with _internal beside it.
2. Click the connection badge: Ollama address should receive focus. Click the model beside the composer: Model should receive focus.
3. Click ON DEVICE or Local by design: idle resource settings should receive focus. Click YOU: voice recognition settings should receive focus.
4. Click Bob’s core, speak after Listening, then click the core again to finish voice mode.
5. Open Capabilities, click a card and inspect the prepared example before sending. Tab to a card and press Enter to do the same with a keyboard.
6. Save a test fact in Memory, click its text, change it and Save memory. Remove the test fact when finished.
7. Copy a reply and paste it into a text editor. No message is sent or executed by copying.
8. On a wide window, click Engine/Model/Memory/Voice in the status panel. On smaller windows use the top bar, composer and sidebar shortcuts.
9. Press a button and check its feedback; switch panels and inspect the entrance motion. Windows reduced-motion preferences should remove animation.

[Full manual](USER-MANUAL.md). [Verification and limitations](TEST-REPORT-0.10.25.md).
