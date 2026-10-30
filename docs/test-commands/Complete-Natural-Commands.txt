# Bob 0.11.13 — complete natural-language test list

This sheet covers all 92 currently advertised action types, plus conversation, voice, UI, phone and optional-feature tests. Examples are requests to try, not a promise that every microphone, monitor, page or player supports them. You can rephrase them; exact wording is not required.

1. Launch the Windows EXE and start Voice. Keep Ollama running for conversational interpretation.
2. Say **Hey Bob** or **Okay Bob** before a new request unless you turned that requirement off. A wake phrase is attention control, not a fixed command grammar.
3. Replace bracketed names/addresses. Use disposable Notepad documents/files. Before file tests, manually create Documents/Bob Manual Test/test.txt and a fresh empty destination folder.
4. Check the transcript, real app/screen/file result and spoken reply. For confirmation, inspect the target before saying yes. Use the accompanying Test-Checklist.csv.
5. Record original brightness/volume and restore them afterward. Disconnecting Wi-Fi can cut off phone control; lock Windows only after saving your work.

## Conversation, listening and interruptions

| Say / do | Expected result |
|---|---|
| Hey Bob, explain how rain forms in three sentences. | Natural answer; no Windows action. |
| While Bob speaks: Hey Bob, please stop talking. | A deliberate, confidently matched enrolled-voice interruption stops the reply. This is not certified sub-200 ms. |
| Hey Bob, stop listening and open YouTube. | Ends the voice session and handles the remaining supported launch request. |
| Hey Bob, give me more time to finish my thoughts. | Inspect the speaking-pause preference in Settings. |
| Hey Bob, respond faster. | Attempts the Quick pause preference; this does not make model inference instantaneous. |
| Hey Bob, use tutor mode. Then: Hey Bob, teach me percentages using an example. | More explanatory wording. |
| Hey Bob, use fast mode. Then: Hey Bob, what does RAM do? | A shorter answer. |
| Hey Bob, use balanced mode. | Returns to the general conversation style. |
| Hey Bob, explain that more simply. | Uses the current conversation. |
| Hey Bob, make that answer shorter. | Rephrases the available answer; does not replay actions. |
| Hey Bob, summarize what we decided and what is still unfinished. | Summary of available bounded history. |
| Reopen an old chat: Hey Bob, continue the plan we discussed. | Uses that chat's available context, not unlimited archival retrieval. |
| Hey Bob, rewrite this with correct grammar: I has a meeting tomorrow. | Rewrites the text without typing it into another app. |
| After a volume change: Hey Bob, no, I meant forty percent. | Attempts a corrected value; verify the actual output level. |
| After a narrow question such as Which one?: the second one. | One reply without another wake phrase is allowed within 12 seconds for the same confidently matched saved voice. |
| Wait ten seconds, then: Hey Bob, bring up Calculator. | The idle timeout must not lose the new capture. |
| End Voice and immediately start Voice again. | Old capture cleanup must not shut down the new session. |
| Stay silent while Bob speaks; separately try table taps and a cough. | No false response stop, command or self-trigger. This needs live verification in your room. |
| If capture cannot decode words, watch the notice. | Explicit repetition request; no blank command dispatched. |

## Apps and Windows

| Feature | Natural request | Check |
|---|---|---|
| Open an application | “Hey Bob, could you bring up Calculator for me?” | A Calculator window appears. Also try Open Notepad or Open Microsoft Edge. | <!-- action:open -->
| Search the web | “Hey Bob, could you look up Windows keyboard shortcuts in my browser?” | Search results open in Edge. This is a web search, not a verified factual answer. | <!-- action:search -->
| Current time and date | “Hey Bob, what's the time and date?” | Bob reports the PC clock and date. | <!-- action:time -->
| System usage | “Hey Bob, how much CPU and memory is my PC using?” | Bob reports CPU and RAM usage. This is not battery or Windows Update status. | <!-- action:status -->
| Windows Update page | “Hey Bob, take me to Windows Update so I can check for updates.” | The Windows Update page opens. Bob does not install updates or prove your PC is up to date. | <!-- action:windows_update -->
| Lock Windows | “Hey Bob, i'm stepping away. Lock my computer, please.” | After approval Windows locks. Test last, when your work is saved; sign back in normally. | <!-- action:lock -->

