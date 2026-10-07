# Bob Desktop — User Manual & Voice Commands

This manual describes the current portable Windows EXE built from this project.
Commands listed here were checked against the desktop runtime. Recognition quality
depends on your microphone, accent and background noise. Release 0.10 uses local
Whisper small.en for English commands and Windows speech for wake words.

## New in 0.10

- **0.10.13** fixes “close all YouTube” and follow-ups such as “close all those”, verifies selected tab closures, and filters noise during interruptions. See [changes and test guide](RELEASE-0.10.13.md).

- **0.10.12** adds Funny, Serious, Discreet and Candid personalities with adjustable traits. Say “Be funnier”, “Be serious”, “Be more honest” or “Set your humor to 80”. See [personality setup and tests](RELEASE-0.10.12.md).

- **0.10.11** refines optional voice matching with sample quality checks, three-template comparisons, Balanced/Strict sensitivity and **Test voice match**. See [changes and tests](RELEASE-0.10.11.md).

- **0.10.10** adds optional **Recognize my voice** in Settings, off by default. Record three samples, enable the switch and save. Delete the profile whenever you want. See [setup and tests](RELEASE-0.10.10.md).

- **0.10.9** continues multi-step tasks using action results and preserves the original goal across confirmations. Try “Open Notepad and type Hello Bob.” See the [changes and test guide](RELEASE-0.10.9.md).

- **0.10.8** supports **“Actually stop listening and open YouTube”**: it ends microphone capture and executes the remaining request. Websites open in Edge with address verification. When voice replies are enabled, typed replies are spoken too. See [0.10.8 guide](RELEASE-0.10.8.md).
- **0.10.7** adds adaptive interruption detection for quiet speech and natural gaps. Speak midway through Bob's reply, then pause for about a second. The status shows whether Bob is waiting for a request or actively capturing it. See [0.10.7 changes](RELEASE-0.10.7.md).
- In **0.10.6**, Bob finishes recording after a short pause using a dedicated voice-activity detector. Interrupt in the middle of his spoken reply: **“Actually, open Notepad.”** Buffered interruptions are now handled even after a single-command microphone capture. See [0.10.6 changes and tests](RELEASE-0.10.6.md).
- Choose **Settings → Personality**: Balanced, Witty butler, Friendly companion, Motivating coach, Precise engineer, or Curious explorer. Save settings. These change conversation style; Ollama must be running for open-ended conversation.
- In **0.10.5**, start a voice conversation once (or say **“Hey Bob”**). Bob uses local WebRTC echo cancellation and keeps listening while speaking or preparing a response. Speak normally to interrupt: **“Actually, open Calculator.”** No microphone click is needed during the conversation. Say **“Stop listening”** or press Stop to finish. The microphone closes when the conversation ends.
- When echo cancellation is active, there is no recording beep: speak naturally. If Bob reports that hands-free interruption is unavailable, voice falls back to taking turns; use the microphone button to interrupt. Set a real microphone and your desired speakers as Windows default devices; do not use Stereo Mix. After changing devices or connecting Bluetooth, end and restart the voice conversation.
- Test with speakers: ask **“Tell me a long story.”** Stay silent for a few seconds; Bob should continue without treating his speech as your command. Then say **“Actually, open Calculator.”** Bob should stop talking and process your request. Try again at different speaker volumes. Physical microphone placement and very loud/clipped speakers affect echo cancellation; headphones help in difficult rooms.
- Say **“List monitors”**, then **“Move Notepad to monitor two.”** Or after opening Notepad: **“Move it to monitor two.”** Numbering is Bob's discovery order, primary first; it may differ from Windows display labels.
- Say **“Type Hello, Bob! in Notepad.”** Explicit Notepad dictation preserves your text and punctuation rather than routing it to remembered Edge context. Bob pastes once, checks the editor, and restores the clipboard. Choose the exact window title when multiple Notepad windows are open.
- Say **“Open Notepad and then type Hello, Bob! in Notepad.”** Direct multi-step requests retain the app context. Broader conversational requests use Ollama; unclear or consequential actions still require confirmation.
- Speech allows a longer pause and flags very uncertain words for review. This cannot recover words the microphone did not capture; inspect a flagged transcript before sending. Dictation is not silently grammar-corrected: ask **“Rewrite this with correct grammar: ...”**, then ask to type the response if that is your intent.
- Say **“Call me in two minutes to check the oven”** for a paid phone-number reminder, **“Remind me on my phone in two minutes to check the oven”** for a webpage alert, or **“Remind me in two minutes to check the oven”** for a PC reminder. Calling setup is at the end of this manual.
- Phone pairing can survive browser closure with **Remember this phone**, and survives Bob restarts. Locked-phone microphone conversation remains unavailable; carrier reminder calls are a separate option.

## Routine execution in 0.6

