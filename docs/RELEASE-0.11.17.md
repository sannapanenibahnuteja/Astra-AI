# Bob 0.11.17 — hands-free conversation

Quit the older Bob and launch `dist/release-0.11.17/Bob/Bob.exe`. Keep `_internal` beside the EXE.

1. Say “Hey Bob” and wait for Bob to show that it is listening.
2. Ask your question. After the reply, continue with “Can you say more about the second one?” or another request in the same chat.
3. Say “stop listening” when you finish. Bob also returns to wake-word standby after 20 seconds without an accepted request. If wake words are off, use the Voice button to start again.

Hands-free follow-ups are on by default. The **Voice** button starts a conversation and the microphone icon still starts a single request. Turn off **Hands-free follow-ups** in **Settings → Conversational audio** to return to wake phrases between turns. During playback, use “Hey Bob, please stop talking” with your saved voice enrolled and verified interruptions enabled. Speech recognition and the configured speaker checks still apply to follow-ups.

To test the flow, say “Hey Bob”, then “What time is it?” After the answer, say “Open Calculator” without a second wake phrase. Check that Calculator opens. Say “stop listening”, then start a new session and let it time out to check standby. Timing and recognition with a real microphone depend on the device and room.