## Volume and individual monitors

| Feature | Natural request | Check |
|---|---|---|
| Read volume | “Hey Bob, how loud is my computer set right now?” | Bob reports the default output volume and mute state. | <!-- action:audio_status -->
| Set volume | “Hey Bob, let's keep the sound at thirty percent.” | The default output reads 30% and is unmuted. Keep test volume comfortable. | <!-- action:volume -->
| Increase volume | “Hey Bob, bring the volume up by ten percentage points.” | Volume increases by 10 percentage points, clamped at 100. | <!-- action:volume_up -->
| Decrease volume | “Hey Bob, that's a bit loud. Lower it by ten percentage points.” | Volume decreases by 10 percentage points, clamped at zero. | <!-- action:volume_down -->
| Mute output | “Hey Bob, could you mute my speakers for a moment?” | Windows output is muted. | <!-- action:mute -->
| Unmute output | “Hey Bob, i'd like the sound back on, please.” | Windows output is unmuted; its existing level is retained. | <!-- action:unmute -->
| List monitors | “Hey Bob, show me my connected monitors and their numbers.” | Lists Bob monitor numbers and positions. Brightness and window movement now share these numbers; they may differ from Windows Settings labels. | <!-- action:list_monitors -->
| Read per-screen brightness | “Hey Bob, how bright is each of my screens right now?” | Reports a separate measured level for each supported screen. Record original values before changing them. | <!-- action:brightness_status -->
| Set brightness | “Hey Bob, leave my laptop alone and put the external monitor at forty percent brightness.” | The selected supported display reads back 40%. Use Set brightness to forty percent for all supported displays. | <!-- action:brightness -->
| Increase brightness | “Hey Bob, the laptop screen is a little dark. Brighten it by ten points.” | Supported displays increase by 10 percentage points. | <!-- action:brightness_up -->
| Relative brightness and target carryover | “Hey Bob, that same screen is too bright now. Ease its brightness down by ten points.” | Only the same recently verified screen decreases. Previous/other-screen references expire after five minutes; missing or ambiguous identities must ask rather than change another screen. | <!-- action:brightness_down -->

## Windows, typing and screen controls

| Feature | Natural request | Check |
|---|---|---|
| List open windows | “Hey Bob, what windows have I got open?” | Bob lists visible titles/processes so you can choose a target. | <!-- action:list_windows -->
| Switch to an app | “Hey Bob, bring Notepad to the front, please.” | The intended Notepad window becomes foreground. | <!-- action:focus_window -->
| Minimize an app | “Hey Bob, could you tuck Notepad into the taskbar?” | Notepad goes to the taskbar. | <!-- action:minimize_window -->
| Restore an app | “Hey Bob, bring Notepad back to its normal window size.” | Notepad returns from minimized/maximized state. | <!-- action:restore_window -->
| Maximize an app | “Hey Bob, let Notepad fill this screen.” | Notepad fills its monitor work area. | <!-- action:maximize_window -->
| Move between monitors | “Hey Bob, can you move Notepad over to my second monitor?” | The actual window moves to monitor 2. Requires a second detected display; follow with Move it to monitor one. | <!-- action:move_window -->
| Read accessible controls | “Hey Bob, what controls are available in the Notepad window?” | Bob lists exposed controls. This is accessibility inspection, not screenshot understanding. | <!-- action:inspect_window -->
| Literal Notepad dictation | “Hey Bob, in Notepad, type exactly: Hello, Bob!” | Check that only Hello, Bob! appears, once. Dictation is literal; Bob must not silently rewrite it. | <!-- action:type_text -->
| Keyboard shortcut | “Hey Bob, select all the text in Notepad using Control A.” | After focusing the disposable Notepad document, all text is selected. Full key catalog appears below. | <!-- action:press_key -->
| Click a named control | “Hey Bob, click the Open button in the Notepad dialog.” | Model-assisted: first inspect Notepad and open a disposable dialog that exposes an Open button. Approve only the correct target. Missing/ambiguous controls should produce an error. | <!-- action:click_control -->
| Close a window | “Hey Bob, i'm finished with this test Notepad window. Close it, please.” | Approve the named window; it disappears, or a save dialog/verification error is reported. Do not test on unsaved important work. | <!-- action:close_window -->
| Inspect focused screen | “Hey Bob, look at the window I was using. What controls can you see?” | After enabling awareness and focusing a disposable app before waking Bob, its accessible labels appear. Password fields and image content are excluded. | <!-- action:screen_inspect -->

