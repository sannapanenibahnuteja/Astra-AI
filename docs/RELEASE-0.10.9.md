# Bob 0.10.9 — Multi-step task execution

Changes from 0.10.8:

- Bob continues planning after ordinary actions, using each result to choose
  the next unfinished step. Previously continuation mostly followed inspections.
- Confirmation preserves the original goal and completed results. “Yes” approves
  the proposed step, then Bob resumes. Later consequential steps need approval.
- The desktop shows the current action or planning stage. Errors stop later steps.
- Duplicate actions, twelve-action and eight-round limits prevent endless loops.
  Stop or voice interruption cancels further planning; completed actions stay done.
- An unverified website launch stops dependent agent steps.

## Setup and tests

1. Quit the old Bob from its tray. Extract this ZIP and start Bob.exe.
2. Start Ollama and choose an installed model in Settings. Enable voice replies
   if desired. Agent planning needs a model supporting tool calls.
3. Say **“Open Notepad and type Hello Bob.”** Both steps should happen from one
   request. This explicit sequence uses the fast command path.
4. Try **“Could you prepare a short welcome note in Notepad for me?”** Bob should
   choose supported actions and finish them. Check the actual typed text.
   Generated text and action choice depend on your local model.
5. Try **“Open Notepad and move Notepad to monitor two.”** Check the destination;
   this requires a second connected display.
6. Try **“Tell me the time and lock my computer.”** The time should appear first;
   approve the lock only when ready. Cancel to keep your PC unlocked.
7. Try **“Find report in my Documents and move those files to my Downloads.”**
   Use disposable test files named report. Check selected paths before approving.
8. During a longer workflow press Stop. Verify no further steps run.

This coordinates existing supported actions. Ambiguous targets may need
clarification. Errors and planning limits are reported instead of claiming the
whole task finished. App startup and model inference still affect speed.

Automated workflow tests cover continuation, approval resume, multiple approvals,
cancellation, failures, duplicates and limits with simulated actions. They do not
prove every local model or application completes these examples successfully.