Straightforward brightness, volume, app opening, window resizing/switching and
single-line typing run without a yes/no prompt. Common combinations joined by
“and”, “then” or commas use a direct path. Unclear speech, fuzzy app matches,
closing/locking, generic button clicks, multiline typing and potentially
consequential keys still ask first. “Press control S” can overwrite a file, so
saving still asks. Bob validates a complete plan before starting it.

Brightness is verified separately for each detected display. Use **What is my
current brightness?** to see Bob's monitor numbering; these numbers are discovery
order and need not match Windows Display Settings numbering. Setting brightness
without a monitor changes all detected supported displays. A failed read-back is
reported instead of pretending the display changed. Positive volume commands also
unmute the active Windows output; they do not change a browser/app-specific mixer.

## New in 0.7: music and video playback

| Say | Action |
| --- | --- |
| “Play music” | Resumes an available Windows media session; if none exists, opens a local track from your Music folder. |
| “Play song Yesterday” | Finds a uniquely matching local filename in Music and opens it in your default player. |
| “Play file C:\Music\track.mp3” | Opens an explicit local audio/video file. |
| “Pause the video” / “Resume” | Pauses or resumes a supported session and checks its state. |
| “Pause in Spotify” / “Resume in Edge” | Targets the named app. Exact media titles can also identify a session. |
| “Stop playback” | Stops the player if it exposes Stop. |
| “Next song” / “Previous track” | Skips where supported and checks the reported track/position. |
| “Rewind thirty seconds” | Moves backward by 30 seconds, within the seekable timeline. |
| “Fast forward two minutes” | Moves forward by two minutes. |
| “Seek to 1:30” / “Go to 1:02:03” | Goes to an absolute timestamp. |
| “Restart the video” | Seeks to its beginning. |
| “Shuffle on” / “Shuffle off” | Changes shuffle where the player exposes it. |
| “Repeat one” / “Repeat all” / “Repeat off” | Changes the player's repeat mode where supported. |
| “Set speed to 1.5x” | Changes playback rate where supported (0.25–4×). |
| “What is playing?” | Reads title, artist, player, playback state and position. |
| “List media players” | Lists Windows media sessions so you can choose an app/title. |
| “Search for music jazz on YouTube” | Opens search results. Choose a result to start playback. Spotify search is also supported. |

Combine commands: **“Pause the video and set volume to twenty percent.”**
Playback commands are routine and do not need a yes/no confirmation. With multiple
playing sessions, name the app or exact title instead of guessing which one to
interrupt. Follow-ups remember the last player/title when no other session is
actively playing. Volume/mute commands control the default Windows audio output.

Windows media-session integration works with players and browser tabs that publish
transport controls. Each app determines which actions it supports. Live streams
may not allow seeking; some apps expose pause/play but no speed, shuffle, repeat,
stop or skipping. Bob reports unsupported or unverified actions instead of sending
blind global hotkeys. Fullscreen, subtitles and audio-track selection are not part
of this playback API. This is not universal control over every website or video.

Opening a local file is reported as **opened**, because actual playback depends on
your chosen default player. “What is playing?” checks its state. Online search does
not claim autoplay and does not bypass login, subscriptions, advertisements or DRM.
Bob does not bundle a music catalog or download songs from streaming services.

## New in 0.6: connections, Windows Settings and files

Quit the previous Bob using **tray icon → Quit Bob**, then launch the new EXE.
Your existing conversations, settings and memories remain in the same data folder.

| Say this | What Bob does |
| --- | --- |
| “Turn Bluetooth on” / “Disable Bluetooth” | Changes the exposed Windows radio and checks its resulting state. |
| “Is Bluetooth on?” / “Check Wi-Fi status” | Reads radio state without changing it. “Wi-Fi status” reports the current connection. |
| “Turn Wi-Fi on” / “Turn Wi-Fi off” | Controls the wireless radio; turning it off asks first because it disconnects you. |
| “List saved Wi-Fi networks” | Lists saved profile names, never passwords. |
| “Connect to Wi-Fi MyNetwork” | Connects to that saved profile and verifies the connected profile. |
| “Disconnect from Wi-Fi” | Asks once, disconnects, and checks the result. |
| “Reconnect Wi-Fi” | Uses the last connected network remembered in this conversation. |
| “Turn airplane mode on” / “Turn aeroplane mode off” | Uses the real Settings toggle. Turning it on asks first. |
| “Turn battery saver on” / “Turn energy saver off” | Uses the exposed battery/energy-saver toggle, expanding its section when necessary. |
| “Is energy saver on?” | Reads the energy-saver toggle. It may open its Settings page. |
| “Open display settings” / “Open privacy settings” | Opens a named Windows Settings page. |
| “Inspect settings” | Reads visible accessible control labels and toggle states. |
| “Set Night light to on in display settings” | Changes a uniquely matching exposed toggle after confirmation and verifies its state. |
| “List files in Downloads” | Lists up to 100 items and remembers the folder. Listing alone does not select every file. |
| “Find report in Downloads” | Searches names and remembers the matching items, up to 50 results/5,000 entries scanned. |
| “Create folder Reports in Documents” | Creates a new folder without overwriting an existing one. |
| “Copy those files to Documents” | Copies the remembered selection into an existing folder, refusing name collisions. |
| “Move those files to Documents” | Shows exact source/destination paths for confirmation, then moves them. |
| “Rename that file to final-report.txt” | Confirms the exact rename; requires one selected item. |
| “Delete that file” | Confirms and sends it to the Recycle Bin. No permanent deletion. |
| “Open file report.txt” | Opens an item relative to the remembered folder. Scripts/installers/shortcuts are excluded. |
| “Show properties of report.txt” | Reports its path, type, size and modified time. Folder contents sizes are not calculated. |
| “Use selected files” | Reads the selection in File Explorer. Bring it to the front before saying “Hey Bob”; Bob remembers that window. |

