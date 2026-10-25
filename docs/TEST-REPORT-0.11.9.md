# Bob 0.11.9 Finance verification — 25 October 2026

[Machine-readable results](TEST-RESULTS-0.11.9.json).

- **513 Python regressions passed** in 51.299 seconds, including **17 Finance
  tests**. A follow-up run of Finance and semantic voice tests passed all 30
  tests after adding the feature capability description to Bob's system prompt.
- Frontend production build and FinancePanel ESLint passed.
- **183 packaged native UI checks passed**, including 19 added checks for the
  off-by-default state, enable/disable, currency setup, exact expense/budget
  totals, purchase preview without ledger writes, transaction editing, manual
  holding valuation/editing, opening the panel from the chat widget, retained
  records across toggle, canceled removal and confirmed deletion.
- Packaged startup and voice handoff fixtures passed with eight navigation
  destinations and no horizontal overflow at 1366px. Window X stopped fixture
  schedulers and reminders.
- The EXE and required runtime/model folder were built with PyInstaller.

Finance arithmetic tests cover 0.10 + 0.20 without floating-point drift,
income/expense/transfer separation, month boundaries, month-specific budgets,
zero-budget removal, over-budget daily guide, fractional holding rounding,
manual valuation changes, currency locking, missing/invalid records, size
limits, persistence after reopening, and totals beyond the 250 displayed rows.
The voice toggle test verifies no LLM transport call or finance-record table
creation for visibility-only requests. Disabling returns no ledger snapshot;
re-enabling retains the data. Toggling does not replace the audio engine.

UI Finance operations use the real service and SQLite in isolated fixture data
folders. No personal financial data, bank account, brokerage or market-price
service was accessed. Other UI integrations (voice, app control, provider links,
pickers and phone) remain simulated in the controls fixture. The Finance voice
shortcut's parser/runtime path was tested, not live microphone recognition.

No new live audio acceptance test was performed for this feature. The previous
interruption candidate still needs the user-operated diagnostic 4 result; this
release does not declare that issue resolved or certify all real voice behavior.
Finance is a local manual tracker, not a live balance, tax or trading service.

[User guide and sample records](FINANCE-GUIDE.md).
