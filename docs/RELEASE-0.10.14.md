# Bob 0.10.14 - Natural voice and corrections

This release prioritizes natural voice, interruptions and corrections from your conversation feature list.

## Changes from 0.10.13

- **Voice choices and previews:** Settings offers Andrew, Ava, Brian and Emma Azure neural voices, or your installed Windows voices. Preview before saving; neural previews require working Azure Speech credentials and do not silently substitute a Windows voice. Reply text goes to Microsoft when using Azure. Private phone webpage audio uses the same selection; Twilio carrier call voices remain separate.
- **Whole windows versus tabs:** “Close all YouTube windows” selects browser windows containing YouTube, including inactive Edge tabs, and warns that every tab in those windows will close. “Close all YouTube tabs” closes only matching tabs. “The first one” retains the rest for “the other one” or “all those”. Closing still requires approval.
- **Honest execution results:** app launches must show a matching app process/window before Bob reports “Opened”. Unverified launches stop dependent steps. Native execution results are retained instead of letting the model invent completion; opening a file, settings page or local media is described as a request when not verified.

- **Speech during generation:** explanations such as “Explain how a computer works” start speaking at sentence boundaries. Verified action results can speak while later steps continue. The desktop avoids reading the completed response a second time. Streaming applies to an active desktop voice session; phone conversations keep their existing playback path.
- **Barge-in:** queued sentences stop when you interrupt. The microphone stays available through the existing echo-cancelled audio loop. If you interrupt a confirmation, the pending action remains available for correction; interrupting is never approval.
- **Thinking pauses:** choose 0.45, 0.65, 1.2 or 1.8 seconds before Bob takes a turn. This is a silence heuristic, not detection of your thoughts.
- **Corrections:** “No, I meant fifty percent” can correct a pending volume/brightness setting or your last successful setting within five minutes. Pending changes need fresh approval; recent routine setters can update immediately on the same monitor/output target. A pending reminder supports a different weekday or an explicit AM/PM time without losing its text or delivery channel.
- **Self-corrections:** “Open Notepad, no actually open Calculator” executes the replacement. Quoted text and dictation are preserved. General corrections still depend on the local model and may need a focused question.
- **Mid-reply edits:** interrupt with “Shorter”, “Just the answer”, “Skip that part” or “Summarize that”. Bob uses the current conversation and cannot repeat actions during these answer edits.
- **Modes:** Balanced, Fast, Tutor and Calm affect answer style. Your personality settings remain independent.
- **Name hints:** editable recognition hints for names, places and project terms. These guide the bundled English recognizer; they do not train a new acoustic model or rewrite dictation.
- Explanations and answer edits use a shorter prompt without Windows tool definitions, reducing unnecessary model processing. Cold model loading can still dominate response time; keep-alive settings trade memory for faster follow-ups.
- Pending approvals expire after five minutes. Unknown or invalid corrections retain the pending intent and ask for the missing value.

## Install and setup

1. Quit the old Bob from its tray menu.
2. Extract the new ZIP and run **Bob.exe**. Check **0.10.14** in the sidebar.
3. Keep Ollama running and select an installed model.
4. In **Settings → Voice & personality**, leave **Speak replies as they arrive** enabled.
5. Choose **Natural** for normal conversation or **Thinking time** if you pause while forming a sentence. Add a few names under **Names and pronunciation hints** and save.
6. Start a voice conversation or use your configured wake words. Interrupt by speaking normally; no microphone click is needed during that conversation.

## Commands to test

### Choose a voice

1. Open **Settings → Voice & personality**.
2. Choose **Azure neural** for natural voice options, or **Windows** for offline speech.
3. For Azure, use the existing neural voice setup button: create an Azure Speech resource, put its region and key in `neural-voice.json`, and set `enabled` to `true`. Twilio credentials are separate. Refresh the voice list after setup.
4. Select Andrew, Ava, Brian or Emma, then **Listen to this voice**. Stop your voice conversation first. Preview does not save the selection.
5. Save settings, restart the voice conversation, and say “Tell me about something interesting”. Choose by listening; naturalness is subjective and rendering/network time still affects latency.

