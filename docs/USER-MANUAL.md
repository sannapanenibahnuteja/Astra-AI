# Bob Desktop — User Manual & Voice Commands

This manual describes the current portable Windows EXE built from this project.
Commands listed here were checked against the desktop runtime. Recognition quality
depends on your microphone, accent and background noise. Release 0.7 uses local
Whisper small.en for English commands and Windows speech for wake words.

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
2. Wait for the short tone. The microphone is then ready.
3. Say a short command, such as **Open calculator**.
4. Pause at the end. Bob submits the recognized sentence and responds.
5. Click the microphone again for another command or to answer a confirmation.

Each attempt waits about eight seconds for speech and records up to twenty
seconds. A pause of roughly 0.9 seconds ends the utterance. Watch the microphone
level, then **Transcribing your words**. The first recognition loads the local
model and may take longer. Uncertain text is shown in the composer and Bob asks
for confirmation: say **yes**, repeat the request, or edit and send it.

### Back-and-forth voice conversation

Click **Start voice conversation** in the right panel. Bob listens, responds,
then listens again. Speak the next request when **Listening** appears.

While it is listening, say **Stop listening**, **Stop voice**, or **Go to sleep**
to end voice mode. You can also click **End voice conversation** or the square
Stop button. Stopping voice mode does not close the app.

### Greeting and wake words

On launch Bob greets you and starts listening automatically after the tone. You do not need to press the microphone button. Disable **Start listening automatically at launch** only if you prefer manual startup. Say **Hey Bob** or **Okay Bob**, pause for
its tone, then say your request. Do not run the wake word and the request together:
the wake listener hands the microphone to the command recognizer after activation.
Follow-up requests use the same conversation. Eight seconds without speech returns
to standby. Closing to the tray ends the voice conversation, while enabled wake
listening continues and can reopen the window.

Bob pauses wake detection during its own speech and during an active voice session.
It does not listen for interruptions while replying: use the square **Stop** button,
then the microphone. Disable **Wake words** in Settings to turn off background
microphone listening. **Test voice output** checks the speaker/TTS path.

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
| No speech detected | Check Windows default input and desktop-app microphone access. Speak after the tone and check the displayed microphone level. |
| Wrong words appear | Move closer to the microphone, reduce background sound, or correct the editable transcript. Command recognition currently supports English. Low-confidence text asks for confirmation. |
| Bob does not hear me while speaking | This version listens between replies. Click Stop to interrupt, then activate the microphone again. |
| No spoken answer | Enable Read replies during voice conversations, save, and check speaker volume/mute. Typed replies are not automatically spoken. |
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
email sending, calendar management, timed reminders, arbitrary scripts, project
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
