# Bob 0.11.13 — complete user manual and test commands

**Individual monitor control:** say the laptop, external screen, upper screen, primary screen, or a number from “list monitors.” Clear previous/other-screen follow-ups last five minutes and require the same verified display. [Monitor tests](test-commands/Monitor-Test-Commands.txt) · [Voice tests](test-commands/Voice-and-Commands-Test.txt).

**Captured-speech recovery:** completed recordings now survive the idle-timeout handoff. A matched user's empty decode gets a bounded alternative echo-cancelled audio pass. If words still cannot be decoded, Bob explicitly asks you to repeat. [Changes and tests](RELEASE-0.11.13.md).

**Adaptive room listening:** [0.11.13 changes and tests](RELEASE-0.11.13.md). Choose **Settings → Conversational audio → Room listening mode → Quiet room**, save, and start a new voice session. Both modes adapt automatically after sustained quiet (Quiet room: one second; Balanced: two). Rising non-speech noise restores stricter capture. Saved-voice and explicit interruption checks remain.

**New optional Finance widget:** [setup, transactions, budgets, portfolio and sample tests](FINANCE-GUIDE.md). Off by default; manual records and dated prices. Show or hide it in Finance, or say “Hey Bob, show my finance widget.”

**0.11.8 voice upgrade:** [Changes, larger-model selection and live tests](RELEASE-0.11.8.md). During replies, say a complete request such as “Hey Bob, please stop talking”; the wake name alone does not stop playback. Interruption now requires separate neural speech evidence as well as saved-voice and final-transcript checks. Large ASR is optional and slower on the tested CPU. Pause learning uses accepted matched-user turns only; it does not retrain neural weights.

**New customer starting point:** open **Get started** to check local setup, open Settings for missing prerequisites, prepare a first task, or copy a minimal support summary. Nothing is recorded or executed by those checks. First-task cards fill the composer; press Send after reviewing. See [0.11.7 changes and tests](RELEASE-0.11.7.md).

**Pending-generation fix in 0.11.6:** [Response-scoped cancellation and microphone calibration test](RELEASE-0.11.6.md). Restart to load newly saved microphone calibration. A raw callback cannot cancel a pending answer; completed saved-voice proof must belong to that exact response.

**Voice interruption fix in 0.11.5:** [Changes and noise test](RELEASE-0.11.5.md). Reply interruption waits for completed saved-voice and explicit-phrase verification. Disable Allow verified voice interruptions to ignore every voice interruption; sound alone never gains permission. Enable saved-voice recognition and focus yourself to use this feature.

**Voice activation in 0.11.5:** say “Hey Bob” or “Okay Bob” before each request and interruption. A wake phrase alone arms one request for eight seconds; the Voice button also arms one request. Say “Hey Bob, please stop talking” to interrupt, or “Stop listening” to end the session. Enable saved-voice recognition and select your own profile for interruptions. Prose replies are now read in full; public/text-only modes and code summaries retain their explicit behavior. Prefix the example commands below with “Hey Bob” when using voice.

**Appearance and app-launch guide:** [0.11.4 changes, every customization command and test steps](RELEASE-0.11.4.md). Click the palette icon to customize individual components. Appearance saves automatically. Clear installed-app launches and unique name typos use a faster local route; less familiar tasks use Ollama with validated tools.

New in this version: [Conversational audio setup, settings, commands and test table](CONVERSATIONAL-AUDIO-GUIDE.md). Includes live provisional captions, playback ducking, learned pauses, additional conversation modes, autonomy and diagnostics. Read its requirement coverage table for hardware/model limits.

Updated 30 October 2026. This guide covers the current Windows EXE: all 92 advertised tool actions, extra opening routes, Edge shortcuts, Settings pages, website aliases, voice controls, speaker profiles, personalities, memory, phone access and reminders. An example is a test you can perform, not a promise that every PC, page or player supports it.

## Contents

