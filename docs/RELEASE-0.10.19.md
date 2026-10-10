# Bob 0.10.19: command repair and verified Edge closure

Changes from 0.10.18:

- Repeated requests such as “I said close all you tube” and “As I said, list windows” use the fast native command handler instead of falling through to Ollama.
- Split spoken names such as “you tube” work for single tabs, all matching tabs, and whole-window groups. Explicit “in Edge” requests work too. Dictated text and negative requests remain unchanged.
- Group tab closure selects across Edge windows and retains the exact selection through approval. Whole-window requests explicitly warn that other tabs in those windows will also close.
- Edge control enumeration recovers from the detached-parent accessibility race found during live testing.
- Tab closure waits for foreground activation before sending the close shortcut. It still refuses to send keys to the wrong window and checks each selected tab disappeared.
- Empty local-model answers receive one compact retry. A second empty reply reports a failure and says nothing changed; model prose cannot invent successful execution.
- Fixed the “whats app” website alias, found by checking every service alias.
- Added a release test ledger and fixtures for every advertised action, every supported browser shortcut, Settings page, website and spoken website alias.

## Run

Quit the old Bob from its tray menu. Run `Bob.exe` inside `dist/release-0.10.19/Bob`. Keep `_internal` beside it. No ZIP extraction is needed. Existing Bob settings and saved profiles remain in the normal local data folder.

## Quick retest

1. Open two disposable YouTube tabs, preferably in different Edge windows.
2. Say “I said close all you tube.” Bob should describe the selected tabs. Say “yes”; only the selected matching tabs should close.
3. Say “As I said, list windows.” A real window list should appear without a model error.
4. For whole windows, say “Close all YouTube windows.” Read the warning about their other tabs before approving.
5. Say “Open Notepad and type Hello Bob into Notepad.” Check the exact text, then try “Move Notepad to monitor two.”
6. Ask a question, then interrupt with “Actually, open calculator.” Bob should stop, capture the complete request, and execute it after your speaking pause.

See [the complete verification report](TEST-REPORT-0.10.19.md) for the actual checks and their limits. The user manual covers existing voice, memory, settings, media and phone setup. This release does not add unrestricted control over arbitrary apps or locked-iPhone wake words.
