# Bob 0.10.15 — Faster startup and ordinary conversation

## Changes from 0.10.14

- Bob is now a portable application folder. The EXE loads speech models and libraries from `_internal` instead of unpacking the large single-file archive each time you start it. Run `Bob.exe` and keep the whole folder together.
- Clear greetings and informational questions use a shorter prompt with no Windows tool schema or app catalog. Saved memory and conversation history remain available. Requests containing actions retain the action planner and execution checks.
- Current time follows the stable instructions instead of preceding them, allowing more of the prompt prefix to be reused by the local model between turns.
- Voice choices, interruptions, corrections and verified tab/window closures from 0.10.14 remain included. This release does not change your model, context size, microphone quality or voice settings.

## Install

1. Quit the old Bob from its tray menu.
2. Extract **ALL** files from `Bob-Windows-x64.zip` into a new folder.
3. Run **Bob.exe** in that folder. Keep **_internal** beside it; copying only the EXE will not work.
4. Check version **0.10.15**. Your existing preferences and memory remain in the same Windows user data folder.

## Test

- Start Bob twice and compare how quickly its window appears with 0.10.14.
- Say “Hello Bob”, “What are black holes?” and “Tell me about astronomy”. These should use the lighter conversation path.
- Say “Open calculator”, then “Open it again”. Direct commands and context should still work.
- While Bob explains, say “Actually, open calculator”. Interruption must still execute the replacement request.
- Test your selected voice and “close all YouTube tabs” as described in the [0.10.14 guide](https://github.com/sannapanenibahnuteja/Astra-AI/blob/main/docs/RELEASE-0.10.14.md).

Cold Ollama model loads, GPU/CPU limits, large conversation histories and network speech can still add delay. The app does not silently select a smaller model or reduce context. If slower responses persist, compare a short new conversation with your long existing one and choose Fast conversation mode in Settings.

The controlled Twilio trial test reached the user's phone and was answered with audible test speech. This verifies that tested route, not a guarantee for future calls. Custom Bob reminder requests remain subject to the trial parameter restrictions documented in [Phone Setup](PHONE-SETUP.md).

## Measurements and verification

On this PC, the previous single-file EXE took 36.8 seconds to finish a smoke-test launch; the portable EXE took 4.5 seconds (about eight times faster in this check). Source runtime import and initialization took about 1.5 seconds. A warm `qwen3:8b` greeting comparison at the existing 8,192-token context produced first text in 1.65 seconds using the previous prompt, versus 0.48 seconds using the lighter prompt; request size fell from 7,415 to 849 bytes. This measured model text generation without speech playback or actions, and is not a universal latency guarantee.

176 regression tests and the portable-package test passed. The production frontend build passed. The packaged UI fixture passed, including an interruption followed by execution of the replacement command. Package tests ensure the ZIP includes its support files and omits unrelated private calling configuration.