## Microsoft Edge

| Feature | Natural request | Check |
|---|---|---|
| Open an address | “Hey Bob, could you take Edge to example.com?” | The address bar shows the requested site; loading/network/login remains the site’s responsibility. | <!-- action:edge_navigate -->
| Search in Edge | “Hey Bob, find some Python tutorials in Edge for me.” | The search results page opens. | <!-- action:edge_search -->
| Navigate, zoom and scroll | “Hey Bob, open another tab in Edge, please.” | A new tab opens. All 19 supported shortcut operations are listed below. | <!-- action:edge_shortcut -->
| List current-window tabs | “Hey Bob, which tabs are open in this Edge window?” | Tab titles are listed and remembered as a scoped selection. | <!-- action:edge_tabs -->
| Choose a named tab | “Hey Bob, take me back to the Example Domain tab.” | An existing uniquely matching Example Domain tab is selected. Use the displayed title. | <!-- action:edge_select_tab -->
| Read accessible page labels | “Hey Bob, what readable labels and controls are on this Edge page?” | Bob lists exposed labels/controls; it does not read every pixel or guarantee a page summary. | <!-- action:edge_inspect -->
| Find text on page | “Hey Bob, look for the word domain on this page.” | Edge’s Find UI receives domain; check its matches yourself. | <!-- action:edge_find -->
| Fill a field | “Hey Bob, put Bob test in the field labelled Search, but don't submit it.” | Use a disposable page with an accessible Edit field named Search, or replace Search with a label from inspection. Text is filled but not submitted. | <!-- action:edge_fill -->
| Click a page control | “Hey Bob, on the Example Domain page, click More information.” | On example.com, approve a matching visible link if exposed. A click does not guarantee the destination operation succeeded. | <!-- action:edge_click -->
| Close one named tab | “Hey Bob, close the YouTube tab I was just using.” | Approve the selected YouTube tab. If several match, choose a listed title or Close the second one. | <!-- action:edge_close_tab -->
| Close a matching tab group | “Hey Bob, i'm done with every YouTube tab. Close all the YouTube tabs and leave the others alone.” | Approve the displayed group; matching YouTube tabs across Edge windows disappear. Unrelated tabs should remain. | <!-- action:edge_close_tabs -->

## Settings, Bluetooth and Wi-Fi

