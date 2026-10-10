# Bob 0.10.19 verification report — 10 October 2026

## What this report proves

**220 automated tests passed, with 422 recorded test/subtest outcomes.** Every one of the 84 advertised model actions has a valid command fixture. All 19 browser shortcuts, 55 Settings pages, 28 website targets and 13 spoken website aliases were validated. No skipped checks in the regression ledger. Frontend production build, desktop UI lint and Git whitespace checks passed.

A command-contract check proves routing/validation accepts its supported parameters; **it does not prove every app, monitor, network or external account works live**. The tests below distinguish those levels. There is no honest way to guarantee every possible task in every Windows app from an automated test suite.

## Live and packaged checks performed

| Area | Result and scope |
|---|---|
| Screenshot requests | “I said close all you tube” selected and closed two real tabs in two disposable Edge windows; approval retained their exact IDs. Personal tabs were excluded from the fixture. “As I said, list windows” bypassed the model in regressions. |
| Edge controls | 11 live checks passed in a disposable profile: accessible page reading, literal field filling, button click and observed result, tabs, find, escape, new tab, tab selection and verified navigation to a local URL. A UIA tree race found on the first run was fixed and the run passed afterward. |
| Two monitors | Live test window moved to monitors 1 and 2. Literal typing into that window was verified. |
| Brightness and volume | Actual laptop and external monitor brightness plus output volume changed in a three-step request in 0.78 seconds. Previous brightness, volume and mute state restored afterward. COM teardown warnings occurred; execution and restoration completed without a failed assertion. |
| Notepad | Exact text “Hello, Bob! Keep A+B = {value}.” saved and compared in a disposable document; only its test tab closed. |
| Windows media | Real Windows session pause, seek to 30 seconds and resume verified on a silent disposable Edge player. Other players' next/previous/rate/shuffle/repeat support remains app-dependent. |
| Local Ollama | Actual qwen3:8b answered a generic greeting, remembered fictional Moon Garden context and produced a validated calculator tool call after compact recovery. The calculator paraphrase recovered in 3.64 seconds at 8192 context; a short arithmetic reply took 0.72 seconds in that controlled run. Tool execution was simulated for the model tests. These are measurements, not latency guarantees. |
| Final EXE startup | Packaged smoke check passed and reported 0.10.19. |
| Final EXE devices/network/media | Bundled native modules successfully read brightness/audio, Wi-Fi/Bluetooth state and media sessions. Connectivity was not changed. |
| Final EXE Windows actions | Dedicated fixture passed focus, exact typing, accessible button click, maximize and restore. Fixture data matched “Hello + {Bob}”. |
| Final EXE frontend | Four navigation destinations, no horizontal overflow, voice round trip and interrupted command execution passed. Input speech and calculator execution were simulated in this UI fixture. |
| Final EXE voice profiles | Synthesized enrollment, a different phrase from the same synthetic speaker, encrypted reload and deletion passed. Similarity 0.929 at Balanced threshold 0.65. This does not establish live accuracy for the user's voice. |
| Whisper in final EXE | Generated calculator/time/memory/search phrases transcribed; silence produced no text. “Stop listening” transcribed correctly but confidence requested review. Whisper rendered short wake phrases as “bulb”; this remains a transcription limitation, not a passing exact-transcript check. |
| Windows wake recognizer | Separate wake recognizer correctly detected generated “Hey Bob” and “Okay Bob”. No live user microphone test performed. |
| Echo and interruption | AEC with generated far/near speech produced no interruption for Bob-only echo; both stronger and quieter near speech interrupted, ended and transcribed “Actually, open calculator” into a reliable action plan. Real room/speaker/microphone performance remains unverified. |
| Phone page | Local HTTP authorization/origin/host checks, pairing encryption, reminder behavior and simulated chat routing passed in regressions. JavaScript reconnection, hidden-page backoff, single-poll protection, token rotation and revocation passed. No physical iPhone/Tailscale session tested in this release. |
| Carrier calls | Configuration, confirmation, escaping, error handling and single-attempt delivery tested with a simulated provider. No new paid/carrier call placed in this release. The earlier user-confirmed Twilio test call is historical evidence only; custom reminder calling previously encountered trial restrictions. |

## Behavior regression coverage

| Family | Tests and limitations |
|---|---|
| Conversation and agent mode | Streaming sentence boundaries, interruptions, cancellation, repairs, references, context expiry/isolation, multi-step approvals, bounded retries and false-success prevention. Model outputs/actions simulated except the explicit Ollama checks above. |
| Memory and profiles | Real fixture databases/files; per-profile memories, encrypted profile persistence, isolated conversations, profile deletion and personality preferences. Synthetic vectors or speech; not authentication. |
| Files and project | Disposable files exercise listing/search/copy/rename/move and protection rules; Explorer selection/opening and recycle APIs use mocks where noted in the test ledger. No personal files changed. |
| Settings and network | Known-page routing, accessible toggle fixtures, Wi-Fi profile selection, denied access, failed readback and confirmations. Radio changes, airplane mode, energy saver and arbitrary Settings controls were not changed live. |
| Media | All transport/value validation, ambiguity/failure behavior, local-media requests and search honesty. Only pause/seek/resume were executed live on a test player. |
| Phone and cloud voices | Auth, pairing, reconnect, reminders and provider failure behavior tested locally/simulated. Physical locked-iPhone delivery, paid Twilio reminders and Azure network synthesis not verified in this release. |
| Packaging | Runtime/models and distribution allowlist tests; final EXE diagnostics above. `_internal` must remain beside Bob.exe. |

## Every advertised action: contract coverage