You can combine dependent steps: **“Find report in Downloads and copy those files
to Documents.”** Or: **“Open Bluetooth settings and set volume to thirty percent.”**
“Turn it back on” refers to the last supported setting in this conversation.
“That file” requires a single remembered item; “those files” means the explicit
find results or Explorer selection. A confirmation freezes exact file paths;
changing Explorer's selection afterward will not redirect the operation.
Earlier completed steps remain completed if a later step is cancelled or fails.

Settings navigation covers system, display, sound, notifications, focus, power,
battery saver, storage, multitasking, about, Bluetooth, devices, printers, mouse,
touchpad, typing, Wi-Fi, airplane mode, network, Ethernet, VPN, proxy, mobile
hotspot, background, colors, themes, lock screen, taskbar, start menu, fonts, apps,
default apps, startup apps, accounts, sign in, other users, date and time,
language, region, accessibility, text size, magnifier, narrator, keyboard,
privacy, microphone, camera, location, Windows Update, update history, recovery,
activation, troubleshoot, remote desktop and gaming.

Generic Settings changes support accessible toggles, dropdowns and numeric
sliders using exact labels discovered by “inspect settings”. Labels currently
assume English Windows. Windows versions, hidden controls, administrator policy,
UAC and disabled hardware can prevent automation. Bob reports that limitation;
it does not have universal control over every Settings dialog or every app.
Battery saver may be unavailable while charging on some Windows versions.
On versions with **Always use energy saver**, that is the control Bob changes.

Wi-Fi connections need a previously saved Windows profile. For a new network,
open Wi-Fi Settings and enter the password there first. Bob never reads or stores
Wi-Fi passwords. If Windows denies the current-network query, Bob reports the
permission error and does not claim a connection succeeded. Multiple Wi-Fi
adapters currently require choosing the adapter in Windows Settings.

File operations use local paths and redirected standard folders (including
OneDrive-backed Documents/Desktop). They exclude system and app-data folders,
network/device paths, symbolic links and junctions. Moves are within one drive;
for another drive, copy, verify, then recycle the original. Bulk operations are
limited to 50 selected roots, with at most 2,000 entries/1 GB per root. Existing
files are never intentionally overwritten. A failed copy can leave partial output;
Bob reports the completed count so you can inspect it before retrying.

Bob's default voice is calm, practical and lightly witty. Change **Settings →
Personality instructions** to specify your preferred name, tone or level of detail.
It uses recent dialogue, saved facts and per-conversation action context. This is
bounded context, not perfect or unlimited memory. Model-assisted workflows can
inspect results and continue for up to four planning stages/twelve tool calls;
routine recognized commands use the direct path without waiting for Ollama.

## 1. First launch

1. Extract `Bob-Windows-x64.zip` into a folder you can keep, then double-click
   `Bob.exe`. The speech model is embedded in the EXE; no models folder is required. No Python,
   Node, terminal or separate Bob backend is needed. Quit the previous app from
   its tray menu first so only one assistant is listening.
2. Start the Ollama application. This PC had `qwen3:8b` installed during testing.
3. Open **Settings** in Bob. Set **Ollama address** to
   `http://127.0.0.1:11434` and **Model** to `qwen3:8b`, or the exact name of another
   installed model with tool support. Click **Save settings**, then **Refresh**.
4. Check that the top status reads **OLLAMA CONNECTED**.
5. Under **Your current project**, browse to the actual folder containing your project and save.
   The app may already select this folder when launched from the project's `dist`
   directory. Verify the setting before using project commands.
6. In Windows Settings → System → Sound → Input, select your microphone.
   Allow microphone access for desktop apps under Windows privacy settings.
   Under **Voice & personality**, enable **Wake words** and **Speak a greeting
   at startup**, then save. Wake words require a Windows English Speech pack.
7. Enable **Read replies during voice conversations** if you want spoken answers.
   Click **Save settings** after changing preferences.

The EXE requires Windows 10/11 x64, Edge WebView2 Runtime, Windows PowerShell 5.1
and, for wake words, an installed Windows English speech recognizer. Ollama and its model are separate
from the EXE. The current release is portable and unsigned.

The page at `http://127.0.0.1:5173/` is a development preview. Use **Bob.exe** for
voice, local memory and Windows commands.