| Feature | Natural request | Check |
|---|---|---|
| Read Bluetooth/Wi-Fi radio | “Hey Bob, is Bluetooth switched on?” | Bob reports radio state. Also try Check Wi-Fi status for the Wi-Fi radio; use Wi-Fi status for the network connection. | <!-- action:radio_status -->
| Change Bluetooth/Wi-Fi radio | “Hey Bob, could you turn Bluetooth on?” | Bob changes and reads back exposed radio state. Also test Turn Bluetooth off, Turn Wi-Fi on and Turn Wi-Fi off; disabling Wi-Fi needs approval. | <!-- action:radio_set -->
| Read connected network | “Hey Bob, which Wi-Fi network is this PC connected to?” | Bob reports the connected network/adaptor information, or a permission error. | <!-- action:wifi_status -->
| List saved networks | “Hey Bob, show me the Wi-Fi networks this PC already knows.” | Saved Windows profile names appear; passwords are not read. | <!-- action:wifi_profiles -->
| Connect to a saved network | “Hey Bob, connect this PC to my saved Wi-Fi network called [network name].” | Replace MyNetwork with an exact saved profile. Connection is checked. Reconnect Wi-Fi reuses previous connection context. | <!-- action:wifi_connect -->
| Disconnect Wi-Fi | “Hey Bob, disconnect this PC from Wi-Fi.” | Approve; Bob checks that the connection ended. Test locally with a way to reconnect. | <!-- action:wifi_disconnect -->
| Open a Settings page | “Hey Bob, take me to the display settings.” | Display Settings opens. Every supported page has an example below. | <!-- action:settings_open -->
| Read current Settings controls | “Hey Bob, what settings can you see on this page?” | Visible accessible labels and states appear; have only one Settings window open. | <!-- action:settings_inspect -->
| Read airplane/energy saver state | “Hey Bob, is energy saver on at the moment?” | Bob reads the exposed setting; it may open its page. Also try Is airplane mode on? | <!-- action:settings_status -->
| Change exposed Settings control | “Hey Bob, switch Night light on in display settings.” | Approve the exact label/value; Bob verifies an exposed toggle. Also try Turn airplane mode off and Turn battery saver on where available. | <!-- action:settings_set -->

## Files and Explorer

| Feature | Natural request | Check |
|---|---|---|
| Create a folder | “Hey Bob, make a folder called Bob Results in Documents.” | A new Bob Results folder appears; existing folders are not overwritten. | <!-- action:file_mkdir -->
| List a folder | “Hey Bob, what files are in Bob Manual Test in Documents?” | Up to 100 items appear; folder context is saved. Listing does not automatically select all files. | <!-- action:file_list -->
| Find filenames | “Hey Bob, find files with test in their name inside Bob Manual Test in Documents.” | Matching names are selected for follow-up operations; this is filename search, not semantic document search. | <!-- action:file_find -->
| Open a file or folder | “Hey Bob, open test.txt from Bob Manual Test in Documents.” | Use the real test-file location. It opens with its Windows association. Scripts/installers/shortcuts are excluded. | <!-- action:file_open -->
| Read properties | “Hey Bob, tell me the size and modified date of that test file.” | Path, type, size and modified date appear. Folder contents are not recursively sized. | <!-- action:file_properties -->
| Use Explorer selection | “Hey Bob, use the files I've selected in File Explorer.” | First select only disposable files and bring Explorer forward before waking Bob. Bob remembers those specific paths. | <!-- action:explorer_selection -->
| Copy selected files | “Hey Bob, make copies of those selected test files in Bob Results in Documents.” | First select a disposable source in another folder. Copies appear without overwriting collisions. Use a fresh destination for repeats. | <!-- action:file_copy -->
| Move selected files | “Hey Bob, move those selected test files into Bob Results in Documents.” | Approve exact source/destination. Same-drive source disappears and destination appears. Cross-drive moves are excluded. | <!-- action:file_move -->
| Rename one item | “Hey Bob, rename this selected test file to renamed-test.txt.” | First select one disposable file. Approve; its actual name changes. | <!-- action:file_rename -->
| Send to Recycle Bin | “Hey Bob, put that disposable test file in the Recycle Bin.” | Approve exact path; the disposable item disappears and can be recovered from Recycle Bin. No permanent deletion. | <!-- action:file_recycle -->

## Music and video

