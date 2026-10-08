# Conversation capability status - Bob 0.10.14

“Model-dependent” means the selected Ollama model attempts the behavior; it is not a deterministic guarantee. This desktop executable has fewer integrations than the proposed assistant feature list.

| # | Requested capability | Current status |
|---|---|---|
| 1 | Interruptibility | Existing echo-cancelled desktop barge-in, extended to streamed speech and queued sentences. |
| 2 | Turn-taking awareness | Added adjustable silence endpoints; cannot know whether you are thinking. |
| 3 | Context carryover | Scoped tabs/files/windows and successful action history. Added recent numeric corrections. General references are model-dependent. |
| 4 | Topic continuity | Saved conversations can be reopened. Prompt uses bounded recent history, not unlimited recall or semantic archive search. |
| 5 | Clarification intelligence | Focused pending-value questions added; other clarification quality is model-dependent. |
| 6 | Implicit intent | Can discuss inferred needs. No connected calendar, traffic, contacts or automatic location service for these scenarios. Suggestions are not authorization to act. |
| 7 | Corrections without restart | Added pending day/time and percentage corrections, plus recent successful numeric setters and explicit in-sentence replacements. General intent editing remains partial. |
| 8 | Multiple intents | Existing bounded Windows workflows, up to 12 actions. Sending texts or moving calendar events is not integrated. |
| 9 | Reference resolution | Scoped tab/file/window references and recent history. No contact relationship directory or universal entity resolver. |
| 10 | Conversational memory | Explicit local saved facts, preferences and conversations, with Memory controls. No automatic inference of all routines/relationships. |
| 11 | Adaptive verbosity | Added Fast/Tutor/Calm/Balanced modes and “Shorter” / “Just the answer”. |
| 12 | Tone matching | Persistent personalities, modes and prompt guidance. No driving sensors or automatic workplace detection. |
| 13 | Personality consistency | Existing persisted presets and adjustable traits; wording consistency still depends on the model. |
| 14 | Multilingual conversation | Text depends on the chosen Ollama model. Bundled speech recognition is English-only; multilingual/code-switching voice is not implemented. |
| 15 | Speech repair | Added explicit replacement-action repair, longer thinking pauses, existing noise filtering. Arbitrary fragments and self-corrections are not universally resolved. |
| 16 | Pronunciation learning | Added editable name/term hints. No automatic acoustic pronunciation training. |
| 17 | Emotional context | Prompt guidance responds to urgency/frustration expressed in words. No vocal emotion detector or mind-reading claims. |
| 18 | Backchanneling | Not implemented; Bob does not insert listening acknowledgements. |
| 19 | Streaming answers | Added sentence speech for explanatory replies and verified action results. Other model replies may wait until complete. No token-level audio generation. |
| 20 | Mid-response adaptation | Added interrupt-and-rephrase cues using conversation history, with action replay disabled. |
| 21 | Shared visual conversation | Screenshot/photo attachment and vision-model chat are not implemented in this desktop UI. Existing accessibility inspection reads exposed controls. |
| 22 | Conversational confirmation | Existing confirmation replies; corrected pending actions require fresh approval. |
| 23 | Progressive trust | Not implemented. Confirmation rules remain explicit; repeated approvals do not silently grant broader permissions. |
| 24 | Proactive entry | Existing due reminders. No calendar-change, traffic, notification or deadline monitoring integrations. |
| 25 | Graceful uncertainty | Existing verified-action errors, ambiguity handling and uncertain-transcript review. Model factual uncertainty remains model-dependent. |
| 26 | Conversation summaries | Can summarize recent available context. No automatic rolling long-conversation summary or complete archive retrieval. |
| 27 | Multiple speakers | Optional single enrolled voice matching exists. Multi-speaker diarization, profiles and room permissions are not implemented. |
| 28 | Conversation modes | Added Balanced, Fast, Tutor and Calm. Deep-thinking, meeting, driving and bedtime integrations are not implemented. |

New controls are in **Settings → Voice & personality**. See [the release test guide](RELEASE-0.10.14.md) for concrete examples. Voice identity matching is approximate, not authentication. All actions remain limited to the implementations and connected services Bob actually has.
