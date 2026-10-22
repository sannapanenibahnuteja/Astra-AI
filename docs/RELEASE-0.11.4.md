# Bob 0.11.4 — your space, your Bob

A simpler black canvas puts the conversation and existing voice-reactive spinning particle orb first. Assistant details and starter cards are optional. The top toolbar always keeps navigation, appearance and details controls available. No voice, identity, memory, phone or action safeguards are removed.

## Make it yours

Click the palette icon → **Customize appearance**. Changes save immediately on this PC; no separate Save is needed. All settings are also available by voice or text. Add **Hey Bob** before voice requests. These are supported component preferences, not arbitrary generated code or pixel-level control of every native Windows element.

| Part | Example request | Choices |
|---|---|---|
| Accent | Make the accent mint | violet, mint, blue, rose, amber, ice; purple/pink/green aliases |
| Background | Set the background graphite | black, graphite, midnight |
| Sidebar surface | Set the sidebar color midnight | default, black, graphite, midnight |
| Message box surface | Set the composer color black | default, black, graphite, midnight |
| Navigation | Make the sidebar compact | expanded, compact, hidden; show/hide sidebar |
| Details | Show details / hide details | on/off |
| Suggestions | Show suggestions | on/off |
| Status labels | Hide status labels | on/off; Stop controls remain available |
| Text | Make the text bigger | small, medium, large, extra large; chat and message-box text |
| Typeface | Set the font mono | system, rounded, mono (installed-font fallbacks apply) |
| Spacing | Set the spacing roomy | compact, comfortable, roomy |
| Corners | Make the corners square | round, soft, square |
| Messages | Set the messages bubbles | plain, bubbles |
| Message box | Make the composer compact | compact, comfortable |
| Width | Set the chat width wide | focused, wide |
| Orb size | Make the orb larger | small, medium, large; scales down on small screens |
| Orb colors | Make the orb purple | multicolor or accent; named accent sets its color |
| Orb motion | Set the orb speed lively | calm, balanced, lively |
| Orb visibility | Hide the orb / show the orb | default remains visible |
| Interaction motion | Make the animations playful | off, subtle, playful; turn off animations |
| Presets | Use focus layout | focus, studio, playful |
| Reset | Reset appearance | restores appearance only |

Try “make the accent mint and hide details.” Explicit supported UI changes take the local path without waiting for Ollama. More unusual UI-only wording uses a compact, schema-constrained local-model request. Mixed UI/app workflows retain the general validated agent. Follow-up corrections include recent appearance context. A live qwen3:8b isolated test completed one unusual appearance request in 4.14 seconds; this is a single observed run, not an instant-response guarantee. Unsupported/ambiguous values must be clarified rather than inventing CSS. Code and quoted dictation are not appearance instructions. Hidden navigation can always be restored using the toolbar. Reduced-motion OS preferences override animations; minimized/offscreen orbs stop rendering.

## Opening installed apps

Discovery now combines Start Menu shortcuts, Windows per-user/machine App Paths and registered executable icons, plus a bounded on-demand scan of standard Program Files and LocalAppData Programs folders. Results are cached to avoid repeated background work. Known installed-app launches, including clear unique typos such as “open calculatr,” bypass an unnecessary model round trip. Compound/unclear requests continue through the existing contextual planner. Newly installed/unusual portable apps may require a full local EXE path. Bob does not scan every drive or guarantee discovery of every hidden/custom installation.

Try “Hey Bob, open calculator”, “Hey Bob, launch visual studio code”, or “open C:\Tools\MyApp.exe” using an actual existing EXE. Executables launch as a single path, without interpreting shell arguments. Launching a process is not reported as verified success until an app window is observed. Apps requiring administrator rights still use Windows permissions. Ambiguous app names may need clarification; consequential actions retain their existing safeguards.

## Speed and context

Bob keeps the current Whisper/speaker neural models and Ollama agent. This release optimizes routing and supplies UI schema/context to the local planner; it does not retrain weights or create an unrestricted neural model. Supported tools, observed results, profile memory, pending intents and task context remain the basis for multi-step work. Unsupported tasks should receive an honest limit and useful next step. Existing streaming answers, validated tool results and no automatic failed-action replay remain. Zero errors, arbitrary tasks and instant model inference cannot be guaranteed.

## Quick acceptance test

1. Close old Bob; launch `dist/release-0.11.4/Bob/Bob.exe`, keeping `_internal` beside it.
2. Open the palette panel. Change each desired field, close/reopen it, then restart Bob: saved choices should remain. Use Reset appearance to undo.
3. Say the table examples with Hey Bob. Check only the named component changes. Test two independent changes together.
4. Hide the sidebar, then restore it with the top-left toolbar toggle. Hide/show details; all main navigation pages remain reachable.
5. Ask a question: the orb reacts and messages animate. Set motion off, then restore playful; also verify Windows reduced-motion behavior.
6. Open an installed app by name, then a clear misspelling. Verify its real window. Try a nonexistent app: Bob must not claim it opened.
7. Give a compound request or uncommon phrasing: Ollama must use supported validated tools or give a specific limit. No invented execution.
8. Re-test voice wake words, saved-voice interruption and a long spoken answer using the existing audio guide.

[Verification evidence](TEST-REPORT-0.11.4.md). Automated UI/agent fixtures simulate integrations; live microphone and arbitrary installed applications still need acceptance checks on your machine. Existing personal data is preserved; appearance is shared on this Windows installation, not tied to a speaker profile.
