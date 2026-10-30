# Bob 0.11.14 — Safari phone pairing startup

- Safari storage/history failures no longer abort the phone page before its first connection request. A blocked storage browser can use the token in memory; the original URL fragment is retained when session persistence fails.
- Missing/expired pairing tokens show an explicit pairing message and a password-style complete-link input instead of remaining on Connecting. Pasted links must belong to this page's origin. Authentication, host/origin checks and private HTTPS requirements remain.
- Reconnect is visible. A state request has a 12-second deadline even if AbortController is unavailable; malformed gateway responses report a proxy/configuration error. Failed/unpaired pages disable Send/Voice until connected.
- Unpair/storage failures are handled safely. Browser storage is optional, not a requirement to control Bob from an already paired tab.

## Use the fix

1. Quit the older Bob, then launch `dist/release-0.11.14/Bob/Bob.exe`. Keep `_internal` beside it. Saved phone pairing is restored; no need to recreate provider credentials.
2. Close the old phone tab. In Bob Settings, copy/open the COMPLETE private pairing link in Safari, including its `#` part. Keep Tailscale on both devices and the PC awake.
3. Look for **Connected · Ready**. If the page says the link is incomplete, paste the full link into the pairing field. Tap Reconnect for a failed network request.
4. Send a harmless text request first, such as “What time is it?” Then test phone voice after Safari microphone/audio permission is granted.

The running gateway and saved token were checked locally and through its configured private HTTPS endpoint; both returned authenticated state successfully. Tokens/URLs/private responses were not printed or changed. Safari-specific checks use simulated browser storage/history/network conditions; a real iPhone acceptance test is still needed. No carrier call or microphone recording was made.
