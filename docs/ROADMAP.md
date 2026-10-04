# Bob Product Roadmap

Bob is evolving from a local Windows assistant into a personal AI operating layer:
conversation, memory, screen understanding, private knowledge search and trusted
actions across devices.

This roadmap is intentionally honest. Some features can be built inside the
current Windows EXE. Others need external services, a native mobile app, cloud
connectors, home automation hubs or regulated-data integrations.

## Current Foundation

The Windows EXE already has the pieces needed for the next stage:

- Local Ollama chat with conversation context.
- Offline Whisper voice transcription and spoken replies.
- Wake-word standby on Windows.
- Explicit memory with user-visible controls.
- Windows app launching, window control, media control, device settings, files,
  Edge automation, reminders and optional Twilio reminder calls.
- Private phone webpage through Tailscale for awake phone voice/chat control.
- A dark futuristic desktop UI and portable Windows release packaging.

## Phase 1: Natural Assistant Core

Goal: make Bob feel less like a command parser and more like a capable assistant.

- Natural conversation for voice and text, including follow-up questions,
  corrections, vague references and casual phrasing.
- Broader multilingual input. English remains the first production target; other
  languages need model and speech-recognition validation.
- Interruption support while Bob is speaking.
- Better "do the same thing as last time" context across windows, files, browser
  tabs, reminders and settings.
- A visible action timeline showing what Bob understood, what it did, and what
  it needs from the user.
- Confirmation only for destructive, privacy-sensitive or externally visible
  actions.

## Phase 2: Personal Memory And Preferences

Goal: let Bob remember useful facts without becoming creepy or opaque.

- Memory categories: preferences, routines, favorite places, important people,
  communication style, recurring tasks and active projects.
- User controls for view, edit, delete, export and pause memory.
- Memory confidence and source metadata: "you told me this", "seen in calendar",
  "inferred from repeated behavior".
- Temporary memory for the current task and durable memory for long-term facts.
- Privacy controls for sensitive categories such as health, finance and family.

## Phase 3: Screen And Document Awareness

Goal: Bob can answer questions about what the user is looking at.

- Screenshot ingestion from the PC with user approval.
- "What does this error mean?", "summarize this page", "read this dialog", and
  "what should I click next?" workflows.
- Document intake for PDFs, images, screenshots, DOCX, TXT, Markdown and CSV.
- OCR and layout-aware extraction.
- Local-first indexing for selected folders.
- Clear boundaries: Bob should never inspect private screens or folders unless
  the user grants access.

## Phase 4: Personal Knowledge Search

Goal: search the user's own digital life with source links and permissions.

- Local files, notes and project folders.
- Email, calendar and cloud storage connectors.
- Photos and screenshots with OCR and image labels.
- Messages and notifications where platform APIs allow it.
- Source-grounded answers with citations, timestamps and quick open buttons.
- Connector permission controls per account and per data type.

## Phase 5: Agent Mode And Cross-App Workflows

Goal: Bob can complete multi-step tasks instead of waiting for every step.

- Task plans with visible steps, progress and cancellation.
- Cross-app workflows such as: "Find the address in that email, add the meeting
  to my calendar, and tell me when to leave."
- Browser and Edge workflows with page inspection before clicking/filling forms.
- Document creation and editing.
- File organization and cleanup.
- Smart error recovery: retry, ask one clarifying question or safely stop.
- Audit log for actions Bob performed.

## Phase 6: Proactive Assistance

Goal: Bob helps at the right time without becoming annoying.

- Daily briefing: calendar, tasks, weather, important messages, deliveries and
  unusual items.
- Deadline, bill, battery, traffic and schedule-conflict warnings.
- Notification digesting and importance filtering.
- Quiet hours and "do not interrupt me unless..." rules.
- User-tunable proactivity levels.
- Explanations for why Bob surfaced something.

## Phase 7: Real-Time Voice And Mobile Companion

Goal: low-latency conversation across PC and phone.

- Real-time voice mode with barge-in interruption.
- Native mobile companion app for reliable microphone, notifications and device
  integrations. The current mobile webpage cannot provide locked-screen wake-word
  listening on iPhone.
- Phone call reminders through Twilio or another calling provider.
- Push notifications for reminders and proactive alerts.
- Secure remote PC control through Tailscale or equivalent private networking.
- Optional hands-free modes where the operating system permits them.

## Phase 8: Multimodal And Camera Assistant

Goal: Bob understands images and live camera context.

- Photos, screenshots and documents as chat attachments.
- Camera assistant for products, appliances, food, signs, plants, documents and
  error screens.
- Location and sensor context where the user grants permission.
- Wearable signals as optional integrations, not always-on surveillance.
- Visual answers that cite what Bob saw and what it inferred.

## Phase 9: Home, Travel, Shopping, Finance, Health And Learning

Goal: domain modules that feel useful but stay permissioned and safe.

- Home automation through Home Assistant, Matter, smart speakers or vendor APIs.
- Travel planning: itineraries, reservations, packing reminders, translation and
  flight monitoring.
- Shopping support: product comparison, price tracking, lists and returns.
- Finance summaries: spending, bills, subscriptions and unusual transactions,
  with confirmation for any financial action.
- Health and wellness: sleep, activity, medication and appointment tracking with
  strict privacy controls.
- Tutor mode: explanations, quizzes, homework help and progress tracking.
- Creative mode: writing, images, presentations, photo edits and video planning.

## Phase 10: Profiles, Permissions And Emergency Support

Goal: make Bob safe for households and sensitive situations.

- Family profiles for children, teens, adults, guests and elderly users.
- Per-profile permissions, content limits and action approvals.
- Emergency contact surfacing and quick assistance flows.
- Emergency detection only through explicit user-approved integrations.
- Local and cloud permission dashboards.
- Exportable audit logs for sensitive actions.

## Capability Matrix

| Capability | Current Status | Needed Next |
| --- | --- | --- |
| Natural conversation | Partial | better interruption, multilingual speech, stronger reference memory |
| Personal memory | Partial | categories, controls, source/confidence metadata |
| Multimodal input | Not built | attachment pipeline, OCR, vision model support |
| Screen awareness | Not built | screenshot capture, vision analysis, permission UI |
| Personal knowledge search | Partial local project search | indexes and account connectors |
| Action-taking | Partial Windows actions | email/calendar/messages/forms with approvals |
| Proactive assistance | Partial reminders | scheduler, priority rules, daily briefing |
| Cross-app workflows | Partial | durable agent plans and connector actions |
| Real-time voice | Partial | low-latency audio loop and barge-in |
| Camera assistant | Not built | native mobile app or webcam/camera pipeline |
| Home automation | Not built | Home Assistant/Matter/provider integrations |
| Device control | Partial Windows | phone controls require native mobile app |
| Travel/shopping/finance/health | Not built | account integrations and domain-specific safety |
| Learning/creative modes | Partial chat only | structured modes, files, image/document tools |
| Family profiles | Not built | identity, permissions and policy layer |
| Emergency features | Not built | explicit integrations and safe escalation flows |

## Build Order

The practical build order is:

1. Improve context, action history and natural follow-ups.
2. Add a permissioned screen/document intake pipeline.
3. Upgrade memory into user-controlled categories.
4. Add local knowledge indexing.
5. Add connector architecture for email, calendar, files and cloud accounts.
6. Add agent-mode planning and audit logs.
7. Build native mobile companion apps for locked-phone notifications and richer
   remote control.
8. Add domain modules such as home, travel, shopping, finance, health and tutor.

This keeps Bob useful immediately while avoiding fake claims about platform
features that require mobile apps, paid providers or external account access.