## 2. Speaking to Bob

### One command at a time

1. Click the microphone beside the message box.
2. Wait for **Listening**. Echo-cancelled mode has no tone; the fallback plays a short tone.
3. Say a short command, such as **Open calculator**.
4. Pause at the end. Bob submits the recognized sentence and responds.
5. Click the microphone again for another command or to answer a confirmation.

Each attempt waits about eight seconds for speech and records up to twenty
seconds. A pause of roughly 0.8 seconds ends the utterance. Watch the microphone
level, then **Transcribing your words**. The first recognition loads the local
model and may take longer. Uncertain text is shown in the composer and Bob asks
for confirmation: say **yes**, repeat the request, or edit and send it.

### Back-and-forth voice conversation

Click **Start voice conversation** in the right panel. When **Echo cancellation
active** appears, speak naturally, including while Bob is talking or thinking.
Your speech interrupts his reply and becomes the next request. Quiet periods do
not end the conversation. If AEC is unavailable, wait for **Listening** between replies.

While it is listening, say **Stop listening**, **Stop voice**, or **Go to sleep**
to end voice mode. You can also click **End voice conversation** or the square
Stop button. Stopping voice mode does not close the app.

### Greeting and wake words

On launch Bob greets you and starts listening automatically. You do not need to press the microphone button. Disable **Start listening automatically at launch** only if you prefer manual startup. Say **Hey Bob** or **Okay Bob**, wait for
**Listening**, then say your request. Do not run the wake word and the request together:
the wake listener hands the microphone to the command recognizer after activation.
Follow-up requests use the same conversation. With AEC active, silence keeps the
session open; say **Stop listening** to return to standby. Closing to the tray ends the voice conversation, while enabled wake
listening continues and can reopen the window.

Bob pauses wake detection during its own speech and during an active voice session.
The session's echo-cancelled microphone listens for interruptions while replying.
The square **Stop** button also stops voice. End the session and disable **Wake
words** in Settings to turn off microphone listening. **Test voice output** checks the speaker/TTS path.

## Windows and multi-step commands (0.6)

| Say | Result |
| --- | --- |
| Set brightness to 40 percent | Adjusts supported displays and reports their measured brightness. |
| Brightness up / Brightness down | Changes both displays by ten percentage points. |
| Set monitor two brightness to forty percent | Adjusts only Bob's monitor 2. |
| Lower external brightness by twenty percent | Lowers external displays by twenty percentage points. |
| Set laptop brightness to 50 | Adjusts the laptop display only. |
| What is my current brightness? | Reads each display's actual value; does not change it. |
| Set volume of fifty percent | Sets and unmutes the active Windows output, then verifies the value. |
| What is my current volume? | Reports the active output's volume and mute state. |
| Set brightness to forty and volume to fifty | Executes both directly without an Ollama call or yes/no prompt. |
| Check for system updates | Opens Windows Update; select Check for updates there to scan. |
| List windows | Lists visible window titles. |
| Switch to Notepad | Focuses the matching window; ambiguous matches require a more specific title. |
| Maximize Notepad / Minimize Notepad / Restore Notepad | Changes that window's state. |
| Maximize it | Uses the previous application target in this conversation. |
| Close Notepad | Requests confirmation, then asks the app to close; save dialogs remain. |
| Inspect window Notepad | Reads labels of accessible controls in that window. |
| Type Good morning Bob into Notepad | Types into the focused editable field; multiline text asks first. |
| Press control S | Confirms, then sends Ctrl+S to the previous application target. |
| Click the Record button in Bob Automation Verification | Uses the planner to activate the named accessible control. |

Try: **“Could you open Notepad, type Good morning Bob into it, maximize that
window and set brightness to forty percent?”** Routine steps run immediately. Bob asks first if a plan contains an ambiguous or consequential action. Say **yes** or **cancel** only when asked. Steps run in order, with up to twelve per
plan. A failure stops later steps and is reported; already completed steps remain.
You can continue entirely by voice. A follow-up request keeps the same
conversation and previous application target. There is no rollback of a completed plan.

Automation works with applications that expose Windows accessibility controls.
Custom canvases, games, administrator prompts and some app-specific controls may
not be controllable. Typing requires an editable field; ambiguous window/control
matches are rejected. Shells and Registry Editor are excluded from text/control
input. External-monitor brightness requires driver/DDC support. This is a bounded
Windows assistant, not unrestricted or guaranteed universal app control.

## 3. Voice-command reference

The same commands can be typed. Use the examples first, then try natural variations.
Names inside angle brackets below are placeholders, not words to say.

### Applications and folders

