# Bob 0.10.8 — Website launch and spoken replies

- Website requests launch Edge directly, choosing a running Edge variant when
  possible. Explicit new-window launch avoids a background-only Edge instance.
  A visible matching address is required before reporting “Opened.”
  An unverified launch reports “Asked Edge” instead of claiming success.
- “Actually stop listening and open YouTube” ends command capture and preserves
  “open YouTube” for execution. Stopping listening alone ends the conversation.
- With voice replies enabled, typed replies are spoken too. This avoids silent
  replies merely because the request arrived as text.
- “Close YouTube” targets a matching Edge tab and verifies its disappearance.
  Multiple matches require an exact title. App-window closure is also checked;
  a window remaining open or showing a save dialog is not reported as closed.

Testing:

1. Quit the old Bob from the tray and run the new EXE.
2. Enable voice replies in Settings and save. Type “What time is it?”; listen for
   the spoken answer.
3. Start a voice conversation. While Bob speaks, say “Actually stop listening and
   open YouTube.” Check that the microphone session ends and Edge opens YouTube.
4. Check the result: “Opened” requires the matching address to be observed. If Bob
   says he could not verify it, inspect the browser instead of assuming success.
5. Say “Close YouTube,” then confirm if asked. Check that only the selected
   matching tab closes. Bob reports failure if it remains visible.

Browser verification confirms the visible address, not successful page loading or
video playback. Wake-word standby remains enabled if your wake setting is on.

Live validation: an ordinary Edge tab-launch request failed to produce a visible
window on this PC. The explicit new-window launch opened YouTube with a verified
address. Closing that dedicated test tab was then verified. No account login or
media playback was performed.
