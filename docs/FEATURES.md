# Bob Feature Matrix

This document tracks Bob's current abilities and the product vision for the
industrial personal assistant described in the roadmap.

## Available In The Current Windows EXE

### Conversation And Voice

- Local Ollama chat with streaming replies.
- Conversation history and recent context.
- Offline Whisper English transcription.
- Wake-word standby on Windows.
- Spoken replies with configurable rate.
- Startup greeting.
- Personality presets.
- Low-confidence speech review.
- Successful action history for natural repeats such as "do that again" and
  "same as last time."

### Memory

- Explicit saved facts.
- Memory screen for viewing, adding and deleting facts.
- Conversation context for follow-up commands.

### Windows Control

- Open apps and folders.
- Control system volume and mute state.
- Read system status.
- Control supported brightness displays.
- List, switch, move, minimize, maximize, restore and close windows.
- Move windows between monitors.
- Inspect accessible controls and click visible controls.
- Type literal text into supported editors such as Notepad.
- Use common keyboard shortcuts with confirmation where needed.

### Devices And Settings

- Bluetooth and Wi-Fi radio control.
- Saved Wi-Fi listing and connection.
- Airplane mode and energy saver through Windows Settings.
- Open many Windows Settings pages.
- Inspect and change accessible settings controls.

### Files

- List folders.
- Find files by name.
- Open files.
- Create folders.
- Copy, move, rename and recycle selected files with confirmation.
- Use File Explorer selection.

### Browser And Edge

- Open websites and searches.
- Edge tab listing and tab selection.
- Page inspection where accessibility exposes labels.
- Fill named fields.
- Click named controls with confirmation.
- Browser shortcuts such as back, reload, zoom, scroll, downloads and history.

### Media

- Play, pause, resume, stop, next and previous for Windows media sessions.
- Seek forward/back or to a timestamp when supported.
- Playback speed, shuffle and repeat where exposed by the player.
- Now-playing status.
- Open local media files.
- Search YouTube or Spotify without claiming autoplay.

### Reminders And Phone Access

- Local reminders.
- Private phone-page reminders.
- Optional Twilio carrier call reminders.
- Private mobile web access through Tailscale while the phone page is open.
- Mobile pairing persistence.

### Packaging And Privacy

- Portable Windows EXE.
- Local data under `%LOCALAPPDATA%\Bob`.
- Local-first speech recognition.
- No bundled cloud analytics.
- Ollama stays on the configured local loopback service.

## Requested Capability Targets

### 1. Natural Conversation

Target: voice and text conversation with interruptions, follow-up questions,
casual language, multilingual support and vague commands such as "do the same
thing as last time."

Status: partial. Follow-ups, casual phrasing and repeat requests work for
supported actions, but multilingual voice and true speech barge-in still need
work.

### 2. Personal Memory

Target: preferences, routines, favorite places, recurring tasks, important people,
communication style and projects with clear user controls.

Status: partial. Explicit facts exist; categorized memory and source controls are
next.

### 3. Multimodal Input

Target: voice, text, photos, screenshots, documents, camera input, location,
sensors and wearable signals.

Status: voice/text only in the desktop app. Screenshots, files, camera and device
signals need new pipelines and permissions.

### 4. Screen Awareness

Target: understand the current phone/computer screen and answer questions about
errors, pages and visible content.

Status: not built. Needs screenshot capture, OCR/vision analysis and a permission
surface.

### 5. Personal Knowledge Search

Target: search across emails, documents, notes, photos, messages, calendar and
cloud storage.

Status: partial local project search only. Needs account connectors and indexing.

### 6. Action-Taking

Target: send emails/messages, create calendar events, set reminders, order food,
book reservations, fill forms, create documents, manage files and control apps.

Status: partial. Windows, files, reminders, Edge and media are supported. External
apps and payments need connectors and confirmations.

### 7. Proactive Assistance

Target: warnings for deadlines, traffic, weather, battery, bills, conflicts and
forgotten routines.

Status: partial reminders only. Needs scheduler, connectors and notification
priority rules.

### 8. Daily Briefing

Target: calendar, messages, weather, tasks, deliveries, news and unusual items.

Status: not built. Needs calendar/email/task/weather connectors.

### 9. Cross-App Workflows

Target: chain work across email, calendar, maps, browser, documents and messages.

Status: partial for local Windows workflows. Needs durable agent plans and
external connectors.

### 10. Agent Mode

Target: Bob completes multi-step tasks with progress, recovery and cancellation.

Status: partial. Bob can run bounded multi-step commands; long-running autonomous
tasks need a task engine and audit log.

### 11. Smart Notifications

Target: summarize notification clutter and surface only important items.

Status: not built. Needs notification access and user priority rules.

### 12. Real-Time Voice Mode

Target: low-latency conversation with interruption while actions run.

Status: partial. Voice works, but true low-latency streaming and barge-in need a
new audio loop.

### 13. Camera Assistant

Target: ask questions about products, plants, appliances, documents, food, signs
and physical objects.

Status: not built. Needs camera input and vision model support.

### 14. Home Automation

Target: lights, AC, TVs, cameras, appliances, speakers and routines.

Status: not built. Needs Home Assistant, Matter or vendor integrations.

### 15. Device Control

Target: settings, apps, media, files, Bluetooth and common PC/phone operations.

Status: partial on Windows. Phone control needs a native mobile app and platform
permissions.

### 16. Travel Assistant

Target: itineraries, flights, reservations, navigation, translation, packing and
recommendations.

Status: not built. Needs connectors and web services.

### 17. Shopping Assistant

Target: compare products, track prices, manage lists and help with returns.

Status: not built. Needs shopping/search integrations.

### 18. Finance Assistant

Target: spending, bills, subscriptions, budgets and unusual transactions, with
confirmation for sensitive actions.

Status: not built. Needs secure finance connectors and strict permission design.

### 19. Health And Wellness

Target: sleep, activity, nutrition, medication, appointments and wearable data.

Status: not built. Needs explicit health integrations and privacy controls.

### 20. Learning And Tutor Mode

Target: adaptive explanations, quizzes, homework help, screen explanation and
progress tracking.

Status: partial through chat. Needs structured learning memory and screen/file
awareness.

### 21. Creative Assistant

Target: write messages, edit photos, generate images, create presentations,
brainstorm and help make videos.

Status: partial through chat. Media generation/editing and presentation workflows
need additional integrations.

### 22. Family Profiles

Target: permissions and behavior for children, teens, adults, guests and elderly
users.

Status: not built. Needs identity, permissions and profile settings.

### 23. Emergency Features

Target: user-approved emergency integrations, contacts and quick access to help.

Status: not built. Needs careful design, explicit permission and local emergency
rules per region.