| Say | Result |
| --- | --- |
| Open calculator | Opens Windows Calculator. |
| Open notepad | Opens Notepad. |
| Open file explorer | Opens File Explorer. |
| Open settings | Opens Windows Settings. |
| Open Chrome | Opens Google Chrome if found in the Start menu. |
| Open Edge | Opens Microsoft Edge if found. |
| Open VS Code | Opens Visual Studio Code if found. |
| Open <application name> | Opens an application listed under Capabilities. |
| Launch calculator / Start calculator / Bring up calculator | Alternative opening phrases. |
| Open it again | Opens the last application opened in this conversation. |
| Open downloads | Opens your standard Downloads folder. |
| Open documents | Opens your standard Documents folder. |
| Open desktop / Open pictures / Open music / Open videos | Opens the named standard folder. |

You can add **please**, **could you**, **can you**, **would you**, or **will you**.
For example: **Hey Bob, could you please open calculator?**

App names come from Start menu shortcuts. Open **Capabilities** to see and filter
the discovered list. Restart Bob after installing a new app. Approximate matches
ask for confirmation. Personal folder paths are read from Windows, including
redirected Documents/Desktop folders.

### Web and websites

| Say | Result |
| --- | --- |
| Open YouTube | Opens YouTube in your default browser. |
| Open Google | Opens Google. |
| Open GitHub | Opens GitHub. |
| Search the web for astronomy | Opens Google search results. |
| Search for Python tutorials | Opens a search for that phrase. |
| Look up weather in Bengaluru | Opens search results for the phrase. |
| Google vegetarian recipes | Opens a Google search. |

You can also type **open https://example.com**. Typing full URLs is usually more
reliable than dictating punctuation. A web search opens your browser; Bob does
not automatically read or summarize the resulting webpage.

### Volume, time and computer status

| Say | Result |
| --- | --- |
| Set volume to 30 percent | Sets speaker volume to 30%. |
| Set the volume to 50 | Sets speaker volume to 50%. |
| Volume up / Turn up the volume | Raises volume by 10 percentage points. |
| Volume down / Turn down the volume | Lowers volume by 10 percentage points. |
| Mute / Mute the volume | Mutes the default speakers. |
| Unmute / Unmute the volume | Unmutes the default speakers. |
| What time is it? / What's the time? | Reports local time and date. |
| System status | Reports CPU and RAM usage. |
| Lock my computer / Lock my PC | Requests confirmation before locking Windows. |

Volume values must be between 0 and 100. If speech recognition spells a number as
words instead of digits, Ollama may interpret the request and ask you to confirm.
Muting also makes Bob's spoken replies inaudible until you unmute.

### Persistent memory

| Say | Result |
| --- | --- |
| Remember that my name is Bhanu | Saves a fact named `name`. |
| Remember that my city is Bengaluru | Saves a fact named `city`. |
| Remember that my bike is GT650 | Saves a fact named `bike`. |
| Recall name / Recall city / Recall bike | Shows matching saved facts. |
| What do you remember about my bike? | Looks up the saved bike fact. |

Use **remember that my <fact name> is <value>** for predictable results. Saving
the same fact name again updates its value. A statement such as **remember to
buy coffee** saves a note-like fact; it does not create a timed reminder.

The **Memory** screen lets you add and delete facts. There is no dedicated
voice command for deleting a memory in this release.

### Text notes

| Say | Result |
| --- | --- |
| Take a note: buy coffee tomorrow | Saves a new text file containing the note. |
| Make a note: discuss the design on Monday | Saves another text note. |
| Save a note: the meeting starts at ten | Saves another text note. |

Use **Settings → Open data folder**, then open `notes`, to find the files.
Notes do not create notifications, calendar events or scheduled reminders.

### Your current project

First select the project folder in Settings and save it.

| Say or type | Result |
| --- | --- |
| Open my project / Open the project | Opens the selected folder in File Explorer. |
| List project files / Show project files | Shows a bounded list of project files. |
| Find in my project README | Finds matching file names or relative paths. |
| Search my project for package | Finds names or paths containing `package`. |
| Read project file README.md | Displays the text of that file. |
| Show file frontend/package.json | Displays the named relative file. |

For paths with slashes, dots or unusual names, type the exact relative path.
After displaying a file, you can ask **Explain this file** in the same conversation;
that explanation uses Ollama and whatever file excerpt fits the conversation context.

Project access is read-only. Search matches file names/paths, not file contents.
Listing returns at most 80 results while scanning up to 5,000 files. Large dependency
folders are skipped. Reading supports UTF-8 files up to 100 KB, displays up to
20,000 characters, and excludes common credential files. These project commands
are read-only. Separate file commands can copy/move/rename/recycle explicitly
named local project items. Building, running code and Git operations are not
exposed as Bob voice commands.

### Confirmations and natural multi-step requests

For a pending confirmation, say **Yes**, **Confirm**, **Go ahead**, or **Yes do it**.
To reject it, say **Cancel**, **No**, or **Never mind**.

For example, this model-assisted request was verified:

> Could you bring up a calculator and reduce the volume to twenty percent?

Bob executes these routine steps immediately. Ambiguous app matches, Wi-Fi
disconnection, enabling airplane mode, arbitrary Settings changes, and
consequential file operations pause for a specific confirmation. Model-assisted
plans support up to twelve actions and four discovery stages. Interpretation
depends on the model; use exact names if Bob asks to clarify.