| Feature | Natural request | Check |
|---|---|---|
| List available players | “Hey Bob, which music or video players can you control right now?” | Bob lists Windows media sessions; choose an app/title if several are present. | <!-- action:media_sessions -->
| Read current playback | “Hey Bob, what's playing at the moment?” | Title, artist, app, state and position are reported where exposed. | <!-- action:media_status -->
| Play/resume | “Hey Bob, carry on playing the music.” | Resumes a suitable session; if none exists, tries a local Music file. Resume in Edge targets Edge. | <!-- action:media_play -->
| Pause playback | “Hey Bob, pause the video for a moment.” | The session reports Paused. Also try Pause in Spotify with that app playing. | <!-- action:media_pause -->
| Stop playback | “Hey Bob, stop playback completely.” | The session reports Stopped if it exposes Stop. | <!-- action:media_stop -->
| Next track | “Hey Bob, i'm not in the mood for this song. Skip to the next one.” | Track title changes if skipping is supported. | <!-- action:media_next -->
| Previous/restart track | “Hey Bob, take me back to the previous track.” | Previous track or restart is verified according to the player’s reported position/title. | <!-- action:media_previous -->
| Seek/restart | “Hey Bob, jump to one minute thirty in this video.” | Playback moves to about 90 seconds. Restart the video seeks to its beginning. | <!-- action:media_seek -->
| Relative forward seek | “Hey Bob, skip forward two minutes.” | Position advances by about 120 seconds, bounded by the timeline. | <!-- action:media_forward -->
| Relative backward seek | “Hey Bob, i missed that bit. Rewind thirty seconds.” | Position moves back about 30 seconds. | <!-- action:media_back -->
| Shuffle | “Hey Bob, mix up the order of the songs. Turn shuffle on.” | The session reports shuffle on. Restore with Shuffle off. | <!-- action:media_shuffle -->
| Repeat modes | “Hey Bob, keep this song on repeat. Repeat just this track.” | Repeat-one is reported. Also test Repeat all and Repeat off. | <!-- action:media_repeat -->
| Playback speed | “Hey Bob, could you play this at one and a half times the normal speed?” | The session reports 1.5× if supported. Restore with Set speed to 1x. Allowed range: 0.25–4×. | <!-- action:media_rate -->
| Open local media | “Hey Bob, play the local song called [filename from my Music folder].” | Finds a uniquely matching local Music filename, not an online catalog. Or Play file C:\Music\track.mp3 with an existing test file. Opening is not proof of playing. | <!-- action:media_open -->
| Find online media | “Hey Bob, find some jazz on YouTube for me.” | Search results open; choose a result yourself. Search for music jazz on Spotify is also supported; login/subscription may be needed. | <!-- action:media_search -->

## Memory, notes and project files

| Feature | Natural request | Check |
|---|---|---|
| Save a fact | “Hey Bob, remember that my favourite colour is blue.” | The fact appears in Memory for the current voice workspace/general workspace. | <!-- action:remember -->
| Retrieve an explicit fact | “Hey Bob, what do you remember about my favourite colour?” | Bob returns the saved fact. This command matches memory names, not every archived message. | <!-- action:recall -->
| Save a text note | “Hey Bob, make a note for me: test Bob again tomorrow.” | A timestamped text file appears under notes in Bob’s data folder. | <!-- action:note -->
| Open chosen project | “Hey Bob, open the project folder I've selected in Settings.” | Explorer opens the configured project folder. | <!-- action:open_project -->
| List project files | “Hey Bob, show me the files in my current project.” | Up to 80 file paths appear, scanning up to 5,000 files. | <!-- action:project_list -->
| Search project paths | “Hey Bob, find README files in my project.” | Matching relative file paths appear; it searches filenames/paths, not file contents. | <!-- action:project_search -->
| Read a project file | “Hey Bob, read README.md from my current project.” | Allowed UTF-8 text appears, truncated at 20,000 characters. Sensitive filenames, out-of-project paths and files over 100 KB are excluded. | <!-- action:project_read -->

## Reminders and routines

| Feature | Natural request | Check |
|---|---|---|
| Create a reminder | “Hey Bob, remind me in two minutes to stretch.” | A PC reminder is saved, then notifies/speaks when due. Other delivery examples appear in the phone section. | <!-- action:reminder_add -->
| List reminders | “Hey Bob, what reminders have I got coming up?” | IDs, due times, delivery channels and statuses appear. | <!-- action:reminder_list -->
| Cancel a pending reminder | “Hey Bob, cancel that reminder I just created.” | Immediately after creating a disposable reminder this cancels it. Or Cancel reminder ab12cd34 using the actual displayed ID. | <!-- action:reminder_cancel -->
| Create a personal routine | “Hey Bob, create a routine called Study time that opens Notepad and sets volume to thirty percent every day at six PM.” | Inspect the proposed steps and time before approval. Saving must not immediately run the steps. Bob and the PC must be awake for scheduled execution; use the builder to enable/pause/delete it. | <!-- action:automation_create -->