1. [First launch](#first-launch)
2. [Everyday controls](#everyday-controls)
3. [Voice, interruptions and speaker profiles](#voice-interruptions-and-speaker-profiles)
4. [Conversation, personalities and context](#conversation-personalities-and-context)
5. [Complete action test catalog](#complete-action-test-catalog)
6. [All Edge shortcuts, Settings pages and websites](#additional-command-catalogs)
7. [Phone access and locked-phone calls](#phone-access-and-locked-phone-calls)
8. [Privacy, backup and resource settings](#privacy-backup-and-resource-settings)
9. [Troubleshooting and test checklist](#troubleshooting-and-test-checklist)
10. [What this version does not do](#what-this-version-does-not-do)

## First launch

1. Quit an older Bob through its tray icon → **Quit Bob**.
2. Double-click `dist/release-0.11.13/Bob/Bob.exe`. Keep `_internal` beside it. This is a directly launchable portable EXE; no ZIP extraction, Python, Node or development server is needed.
3. Windows 10/11 x64, WebView2 Runtime and Windows PowerShell 5.1 are required. Wake words additionally need a Windows English speech recognizer.
4. Start your installed Ollama application. If it is not installed, use Bob's **Get Ollama for Windows** link first. Download a model through Ollama before choosing it in Bob. In Bob → **Settings → Local intelligence**, set address `http://127.0.0.1:11434` and the exact installed model name, for example `qwen3:8b`. Save settings, then Refresh. Look for **OLLAMA CONNECTED**. Model downloads are separate from Bob.
5. In Windows **Settings → System → Sound**, select the correct default microphone and output. Allow microphone access for desktop apps under Windows privacy settings. Avoid Stereo Mix.
6. In Bob **Voice & personality**, turn on voice replies, Wake words and startup greeting if desired. Save settings, then use **Test voice output**.
7. In **Your current project**, Browse to the real project folder and save if you want project tools.
8. Start with typed **What time is it?**, then speak **Hey Bob**, wait for Listening, and ask the same question. You should see a reply and hear it if speech output is enabled.

Direct typed commands and saved routine playback can work without Ollama. Clear supported appearance preferences and explicit known app/site launches have a direct voice path. Other spoken tasks use Ollama for semantic interpretation, along with open-ended conversation and model-assisted workflows. The browser development preview at localhost:5173 does not replace the native EXE.

## Everyday controls

| Control | How to use and test |
|---|---|
| Assistant | Type a request, press Enter to send; Shift+Enter adds a line. Check the reply and the actual action. |
| New conversation | Start a separate conversation. Previous chats remain in Recent conversations. Scoped action references belong to their conversation. |
| Recent conversations | Reopen a saved chat, then ask Summarize our discussion. Summaries use available bounded history. |
| Microphone | Capture a request. Wait for Listening before speaking. |
| Voice / Start voice conversation | Use Voice beside the message box (or the side panel on wide windows). Start once, then speak naturally between replies. No mic click is needed for every desktop turn. |
| Stop / End voice conversation | Stop the current response/capture or end the session. Say Stop listening to finish hands-free mode. |
| Read aloud | Replay a displayed assistant message. Useful when automatic speech is disabled. |
| Memory | Choose a workspace, add a name/detail, inspect saved facts and remove individual facts with the trash button. |
| Capabilities | Review supported action categories; filter installed apps and click an app chip to request opening it. |
| Settings | Save after changing preferences. Voice Preview lets you listen before saving the voice selection. |
| Tray | X quits Bob and stops voice, routines and remote access. Minimize to keep it running; the tray menu can reopen or quit. |
| Open data folder | Opens local data/configuration/notes. Do not post its credential files or pairing links. |

## Voice, interruptions and speaker profiles

### Natural voice conversation

Say **Hey Bob** or **Okay Bob**, wait for Listening, then speak. In active echo-cancelled desktop mode there is no recording beep. If duplex audio is unavailable, the fallback uses turn-taking and a tone; hands-free mid-reply interruption is then unavailable.

| Feature | Test | What to check |
|---|---|---|
| Wake word | Hey Bob → What time is it? | Conversation begins and the request is processed. |
| Hands-free follow-up | Set volume to thirty percent → What is my current volume? | Second request works without clicking the mic again. |
| Mid-reply interruption | Explain how rain forms → Hey Bob, actually open calculator | Bob stops the active answer and processes the replacement request; Calculator actually opens. |
| Echo rejection | Ask Tell me a long story, then remain silent | Bob should not treat its own output as your speech. Loud room echo can still cause problems. |
| Shorter answer | During an explanation say Hey Bob, shorter or Hey Bob, just the answer | Bob attempts a concise rephrasing using available context; it should not repeat previous actions. |
| End listening plus action | Actually stop listening and open YouTube | Capture ends and the remaining supported opening request is processed. |
| Uncertain transcript | Inspect any flagged words before sending | Confirm/edit the text; do not approve a misheard action. |
| Literal dictation | Type Hello, Bob! in Notepad | Exact words appear once. Bob does not silently grammar-correct dictated content. |
| Longer pauses | Give me more time to think | Pause setting becomes Thinking time; save/inspect it in Settings. |
| Faster fixed pauses | Respond faster | Pause setting becomes Quick. Return to Natural in Settings when wanted. |
| Custom names | Add your name/project names under Names and pronunciation hints; save, then speak them | Hints can improve English transcription; they are not acoustic voice training. |

Natural pacing waits 450 ms for turns with under 0.6 seconds of detected speech, 650 ms normally, and 950 ms after at least 2.5 seconds of speech. Quick is fixed 450 ms, Patient 1.2 seconds, Thinking 1.8 seconds. Enrollment uses a longer pause. If you resume before the deadline, the same turn continues; a longer pause can split your sentence. Turn capture is bounded to about 20 seconds.

Whisper prepares at conversation start and transcribes completed turns, not each word live. English recognition remains imperfect. Native actions already executing are protected from acoustic onset cancellation; interrupting a reply does not undo completed steps. [Full voice pipeline and diagram](VOICE-PIPELINE.md).

### Choose Bob's spoken voice

In **Settings → Voice & personality → Bob’s voice**, choose Automatic, Windows or Azure neural. Windows voices are the installed offline voices; select one, click **Listen to this voice**, then Save. Automatic uses configured Azure when available and Windows otherwise. Azure requests can fall back to Windows on failure; check notices if the sound changes.

Available neural choices are **Andrew, Ava, Brian and Emma**, plus the voice set in the Azure configuration. They need internet and your Azure Speech account; reply text is sent to Microsoft. These choices affect desktop and private-phone webpage replies. Twilio carrier calls use a separate fixed reminder voice.

To configure Azure: create a Speech resource, obtain its resource key and region, use **Set up neural voice** in Bob, and open the data folder. In `neural-voice.json`, keep valid JSON and set:

```json
{
  "enabled": true,
  "region": "YOUR_RESOURCE_REGION",
  "key": "YOUR_PRIVATE_RESOURCE_KEY",
  "voice": "en-US-AndrewMultilingualNeural"
}
```

Select Azure/Andrew, preview, then save. Preview must audibly play; configuration existing alone is not proof it works. Test each available voice and adjust **Speaking pace** (-5 to +5). Select Windows again for offline speech. See Microsoft's [Speech setup guide](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-text-to-speech?pivots=programming-language-python) for resource key/region setup. A multilingual voice name does not make Bob's English recognizer multilingual.

### Recognize people by voice — optional

1. End the current conversation. Open **Settings → Recognize my voice** and enter your preferred name.
2. Click **Record sample**, wait for Listening, speak normally for 5–10 seconds, then pause about two seconds. Example sentences are suggestions, not a spelling test.
3. Repeat for three samples in a quiet room using your normal microphone.
4. Enable **Recognize my voice**, choose Balanced and Save settings.
5. Click **Test voice match**, say a new five-second sentence, then pause. The test does not execute what you say. Check Recognized as your name.
6. Start a conversation and give a normal full-sentence request. A confident match can resume your profile's conversation, memories and personality and greet you.
7. Use **Add another person** for another three-sample profile; up to eight profiles are supported. Assign each a personality in its dropdown.
8. Use Strict if other voices match incorrectly. Disable recognition to keep profiles without matching; Delete removes a profile. Deleting voice features does not erase its saved chats/memories—review those separately in Memory/Recent conversations.

Try two enrolled people: each says a full sentence, then inspect the recognized name, their resumed conversation and memory workspace. A short Yes may be uncertain and ordinary commands can still proceed. Speaker recognition is approximate personalization, not authentication, owner-only interruption filtering or family permissions.

## Conversation, personalities and context

Open-ended examples below need Ollama. Response quality depends on the selected model and available recent context.

| Feature | Example/test | Expected behavior and limit |
|---|---|---|
| Casual conversation | Hi Bob, how are you? | Natural text/spoken reply; no fabricated action. |
| Explanation | Explain how rain forms | Explanatory answer; Speak replies as they arrive can begin at sentence boundaries. |
| Tutor | Use tutor mode → Teach me percentages with an example | Step-by-step wording. There is no persistent learning-progress service. |
| Fast answers | Use fast mode → Explain what RAM does | Short useful answer first. |
| Calm answers | Use calm mode → Help me break this task into small steps | Simple, calmer wording. |
| Balanced | Use balanced mode | Restores general conversation mode. |
| Rephrasing | Rewrite this with correct grammar: I has a meeting tomorrow | Produces revised text. Explicitly request typing it if wanted; rewriting alone must not type into an app. |
| Recent response as dictation | After a harmless short rewritten sentence: Type your previous response in Notepad | Model-assisted; inspect exact intended text and actual editor content. |
| Shortening/skipping | Shorter / Skip that part / Summarize that | Rephrases available context; does not replay previous actions. |
| Topic continuity | Reopen an old conversation → Continue the plan we discussed | Uses available bounded recent messages; not unlimited archived retrieval. |
| Discussion summary | Summarize our decisions and remaining tasks | Summarizes available conversation, not your entire email/calendar. |
| Explicit preferences | Remember that my preferred name is Bhanu | Saves a fact you can inspect/remove in Memory. |
| Repeat successful action | Open calculator → Do the same thing as last time | Reuses recent successful action in that chat. Inspect the proposed action before approval if asked. |
| App reference | Open Notepad → Move it to monitor two | Uses recent app context; requires two monitors. |
| Files reference | Find test in Bob Manual Test in Documents → Show properties of that file | Needs exactly one selected result; otherwise choose a specific item. |
| Tab reference | Close YouTube finds several → Close the second one | Uses the recent tab list, not a window literally named second one. |
| Bulk reference | Close YouTube finds several → Close all those | Closes the scoped listed tabs after approval. A previous window list instead means those whole windows. |
| Recent numeric correction | Set volume to thirty percent → No, I meant forty percent | Supported numeric correction attempts a new 40% change; check read-back. |
| In-sentence replacement | Open calculator, no actually open Notepad | Supported explicit repair favors the replacement request; arbitrary corrections remain partial. |
| Pending reminder correction | Remind me in two hours to check the oven, ask me before scheduling it → No, I meant Friday | Updates the pending reminder date, retaining time; inspect the new due date and approve or cancel. For time say No, I meant 6 PM. |
| Approve/cancel | Yes / Cancel | Approves or cancels the current concrete pending action. Changed pending actions require fresh approval. |
| Multistep direct command | Open Notepad and type Hello Bob in Notepad | Notepad opens, then literal words are inserted. Earlier completed steps remain completed after later failure. |
| Dependent file workflow | Find test in Bob Manual Test in Documents and copy those files to Downloads | Uses find results; refuse collisions. Test with disposable files. |
| Mixed workflow | Pause the video and set volume to twenty percent | Both supported steps execute and report results; inspect player and output level. |
| Model-assisted agent workflow | Open Notepad, write a short checklist for testing Bob, and leave it ready to review | A model can plan supported tool steps based on results. Exact text and target still need checking; no universal autonomous app control. |

Model-assisted workflows are bounded to four planning stages/twelve tool calls. General implicit needs, emotional tone, summaries and references are model-dependent. A request such as I'm hungry can lead to discussion, but there is no connected location/food ordering service. Asking to send a message cannot work as a first-class messaging integration in this version.

### Personality choices and traits

Choose a preset in Settings, Save, then ask **Tell me about a rainy day in two sentences** to compare wording. Personality changes wording, not app permissions or factual truthfulness.

| Preset | How to select/test |
|---|---|
| Balanced | Choose it in Settings, save, then use the same rainy-day question. |
| Witty butler | Choose it in Settings, save, then use the same rainy-day question. |
| Friendly companion | Choose it in Settings, save, then use the same rainy-day question. |
| Motivating coach | Choose it in Settings, save, then use the same rainy-day question. |
| Precise engineer | Choose it in Settings, save, then use the same rainy-day question. |
| Curious explorer | Choose it in Settings, save, then use the same rainy-day question. |
| Funny companion | Choose it in Settings, save, then use the same rainy-day question. |
| Serious professional | Choose it in Settings, save, then use the same rainy-day question. |
| Discreet assistant | Choose it in Settings, save, then use the same rainy-day question. |
| Candid advisor | Choose it in Settings, save, then use the same rainy-day question. |

Voice style changes: **Be funnier**, **Be serious**, **Be discreet**, **Be more honest**, **Be balanced**, **No jokes**. You can also say **Set your humor to 80**, **Set your seriousness to 90**, **Set your discretion to 90**, or **Set your honesty to 90**. Each trait is 0–100; inspect Settings afterward. Reset traits restores preset defaults. Custom Personality instructions can specify a name or concise wording; Save to apply.

Honesty means tactful versus frank feedback: Bob must remain truthful at every setting. Discretion controls wording, not encrypted storage, permissions or a private mode. Serious topics should remain clear even with humor high.

## Complete action test catalog

Run a typed example first, then the same spoken example. This separates command execution from recognition quality. A good test checks the actual window/file/value, not just Bob's answer. Commands that close, rename, recycle, disconnect or call may require approval; do not say Yes if the displayed target is wrong.

### Applications, websites and system information

Use these from voice or the message box. Installed applications vary by computer. The Applications list in Capabilities is the available catalog.

| Feature | Read this command | Check this result |
|---|---|---|
| Open an application | **Open calculator** | A Calculator window appears. Also try Open Notepad or Open Microsoft Edge. | <!-- action:open -->
| Search the web | **Search the web for Windows keyboard shortcuts** | Search results open in Edge. This is a web search, not a verified factual answer. | <!-- action:search -->
| Current time and date | **What time is it?** | Bob reports the PC clock and date. | <!-- action:time -->
| System usage | **System status** | Bob reports CPU and RAM usage. This is not battery or Windows Update status. | <!-- action:status -->
| Windows Update page | **Check for system updates** | The Windows Update page opens. Bob does not install updates or prove your PC is up to date. | <!-- action:windows_update -->
| Lock Windows | **Lock my computer** | After approval Windows locks. Test last, when your work is saved; sign back in normally. | <!-- action:lock -->

### Volume and brightness

Before testing, note your original levels and restore them afterward. Volume applies to the default Windows output, not each app mixer. Brightness needs supported WMI/DDC hardware; some monitors require DDC/CI enabled in their physical menu.

| Feature | Read this command | Check this result |
|---|---|---|
| Read volume | **What is my current volume?** | Bob reports the default output volume and mute state. | <!-- action:audio_status -->
| Set volume | **Set volume to thirty percent** | The default output reads 30% and is unmuted. Keep test volume comfortable. | <!-- action:volume -->
| Increase volume | **Increase volume by ten percent** | Volume increases by 10 percentage points, clamped at 100. | <!-- action:volume_up -->
| Decrease volume | **Lower volume by ten percent** | Volume decreases by 10 percentage points, clamped at zero. | <!-- action:volume_down -->
| Mute output | **Mute the volume** | Windows output is muted. | <!-- action:mute -->
| Unmute output | **Unmute the volume** | Windows output is unmuted; its existing level is retained. | <!-- action:unmute -->
| Read display brightness | **What is my current brightness?** | Bob lists supported displays and their brightness. Use these numbers for brightness commands. | <!-- action:brightness_status -->
| Set brightness | **Set brightness on monitor two to forty percent** | The selected supported display reads back 40%. Use Set brightness to forty percent for all supported displays. | <!-- action:brightness -->
| Increase brightness | **Increase brightness by ten percent** | Supported displays increase by 10 percentage points. | <!-- action:brightness_up -->
| Decrease brightness | **Lower brightness by ten percent** | Supported displays decrease by 10 percentage points. | <!-- action:brightness_down -->

### Windows, monitors, typing and keyboard controls

Open a disposable Notepad document first. Name an app or exact window title when several match. If no target is named, Bob may reuse recent app context; explicitly focus/name your target for keyboard tests. Generic clicks can need Ollama to interpret the request.

| Feature | Read this command | Check this result |
|---|---|---|
| List open windows | **List windows** | Bob lists visible titles/processes so you can choose a target. | <!-- action:list_windows -->
| List monitor destinations | **List monitors** | Bob lists displays, primary first. These numbers are shared by brightness and window movement; they may differ from Windows Settings labels. | <!-- action:list_monitors -->
| Switch to an app | **Switch to Notepad** | The intended Notepad window becomes foreground. | <!-- action:focus_window -->
| Minimize an app | **Minimize Notepad** | Notepad goes to the taskbar. | <!-- action:minimize_window -->
| Restore an app | **Restore Notepad** | Notepad returns from minimized/maximized state. | <!-- action:restore_window -->
| Maximize an app | **Maximize Notepad** | Notepad fills its monitor work area. | <!-- action:maximize_window -->
| Move between monitors | **Move Notepad to monitor two** | The actual window moves to monitor 2. Requires a second detected display; follow with Move it to monitor one. | <!-- action:move_window -->
| Read accessible controls | **Inspect window Notepad** | Bob lists exposed controls. This is accessibility inspection, not screenshot understanding. | <!-- action:inspect_window -->
| Literal dictation | **Type Hello, Bob! in Notepad** | The editor contains exactly Hello, Bob! once. Check punctuation; spoken recognition can still be wrong. | <!-- action:type_text -->
| Keyboard shortcut | **Press control A** | After focusing the disposable Notepad document, all text is selected. Full key catalog appears below. | <!-- action:press_key -->
| Click a named control | **Click the Open button in Notepad** | Model-assisted: first inspect Notepad and open a disposable dialog that exposes an Open button. Approve only the correct target. Missing/ambiguous controls should produce an error. | <!-- action:click_control -->
| Close a window | **Close Notepad** | Approve the named window; it disappears, or a save dialog/verification error is reported. Do not test on unsaved important work. | <!-- action:close_window -->

### Microsoft Edge

Start Edge first. With several windows, focus the intended one before waking Bob or supply its exact title. Ordinary navigation/tab lists use that window; named bulk tab closure searches matching tabs across Edge windows. Page labels must be visible, unique and accessible.

| Feature | Read this command | Check this result |
|---|---|---|
| Open an address | **In Edge go to example.com** | The address bar shows the requested site; loading/network/login remains the site’s responsibility. | <!-- action:edge_navigate -->
| Search in Edge | **In Edge search for Python tutorials** | The search results page opens. | <!-- action:edge_search -->
| Navigate, zoom and scroll | **In Edge open another tab** | A new tab opens. All 19 supported shortcut operations are listed below. | <!-- action:edge_shortcut -->
| List current-window tabs | **In Edge list tabs** | Tab titles are listed and remembered as a scoped selection. | <!-- action:edge_tabs -->
| Choose a named tab | **In Edge switch to the Example Domain tab** | An existing uniquely matching Example Domain tab is selected. Use the displayed title. | <!-- action:edge_select_tab -->
| Read accessible page labels | **In Edge read this page** | Bob lists exposed labels/controls; it does not read every pixel or guarantee a page summary. | <!-- action:edge_inspect -->
| Find text on page | **In Edge find domain on this page** | Edge’s Find UI receives domain; check its matches yourself. | <!-- action:edge_find -->
| Fill a field | **In Edge fill Bob test into the Search field** | Use a disposable page with an accessible Edit field named Search, or replace Search with a label from inspection. Text is filled but not submitted. | <!-- action:edge_fill -->
| Click a page control | **In Edge click More information** | On example.com, approve a matching visible link if exposed. A click does not guarantee the destination operation succeeded. | <!-- action:edge_click -->
| Close one named tab | **Close YouTube** | Approve the selected YouTube tab. If several match, choose a listed title or Close the second one. | <!-- action:edge_close_tab -->
| Close a matching tab group | **Close all YouTube** | Approve the displayed group; matching YouTube tabs across Edge windows disappear. Unrelated tabs should remain. | <!-- action:edge_close_tabs -->

### Windows connections and Settings

Use the keyboard/mouse to restore connectivity if needed. Do not turn off Wi-Fi or enable airplane mode during a remote-phone test: it can cut off your connection. Settings controls depend on English labels, Windows version, exposed accessibility and permissions.

| Feature | Read this command | Check this result |
|---|---|---|
| Read Bluetooth/Wi-Fi radio | **Is Bluetooth on?** | Bob reports radio state. Also try Check Wi-Fi status for the Wi-Fi radio; use Wi-Fi status for the network connection. | <!-- action:radio_status -->
| Change Bluetooth/Wi-Fi radio | **Turn Bluetooth on** | Bob changes and reads back exposed radio state. Also test Turn Bluetooth off, Turn Wi-Fi on and Turn Wi-Fi off; disabling Wi-Fi needs approval. | <!-- action:radio_set -->
| Read connected network | **Wi-Fi status** | Bob reports the connected network/adaptor information, or a permission error. | <!-- action:wifi_status -->
| List saved networks | **List saved Wi-Fi networks** | Saved Windows profile names appear; passwords are not read. | <!-- action:wifi_profiles -->
| Connect to a saved network | **Connect to Wi-Fi MyNetwork** | Replace MyNetwork with an exact saved profile. Connection is checked. Reconnect Wi-Fi reuses previous connection context. | <!-- action:wifi_connect -->
| Disconnect Wi-Fi | **Disconnect from Wi-Fi** | Approve; Bob checks that the connection ended. Test locally with a way to reconnect. | <!-- action:wifi_disconnect -->
| Open a Settings page | **Open display settings** | Display Settings opens. Every supported page has an example below. | <!-- action:settings_open -->
| Read current Settings controls | **Inspect settings** | Visible accessible labels and states appear; have only one Settings window open. | <!-- action:settings_inspect -->
| Read airplane/energy saver state | **Is energy saver on?** | Bob reads the exposed setting; it may open its page. Also try Is airplane mode on? | <!-- action:settings_status -->
| Change exposed Settings control | **Set Night light to on in display settings** | Approve the exact label/value; Bob verifies an exposed toggle. Also try Turn airplane mode off and Turn battery saver on where available. | <!-- action:settings_set -->

### File Explorer and local files

Create a new disposable Bob Manual Test folder in Documents using Windows first, then a test.txt file inside it. Do not reuse an existing important folder. Give full paths or establish folder context. Replace sample paths with your actual Documents location, including OneDrive redirection. Never use important files for delete/move tests.

| Feature | Read this command | Check this result |
|---|---|---|
| List a folder | **List files in Bob Manual Test in Documents** | Up to 100 items appear; folder context is saved. Listing does not automatically select all files. | <!-- action:file_list -->
| Find filenames | **Find test in Bob Manual Test in Documents** | Matching names are selected for follow-up operations; this is filename search, not semantic document search. | <!-- action:file_find -->
| Create a folder | **Create folder Bob Results in Documents** | A new Bob Results folder appears; existing folders are not overwritten. | <!-- action:file_mkdir -->
| Open a file or folder | **Open file test.txt in Bob Manual Test in Documents** | Use the real test-file location. It opens with its Windows association. Scripts/installers/shortcuts are excluded. | <!-- action:file_open -->
| Read properties | **Show properties of test.txt in Bob Manual Test in Documents** | Path, type, size and modified date appear. Folder contents are not recursively sized. | <!-- action:file_properties -->
| Use Explorer selection | **Use selected files** | First select only disposable files and bring Explorer forward before waking Bob. Bob remembers those specific paths. | <!-- action:explorer_selection -->
| Copy selected files | **Copy those files to Documents** | First select a disposable source in another folder. Copies appear without overwriting collisions. Use a fresh destination for repeats. | <!-- action:file_copy -->
| Move selected files | **Move those files to Documents** | Approve exact source/destination. Same-drive source disappears and destination appears. Cross-drive moves are excluded. | <!-- action:file_move -->
| Rename one item | **Rename that file to renamed-test.txt** | First select one disposable file. Approve; its actual name changes. | <!-- action:file_rename -->
| Send to Recycle Bin | **Delete that file** | Approve exact path; the disposable item disappears and can be recovered from Recycle Bin. No permanent deletion. | <!-- action:file_recycle -->

### Music and video

Start a local track or a video in a player that publishes Windows media controls. Each app decides which operations it supports. Live streams often cannot seek; unsupported operations must return an error. Playback commands do not require a yes/no prompt.

| Feature | Read this command | Check this result |
|---|---|---|
| List available players | **List media players** | Bob lists Windows media sessions; choose an app/title if several are present. | <!-- action:media_sessions -->
| Read current playback | **What is playing?** | Title, artist, app, state and position are reported where exposed. | <!-- action:media_status -->
| Play/resume | **Play music** | Resumes a suitable session; if none exists, tries a local Music file. Resume in Edge targets Edge. | <!-- action:media_play -->
| Pause playback | **Pause the video** | The session reports Paused. Also try Pause in Spotify with that app playing. | <!-- action:media_pause -->
| Stop playback | **Stop playback** | The session reports Stopped if it exposes Stop. | <!-- action:media_stop -->
| Next track | **Next song** | Track title changes if skipping is supported. | <!-- action:media_next -->
| Previous/restart track | **Previous track** | Previous track or restart is verified according to the player’s reported position/title. | <!-- action:media_previous -->
| Seek/restart | **Seek to 1:30** | Playback moves to about 90 seconds. Restart the video seeks to its beginning. | <!-- action:media_seek -->
| Relative forward seek | **Fast forward two minutes** | Position advances by about 120 seconds, bounded by the timeline. | <!-- action:media_forward -->
| Relative backward seek | **Rewind thirty seconds** | Position moves back about 30 seconds. | <!-- action:media_back -->
| Shuffle | **Shuffle on** | The session reports shuffle on. Restore with Shuffle off. | <!-- action:media_shuffle -->
| Repeat modes | **Repeat one** | Repeat-one is reported. Also test Repeat all and Repeat off. | <!-- action:media_repeat -->
| Playback speed | **Set speed to 1.5x** | The session reports 1.5× if supported. Restore with Set speed to 1x. Allowed range: 0.25–4×. | <!-- action:media_rate -->
| Open local media | **Play song Yesterday** | Finds a uniquely matching local Music filename, not an online catalog. Or Play file C:\Music\track.mp3 with an existing test file. Opening is not proof of playing. | <!-- action:media_open -->
| Find online media | **Search for music jazz on YouTube** | Search results open; choose a result yourself. Search for music jazz on Spotify is also supported; login/subscription may be needed. | <!-- action:media_search -->

### Memory, notes and your project

Choose and save Your current project in Settings before project tests. Use a harmless project with README.md. Project functions read/list/search files; they do not edit code or run a build.

| Feature | Read this command | Check this result |
|---|---|---|
| Save a fact | **Remember that my favorite color is blue** | The fact appears in Memory for the current voice workspace/general workspace. | <!-- action:remember -->
| Retrieve an explicit fact | **What do you remember about my favorite color?** | Bob returns the saved fact. This command matches memory names, not every archived message. | <!-- action:recall -->
| Save a text note | **Take a note: test Bob again tomorrow** | A timestamped text file appears under notes in Bob’s data folder. | <!-- action:note -->
| Open chosen project | **Open my project** | Explorer opens the configured project folder. | <!-- action:open_project -->
| List project files | **List project files** | Up to 80 file paths appear, scanning up to 5,000 files. | <!-- action:project_list -->
| Search project paths | **Find in my project README** | Matching relative file paths appear; it searches filenames/paths, not file contents. | <!-- action:project_search -->
| Read a project file | **Read project file README.md** | Allowed UTF-8 text appears, truncated at 20,000 characters. Sensitive filenames, out-of-project paths and files over 100 KB are excluded. | <!-- action:project_read -->

### Reminders: PC, webpage and phone number

Reminders are one-shot and require Bob running when due. Phone-number calls need Twilio configuration and approval; do not run a call example unless you want the paid attempt. Webpage alerts require the paired page open and phone awake.

| Feature | Read this command | Check this result |
|---|---|---|
| Create a reminder | **Remind me in two minutes to take a break** | A PC reminder is saved, then notifies/speaks when due. Other delivery examples appear in the phone section. | <!-- action:reminder_add -->
| List reminders | **Show my reminders** | IDs, due times, delivery channels and statuses appear. | <!-- action:reminder_list -->
| Cancel a pending reminder | **Cancel reminder that reminder** | Immediately after creating a disposable reminder this cancels it. Or Cancel reminder ab12cd34 using the actual displayed ID. | <!-- action:reminder_cancel -->

## Additional command catalogs

### Extra opening routes

These routes supplement the 90 tool actions above. **Open Documents**, **Open Downloads**, **Open Desktop**, **Open Pictures**, **Open Music**, **Open Videos** open standard folders. The requested folder path is remembered, but the Explorer display is not always verified.

**Open example.com** opens an explicit HTTP/HTTPS site. Known services below can open their websites when the application is absent; an installed matching application may take priority. **Open YouTube app** and **Open website for Spotify** are accepted opening phrases. An unknown app/domain is not invented: supply a real website address or search for it. Opening a web service does not integrate its messages/calendar/accounts with Bob.

The legacy **Open my Bob** route only opens a configured `bob_url` in a browser. The current Settings UI does not expose that URL field; it is not account linking or memory synchronization with ChatGPT/Astra.

### All Edge shortcut operations

Use a disposable browsing window. Page scrolling needs a long page, and Back/Forward need navigation history. Reopen requires a previously closed tab. Escape uses the generic keyboard path after focusing Edge rather than a direct Edge shortcut phrase.

| Operation | Example | Check |
|---|---|---|
| Back | **In Edge go back** | Observe back; closing asks first. Escape may depend on focus/context. |
| Forward | **In Edge go forward** | Observe forward; closing asks first. Escape may depend on focus/context. |
| Reload | **In Edge refresh the page** | Observe reload; closing asks first. Escape may depend on focus/context. |
| New Tab | **In Edge open a new tab** | Observe new tab; closing asks first. Escape may depend on focus/context. |
| Close Tab | **In Edge close this tab** | Observe close tab; closing asks first. Escape may depend on focus/context. |
| Reopen Tab | **In Edge reopen the closed tab** | Observe reopen tab; closing asks first. Escape may depend on focus/context. |
| Next Tab | **In Edge next tab** | Observe next tab; closing asks first. Escape may depend on focus/context. |
| Previous Tab | **In Edge previous tab** | Observe previous tab; closing asks first. Escape may depend on focus/context. |
| Downloads | **In Edge show downloads** | Observe downloads; closing asks first. Escape may depend on focus/context. |
| History | **In Edge show history** | Observe history; closing asks first. Escape may depend on focus/context. |
| Favorites | **In Edge show favorites** | Observe favorites; closing asks first. Escape may depend on focus/context. |
| Zoom In | **In Edge zoom in** | Observe zoom in; closing asks first. Escape may depend on focus/context. |
| Zoom Out | **In Edge zoom out** | Observe zoom out; closing asks first. Escape may depend on focus/context. |
| Reset Zoom | **In Edge reset zoom** | Observe reset zoom; closing asks first. Escape may depend on focus/context. |
| Scroll Down | **In Edge scroll down** | Observe scroll down; closing asks first. Escape may depend on focus/context. |
| Scroll Up | **In Edge scroll up** | Observe scroll up; closing asks first. Escape may depend on focus/context. |
| Top | **In Edge go to the top** | Observe top; closing asks first. Escape may depend on focus/context. |
| Bottom | **In Edge go to the bottom** | Observe bottom; closing asks first. Escape may depend on focus/context. |
| Escape | **Switch to Microsoft Edge, then Press Escape** | Observe escape; closing asks first. Escape may depend on focus/context. |

### All generic keyboard shortcuts

Focus the intended disposable app first. Say **Press** followed by the item below; for example **Press control F**. Letters such as control/control-plus can normalize to Ctrl. Enter, Ctrl+S, Ctrl+V and Ctrl+W can have consequential effects and ask first. A delivered keystroke is not proof the app completed an operation. Ctrl+S may open a save dialog; Bob does not silently finish that dialog.

| Supported key | Example to read |
|---|---|
| enter | **Press enter** |
| tab | **Press tab** |
| escape | **Press escape** |
| backspace | **Press backspace** |
| up | **Press up** |
| down | **Press down** |
| left | **Press left** |
| right | **Press right** |
| page up | **Press page up** |
| page down | **Press page down** |
| home | **Press home** |
| end | **Press end** |
| ctrl+a | **Press control a** |
| ctrl+c | **Press control c** |
| ctrl+v | **Press control v** |
| ctrl+z | **Press control z** |
| ctrl+s | **Press control s** |
| ctrl+f | **Press control f** |
| ctrl+l | **Press control l** |
| ctrl+t | **Press control t** |
| ctrl+w | **Press control w** |
| ctrl+tab | **Press control tab** |
| shift+tab | **Press shift tab** |
| alt+left | **Press alt left** |
| alt+right | **Press alt right** |
| f5 | **Press f5** |

### Every supported Windows Settings page

Each command opens a page, not changes all settings on it. Some Windows versions redirect or do not expose a page. After opening, say **Inspect settings**, then use a visible exact label, for example **Set Night light to on in display settings**. Exposed toggles, dropdowns and numeric sliders are supported, not every button/dialog. English labels, administrator policy and hardware restrictions apply. Restore any setting you change while testing.

| Page | Command |
|---|---|
| System | **Open system settings** |
| Display | **Open display settings** |
| Sound | **Open sound settings** |
| Notifications | **Open notifications settings** |
| Focus | **Open focus settings** |
| Power | **Open power settings** |
| Battery Saver | **Open battery saver settings** |
| Storage | **Open storage settings** |
| Multitasking | **Open multitasking settings** |
| About | **Open about settings** |
| Bluetooth | **Open bluetooth settings** |
| Devices | **Open devices settings** |
| Printers | **Open printers settings** |
| Mouse | **Open mouse settings** |
| Touchpad | **Open touchpad settings** |
| Typing | **Open typing settings** |
| Wifi | **Open wifi settings** |
| Airplane Mode | **Open airplane mode settings** |
| Network | **Open network settings** |
| Ethernet | **Open ethernet settings** |
| Vpn | **Open vpn settings** |
| Proxy | **Open proxy settings** |
| Mobile Hotspot | **Open mobile hotspot settings** |
| Background | **Open background settings** |
| Colors | **Open colors settings** |
| Themes | **Open themes settings** |
| Lock Screen | **Open lock screen settings** |
| Taskbar | **Open taskbar settings** |
| Start Menu | **Open start menu settings** |
| Fonts | **Open fonts settings** |
| Apps | **Open apps settings** |
| Default Apps | **Open default apps settings** |
| Startup Apps | **Open startup apps settings** |
| Accounts | **Open accounts settings** |
| Sign In | **Open sign in settings** |
| Other Users | **Open other users settings** |
| Date And Time | **Open date and time settings** |
| Language | **Open language settings** |
| Region | **Open region settings** |
| Accessibility | **Open accessibility settings** |
| Text Size | **Open text size settings** |
| Magnifier | **Open magnifier settings** |
| Narrator | **Open narrator settings** |
| Keyboard | **Open keyboard settings** |
| Privacy | **Open privacy settings** |
| Microphone | **Open microphone settings** |
| Camera | **Open camera settings** |
| Location | **Open location settings** |
| Windows Update | **Open windows update settings** |
| Update History | **Open update history settings** |
| Recovery | **Open recovery settings** |
| Activation | **Open activation settings** |
| Troubleshoot | **Open troubleshoot settings** |
| Remote Desktop | **Open remote desktop settings** |
| Gaming | **Open gaming settings** |

Airplane mode uses the exposed Settings toggle: **Turn airplane mode on** needs approval because it can disconnect you; **Turn airplane mode off** restores it. **Turn battery saver on/off** depends on Windows exposing its energy-saver control, sometimes unavailable while charging. This is not full control of all system-tray items or paired Bluetooth device management.

### Every known web service

Test opening only; verify the address. Login, payment, messaging, calendar changes, form submission and content playback are separate from opening a site.

| Service | Command | Website fallback |
|---|---|---|
| Youtube | **Open youtube** | https://www.youtube.com |
| Google | **Open google** | https://www.google.com |
| Github | **Open github** | https://github.com |
| Spotify | **Open spotify** | https://open.spotify.com |
| Netflix | **Open netflix** | https://www.netflix.com |
| Whatsapp | **Open whatsapp** | https://web.whatsapp.com |
| Telegram | **Open telegram** | https://web.telegram.org |
| Discord | **Open discord** | https://discord.com/app |
| Gmail | **Open gmail** | https://mail.google.com |
| Outlook | **Open outlook** | https://outlook.live.com |
| Instagram | **Open instagram** | https://www.instagram.com |
| Facebook | **Open facebook** | https://www.facebook.com |
| X | **Open x** | https://x.com |
| Reddit | **Open reddit** | https://www.reddit.com |
| Amazon | **Open amazon** | https://www.amazon.in |
| Prime Video | **Open prime video** | https://www.primevideo.com |
| Chatgpt | **Open chatgpt** | https://chatgpt.com |
| Notion | **Open notion** | https://www.notion.so |
| Canva | **Open canva** | https://www.canva.com |
| Figma | **Open figma** | https://www.figma.com |
| Google Docs | **Open google docs** | https://docs.google.com |
| Google Drive | **Open google drive** | https://drive.google.com |
| Google Maps | **Open google maps** | https://maps.google.com |
| Google Calendar | **Open google calendar** | https://calendar.google.com |
| Microsoft Teams | **Open microsoft teams** | https://teams.microsoft.com |
| Zoom | **Open zoom** | https://app.zoom.us |
| Slack | **Open slack** | https://app.slack.com |
| Youtube Music | **Open youtube music** | https://music.youtube.com |

Supported alternate/spoken service names:

| Alias | Test command | Means |
|---|---|---|
| you tube | **Open you tube** | youtube |
| you-tube | **Open you-tube** | youtube |
| yt | **Open yt** | youtube |
| spot ify | **Open spot ify** | spotify |
| what sapp | **Open what sapp** | whatsapp |
| whats app | **Open whats app** | whatsapp |
| twitter | **Open twitter** | x |
| g mail | **Open g mail** | gmail |
| google mail | **Open google mail** | gmail |
| chat gpt | **Open chat gpt** | chatgpt |
| teams | **Open teams** | microsoft teams |
| primevideo | **Open primevideo** | prime video |
| you tube music | **Open you tube music** | youtube music |

## Phone access and locked-phone calls

### Choose the right connection

| Feature | Requirement | Locked iPhone? |
|---|---|---|
| Private chat and voice control | Tailscale, paired HTTPS webpage, PC awake/signed in with Bob running | Keep page open and phone awake for microphone conversation. |
| Phone-page reminder alert | Paired page open with audio allowed | No guaranteed locked/background delivery. |
| Carrier reminder call to your number | Twilio account/configuration, connectivity, Bob running | Can ring while locked, subject to signal, Focus, call blocking and carrier routing. |
| Locked-screen Hey Bob | Not implemented | No. The webpage cannot provide this capability. |

### Private mobile webpage setup

1. Install Tailscale on PC and iPhone. Sign into the same private network and connect both.
2. Keep Bob running. Open PowerShell on the PC and run:

```powershell
tailscale serve --bg http://127.0.0.1:8787
```

3. Complete HTTPS enablement if prompted. Copy the printed `https://your-pc.your-tailnet.ts.net` address. Use private Serve; do not use public Funnel or router port forwarding. See [Tailscale Serve documentation](https://tailscale.com/docs/reference/tailscale-cli/serve).
4. In Bob **Settings → Phone & reminders**, paste the HTTPS address and click **Enable mobile access**. A localhost-only preview cannot connect from the phone.
5. Open the generated pairing link on the phone with Tailscale connected. Keep the whole link private. **Remember this phone** retains pairing on your own browser/device.
6. End desktop voice mode. On the phone tap **Start private voice conversation**, allow the microphone, and keep the phone awake. Speak, pause, wait for the reply; it listens again after answering.
7. If a transcript is flagged, correct/check it and Send. If autoplay is blocked, tap the audio Play control. Phone voice is turn-taking, not the desktop full-duplex interruption loop.
8. Say **Stop listening** or tap Stop to finish. **Disable & revoke links** revokes access; creating a new pairing link invalidates older links. Pairing survives normal Bob restarts.

Test from the phone: **What time is it?**, **Open calculator**, **Set volume to thirty percent**, **Show my reminders**. Verify the actual PC change. Then disconnect/reconnect Tailscale and reopen the page; inspect results before resending a command. The webpage retries status checks with backoff but does not automatically replay PC commands after a network failure.

The PC must be awake, signed into an accessible Windows desktop and running Bob. Controls cannot bypass Windows lock/UAC. The phone page is not a screen-sharing viewer. Phone replies use your saved Windows/Azure voice selection; Windows is local, Azure sends reply text to Microsoft. Desktop and phone share an engine: if busy, stop desktop voice mode and wait.

### Phone-page reminders

Say **Remind me on my phone in two minutes to take a break**. Keep the paired page open and audio enabled. Check the alert and spoken output when due. This is not a dialer call, iOS push notification or guaranteed locked-screen alert. Say **Show my reminders** to inspect missed/pending statuses.

### Twilio calls to your phone number

1. In Twilio Console, obtain an Account SID, Auth Token and a voice-capable sender number. Use **live account credentials**, not Twilio test credentials, for a real ring. Enable outbound permissions for your destination country and complete any required account/number setup.
2. Trial accounts have template/custom-TwiML and destination restrictions. Bob submits its own reminder TwiML; the request can be rejected under trial restrictions. Do not assume a Console test call proves Bob's custom call is permitted. Check [Twilio's trial Voice instructions](https://www.twilio.com/docs/usage/trials/try-out-voice); upgrade if your current restriction blocks the Bob request. Provider charges may apply.
3. In Bob **Settings → Phone & reminders**, use **Create calling configuration**, then **Open data folder**. Edit `phone-calls.json` with Notepad. Keep valid JSON:

```json
{
  "enabled": true,
  "account_sid": "AC_REPLACE_WITH_YOUR_LIVE_ACCOUNT_SID",
  "auth_token": "REPLACE_WITH_YOUR_PRIVATE_AUTH_TOKEN",
  "from_number": "+REPLACE_WITH_TWILIO_VOICE_NUMBER",
  "to_number": "+REPLACE_WITH_YOUR_PHONE_NUMBER"
}
```

4. Replace every placeholder. Numbers must use international format with `+` and country code; for example an Indian number starts `+91`. Save. Do not share or commit this file.
5. Keep PC awake, internet connected and Bob running. Say **Call me in two minutes to test my reminder**. Inspect destination/time/message, then approve if you want the call attempt.
6. Say **Show my reminders**. Check the saved reminder's ID/channel/status. At the due time, answer your phone and listen for the reminder.
7. Repeat with your iPhone locked only after the first call succeeds. Ensure cellular reception and that Focus/unknown-caller screening/block lists allow the caller. A call can ring while locked without Tailscale or the Bob webpage on the phone.

These are one-way reminder calls: they speak and end. They do not listen to replies or let you control the PC by talking into that carrier call. They are not end-to-end encrypted; Twilio receives the phone numbers and reminder text. No public webhook is needed for this current outbound announcement implementation.

**Call submitted** means Twilio accepted an attempt, not that the phone rang or you answered. Bob attempts once, does not automatically redial, and fails calls over five minutes late rather than unexpectedly ringing after a long shutdown. A completed provider call can be voicemail. The carrier call uses a fixed Twilio neural reminder voice, separate from Bob's selected conversational voice/personality.

If no call arrives: inspect the reminder detail, then Twilio **Monitor → Logs → Calls**, exact sender number/Voice support, allowed country, trial restrictions and verified destination if required. A busy/no-answer status is not proof of the cause. Do not keep resending calls without checking logs.

### Opening Bob with Siri

You can make a private iPhone Shortcut named **Talk to Bob**, with the pairing URL and **Open URLs**, then say **Siri, Talk to Bob**. Unlock if prompted and start webpage voice mode. This opens the page; it does not enable always-on Hey Bob while locked.

### All reminder test variants

| Read this | Check |
|---|---|
| Remind me in two minutes to take a break | Local saved reminder, then desktop alert/spoken output when Bob is free. |
| Remind me on my phone in two minutes to take a break | Alert on the active paired phone page. |
| Call me in two minutes to take a break | Approved Twilio attempt, then actual ring and spoken message if delivery succeeds. |
| Remind me in two hours to check the oven, ask me before scheduling it | Pending approval rather than immediate scheduling. |
| No, I meant 6 PM | Before approval, edits the pending reminder time; verify the full revised due date. |
| Cancel | Cancels the current pending approval. |
| Show my reminders | Displays reminders, IDs, channel and status. |
| Cancel reminder that reminder | Cancels the last referenced pending reminder. |
| Cancel reminder ab12cd34 | Replace with the actual eight-character pending reminder ID. |

Relative seconds/minutes/hours/days are supported directly. Specific calendar-day requests can need the model and should be checked carefully. There is no recurring-reminder scheduler or two-way telephone conversation in this version.

## Privacy, backup and resource settings

- **Data:** default local folder is `%LOCALAPPDATA%\Bob` (unless overridden). It contains the database, notes and private configuration. Conversations and settings persist across releases.
- **Memory:** inspect each person's workspace and General workspace in Memory. Save/forget explicit facts with the UI. Removing voice features does not automatically remove saved chats/facts. The UI has no universal erase-everything command or encrypted conversation vault.
- **Voice:** ordinary transcription does not save recordings to disk. Speaker features are encrypted for the Windows account; they are not access control. Azure and Twilio have separate cloud data flows.
- **Pairing:** secret links grant remote command access to authorized network users possessing them. Disable/revoke when no longer wanted. Tailscale/HTTPS secures transport, not access by someone holding an unlocked device/link.
- **Backup:** quit Bob, then privately copy its data folder. Restore only with Bob closed. Keep credentials and biometric data out of public backups/GitHub. A backup for another Windows account may not decrypt speaker/pairing data.
- **Idle memory:** choose Ollama Unload model after idle: every response, 30 seconds, 2 minutes, 5 minutes or 10 minutes. Longer retention speeds follow-ups but uses more memory. This setting controls Ollama, separately from Whisper's approximately 3-minute session / 1-minute inactive idle release.
- **Context size:** 2,048, 4,096 or 8,192 tokens; more context consumes more resources and still does not provide unlimited memory.
- **Background:** X quits Bob and all its services; minimizing pauses animations while keeping Bob available. Startup auto-listening uses an active mic/session and more resources than standby. Bob must remain running for reminders and phone access.

File tools exclude protected system/app-data folders, network/device paths, symlinks/junctions and permanent deletion. Bulk selection is bounded to 50 roots, with limits of 2,000 entries/1 GB per root; name search scans at most 5,000 entries and returns at most 50 matches. Copies refuse collisions; partial copies after an error need inspection before retrying.

## Troubleshooting and test checklist

| Problem | Try this |
|---|---|
| Bob does not wake | Enable Wake words, save, check default microphone and installed Windows English speech pack. Test using Start voice conversation to separate wake detection from transcription. |
| Bob waits too long / cuts off thoughts | Choose Natural, Patient or Thinking; end/restart voice mode after changing audio devices. Background noise can delay endpoints. |
| Background noise interrupts Bob | Reduce speaker volume, move microphone away from speakers, use a quieter room/headphones, confirm echo cancellation active. Voice identity is not owner-only interruption filtering. |
| Wrong transcript | Add names/term hints, speak after Listening, check default mic gain and review flagged words. Type the same request to test the execution path. |
| Voice identity uncertain | Use a full sentence and Test voice match, record fresh quiet samples with the same mic. Balanced is less strict; Strict can reduce false matches. |
| No spoken reply | Enable voice replies, save, use Test voice output/Preview, check output/mute. If Azure fails, choose a working Windows voice. |
| Empty/slow model answer | Start/refresh Ollama, verify exact installed model and available resources. Large models/load time cause delay. Try a direct command to isolate model latency. |
| Bob says opened but no app | Inspect its wording: launch requested/unverified is not success. List windows, check application startup; report the exact request/result if a verified claim is wrong. |
| Close all YouTube ambiguous | Say Close all YouTube tabs, inspect selected tab titles and approve. To close whole browser windows say Close all YouTube windows; they include unrelated tabs in those windows. |
| No current reference | Name the app/site/file again. Tab/window selections expire and are scoped; Close all must not mean every app on the PC. |
| Edge wrong window | Focus the intended Edge window before waking Bob; provide its exact title if needed. Native accessibility cannot control every page/canvas/dialog. |
| Brightness unchanged | Read brightness first, choose its actual display number, enable monitor DDC/CI if supported, check hardware/driver errors. Use the shared Bob monitor numbers from List monitors; unsupported identities must not fall back to another screen. |
| Volume unchanged | Check the default output device, mute and physical speaker controls. Bob does not change per-app mixer levels. |
| Settings control missing | Inspect settings, use exact exposed label, keep one Settings window open; Windows version/UAC/policy can block it. |
| File rejected | Use a regular local disposable path, explicit selection, same-drive move and collision-free destination. |
| Media control unsupported | List media players, name the app/title, start playback there. The app must expose the requested Windows control. |
| Phone cannot connect | Bob running, mobile enabled, both devices connected to Tailscale, PC awake; check tailscale serve status. Use private HTTPS pairing link, not phone localhost. |
| Phone says busy | Stop desktop voice mode and wait for current engine work. |
| Carrier call absent | Inspect reminder detail and Twilio Logs before retrying; verify live credentials, sender, country permissions and account restrictions. |

### Suggested test order

1. Type time/status, open Calculator and Notepad, then test voice output/wake.
2. Test conversation, short replies, pauses and interruption with harmless app opening.
3. Test Settings choices, every personality/mode and three-sample speaker matching if enabled.
4. Record original volume/brightness, test their commands, restore values.
5. Test window movement on two monitors and literal dictation in a disposable document.
6. Open disposable Edge tabs, test all navigation shortcuts and then named/bulk closing.
7. Test every Settings page; change only reversible supported controls, then restore.
8. Use disposable files to test list/find/select/copy/move/rename/recycle. Verify Explorer/Recycle Bin yourself.
9. Test media controls against a local track/video with the required player support.
10. Test memory/notes/project reads, reopened conversation and bounded multistep tasks.
11. Test local reminders, then paired mobile chat/voice/alerts, then a paid carrier call only when desired.
12. Test lock/disconnection last from the PC, with saved work and a way to reconnect.

For each row record **typed result**, **spoken transcript**, **actual observed result** and **error/limitation**. Mark unavailable hardware/integrations as Not available rather than Passed. Examples are a user checklist; no calls or destructive tests were executed to write this manual. Previous automated/native release evidence is in [0.10.21 test report](TEST-REPORT-0.10.21.md), including its initial packaged speech timeout and successful retry.

## What this version does not do

This manual covers implemented capabilities, not the larger proposed feature list. Bob does not currently provide:

- Universal control of every Windows app, administrator prompt or Settings page; unlimited screen/desktop understanding.
- Screenshot/document/photo attachment chat, live camera recognition, phone sensor/location or wearable ingestion.
- Connected email/message/contact/calendar/cloud search and first-class send/book/order workflows. Opening Gmail/Calendar is only opening their websites.
- Home automation, traffic/flight monitoring, finance accounts, health/medication integrations, emergency detection or family permission profiles.
- Persistent lock-screen iPhone microphone/wake words, native iOS push alerts, two-way Twilio calls or end-to-end encrypted carrier calls.
- Multilingual speech recognition, room diarization, secure voice login, automatic pronunciation training, perfect reference resolution or learned confirmation exemptions.
- Automatic monitoring/daily briefings from external services, listening backchannels or unlimited autonomous tasks.

Text translation, writing, brainstorming, quizzes and general advice can be attempted by the selected model, but do not imply connected external data, file-generation tools or reliable specialized integrations. Specific actions must remain within the supported catalogs above.

## Version and change reference

0.10.21 adds adaptive Natural pause timing, background Whisper preparation, model reuse/idle timer protection and the voice pipeline guide. It retains 0.10.20's accepted-confirmation cancellation fix and earlier tab/context/launch verification work. Historical changes: [release notes](RELEASE-0.10.21.md), [voice explanation](VOICE-PIPELINE.md), [test evidence](TEST-REPORT-0.10.21.md).

0.10.22 refreshes the desktop with charcoal surfaces, a mint accent, quieter cards and a compact Bob mark. The Voice button stays beside the composer, including when the side panel is hidden. [Interface changes and test guide](RELEASE-0.10.22.md).

0.10.23 adds a deep navy interface, cyan/violet accents, a compact holographic core and luminous cards. Navigation, voice and command behavior remain unchanged. [Changes and test guide](RELEASE-0.10.23.md).

The 0.10.23 core has slow orbital motion and a gentle pulse. Use Windows accessibility animation preferences to reduce motion; Bob also pauses decorative animation while hidden.

0.10.24 uses a plain black background, makes the footer Settings icon clickable, upgrades single capture to hands-free when Voice is pressed, and fixes case-insensitive app filtering. Read aloud and Test voice output now work with automatic replies disabled. See [button verification](TEST-REPORT-0.10.24.md).

0.10.25 added clickable connection/model/resource/voice status controls, a voice-toggle Bob core, editable memory cards, capability examples prepared for review, message copying, and press/hover/state motion. See [interactive controls and examples](RELEASE-0.10.25.md).


## New in 0.10.26: personal setup, routines and screen awareness

- **Close:** click X. Bob exits, including microphone, mobile access and scheduled work. Keep the PC awake and Bob minimized for reminders and daily routines.
- **Personal setup:** first launch asks four optional questions: name, response style, projects, priorities. Skip any question; review before **Save selected memories**. **Settings → Personal setup** reopens it. Facts go to the active voice profile or general workspace; edit/delete in **Memory**. Startup greetings can use the preferred name. Bob has animated listening/thinking/speaking states and consistent personality controls; it does not have feelings or consciousness.
- **Automations:** select **Use focus template**, or name a routine and enter one task per step. **Add step/Remove step** changes the sequence; up to twelve actions. **Save routine**, then **Run [name]**. Example: **Open notepad**, **Set volume to 20 percent**. Run now uses chat and normal confirmations. Say **Run my routine Focus time** to run the saved template by voice or text. Names must be unique; unknown or duplicate names ask for correction. Its results appear in chat. **Edit**, **Clear editor**, **Delete routine**, **Refresh results** are functional.
- **Daily routines:** choose a time in local Windows time before saving. Leave time blank for manual use. Daily routines only accept explicit opening/search/folder, sound, brightness and media transport actions; uncertain or confirmation-required tasks are rejected at save and rechecked before execution. Enabled can pause a routine. Bob and the PC must remain running. Passive voice listening is allowed; active work queues the due routine until it finishes. Polling is every ten seconds, no continuous model calls. Delays up to 30 minutes are caught up; queued runs survive restart for up to 24 hours. Each routine is claimed before execution to avoid repeats after restart. Failure stops remaining steps; inspect the latest daily result and rerun manually if needed.
- **Screen awareness:** turn on **Settings → On-demand screen awareness**, then **Save settings**. Focus the app you want (any monitor), say **Hey Bob**, then **Look at my screen**. Bob reads accessible labels/text, excluding password controls; there is no continuous capture, screenshot vision or camera analysis. Read results stay in conversation history, so delete the conversation to remove them.
- **Screen control example:** after reading the app, say **Click Record in this window** (replace Record with a label Bob listed), then **Yes**. Bob uses the selected window handle and an exact unique label, checks the window still exists, and refuses ambiguous controls. Observations expire after five minutes. **Click that button in this window** asks which visible label rather than guessing. UIA invocation reports an activation request, not an unverified completed task. Focus and type/key/move commands remain available, subject to app permissions. **Move Notepad to monitor two** moves a named app window; **List monitors** shows numbering.
- **Understanding screen text:** after **Look at my screen**, ask **What does that error mean?** The local model can explain accessible text using recent context; it cannot see an image-only error. Inspect again after the screen changes. Pages and window labels are data, not instructions to execute.

### Quick tests for this upgrade

1. Relaunch the new EXE, complete or skip setup, then check **Memory**. Only submitted nonempty answers should appear.
2. Build the focus template and run it; verify Notepad is visible and volume actually becomes 20%. This changes your volume.
3. Edit the routine to a time one minute ahead; stop voice conversation, keep Bob open and awake. Refresh results after that minute. Disable or delete it afterward.
4. With a disposable app open, enable awareness, focus it, wake Bob and say **Look at my screen**. Confirm listed text matches that app. Use an observed harmless control label to test clicking.
5. Close the target app, then ask to click the old control. Bob should refuse the stale window.
6. Click Bob’s X. Confirm Bob exits and its tray icon disappears. Reopen the EXE before using phone access or reminders.


| New tool action | Read this command | Check this result |
|---|---|---|
| Inspect focused screen | **Look at my screen** | After enabling awareness and focusing a disposable app before waking Bob, its accessible labels appear. Password fields and image content are excluded. | <!-- action:screen_inspect -->


## New in 0.10.27: free local day planner

See **DAY-PLANNER.md** beside the EXE for the simple setup and detailed examples. Add your day’s full starting address, start time, arrival buffer and stops in **Day planner**. Timed stops are appointments; blank times are flexible tasks. Duration is time spent at the stop. Manual drive minutes are used only with **Use manual travel estimates**.

Save, then **Plan with local AI**. One request sends addresses to Ollama on this PC; no routing API account, key or billing is needed. These are rough AI guesses, not live traffic or measured travel times. Open the free Maps links to check real routes and traffic, then enter checked drive minutes and use manual planning for a more dependable schedule. Calculated results are discarded when you edit/delete or close Bob. Saved appointments are local user data. No automatic calendar sync, GPS tracking, background traffic monitoring or shortest-route optimization is included. Reorder stops yourself or **Order appointments by time**; confirm destinations in Google Maps.

| New action | Example command | Expected result |
|---|---|---|
| Start a day | **Tomorrow I’ll start at 8 AM from [full address], with 15 minutes to spare at each stop** | The local LLM uses day_start, or asks for missing details. Starting point/time/buffer are saved. | <!-- action:day_start -->
| Add appointment | **Add my dentist appointment tomorrow at 10 AM at [full clinic address]; I’ll be there for 30 minutes** | Saved in Bob’s day plan; external calendars are not modified. | <!-- action:day_add -->
| Show saved schedule | **Show my day tomorrow** | User-entered stops and times appear. | <!-- action:day_show -->
| Estimate travel | **Plan my day tomorrow** / **When should I leave?** | Rough local AI estimates, leave times and conflicts appear in Day planner; an installed local Ollama model is required. No live traffic is available to the model. The follow-up reuses the selected day. Voice mode speaks the first departure. | <!-- action:day_refresh -->
| Open driving route | **Open the driving route to stop two for tomorrow** | The local LLM uses day_route with target 2 and opens Google Maps. Check its chosen destination before traveling. | <!-- action:day_route -->

Test with two disposable appointments. Use a 30-minute manual drive and 15-minute buffer before a 09:00 appointment: start at 08:00 and Bob should suggest 08:15 departure, 08:45 arrival. Change start to 08:50 and it should flag a 35-minute buffer-inclusive conflict without moving the appointment. AI times are guesses and can differ. Delete the test day afterward. Neither AI nor manual estimates guarantee arrival time.


## New in 0.10.28: commands by meaning

Start Ollama and launch the new Bob.exe. Select your installed local model in Settings. Wake Bob, then speak naturally. Clear supported appearance changes and known app/site launches take a direct path; other completed transcripts go to Ollama with recent conversation, selected targets and action history. Ollama maps your meaning into supported actions; you do not need a memorized command phrase. The validated action layer still requires important confirmations and reports actual results. If the model is unavailable, tasks needing semantic planning report failure rather than falling back to a guessed command. Clear direct requests and text keep their fast paths.

Examples to test:
- “It's a bit too loud; bring it down a little.” Check the real Windows volume decrease.
- “Get YouTube up and bring the volume to twenty percent.” Check both the real website and volume.
- “I'm done with every YouTube page; close all of them.” Review the selected tabs, say Yes, and check they close across Edge windows.
- After Bob lists several matching YouTube tabs: “Close all those.” The stored selection should carry forward; new unrelated tabs should remain untouched.
- “Put this in Notepad: Wait, actually do not close anything!” Check the literal dictated words; they must not become separate commands.
- “Do not open YouTube. Just tell me what it is.” Expect an explanation and no app action.
- After setting volume to 40%: “No, I meant twenty.” Check the correction changes volume to 20%.
- “Move it over there.” Without a known target/monitor, Bob should ask which window/monitor rather than claim success.

Low latency: known independent steps are batched. When Ollama marks a complete plan's final step, Bob reports its verified result immediately without asking the model for a second reply. Inspection-dependent workflows still need another planning round. Informational answers can stream in spoken sentences. Warm model dry-run timings are not guarantees: end-to-end response time also includes your speech pause, Whisper, Windows action verification and voice generation. Keeping the model warm in Settings trades memory for responsiveness.

## New in 0.10.29: profiles, natural memory, location and voice routines

See [the new features and test guide](RELEASE-0.10.29.md) for step-by-step tests.

- Enroll each person separately in Settings → Recognize my voice. A clear match selects that person's chat/memory and displays their name and initials. Uncertain voices use a separate conversation. A name spoken in a sentence is not proof of identity.
- Say “My favorite food is dosa”, “I usually exercise in the morning”, “Call me Alex”, or “Maya is my sister”. Clear explicit statements are saved to the current recognized profile. Text in a profile conversation also saves to that profile. Supported relationship words include parents, siblings, children, spouse, partner, friend, colleague, manager, cousin and roommate. Each person's stated relationships stay in their own memory; no assumptions or cross-profile memory searches. Use the Memory profile selector to inspect, edit or delete facts.
- Settings → Remember personal facts from conversations controls automatic saving. Turning it off keeps existing facts and explicit remember commands available. Quoted examples, uncertain/negative statements and sensitive credentials are not automatically saved. This is a conservative local extractor, not comprehensive semantic memory of everything you say.
- Say “Set up a daily routine called Morning at 8 AM: open YouTube and set volume to 35 percent.” Bob reads the name, daily time and sequence and asks once before saving. Say “yes”, then check Automations. The routine runs without asking again at the scheduled time while Bob is running (queued if busy). It does not run immediately when created. Up to twelve explicit steps; scheduled steps support opening apps/sites/folders, search, sound, brightness and media transport. Event triggers, conditional branches and arbitrary unattended UI actions are not supported. For complex manual sequences leave out the schedule and say “Run my routine Morning”. Disable/delete a routine in Automations. Times follow the PC's local clock.
- New tool action `automation_create`: stores the voice-described routine after one approval. Existing actions remain listed above. Start Ollama before voice setup; the scheduler does not call the model repeatedly.
- Optional Day planner location: allow it, open Windows location permissions, refresh, select Start from my current location, add named destinations with city/area, save and calculate. Location is refreshed on demand. No billing; driving times are still estimates, not live traffic.
- Ordinary spoken launches and selected Edge tab closes no longer ask for another approval. Ambiguous targets still need clarification; low-confidence speech needs review; consequential operations retain confirmation.

## Fixed in 0.10.30: timed routines and personal context

A daily routine runs even when Bob is passively listening. Active responses/transcription defer it without losing the due time. The queue persists across restarts and expires after 24 hours; a startup/wake delay of under 30 minutes catches the most recent scheduled time. Old unqueued schedules are not replayed. Polling is every ten seconds, so allow up to ten seconds after the scheduled time. Updating the time re-arms the routine. The Automations page updates results every five seconds while visible.

Test: create an enabled routine with “set volume to 20 percent”, choose a local PC time one minute ahead, save and leave Bob in voice conversation. Wait until the scheduled minute plus ten seconds. Check the volume and the routine result. Disable/delete the test afterward. If Bob is replying at the due time, the result shows Queued and executes afterward. Keep Bob open/minimized; X exits and disables its background scheduler.

Recognized users' names now appear early in the model context. Only their own saved facts and conversation are supplied; relationship searches handle punctuation such as “Who is Maya?” Enroll users individually and compare “What is my favorite drink?” after saving distinct preferences to each profile. Uncertain matches do not borrow a previous speaker's profile.

## New in 0.10.31: explicit schedule activation

A time alone does not start a paused routine. In Automations click **Enable schedule**, or edit it, check **Enabled**, and save. A prominent paused warning explains when it cannot run. **Pause schedule** stops timed execution without deleting the steps/time. Enabling a schedule whose time passed less than 30 minutes ago can run it immediately.

## New in 0.10.32: particle orb and enrolled-speaker listening

See [setup and test commands](RELEASE-0.10.32.md). The colorful particle sphere follows mic volume while listening and output volume while speaking, with gentle easing; it pauses in the background. Enroll three varied eight-to-twelve-second samples per person in a quiet room (minimum four usable seconds per new sample). Settings shows the captured duration. With recognition enabled, only confident enrolled voices can issue desktop microphone commands or interrupt; choose all saved voices or one person. Unknown voices are discarded before transcription. Speaker verification adds a short interruption delay; speak a full sentence. Use “Yes please go ahead and do it” for a longer approval. Existing saved profiles are preserved, and recognition can be turned off. Overlapping speech cannot be reliably separated, and voice identification is not authentication.


### Enrollment at your own pace (0.10.33)

Settings → Recognize my voice → enter your name → Record sample. Wait for Listening, read naturally, and click Finish sample when done. Pauses will not cut you off. You have 60 seconds; Cancel recording discards only the current recording. Repeat three times. Each sample still needs four seconds of usable speech; aim for eight to twelve. Exact example words are optional. Normal conversational timing is unchanged.


### If captured speech produces no text (0.10.34)

Watch the voice status: Bob checks the saved voice before transcribing. A rejected match now shows an explanation beside the voice controls. Stop conversation mode, open Settings → Recognize my voice → Test voice match, and speak a full sentence. This diagnostic records even if your saved profile cannot match. Enrollment itself saves voice features and does not transcribe the example sentence. Empty Whisper results get one guarded retry when speech is present. Uncertain words still appear for review. Your recognition settings are not changed automatically.


### Calibrate your laptop microphone (0.10.35)

Stop voice conversation. Settings → Calibrate my microphone: Measure room noise (stay quiet for three seconds), then Record my normal voice (speak for ten seconds). The calibrated label confirms it was saved automatically. Calibration follows the exact Windows WASAPI default input and is ignored if you switch microphones. Repeat after changing rooms or input devices. No audio is saved.

Enrollment now captures immediately after Listening instead of waiting for a command-volume threshold. Its live meter and microphone name help you check input. Read naturally, pause freely and click Finish sample; the 60-second limit remains. Blank audio, clipped/noisy audio and samples with less than four usable seconds are still rejected. Start a fresh profile only if your existing profile fails Test voice match. For more natural conversation choose the natural pause setting (650 ms), then Save settings. Interruptions still require a confident saved-voice match when recognition is enabled.


### Repair a saved voice without losing its memories (0.10.36)

Stop voice mode. Settings → Recognize my voice → Re-record beside your existing profile. Record three varied samples at your usual microphone distance. Finish each sample when done. Until all three are accepted, the old saved profile remains available. Cancel re-recording keeps it. Completion replaces only that voice enrollment; profile ID, memory, personality and conversation association remain. Test voice match with a different sentence, then try conversation and interruption. You do not need to create another user name. Duplicate profiles are not automatically merged. Speaker verification now uses an echo-cancelled audio channel closer to enrollment; transcription keeps its noise-suppressed channel. Matching remains approximate.


Short live requests no longer fail solely for having less than one second of speech: half a second of usable speech can reach the matcher. Short requests still use a higher similarity cutoff; very brief or weak matches are rejected. Enrollment still needs four usable seconds per sample. A successful full request can now interrupt Bob even if the early partial voice check missed. You do not need to re-record a profile that passes Test voice match.

Full natural test sheet: [92 action types and all supported page/site/key/Edge variants](test-commands/Complete-Natural-Commands.md).