A different request clears a pending confirmation. A spoken **Cancel** answers
a pending plan; use the square Stop button to interrupt active generation.

## 4. Conversation, context and screen controls

You can ask ordinary questions, draft text, brainstorm or ask for explanations by
voice or typing. For example: **Help me plan tomorrow**, **Explain this more simply**,
or **Make your previous answer shorter**. These require Ollama.

| Control | How to use it |
| --- | --- |
| New conversation | Starts a separate chat context. Saved personal facts remain available. |
| Recent conversations | Reopens a saved conversation. |
| Trash icon beside a conversation | Deletes that conversation. |
| Memory | Add or remove explicit saved facts. |
| Capabilities | Review available actions and discovered applications. |
| Settings | Configure model, project, voice, personality and resources. |
| Read aloud | Speaks an assistant response when voice output is enabled. |
| Square Stop button | Stops the current response or voice activity. |
| Enter | Sends the typed message. |
| Shift + Enter | Adds a line break. |

Chat history is stored, but only a bounded recent portion goes to the model.
Very long excerpts may be shortened. Use explicit saved facts for information
you want available across separate conversations. Memory retrieval remains
limited by the chosen context size.

## 5. Background operation and performance

- The window's close button hides Bob in the system tray.
- Double-click the tray icon, or right-click and choose **Open Bob**, to reopen it.
- Right-click the tray icon and choose **Quit Bob** to exit completely.
- Closing to the tray stops the active conversation and suspends the web renderer. Enabled wake detection continues.
- There is no automatic startup at Windows login. Wake words work while Bob is running, including in the tray.

In **Settings → Background & resources**, choose:

| Setting | Trade-off |
| --- | --- |
| Unload after every response / 30 seconds | Lower idle model memory; more frequent model-loading delays. |
| Unload after 2 minutes | Default balance between idle memory and follow-up speed. |
| Unload after 5–10 minutes | Keeps the model ready longer, consuming memory while loaded. |
| 2,048-token context | Less context and lower model context-memory use. |
| 4,096-token context | Default context size. |
| 8,192-token context | More conversation context with higher memory use. |

Model size matters more than UI animation. The desktop shell still uses several
hundred MB; Ollama can use several GB separately. These settings do not make an
8-billion-parameter model fit into very little RAM. A cold model can take much
longer to answer than a warm model.

## 6. Troubleshooting

| Problem | What to check |
| --- | --- |
| OLLAMA OFFLINE | Start Ollama; verify the saved local address, then Refresh. |
| MODEL NEEDED / model error | Choose an installed model by its exact name and Save settings. |
| The browser says desktop preview | Launch Bob.exe instead of using the development webpage. |
| No speech detected | Check Windows default input and desktop-app microphone access. Use a real microphone, wait for Listening and check the displayed microphone level. |
| Wrong words appear | Move closer to the microphone, reduce background sound, or correct the editable transcript. Command recognition currently supports English. Low-confidence text asks for confirmation. |
| Bob does not hear me while speaking | Start a voice conversation and check for Echo cancellation active. Restart the session after changing audio devices. If unavailable, use Stop and the microphone. |
| No spoken answer | Enable voice replies, save, and check speaker volume/mute. In 0.10.8, typed replies are spoken too. Interrupted/stopped replies are not read to completion. |
| An application is not found | Use its displayed name under Capabilities; restart Bob after installing it. |
| A project file is not found | Check the saved project root and exact relative path. Try typing the path. |
| First answer is slow | Ollama may be loading the model. Wait, or increase the model idle timeout for faster subsequent turns. |
| The app seems to remain open | It is in the tray. Choose Quit Bob there to exit. |

## 7. Data, updates and limits

Use **Settings → Open data folder** to open `%LOCALAPPDATA%\Bob`.
`bob.db` stores settings, history and saved facts; `notes` contains text notes.
Quit Bob before copying the data folder as a backup. Updates to the EXE use this
same data folder unless you explicitly change the data location.

To update, quit the old version through its tray menu, extract the new ZIP and run
Bob.exe from the extracted folder, or use the standalone EXE. Keep Ollama running for chat and model-assisted interpretation.

The implemented action set covers the commands above. Universal computer control,
email sending, calendar management, arbitrary scripts, project
editing, shutdown/restart, and synchronization with a custom ChatGPT GPT are not
implemented. Ordinary chat can discuss these tasks but does not perform them.

## 8. Two-minute first-use practice

1. Start voice conversation.
2. Say **Open calculator**.
3. When Listening returns, say **Remember that my name is Bhanu**.
4. Say **Recall name**.
5. Say **What time is it?**
6. Say **Open my project** after choosing the project in Settings.
7. Say **Stop listening** while the microphone is listening.

You can type these same commands if microphone recognition needs adjustment.


## Version 0.8: everyday phrasing and Microsoft Edge