## Day planning

| Feature | Natural request | Check |
|---|---|---|
| Start a day | “Hey Bob, tomorrow I'll start at eight AM from [full address]. Give me fifteen minutes of spare time at each stop.” | The local LLM uses day_start, or asks for missing details. Starting point/time/buffer are saved. | <!-- action:day_start -->
| Add appointment | “Hey Bob, add a dentist appointment tomorrow at ten AM at [full clinic address]. I'll be there for thirty minutes.” | Saved in Bob’s day plan; external calendars are not modified. | <!-- action:day_add -->
| Show saved schedule | “Hey Bob, what does my day look like tomorrow?” | User-entered stops and times appear. | <!-- action:day_show -->
| Estimate travel | “Hey Bob, work out my travel plan for tomorrow and tell me when I should leave.” | Rough local AI estimates, leave times and conflicts appear in Day planner; an installed local Ollama model is required. No live traffic is available to the model. The follow-up reuses the selected day. Voice mode speaks the first departure. | <!-- action:day_refresh -->
| Open driving route | “Hey Bob, open the driving route to my second stop tomorrow.” | The local LLM uses day_route with target 2 and opens Google Maps. Check its chosen destination before traveling. | <!-- action:day_route -->

## Appearance

| Feature | Natural request | Check |
|---|---|---|
| Customize appearance | “Hey Bob, make the background black, use a cyan accent, hide the extra details and keep the spinning orb visible.” | Only requested supported appearance preferences change. Review the live UI and use Appearance controls to restore the previous look. | <!-- action:appearance -->

## Additional natural multi-step and reference tests

- “Hey Bob, bring up Notepad, write a short checklist for testing Bob, and leave it ready for me to review.”
- “Hey Bob, pause the video and bring the volume down to twenty percent.”
- “Hey Bob, put my laptop at forty percent brightness and the external monitor at sixty.”
- “Hey Bob, make that same screen a little brighter.” Then: “Hey Bob, put the other screen at fifty percent.”
- “Hey Bob, open Notepad.” Then: “Hey Bob, move it to monitor two.”
- After a scoped tab list: “Hey Bob, close the second one.” Or: “Hey Bob, close all those.” Verify only the referenced tabs.
- After a harmless successful action: “Hey Bob, do the same thing as last time.” Check the proposed result; sensitive actions still need approval.

## Personality and voice identity

- “Hey Bob, be funnier.” / “Hey Bob, be serious.” / “Hey Bob, be discreet.” / “Hey Bob, be more honest.” / “Hey Bob, no jokes.”
- “Hey Bob, set your humor to eighty.” / “Hey Bob, set your seriousness to ninety.” / “Hey Bob, set your discretion to ninety.” / “Hey Bob, set your honesty to ninety.” Inspect Settings.
- Enroll/test/select saved voices in Settings. Speak a full sentence and check the avatar/name, resumed chat and memory workspace. Short one-word identification can be uncertain.
- Choose a voice in Settings → Bob’s voice, use Listen to this voice, then Save. Compare the same question with each voice. Azure choices need that provider configured; Windows choices use installed voices. Voice selection/enrollment is a UI setup test, not a guaranteed voice command.

## Finance — optional widget

- “Hey Bob, show my finance widget.” / “Hey Bob, hide my finance widget.”
- In Finance, manually add/edit/delete a disposable transaction; set a monthly budget; try the purchase preview; add/edit/remove a manual holding and price; disable/re-enable the widget and check retention.
- Voice transaction edits, bank sync, automatic live stock prices and trades are not implemented. Do not test them as advertised commands.

## Phone and call reminders — setup required

