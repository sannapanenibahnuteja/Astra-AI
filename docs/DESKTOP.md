# Project assessment and desktop implementation

The original project combines a React/Vite frontend, Zustand stores, several
overlapping Three.js visualizations and voice listeners, and a FastAPI backend
with Windows app/volume/file handlers. There were two backend entry points and
duplicate streaming routes. The desktop folder and documentation were empty.

The original active chat route treated any sentence containing `open`, `launch`
or `start` as a command. Its Ollama prompt contained saved facts and only the latest
message, so chat history did not reach the model. Dependencies needed by Windows
handlers were missing from backend/requirements.txt. Persistent data lived beside
backend source files, unsuitable for a packaged Windows app.

The desktop release adds a single coherent runtime under `desktop/` and switches
the active React entry point to `frontend/src/desktop`. Existing legacy code and
the user's pre-existing modifications remain in place. The release does not
depend on the old FastAPI server or its unauthenticated command endpoints.

## Active flow

React → pywebview native bridge → deterministic command parser or Ollama streaming
→ validated action plan → Windows action → persisted result.

- Exact commands avoid model inference. Fuzzy application matches ask before launching.
- Indirect requests use Ollama's structured tool calls. All actions are validated;
  routine sequences execute directly; ambiguous/consequential sequences require confirmation.
- SQLite stores conversations, facts, per-conversation application context and settings.
- File reads are constrained to the selected project folder; no project writes.
- A constrained Windows speech subprocess detects Hey Bob / Okay Bob in standby.
  Command audio uses sounddevice and local faster-whisper small.en on CPU int8.
  VAD rejects non-speech; uncertain transcripts require confirmation and remain editable.
  The speech model releases after 60 idle seconds. Normal recordings stay in memory.
- The system tray keeps the app accessible. Closing to tray ends conversation capture; enabled wake detection remains available.
  CSS animations pause while hidden. Ollama keep-alive and context size are configurable.
- The production bundle has no remote fonts, analytics, Three.js or WebGL dependency
  in its active import graph. The old source dependencies remain for legacy code.

## Validation

The follow-up release adds cancellable streaming while waiting for response
headers and prompt budgeting that scales with context size. A real loopback-server
regression verifies cancellation in under one second and checks that the next
request can start without duplicate history. Thirty-eight regression tests pass,
including the Ollama connection-status check.

The regression suite covers persistent/isolation behavior, duplicate memories,
fuzzy confirmation, conversational false positives, context, streaming prompt
history, model action validation, cancellation of pending plans, project traversal,
credential-file exclusion, settings validation and failure reporting.

Real Ollama checks on this computer passed with qwen3:8b: a remembered project name
was recalled in the next turn, and an indirect calculator/volume request became
the correct two-step confirmation plan. No OS action was performed by that test.
The cold first request took about 67 seconds; warm follow-ups took about 0.2 and
1 second. These are test observations, not guaranteed latency.

Voice regression fixtures verify both wake phrases through Windows grammar and
command transcription through the actual local model. Silence produces no command.
Synthetic audio does not guarantee real microphone/accent/noise performance.
The microphone default on this PC was Realtek Audio; the wake listener reached ready.

## Limits

This is a portable unsigned Windows application, not a signed installer.
Ollama/model installation is separate. The EXE embeds the English speech model; no sidecar folder is required. Wake recognition requires an English Windows
speech pack. Spoken interruption during replies, autonomous arbitrary GUI control, email,
calendar, code-editing agent or universal task execution is implemented.

The browser development server is a visual preview. Launch the native application
for Windows integration. Memory remains in the same per-user data folder across
app updates; packaging never embeds local conversations or project files.

## 0.4 Windows integration validation

The Windows command layer was exercised against a dedicated disposable WinForms
fixture: focus, literal text including braces/modifier characters, accessible
button activation, maximize, restore and minimize. The fixture recorded the exact
expected text. Both detected displays accepted their existing brightness value
and reported it back (no visible brightness change during testing).