Quit the older Bob from its tray menu, then run Bob.exe from release-0.8. Your existing Bob data and settings are retained. Keep Ollama running for conversational interpretation.

Exact aliases take the fast local path: “make it louder”, “a little quieter”, “brighten the screen”, “show running apps”, “fire up calculator”, “pull up Notepad”, and “dial down the volume”. Polite prefixes may be combined. Close fuzzy matches for a small set of reversible phrases are offered for confirmation; ambiguous matches go to the conversational planner. Dictation, searches and file names are not globally autocorrected.

Open Edge first. Focus your intended Edge window before saying “Hey Bob” if several windows are open. You can also specify an exact window title through the planner.

- “In Edge, open another tab and search for Python docs.”
- “Go to example.com in Edge.”
- “List tabs in Edge.” / “Switch to the Documentation tab in Edge.”
- “Go back a page in Edge.” / “Refresh the page in Edge.”
- “Read this page in Edge.”
- “Find privacy on this page in Edge.”
- “Type Hello Bob into the Search field in Edge.”
- “Click Learn more in Edge.” (confirmation required)
- “Zoom in in Edge.” / “Scroll down in Edge.”
- “Open downloads in Edge.” / “Show history in Edge.” / “Open favorites in Edge.”
- “Close this tab in Edge.” (confirmation required) / “Reopen the closed tab in Edge.”

After an Edge action, short follow-ups such as “next tab”, “go back”, and “scroll down” reuse Edge context. Named fields and controls must be exposed by the page's Windows accessibility tree. Read the page first to discover labels. Duplicate labels need clarification. Password fields are excluded. Filling a field does not submit a form. Navigation and shortcut responses report that input was sent, not that the website completed its operation.

This is not universal control of every website: canvas-only controls, inaccessible pages, browser security prompts, CAPTCHAs and protected operations can require manual interaction. Voice accuracy still depends on microphone input and the local speech model.