- On the paired private phone webpage, try: “Hey Bob, open Calculator on my PC.” Check the PC, not just the webpage reply.
- “Hey Bob, remind me on my phone in two minutes to stretch.” Requires the active paired page for the webpage alert.
- “Hey Bob, call me in two minutes to stretch.” This schedules a real provider call and can incur charges. Use only with configured Twilio credentials and your destination number; check the actual call and reminder/provider status.
- A carrier call can ring a locked iPhone subject to carrier/Focus/blocking. The phone webpage does not provide locked-screen Hey Bob or guaranteed background microphone conversation.

## UI setup and controls that must also be tested manually

- New conversation and Recent conversations: create, reopen and delete a disposable chat.
- Read aloud: replay a displayed response. Stop: stop it. Compare with automatic speech enabled/disabled.
- Appearance editor: change one control at a time (orb, accent, density/details, font/layout/animations); check that only the requested setting changes. Follow system reduced-motion behavior.
- Memory: inspect the right profile workspace, edit and delete only the test fact.
- Routines: inspect a disposable routine, pause it, enable it, leave Bob/PC awake through its due time, verify the real action, then remove that test routine. Leave existing paused routines alone.
- Day planner: inspect origin, stop addresses, travel estimates and conflicts. Estimates are rough local-model values; live traffic and guaranteed current-location routing are not provided.
- Voice setup: microphone calibration, enrollment, test saved voice, Windows/neural voice preview, room mode, wake/interrupt switches and the latency diagnostics panel.
- Minimize: Bob can remain running. X: Bob should quit and stop its microphone/routines/remote server.

## Negative tests — no unintended actions

- “Hey Bob, don’t open YouTube. Just tell me what it is.”
- “Hey Bob, don’t touch the brightness. Explain DDC/CI.”
- “Hey Bob, set monitor nine to forty percent brightness.” On a two-monitor PC, expect a missing-monitor error and no other screen change.
- Wait over five minutes after a brightness target, then: “Hey Bob, dim that same screen.” Expect a request for a screen rather than an expired target.
- Another person talks, or a TV speaks while Bob replies: no unintended action/response stop should occur. Speaker matching is approximate; record any failures in the checklist.

## Every supported Settings page

| Page | Request (prefix Hey Bob) |
|---|---|
| System | **Could you open system settings** |
| Display | **Could you open display settings** |
| Sound | **Could you open sound settings** |
| Notifications | **Could you open notifications settings** |
| Focus | **Could you open focus settings** |
| Power | **Could you open power settings** |
| Battery Saver | **Could you open battery saver settings** |
| Storage | **Could you open storage settings** |
| Multitasking | **Could you open multitasking settings** |
| About | **Could you open about settings** |
| Bluetooth | **Could you open bluetooth settings** |
| Devices | **Could you open devices settings** |
| Printers | **Could you open printers settings** |
| Mouse | **Could you open mouse settings** |
| Touchpad | **Could you open touchpad settings** |
| Typing | **Could you open typing settings** |
| Wifi | **Could you open wifi settings** |
| Airplane Mode | **Could you open airplane mode settings** |
| Network | **Could you open network settings** |
| Ethernet | **Could you open ethernet settings** |
| Vpn | **Could you open vpn settings** |
| Proxy | **Could you open proxy settings** |
| Mobile Hotspot | **Could you open mobile hotspot settings** |
| Background | **Could you open background settings** |
| Colors | **Could you open colors settings** |
| Themes | **Could you open themes settings** |
| Lock Screen | **Could you open lock screen settings** |
| Taskbar | **Could you open taskbar settings** |
| Start Menu | **Could you open start menu settings** |
| Fonts | **Could you open fonts settings** |
| Apps | **Could you open apps settings** |
| Default Apps | **Could you open default apps settings** |
| Startup Apps | **Could you open startup apps settings** |
| Accounts | **Could you open accounts settings** |
| Sign In | **Could you open sign in settings** |
| Other Users | **Could you open other users settings** |
| Date And Time | **Could you open date and time settings** |
| Language | **Could you open language settings** |
| Region | **Could you open region settings** |
| Accessibility | **Could you open accessibility settings** |
| Text Size | **Could you open text size settings** |
| Magnifier | **Could you open magnifier settings** |
| Narrator | **Could you open narrator settings** |
| Keyboard | **Could you open keyboard settings** |
| Privacy | **Could you open privacy settings** |
| Microphone | **Could you open microphone settings** |
| Camera | **Could you open camera settings** |
| Location | **Could you open location settings** |
| Windows Update | **Could you open windows update settings** |
| Update History | **Could you open update history settings** |
| Recovery | **Could you open recovery settings** |
| Activation | **Could you open activation settings** |
| Troubleshoot | **Could you open troubleshoot settings** |
| Remote Desktop | **Could you open remote desktop settings** |
| Gaming | **Could you open gaming settings** |

