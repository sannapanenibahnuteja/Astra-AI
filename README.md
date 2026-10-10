# Bob Desktop

A Windows personal AI assistant built from this Bob project: React interface,
Python native bridge, Ollama conversation and Windows actions. The desktop app
uses a minimal, dark holographic interface with a JARVIS-inspired core, without
a WebGL render loop.

For the long-term assistant plan, see the [product roadmap](docs/ROADMAP.md) and
[feature matrix](docs/FEATURES.md). They track the current Windows EXE against
the larger vision: natural conversation, personal memory, screen awareness,
knowledge search, agent mode, mobile access, proactive help and domain modules.

## Run the Windows app

1. Run `dist/release-0.10.19/Bob/Bob.exe` directly. Keep `_internal` beside the EXE: it contains the runtime and speech models. No release ZIP needs to be extracted.
2. Start [Ollama for Windows](https://ollama.com/download/windows). Install a model
   with tool support, for example `ollama pull qwen3:8b`. This computer already has
   `qwen3:8b`; distributing Bob does **not** distribute the model.
3. In Bob Settings, refresh the connection and choose your installed model.
4. Choose your current project folder and save settings.
5. Bob greets you and starts listening automatically at startup. Say **Hey Bob** or **Okay Bob**, wait for **Listening**,
   then speak. Alternatively click the microphone or **Start voice conversation**.
   With **Echo cancellation active**, speak anytime to interrupt Bob. Say **stop listening** to return to wake-word standby.

Windows 10/11 x64, Microsoft Edge WebView2 Runtime, Windows PowerShell 5.1 and a
Windows English Speech pack (for wake words only) are required. English command
transcription uses the bundled Whisper small.en model offline. Python and Node are bundled/not needed
by end users. This is a portable, unsigned EXE; it is not an installer or a signed
Microsoft Store release. Get missing WebView2 from Microsoft's official website.

Closing the window hides Bob in the system tray. Double-click its tray icon to
reopen, or right-click → Quit Bob to exit. Closing to tray ends the current voice
conversation; wake detection continues if enabled. Disable **Wake words** in
Settings to stop background listening. Minimized/hidden animations pause.

## Working features

- Streaming local chat, recent conversation context, saved conversations and deletion.
- Stop interrupts a pending model request, including cold model loading. Prompt
  excerpts scale with the selected context size; the current request is retained.
- Explicit persistent memory: `remember that my bike is GT650`, `recall bike`,
  plus a memory screen to add and delete facts.
- Offline Whisper command transcription, a startup greeting, spoken replies and
  configurable speaking speed. Wake detection uses a separate constrained Windows
  recognizer. Low-confidence transcripts ask for confirmation and stay editable.
  Follow-up voice turns share conversation context; silence returns to standby.
- Direct commands execute immediately: `open calculator`, `open downloads`,
  `search the web for astronomy`, `set volume to thirty percent`, `mute`, `unmute`,
  `take a note: buy coffee`, `system status`, `what time is it`.
- Start menu discovery, conservative fuzzy application matching, and per-conversation
  `open it again` context. Fuzzy matches and PC locking ask for confirmation.
- Natural paraphrases and multi-step requests use Ollama tool calls. Routine actions execute immediately; ambiguous or consequential actions ask first. Up to twelve supported actions
  per request. Each proposed action is validated; dependent file targets resolve after prior steps. Consequential steps pause for confirmation with exact targets.
- Project access: `open my project`, `list project files`, `find in my project README`,
  `read project file README.md`. Reads are bounded to the selected folder; directory
  traversal, common credential files and large files are excluded. File search
  matches names, not contents. Project access is read-only.

Model interpretation can be wrong. Bob cannot execute every conceivable task:
email integration, unrestricted GUI control, calendar, repository editing, shutdown and arbitrary
shell commands are not implemented. Unsupported requests receive conversational
help. Model-generated scripts are never automatically executed. This project
connection does not connect to a ChatGPT GPT or synchronize another assistant.

## Windows control in 0.8

Brightness, window listing/switching/minimizing/maximizing/restoring/closing,
accessible-control inspection and activation, literal typing and common keyboard
shortcuts are available. Name the target application, then use follow-ups such as
“maximize it.” Routine compound requests run as ordered steps without repeated confirmation.
Execution stops on an error and reports completed steps. Windows Update requests
open the proper settings page, not CPU/memory status. See docs/USER-MANUAL.md.
The [Windows settings URI](https://learn.microsoft.com/en-us/windows/apps/develop/launch/launch-settings),
[pywinauto accessibility controls](https://pywinauto.readthedocs.io/en/latest/code/pywinauto.controls.uiawrapper.html)
and [screen brightness API](https://crozzers.github.io/screen_brightness_control/extras/Quick%20Start%20Guide.html)
underlie these integrations. Not all applications expose usable automation controls.

Bluetooth and Wi-Fi radios use the native Windows radio API with state readback.
Saved Wi-Fi connections use Windows WLAN inventory and `netsh`, without accessing
passwords. Airplane mode and energy saver use the real Settings accessibility
controls. Named Settings pages, exact-label toggles/dropdowns/sliders, and local
file list/find/open/create/copy/move/rename/recycle operations are supported.
File changes refuse overwrites; moves, renames and recycling ask about concrete
paths. Per-conversation context resolves setting and file follow-ups. A bounded
model tool loop can inspect controls/files before choosing subsequent actions.
See [the full manual](docs/USER-MANUAL.md) for examples and platform limits.

Music/video controls include pause, resume, stop, next/previous, seeking, speed,
shuffle/repeat and now-playing information for compatible Windows media sessions.
Name an app or exact title when several players are open. Local tracks/videos open
in the default player; YouTube/Spotify searches open results without claiming
playback. Controls depend on what each player exposes to Windows.

## Performance and privacy

The UI uses CSS/SVG and WebView2. Enabled wake detection keeps a Windows speech
process and microphone active in standby. Whisper loads only for transcription,
uses two CPU threads, and releases its model after 60 seconds without a transcription.
No audio files are saved by normal capture. Chat polling occurs only while generating.
Ollama is used only on demand; settings control context size and model unloading
(default 2 minutes). A cold model may take noticeably longer to load than a warm
model. Larger models consume several GB of RAM/VRAM independently of the UI.
Choose a smaller installed tool-capable model for a lighter machine.
Prompt sizing uses a conservative byte estimate rather than a model-specific
tokenizer; long messages are marked when shortened for the model. Full text stays
in saved history.

Data lives under `%LOCALAPPDATA%\Bob`: `bob.db`, notes, WebView storage and logs.
Use **Open data folder** in Settings. Chat text and facts go to the configured
loopback Ollama service. Web searches and opened websites use your default browser.
No external fonts or analytics are loaded by the interface. Recognition quality
still depends on your microphone, accent and environment. Desktop voice sessions
support spoken interruptions through local WebRTC echo cancellation. If the device
cannot initialize duplex audio, use Stop and the microphone. Existing user history is
copied to the renamed data folder on first launch; historical messages are preserved.

## Development

```powershell
.\venv\Scripts\python.exe -m pip install -r desktop/requirements.txt
cd frontend
npm ci
npm run build
cd ..
.\venv\Scripts\python.exe scripts/download-speech-model.py
.\venv\Scripts\python.exe -m desktop.main
```

`npm run dev` in `frontend` shows the interface in a browser. **Native functionality
is available inside the Windows app only**; the browser preview is not connected
to the desktop bridge. The existing FastAPI backend is retained as legacy code;
it is not started by the packaged desktop app. User edits in legacy files are preserved.

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p 'test_desktop*.py' -v
cd frontend
npx --no-install eslint src/desktop src/App.jsx src/main.jsx
npm run build
cd ..
.\scripts\build-windows.ps1
```

Current launchable build: `dist/release-0.10.19/Bob/Bob.exe`, with `_internal` and the user guide beside it. Do not move the EXE out of that folder. The source models under dist/models are build inputs; copies under `_internal/models` are required at runtime.

See [0.10.19 command repairs, Edge fixes and tests](docs/RELEASE-0.10.19.md).
Optional integration checks: `python scripts/verify-ollama.py` (local model,
does not execute planned OS actions), `python scripts/verify-voice.py` (synthetic
WAV fixtures and wake grammar checks; no microphone), `python -m desktop.main
--voice-test-dir .cache/voice-fixtures --data-dir .cache/voice-test`, and `python -m desktop.main --ui-test
--data-dir .cache/ui-test` (temporary real desktop window).

Implementation follows the [Ollama chat API](https://docs.ollama.com/api/chat)
and [pywebview packaging guidance](https://pywebview.flowrl.com/guide/freezing).

Brightness now addresses each monitor through its own hardware method and verifies
read-back. Commands support all displays, internal/external displays, and Bob's
numbered monitors. Volume setters verify the active Windows endpoint and unmute
positive volume settings. Read-only status queries never change brightness/volume.
Common device and compound commands bypass Ollama for lower latency.

## Edge and conversational aliases in 0.8

Bob now supports Edge navigation, tab discovery/selection, page accessibility inspection, named field filling, confirmed control activation, find, scrolling, zoom, history, favorites and downloads. Start with “in Edge” and use short follow-ups after that. Everyday aliases run locally; broader semantic requests require Ollama. See the updated user manual for examples and accessibility limitations.

Regression checks: `python -m unittest discover -s tests`. Opt-in native Edge fixture: `python scripts/verify-edge.py` (isolated profile, local test page, no personal tabs).

## Phone access, reminder calls and usability in 0.10

See [phone setup](docs/PHONE-SETUP.md) for private Tailscale HTTPS pairing and optional paid Twilio reminder calls. Calls can ring a locked phone but are not end-to-end encrypted; they speak reminders, not two-way conversations. The private webpage supports voice/chat PC control while awake. Pairing now survives Bob restarts, with optional trusted-phone persistence.

This release adds six conversation personalities, explicit monitor-to-monitor window movement, literal Notepad dictation with verified Unicode paste, and more cautious review of uncertain speech. See [the manual](docs/USER-MANUAL.md) for examples. No assistant can guarantee arbitrary application control or flawless recognition; supported accessibility actions and existing confirmations remain in force.

Full release verification: [test report](docs/TEST-REPORT-0.10.19.md).