The following table is **validation coverage**, not an assertion that all 84 actions were executed on the user's system. Detailed behavior fixtures are identified in the test ledger.

| Action | Family | Command contract |
|---|---|---|
| `audio_status` | Windows, memory and project | Passed |
| `brightness` | Windows, memory and project | Passed |
| `brightness_down` | Windows, memory and project | Passed |
| `brightness_status` | Windows, memory and project | Passed |
| `brightness_up` | Windows, memory and project | Passed |
| `click_control` | Windows, memory and project | Passed |
| `close_window` | Windows, memory and project | Passed |
| `edge_click` | Edge | Passed |
| `edge_close_tab` | Edge | Passed |
| `edge_close_tabs` | Edge | Passed |
| `edge_fill` | Edge | Passed |
| `edge_find` | Edge | Passed |
| `edge_inspect` | Edge | Passed |
| `edge_navigate` | Edge | Passed |
| `edge_search` | Edge | Passed |
| `edge_select_tab` | Edge | Passed |
| `edge_shortcut` | Edge | Passed |
| `edge_tabs` | Edge | Passed |
| `explorer_selection` | Files | Passed |
| `file_copy` | Files | Passed |
| `file_find` | Files | Passed |
| `file_list` | Files | Passed |
| `file_mkdir` | Files | Passed |
| `file_move` | Files | Passed |
| `file_open` | Files | Passed |
| `file_properties` | Files | Passed |
| `file_recycle` | Files | Passed |
| `file_rename` | Files | Passed |
| `focus_window` | Windows, memory and project | Passed |
| `inspect_window` | Windows, memory and project | Passed |
| `list_monitors` | Windows, memory and project | Passed |
| `list_windows` | Windows, memory and project | Passed |
| `lock` | Windows, memory and project | Passed |
| `maximize_window` | Windows, memory and project | Passed |
| `media_back` | Media | Passed |
| `media_forward` | Media | Passed |
| `media_next` | Media | Passed |
| `media_open` | Media | Passed |
| `media_pause` | Media | Passed |
| `media_play` | Media | Passed |
| `media_previous` | Media | Passed |
| `media_rate` | Media | Passed |
| `media_repeat` | Media | Passed |
| `media_search` | Media | Passed |
| `media_seek` | Media | Passed |
| `media_sessions` | Media | Passed |
| `media_shuffle` | Media | Passed |
| `media_status` | Media | Passed |
| `media_stop` | Media | Passed |
| `minimize_window` | Windows, memory and project | Passed |
| `move_window` | Windows, memory and project | Passed |
| `mute` | Windows, memory and project | Passed |
| `note` | Windows, memory and project | Passed |
| `open` | Windows, memory and project | Passed |
| `open_project` | Windows, memory and project | Passed |
| `press_key` | Windows, memory and project | Passed |
| `project_list` | Windows, memory and project | Passed |
| `project_read` | Windows, memory and project | Passed |
| `project_search` | Windows, memory and project | Passed |
| `radio_set` | Settings and connectivity | Passed |
| `radio_status` | Settings and connectivity | Passed |
| `recall` | Windows, memory and project | Passed |
| `remember` | Windows, memory and project | Passed |
| `reminder_add` | Reminders | Passed |
| `reminder_cancel` | Reminders | Passed |
| `reminder_list` | Reminders | Passed |
| `restore_window` | Windows, memory and project | Passed |
| `search` | Windows, memory and project | Passed |
| `settings_inspect` | Settings and connectivity | Passed |
| `settings_open` | Settings and connectivity | Passed |
| `settings_set` | Settings and connectivity | Passed |
| `settings_status` | Settings and connectivity | Passed |
| `status` | Windows, memory and project | Passed |
| `time` | Windows, memory and project | Passed |
| `type_text` | Windows, memory and project | Passed |
| `unmute` | Windows, memory and project | Passed |
| `volume` | Windows, memory and project | Passed |
| `volume_down` | Windows, memory and project | Passed |
| `volume_up` | Windows, memory and project | Passed |
| `wifi_connect` | Settings and connectivity | Passed |
| `wifi_disconnect` | Settings and connectivity | Passed |
| `wifi_profiles` | Settings and connectivity | Passed |
| `wifi_status` | Settings and connectivity | Passed |
| `windows_update` | Windows, memory and project | Passed |

## Repeat the checks

- `venv\Scripts\python.exe scripts\verify-release-tests.py` runs every regression and records outcomes.
- `npm run build` in `frontend` builds the UI.
- `scripts/verify-edge.py`, `verify-tab-groups.py`, `verify-v010.py`, `verify-notepad.py`, `verify-media-fixture.py` run live disposable fixtures. Run GUI fixtures sequentially to avoid competing for foreground focus.
- `scripts/verify-device-execution.py` temporarily changes and restores actual brightness/volume.
- `scripts/verify-interruption.py` checks generated-speech echo/interruption/transcription.
- `Bob.exe --smoke-test`, `--device-test`, `--system-test`, `--media-test`, `--speaker-test`, `--ui-test` accept `--data-dir` for isolated verification. The UI fixture simulates speech and calculator execution.

Per-check outcomes: [TEST-RESULTS-0.10.19.json](TEST-RESULTS-0.10.19.json). Changes and short user retest guide: [RELEASE-0.10.19.md](RELEASE-0.10.19.md).

## Limits you should know

Bob does not provide arbitrary control over every app, perfect recognition, biometric authentication, or a locked-iPhone “Hey Bob” listener. Cloud/phone capabilities require their configured providers and actual device verification. The broader 23-feature product vision remains partly implemented; this release does not convert roadmap targets into shipped features. See FEATURES.md and CONVERSATION-CAPABILITIES.md for scope.