## Website fallbacks

| Service | Request (prefix Hey Bob) | Website |
|---|---|---|
| Youtube | **Bring up youtube** | https://www.youtube.com |
| Google | **Bring up google** | https://www.google.com |
| Github | **Bring up github** | https://github.com |
| Spotify | **Bring up spotify** | https://open.spotify.com |
| Netflix | **Bring up netflix** | https://www.netflix.com |
| Whatsapp | **Bring up whatsapp** | https://web.whatsapp.com |
| Telegram | **Bring up telegram** | https://web.telegram.org |
| Discord | **Bring up discord** | https://discord.com/app |
| Gmail | **Bring up gmail** | https://mail.google.com |
| Outlook | **Bring up outlook** | https://outlook.live.com |
| Instagram | **Bring up instagram** | https://www.instagram.com |
| Facebook | **Bring up facebook** | https://www.facebook.com |
| X | **Bring up x** | https://x.com |
| Reddit | **Bring up reddit** | https://www.reddit.com |
| Amazon | **Bring up amazon** | https://www.amazon.in |
| Prime Video | **Bring up prime video** | https://www.primevideo.com |
| Chatgpt | **Bring up chatgpt** | https://chatgpt.com |
| Notion | **Bring up notion** | https://www.notion.so |
| Canva | **Bring up canva** | https://www.canva.com |
| Figma | **Bring up figma** | https://www.figma.com |
| Google Docs | **Bring up google docs** | https://docs.google.com |
| Google Drive | **Bring up google drive** | https://drive.google.com |
| Google Maps | **Bring up google maps** | https://maps.google.com |
| Google Calendar | **Bring up google calendar** | https://calendar.google.com |
| Microsoft Teams | **Bring up microsoft teams** | https://teams.microsoft.com |
| Zoom | **Bring up zoom** | https://app.zoom.us |
| Slack | **Bring up slack** | https://app.slack.com |
| Youtube Music | **Bring up youtube music** | https://music.youtube.com |

## Every supported keyboard shortcut

| Key | Request (prefix Hey Bob) |
|---|---|
| enter | **Could you press enter** |
| tab | **Could you press tab** |
| escape | **Could you press escape** |
| backspace | **Could you press backspace** |
| up | **Could you press up** |
| down | **Could you press down** |
| left | **Could you press left** |
| right | **Could you press right** |
| page up | **Could you press page up** |
| page down | **Could you press page down** |
| home | **Could you press home** |
| end | **Could you press end** |
| ctrl+a | **Could you press control a** |
| ctrl+c | **Could you press control c** |
| ctrl+v | **Could you press control v** |
| ctrl+z | **Could you press control z** |
| ctrl+s | **Could you press control s** |
| ctrl+f | **Could you press control f** |
| ctrl+l | **Could you press control l** |
| ctrl+t | **Could you press control t** |
| ctrl+w | **Could you press control w** |
| ctrl+tab | **Could you press control tab** |
| shift+tab | **Could you press shift tab** |
| alt+left | **Could you press alt left** |
| alt+right | **Could you press alt right** |
| f5 | **Could you press f5** |

## Edge navigation variants

| Operation | Request (prefix Hey Bob) | Check |
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

