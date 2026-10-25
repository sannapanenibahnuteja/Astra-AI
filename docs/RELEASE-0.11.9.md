# Bob 0.11.9 — optional Finance widget

- Off-by-default chat widget and full Finance panel.
- Manual transaction ledger with expenses, income, transfers, categories, dates,
  edits and confirmed record deletion.
- Month-specific budgets, exact minor-unit totals, category breakdowns and a
  current-month daily budget guide.
- Purchase previews that show budget impact without creating a transaction.
- Manual portfolio holdings with fractional units, dated prices, recorded cost,
  valuation and unrealized differences.
- Explicit local voice commands: “Hey Bob, show my finance widget” and “Hey Bob,
  hide my finance widget.” No financial records are sent to a model by these
  commands. Finance operations otherwise use the panel.
- Toggle changes preserve records and do not reconfigure the active audio engine.
  Disabled snapshot calls return only the disabled flag; disabled mutations fail.
- One currency per ledger; changing the currency of existing records is blocked.

Launch `dist/release-0.11.9/Bob/Bob.exe` with `_internal` beside it. Open **Finance**
and enable the widget. Follow the [setup and sample tests](FINANCE-GUIDE.md).

This is a local manual tracker, not a bank/broker integration, payment tool,
live-price service or investment adviser. The optional widget adds no background
polling or bank account access. It does not change the earlier voice pipeline;
the outstanding live interruption acceptance from 0.11.8 remains separate.
