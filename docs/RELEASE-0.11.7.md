# Bob 0.11.7 — a clearer customer starting point

- New **Get started** screen with on-demand local setup checks and specific
  recovery guidance. First-time personal setup leads into this screen.
- Read-only probes check Ollama/model availability, bundled speech files and
  audio device availability. They do not capture audio or load AI models.
- First-task cards prepare a request in the composer so the user reviews it
  before execution. They do not silently run tasks or create routines.
- Copy a minimal setup summary for support without personal data or raw errors.
- Current desktop architecture documentation replaces the old Gemini diagram.
- Customer release plan includes live acceptance tests, positioning and the
  remaining work needed before accepting payments.

## Try it

Launch `dist/release-0.11.7/Bob/Bob.exe`, keeping `_internal` beside it. Open
**Get started**, click **Check again**, inspect the statuses, and use **Open
settings** for missing prerequisites. Choose **Your first action**, review
“Open calculator” in the composer, then Send and check the actual window.
Copy the setup summary and inspect it before sharing.

Existing voice cancellation, personal calibration, memory and action permissions
are preserved. Setup availability does not guarantee a live workflow succeeds.
No checkout, activation service, signed installer or universal automation was
added. See [customer release plan](CUSTOMER-RELEASE.md).
