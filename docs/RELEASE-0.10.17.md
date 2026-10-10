# Bob 0.10.17 — Easier voice registration and personal voice profiles

## Changes from 0.10.16

- Registration allows a 1.8-second pause between parts of a sentence instead of using the short conversational cutoff. The UI shows when the microphone is ready, including fallback capture after the input stream and cue are ready. The ordinary command cutoff is restored after recording, even on errors.
- Speak freely for five to ten seconds. The displayed sentences are suggestions: enrollment and voice-match testing do not transcribe, compare wording or execute commands.
- Balanced matching adapts within a bounded range to variation among your three enrollment samples. It still requires agreement from multiple templates. Strict keeps its higher cutoff, and short phrases still require stronger evidence. Existing encrypted profiles remain readable and gain the same bounded calibration from their stored templates.
- Add up to eight people in Settings. Each confident voice match selects the corresponding profile and resumes that person's dedicated conversation, action context and personal memories. Close matches between two people remain uncertain and do not switch profiles.
- Choose a personality per person, or inherit the main personality. Bob gives a short personal greeting when a different person is recognized, with Greetings enabled. It does not greet on every request.
- Voice features and personality choices remain encrypted using Windows account protection. Recordings are not saved. Recognition remains optional and is not authentication, an access-control system or permission to perform sensitive actions.
- Clear commands and conservative fuzzy matches retain the quick native path. A dry-run comparison did not show better interpretation from the local model for two calculator requests, so those paths were retained. Requests outside the grammar still use the existing local Ollama tool planner, with the same validation, confirmations and execution checks. Offline or unsupported models must report failure instead of inventing success.
- The release is a normal launchable **Bob.exe** with its runtime folder beside it. There is no need to extract a release ZIP.

## Simple setup and tests

1. Quit the old Bob using its tray menu. Run **Bob.exe** from the new `dist/release-0.10.17/Bob` folder. Keep `_internal` beside it. Existing settings are kept.
2. Settings → Recognize my voice: enable the optional toggle, choose **Balanced**, and save. Your previous saved voice is retained.
3. Click **Test voice match**. Wait for **Listening**, then speak normally for five to ten seconds. Pause for two seconds. Nothing said in this test runs as a command.
4. If your old samples still do not work, delete only your voice entry and record three fresh samples under your name. Keep roughly the same microphone distance. Any natural sentences work; wording and accent do not have to match the examples.
5. Start a voice conversation and say “Hey Bob, could you please open calculator?” A confident match shows your name and uses your personal conversation. With Greetings enabled, Bob greets you on the first match or when switching people.
6. Click **Add another person** and record their three samples. Choose **Friendly**, **Funny**, **Serious**, **Witty butler** or another personality for each saved person. Have them take turns speaking a full sentence: the active profile and conversation should change. Similar or uncertain voices should leave the current profile unchanged.
7. Say “Remember that my favorite drink is tea.” After another person is recognized, save a different drink. Ask “Recall my favorite drink” as each person: each should receive their own value. The Memory page opens the active person's facts. Use its **Memory workspace** selector to review general facts or another saved/older profile. Old general facts are preserved, not silently assigned to a person.
8. For command understanding, “open calculator” uses the direct path. “Open calculatr” uses the conservative fuzzy matcher and asks before opening its proposed match. Requests outside the grammar use local model planning. Keep Ollama running and choose a tool-capable model. A model interpretation is not proof an action completed; check the app or setting.

Deleting a voice entry removes its encrypted voice features, not saved conversations or facts. Those remain manageable through the conversation and Memory controls. All people using this Windows account can still see the app's history. This is personalization, not isolation from other users of the PC.

198 regression tests, the frontend lint checks and the production frontend build passed. The real speaker model matched a fourth generated sentence after enrollment on three distinct sentences (similarity 0.929 against cutoff 0.65), and the match survived encrypted reload. No user microphone was used.

Real microphone accuracy still depends on speech length, microphone quality and room noise. Generated speech and regression checks cannot guarantee recognition of your live voice; use the no-action test above to check it.
