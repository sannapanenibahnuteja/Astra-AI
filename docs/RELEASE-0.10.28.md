# Bob 0.10.28 — semantic voice commands and faster completed tasks

Changes from 0.10.27:
- Ordinary spoken tasks go to local Ollama before phrase parsing. Spoken corrections are preserved for the model, and recent executed actions join conversation/task context.
- Structured JSON voice intent plans avoid empty native tool-call responses observed with the installed qwen3:8b model. Clear informational conversation retains sentence streaming.
- Meaning maps to the existing validated actions, with up to twelve steps and eight planning rounds. No arbitrary shell execution or new unlimited app access.
- Tab pronouns from model plans reuse the stored tab selection; missing selection asks a specific question. Confirmation freezes the selection before closing.
- Final-step metadata skips a redundant model round after successful execution, including after approval. Independent known actions can be batched; failed actions stop the plan.
- Spoken generation is bounded to 512 output tokens with thinking disabled. No new billing service or model download.

Start Ollama, use your installed model, and test the examples under New in 0.10.28 in the user manual. Exact wake/stop/approval controls, explicit conversation preferences and saved routines retain immediate handling. Text keeps its existing fast path. Instant response cannot be guaranteed; latency includes transcription, model load/inference, actual Windows work and speech output.
