# Bob 0.11.16 — smoother voice turns and conversation continuity

Quit older Bob from its tray menu, then launch `dist/release-0.11.16/Bob/Bob.exe`. Keep `_internal` beside it. This is a directly launchable Windows build. Existing chat history, memories, voice profiles and settings are reused.

- Conversation context now survives a restart. Reopen the same chat to carry forward its topic, numbered options and relevant follow-ups. A new topic clears old choices. Deleting the chat also deletes this saved context. Matching a saved voice continues to select that profile's chat and saved facts.
- Spoken explanations that clearly do not require an action use a compact model prompt and stream complete sentences without sending the Windows tool list. Unclear requests and multi-step actions still use the validated planner. Saved context cannot replay an old approval.
- Plain spoken volume percentages and explicitly numbered brightness controls now take the local path. They still check the Windows device result. The spoken percentage and monitor number remain separate.
- The duplex microphone path now hands resampled float audio directly to Whisper, avoiding a WAV encode/decode and duplicate amplification. The final decoder uses the actual turn's room mode. Speaker verification, echo cancellation and interruption checks are preserved.
- Unchanged text no longer redraws the chat on every poll. Spoken playback is no longer held up by refreshing the sidebar, and a streamed profile greeting no longer causes the answer to be spoken twice. Bob can also save an explicitly stated preference such as “I prefer short replies” as a communication style in a recognized profile when conversation memory is enabled.

## Try it

1. **Natural question:** “Hey Bob, explain why we see rainbows.” Listen for a short answer that starts as complete sentences become available.
2. **Continue after reopening:** “Hey Bob, suggest two numbered places for a quiet afternoon.” Quit and launch Bob again, open that chat, and say “Hey Bob, tell me more about the second one.” For the exact numbered choice, say “Hey Bob, the second one.”
3. **Correct a request:** “Hey Bob, no, I meant Friday.” Use this after discussing a different day. The latest correction should guide the next reply.
4. **Common control:** “Hey Bob, could you set the volume to twenty percent?” Check the Windows volume indicator.
5. **Two monitors:** “Hey Bob, list monitors,” then “Hey Bob, set brightness on monitor two to forty percent.” Check that display; support still depends on the monitor and its driver.
6. **Preference:** With your saved voice selected, “Hey Bob, I prefer short replies.” Check the profile's Memory view and ask another question.
7. **Noise and interruption:** In a voice session, ask for a story. Tap the table during playback; then say “Hey Bob, please stop talking.” Test on the microphone and speakers you normally use.

The compact chat context is stored locally with the conversation. Explicit profile facts remain editable in Memory. No microphone recordings are saved by this feature, and it does not retrain model weights. Latency depends on the installed speech and chat models, hardware and room acoustics. Automated and generated-audio checks do not establish live microphone accuracy or perceived naturalness.