Edge shortcuts follow [Microsoft's shortcut reference](https://support.microsoft.com/en-us/edge/keyboard-shortcuts-in-microsoft-edge).


# Bob 0.10 — private phone conversation and PC control

Bob offers a private phone webpage and separate, optional carrier reminder calls. Your phone and PC communicate through Tailscale's encrypted device connection and HTTPS. The PC runs Whisper speech recognition, local Ollama reasoning and offline Windows speech for phone replies. The private voice path does not use browser cloud recognition, Twilio or Azure speech.

## Setup

1. Quit older Bob instances from the tray. Extract the 0.10 ZIP and launch Bob.exe. Start Ollama and select your installed model in Bob Settings. Direct actions work without Ollama; open-ended conversation requires it.
2. Install [Tailscale](https://tailscale.com/download) on your Windows PC and phone. Sign both into the same private Tailscale network and connect them. Only grant access to your own trusted devices.
3. In Windows PowerShell, run:

   ```powershell
   tailscale serve --bg http://127.0.0.1:8787
   ```

   Follow Tailscale's HTTPS enablement link if it presents one. Copy the `https://your-pc.your-tailnet.ts.net` address it prints. Use Serve, not Funnel: this should be private to your network, not published to the internet. No router port forwarding is needed.
4. In **Bob → Settings → Phone & reminders**, paste that HTTPS address and click **Enable mobile access**.
5. Open the generated private pairing link on your phone with Tailscale connected. The part after `#` is a secret access token; do not share or post it. The phone page removes it from the address bar and keeps it for that browser-tab session. Select **Remember this phone** only on your own phone to retain pairing when reopening the browser.
6. End any active desktop voice conversation by saying “stop listening”. On the phone, tap **Start private voice conversation** and allow microphone access. Keep the page open and the phone awake.
7. Speak, pause, and wait for Bob's reply. The phone records up to 20 seconds per turn. Audio is transcribed on your PC. After a reply it listens again. Low-confidence transcripts stay in the box for you to check and send. If your phone blocks autoplay, press Play in the audio player, then restart voice mode when ready.
8. Say “stop listening” or tap **Stop** to end the phone voice session. **Disable & revoke links** in desktop Settings stops remote access. A new pairing link invalidates the old one. Pairing is encrypted for your Windows account and restored when Bob restarts.

The PC must be awake, signed in, connected to the internet and running Bob. Windows controls operate in that signed-in desktop; they cannot bypass the lock screen or administrator prompts. The mobile page is a voice/chat remote, not a streamed desktop display.

## Try it

- “Could you open calculator for me?”
- “Set the volume to thirty percent.”
- “In Edge, open another tab and search for Python tutorials.”
- “Make this easier to read in Edge.”
- “Remind me in ten minutes to take a break.”
- “Call me in two minutes to check the oven.”
- “Show my reminders.”
- “Cancel reminder” followed by the displayed eight-character reminder ID.

“Remind me” creates a desktop notification and spoken reminder. “Remind me on my phone” creates a **private phone-page alert**. “Call me” schedules a separate paid carrier call after confirmation and account setup below. Phone alerts appear and speak while the paired page is open with audio enabled. They do not ring through the phone's dialer, wake a locked phone, or work with the browser closed. Missed alerts remain in the reminder list. Reminders survive Bob restarts, but delivery needs Bob running; local reminders may be delayed until its voice engine is free.

## Privacy and voice

- Private phone audio goes only to your PC through the authenticated gateway. Audio uploads are bounded and decoded in memory; generated reply WAV files use a temporary folder removed after transfer. Chat transcripts remain in Bob's normal local history.
- Phone replies use offline Windows speech, regardless of the optional Azure setting for desktop speech. Voice quality depends on the installed Windows speech engine. This is turn-taking conversation, not simultaneous speaking and interruption.
- The separate optional neural desktop voice sends desktop reply text to Azure only after you explicitly configure and enable it. Leave it disabled for fully local speech.
- A paired phone can request the same supported actions as the desktop. Existing confirmations still apply. The app binds only to `127.0.0.1`, validates host/origin, and requires its pairing token for APIs.
- Carrier calls send reminder text and phone numbers to Twilio. They are not end-to-end encrypted and are separate from the private webpage.

Tailscale documents its [device encryption](https://tailscale.com/docs/concepts/tailscale-encryption) and [private HTTPS Serve setup](https://tailscale.com/docs/features/tailscale-serve). Encryption protects transit; it does not protect an unlocked phone or PC from someone using it.

## Troubleshooting

- **Cannot connect:** confirm Bob mobile access is enabled, both devices are connected to Tailscale, the PC is awake, and `tailscale serve status` shows port 8787. Use the HTTPS URL, not localhost on the phone.
- **Pair again:** old links are invalid after disabling access, creating another link.
- **Microphone unavailable:** allow browser microphone permission and open the HTTPS page in a current mobile browser. Typed messages remain available.
- **Bob is busy:** end desktop voice mode and wait for its current response. Desktop and phone share one command engine.
- **Ollama offline:** start Ollama on the PC and refresh Bob's connection. Speech recognition and direct commands still run locally.
- **Edge not found:** open Edge on the PC first. With multiple Edge windows, focus the intended one before waking Bob, or specify its exact title. Accessibility limitations still apply.

Validation covers unit tests, a disposable native Edge fixture, local HTTP authentication checks, and local WAV synthesis/transcription. Your phone/Tailscale network must still be paired and tested; a real external phone connection cannot be verified before your account setup.

## Phone-number reminders (including a locked phone)

1. Create a [Twilio account](https://www.twilio.com/docs/voice/api/call-resource), get a voice-capable Twilio number, and enable calls to your destination country. Trial accounts require a verified destination and have restrictions; provider charges apply.
2. In Bob, open **Settings → Phone & reminders → Create calling configuration**, then open the data folder.
3. Edit `phone-calls.json` in that folder. Set `enabled` to `true`; fill in `account_sid`, `auth_token`, `from_number` (your Twilio number), and `to_number` (your own phone). Numbers must include `+` and the country code. Save the file. Keep credentials private; never commit this file.
4. Leave Bob running and the PC awake with internet access. Say **“Call me in two minutes to check the oven.”** Review the reminder and confirm it. No public webhook or Tailscale connection on the phone is needed for these calls.
5. Answer the incoming call to hear Bob's reminder. The call can ring while the phone is locked, subject to reception, phone settings and Do Not Disturb. Check Twilio call logs if it fails.

These calls speak a reminder and end; they do not listen to replies or provide two-way PC control. Use the private webpage while the phone is awake for conversation and PC actions. A browser cannot promise continuous microphone use while the phone is locked. Bob does not provide background push notifications.

**Call submitted** means the provider accepted the request, not that you answered. Bob makes one attempt, does not automatically redial, and marks calls more than five minutes overdue as failed rather than ringing unexpectedly after a long shutdown. Reminder text uses Twilio's [neural Say voice](https://www.twilio.com/docs/voice/twiml/say); desktop personality settings do not change that voice.

If Bob saves the reminder but the call never arrives, check these Twilio Console pages:

- **Phone Numbers > Manage > Active numbers** must show the exact `from_number` in `phone-calls.json`, and that number must support **Voice**.
- **Verified Caller IDs** must show your `to_number` when using a trial Twilio account.
- **Voice > Settings > Geo permissions** must allow calling your phone's country.
- **Monitor > Logs > Calls** shows the provider-side failure reason. Bob 0.10.2 also shows Twilio's error code/message in the reminder detail when the submission is rejected.

## Window follow-ups (0.10.1)

If “close YouTube” finds several windows, say **“close all those”**, **“close both”**, or **“close the second one.”** Bob remembers the specific listed windows for three minutes in that conversation. One confirmation covers the displayed group. A browser window closure closes all tabs in that window; this is not a request to close only YouTube tabs. If a listed window changes or disappears, refresh the choices by naming the app again. The phone connection retries status reads with backoff; it never retries commands automatically.

For iPhone voice access and limitations, see Phone-Setup.md in the release ZIP.