A live qwen3:8b check produced an ordered Notepad/open, literal text/type,
window/maximize and brightness/40 plan. The check verified the exact dictated text
and did not execute the proposed actions. Model interpretations remain fallible.

Automatic listening starts after the greeting. Wake detection resumes after idle
timeout. The speech model is embedded in the executable, fixing the former
missing-sidecar failure. Voice capture calibrates against a short ambient-noise
sample before its ready tone. Speak after that tone.

## 0.5 verification

Both displays were changed by five percentage points and verified through WMI
(laptop) and VCP (external). The active Realtek output was changed by five points
and read back. Original values were restored. The complete direct-command path
changed both monitors plus volume in 0.58 seconds on this PC, without a model call
or confirmation. This is an observed test time, not a latency guarantee.

## 0.6 integration and validation

`settings_control.py` maps named Settings pages and reads UI Automation controls.
The Windows 11 Settings frame on this PC is hosted by ApplicationFrameHost; the
integration supports that host as well as SystemSettings.exe. Energy saver uses
the section's ExpandCollapse pattern and its Always use energy saver toggle.
`network.py` uses WinRT radios through a short-lived Windows PowerShell helper,
plus WLAN API inventory and fixed-argument netsh
commands. Wi-Fi profile keys are never requested. Packaged `--system-test` reads
radio and connection state without changing networking.

`files.py` handles explicit local file operations, redirected personal folders,
foreground Explorer selection, frozen approval targets, source identity checks,
exclusive-create copies and Recycle Bin deletion. Changes stop on failure and
report completed counts. Cross-drive moves and system/app-data changes are excluded.

The runtime executes dependent steps in order and confirms consequential steps
at the point their concrete targets are known. Model-assisted discovery can use
up to four rounds/twelve tools, consuming real observations and rejecting repeated
completed steps. Direct commands still avoid the model entirely. Per-conversation
context stores the last setting, Wi-Fi profile, working folder and selection.

Unit/integration coverage includes negation, settings-name conjunctions, quoted
paths, compound references, overwrite prevention, changed approval sources,
Wi-Fi denied access/failed readback, Settings state verification and a model
inspection-to-action round trip. Live checks read Bluetooth/Wi-Fi/airplane/energy
states and exercise idempotent radio/energy-saver setters without disconnecting
networking. Actual Wi-Fi disconnect/reconnect and arbitrary Settings values were
not exercised on the user's active connection.

API references:
- https://learn.microsoft.com/en-us/uwp/api/windows.devices.radios.radio
- https://learn.microsoft.com/en-us/windows/win32/nativewifi/native-wifi-reference
- https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh-wlan
- https://learn.microsoft.com/en-us/windows/apps/develop/launch/launch-settings
- https://docs.ollama.com/capabilities/tool-calling

Radio isolation was verified after reproducing a PyWinRT/ONNX Runtime native
import crash. Bob does not import PyWinRT or bundle it; the OS helper avoids
loading radio and speech native libraries in the same process.

## 0.7 media integration

`desktop/media.py` uses Windows GlobalSystemMediaTransportControlsSession via a
short-lived PowerShell WinRT helper. It queries capability flags and verifies the
reported playback state, position, track or setting after commands. It supports
player/title targeting, handles nullable shuffle/repeat/rate metadata, refuses
ambiguous sessions, and does not fall back to blind global media keystrokes.
Local media opening is limited to audio/video extensions; streaming-service search
is explicitly reported as search, not playback.

The live test used a disposable silent browser Media Session, successfully pausing,
seeking to exactly 30 seconds, and resuming. Existing user media was not targeted.
Run `scripts/verify-media.py --serve`, open its localhost URL and press Play, then
run `scripts/verify-media.py --verify`. The fixture supports HTTP byte ranges so
its seeking behavior reflects a real seekable media source. `Bob.exe --media-test`
performs a read-only packaged session inventory.

Reference: https://learn.microsoft.com/en-us/uwp/api/windows.media.control.globalsystemmediatransportcontrolssession
