# Bob 0.10.18 — Open services on the web

## Changes from 0.10.17

- Open supported services in the browser when their app is not installed. The catalog includes YouTube, YouTube Music, Spotify, Netflix, WhatsApp, Telegram, Discord, Gmail, Outlook, Instagram, Facebook, X/Twitter, Reddit, Amazon India, Prime Video, ChatGPT, Notion, Canva, Figma, Google Docs/Drive/Maps/Calendar, Teams, Zoom and Slack.
- Recognize wording such as “YouTube app”, “you tube”, “YouTube website”, “website for Spotify” and “in the browser”. Explicit addresses such as `youtube.com` work without saying HTTPS.
- Prefer an installed app for services such as Spotify. “Open Spotify website” explicitly selects the web version. YouTube, Google and GitHub retain their existing website behavior.
- Optional Edge window discovery no longer blocks browser launch when discovery fails. If starting Edge raises a launch error, Bob asks Windows to use the default browser instead.
- After a verified website launch, “open it again” refers to that website rather than an earlier desktop app.
- Unknown brands do not become invented `.com` addresses or automatic searches for private local paths. Bob asks for the website address or an explicit search request.
- Existing voice profiles, settings and phone setup are retained.

## Install and test

1. Quit old Bob from the tray. Run `dist/release-0.10.18/Bob/Bob.exe` directly. Keep `_internal` beside it. No ZIP is required.
2. Say “Hey Bob”, wait for Listening, then “Open YouTube”. A browser window should open. Also try “Open the YouTube app” or type the request to distinguish speech recognition from launching.
3. Say “Open Spotify” or “Open WhatsApp”. If the app is installed, Bob opens it; otherwise the supported web version opens. Some services require you to sign in.
4. Say “Open Spotify website” to use the web version even with Spotify installed.
5. Say “Open youtube.com” or “Open github.com”.
6. After a verified website launch, say “Open it again”.
7. For an unknown service, give its full website address or say “Search for [name] official website”. Bob should not guess an address.

Bob reports “Opened” only when it can observe the requested address in Edge. If it says “Asked Windows/Edge”, the launch request was sent but the page was not verified. Web services do not turn desktop-only applications into web apps, and opening a page does not sign you in or bypass a subscription.

206 regression tests and the production frontend build passed. A live launch opened YouTube in Edge and verified its visible address on this PC.
