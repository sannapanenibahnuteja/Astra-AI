# Bob 0.10 — private phone conversation and PC control

Bob offers a private phone webpage and separate, optional carrier reminder calls. Your phone and PC communicate through Tailscale's encrypted device connection and HTTPS. The PC runs Whisper speech recognition, local Ollama reasoning and offline Windows speech for phone replies. The private voice path does not use browser cloud recognition, Twilio or Azure speech.

## Setup

1. Quit older Bob instances from the tray. Extract the 0.10 ZIP and launch Bob.exe. Start Ollama and select your installed model in Bob Settings. Direct actions work without Ollama; open-ended conversation requires it.
2. Install [Tailscale](https://tailscale.com/download) on your Windows PC and phone. Sign both into the same private Tailscale network and connect them. Only grant access to your own trusted devices.
3. In Windows PowerShell, run:

   ```powershell
   tailscale serve --bg http://127.0.0.1:8787
   ```

   Follow Tailscale's HTTPS enablement link if it presents one. Copy the `https://your-pc.your-tailnet.ts.net` address it prints. Use Serve, not Funnel: this should be private to your network, not published to the internet. No router port forwarding is needed.
4. In **Bob → Settings → Phone & reminders**, paste that HTTPS address and click **Enable mobile access**.
5. Open the generated private pairing link on your phone with Tailscale connected. The part after `#` is a secret access token; do not share or post it. The phone page removes it from the address bar and keeps it for that browser-tab session. Select **Remember this phone** only on your own phone to retain pairing when reopening the browser.
6. End any active desktop voice conversation by saying “stop listening”. On the phone, tap **Start private voice conversation** and allow microphone access. Keep the page open and the phone awake.
7. Speak, pause, and wait for Bob's reply. The phone records up to 20 seconds per turn. Audio is transcribed on your PC. After a reply it listens again. Low-confidence transcripts stay in the box for you to check and send. If your phone blocks autoplay, press Play in the audio player, then restart voice mode when ready.
8. Say “stop listening” or tap **Stop** to end the phone voice session. **Disable & revoke links** in desktop Settings stops remote access. A new pairing link invalidates the old one. Pairing is encrypted for your Windows account and restored when Bob restarts.

The PC must be awake, signed in, connected to the internet and running Bob. Windows controls operate in that signed-in desktop; they cannot bypass the lock screen or administrator prompts. The mobile page is a voice/chat remote, not a streamed desktop display.

## Try it

- “Could you open calculator for me?”
- “Set the volume to thirty percent.”
- “In Edge, open another tab and search for Python tutorials.”
- “Make this easier to read in Edge.”
- “Remind me in ten minutes to take a break.”
- “Call me in two minutes to check the oven.”
- “Show my reminders.”
- “Cancel reminder” followed by the displayed eight-character reminder ID.

“Remind me” creates a desktop notification and spoken reminder. “Remind me on my phone” creates a **private phone-page alert**. “Call me” schedules a separate paid carrier call after confirmation and account setup below. Phone alerts appear and speak while the paired page is open with audio enabled. They do not ring through the phone's dialer, wake a locked phone, or work with the browser closed. Missed alerts remain in the reminder list. Reminders survive Bob restarts, but delivery needs Bob running; local reminders may be delayed until its voice engine is free.

## Privacy and voice

- Private phone audio goes only to your PC through the authenticated gateway. Audio uploads are bounded and decoded in memory; generated reply WAV files use a temporary folder removed after transfer. Chat transcripts remain in Bob's normal local history.
- Phone replies use offline Windows speech, regardless of the optional Azure setting for desktop speech. Voice quality depends on the installed Windows speech engine. This is turn-taking conversation, not simultaneous speaking and interruption.
- The separate optional neural desktop voice sends desktop reply text to Azure only after you explicitly configure and enable it. Leave it disabled for fully local speech.
- A paired phone can request the same supported actions as the desktop. Existing confirmations still apply. The app binds only to `127.0.0.1`, validates host/origin, and requires its pairing token for APIs.
- Carrier calls send reminder text and phone numbers to Twilio. They are not end-to-end encrypted and are separate from the private webpage.

Tailscale documents its [device encryption](https://tailscale.com/docs/concepts/tailscale-encryption) and [private HTTPS Serve setup](https://tailscale.com/docs/features/tailscale-serve). Encryption protects transit; it does not protect an unlocked phone or PC from someone using it.

## Troubleshooting

- **Cannot connect:** confirm Bob mobile access is enabled, both devices are connected to Tailscale, the PC is awake, and `tailscale serve status` shows port 8787. Use the HTTPS URL, not localhost on the phone.
- **Pair again:** old links are invalid after disabling access, creating another link.
- **Microphone unavailable:** allow browser microphone permission and open the HTTPS page in a current mobile browser. Typed messages remain available.
- **Bob is busy:** end desktop voice mode and wait for its current response. Desktop and phone share one command engine.
- **Ollama offline:** start Ollama on the PC and refresh Bob's connection. Speech recognition and direct commands still run locally.
- **Edge not found:** open Edge on the PC first. With multiple Edge windows, focus the intended one before waking Bob, or specify its exact title. Accessibility limitations still apply.

Validation covers unit tests, a disposable native Edge fixture, local HTTP authentication checks, and local WAV synthesis/transcription. Your phone/Tailscale network must still be paired and tested; a real external phone connection cannot be verified before your account setup.

## Phone-number reminders (including a locked phone)

1. Create a [Twilio account](https://www.twilio.com/docs/voice/api/call-resource), get a voice-capable Twilio number, and enable calls to your destination country. Trial accounts require a verified destination and have restrictions; provider charges apply.
2. In Bob, open **Settings → Phone & reminders → Create calling configuration**, then open the data folder.
3. Edit `phone-calls.json` in that folder. Set `enabled` to `true`; fill in `account_sid`, `auth_token`, `from_number` (your Twilio number), and `to_number` (your own phone). Numbers must include `+` and the country code. Save the file. Keep credentials private; never commit this file.
4. Leave Bob running and the PC awake with internet access. Say **“Call me in two minutes to check the oven.”** Review the reminder and confirm it. No public webhook or Tailscale connection on the phone is needed for these calls.
5. Answer the incoming call to hear Bob's reminder. The call can ring while the phone is locked, subject to reception, phone settings and Do Not Disturb. Check Twilio call logs if it fails.

These calls speak a reminder and end; they do not listen to replies or provide two-way PC control. Use the private webpage while the phone is awake for conversation and PC actions. A browser cannot promise continuous microphone use while the phone is locked. Bob does not provide background push notifications.

**Call submitted** means the provider accepted the request, not that you answered. Bob makes one attempt, does not automatically redial, and marks calls more than five minutes overdue as failed rather than ringing unexpectedly after a long shutdown. Reminder text uses Twilio's [neural Say voice](https://www.twilio.com/docs/voice/twiml/say); desktop personality settings do not change that voice.
