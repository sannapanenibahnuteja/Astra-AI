# Bob 0.10.26 — personal routines and on-demand screen context

Changes from 0.10.25:
- Native X quits rather than hiding. Independent cleanup handles a service failure and stops voice, phone, reminders and daily routines.
- Automation builder: named, editable multi-step routines; manual chat/voice execution (“run my routine Focus time”) and bounded daily schedules; durable status, pause and deletion.
- Optional personal setup: four questions, skip/back/review/save, scoped memory and personalized startup greeting.
- Screen awareness opt-in: read accessibility labels from the app focused before Bob, retain fresh context, and confirm clicks against exact labels and window handles. No continuous desktop capture or screenshot vision.
- General UI activation replies now describe dispatch honestly instead of claiming the task completed.
- Animated state feedback and button motion remain; the new setup and routine interfaces use the same black theme.

See the complete user manual’s **New in 0.10.26** section for examples and tests. Daily routines require Bob running and idle; closing Bob stops remote access and reminders.