All four presets are American English multilingual neural voices. Your existing configured voice remains selectable. [Microsoft’s voice catalog](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support) lists supported voices. Windows voices depend on installed SAPI language packs and are generally less expressive. Carrier calls use their own provider voice and do not inherit this picker.

### Check context and truthful results

- Open YouTube in two Edge windows with another non-YouTube tab in each. Say “Close all YouTube tabs”, check the listed titles, then approve: other tabs should remain.
- Repeat with “Close all YouTube windows”: the confirmation must warn that all tabs in the selected windows close. Cancel if those other tabs are valuable.
- Ask “Close YouTube” with multiple matches, then “Close the first one”. After approving, “Close the other one” should refer to the remaining match.
- A launch Bob cannot verify must say so instead of “Opened”; dependent steps should stop.

| Test | Say / do | Expected result |
|---|---|---|
| Streaming | “Explain how a computer works.” | Bob starts speaking before the entire explanation is generated. |
| Redirect | While Bob speaks: “Actually, open calculator.” | Speech stops, the complete new request is captured, and Calculator opens. Already completed actions are not undone. |
| Shorten | While Bob explains: “Shorter.” | A shorter answer on the same topic, without repeating Windows actions. |
| Thinking pause | “Give me more time to think.” Then “Open…” pause for one second “…calculator.” | The words remain in one captured request with the 1.8-second pause setting. |
| Faster turn | “Respond faster.” | Changes the silence wait to 0.45 seconds. |
| In-sentence correction | “Open Notepad, no actually open Calculator.” | Executes only the replacement request. |
| Correct a setting | “Set the volume to forty percent.” Then “No, I meant fifty percent.” | Updates the last successful volume target to 50%, within five minutes. |
| Pending correction | During a pending reminder approval: “No, I meant Friday.” | Keeps its text/channel and clock time, changes the date to Friday, and asks for fresh approval. Say “Yes” only after checking the new date/time. |
| Explicit time | During that approval: “Actually at 9 AM.” | Updates the pending reminder time and asks for fresh approval. |
| Modes | “Switch to fast mode”, “Use tutor mode”, “Use calm mode”, “Use balanced mode”. | Changes response style and persists it. |
| Name hints | Add your commonly used names in Settings, save, then speak a sentence containing them. | Hints can improve recognition; uncertain transcripts still require review. |
| Tab references | “Close all YouTube tabs”, or “close all those” after Bob lists matches. | The 0.10.13 scoped selection and verified closure behavior remains. |

For a safe pending-reminder test without a carrier call, say **“Remind me in two days to take a break, and check with me first.”** Bob should ask for approval without saving the reminder yet. Say **“No, I meant Friday”**, check the new date/time, then say **“Cancel”** to leave nothing scheduled. Paid carrier call reminders require the existing Twilio setup and always require approval.

Recognition depends on the microphone and room. Nearby people or television speech may still trigger speech detection. Very long pauses can split a request. The current local speech model is English-only. These improvements do not provide every integration or all 28 conversation features; see the [complete capability status](CONVERSATION-CAPABILITIES.md).

## Verification

174 automated tests passed. They cover speech before generation completes, no duplicate readout, cancellation of queued speech, preserved pending approval, percentage/day corrections, explicit reminder approval and cancellation, thinking pauses, voice selection and preview validation, scoped window/tab follow-ups, unverified launches and the existing Windows features. The frontend production build passed.

Generated normal and quiet speech passed through echo cancellation and the Natural pause endpoint to reliable Calculator action plans; Bob-only echo caused no interruption. A live local Ollama check with simulated speakers produced its first speakable sentence at about 2.8 seconds with the shorter prompt. Actual audio rendering adds time, and a cold model load was much slower. This is not a guarantee of low latency on every PC or with every model.
