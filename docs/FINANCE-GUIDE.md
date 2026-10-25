# Finance widget — Bob 0.11.9

## Turn it on or off

Open **Finance** in the sidebar and turn on **Show Finance widget**, or click
**Enable Finance widget**. It starts off. When enabled, a compact spending card
also appears in the chat workspace; click it to return to Finance.

When Bob is listening, say **“Hey Bob, show my finance widget”** or **“Hey Bob,
hide my finance widget.”** These explicit switches run locally without sending
financial records to a model. Hiding keeps your records; it does not delete them.
Other voice finance operations and bank synchronization are not implemented.

## Record and manage transactions

1. Before your first record, choose INR, USD, EUR or GBP under **Ledger currency**.
   A ledger uses one currency. Currency locks while any transaction, holding or
   monthly budget exists; Bob never silently converts stored amounts.
2. In **Activity**, choose a month. Enter the transaction date, type, amount,
   description and category, then click **Add transaction**.
3. Expenses reduce net recorded cash flow; income increases it. Transfers are
   shown separately and excluded from both income and expenses.
4. Use the pencil to edit an entry. Use the bin to request removal, then confirm
   **Remove finance record**, or **Keep record** to cancel. This edits Bob's local
   tracker only, never a bank account or brokerage order.
5. The list shows the newest 250 entries in the selected month. Totals include
   every entry for that month. Change months to view other records.

## Spend with a plan

Set **Monthly spending budget** and click **Save budget**. A budget belongs to the
selected month only. Enter zero to remove it. Bob shows recorded expenses,
remaining budget, category totals and factual spending observations.

For the current month, the daily guide divides the nonnegative budget remaining
by the days left, including today. It is not a bank balance or an affordability
assessment: unrecorded bills, debts and expenses are unknown.

Enter a **Planned purchase amount** and click **Check purchase** to preview its
effect on the entered budget. This does not save a transaction or buy anything.

Example: budget 1,000; recorded expenses 25.50; planned purchase 50. The preview
leaves **924.50** of that budget. Add the actual expense separately if it happens.

## Build a manual portfolio

Open **Portfolio**. Enter a holding name, units, average cost per unit, manual
price per unit and price date. Click **Add holding**. Fractional units support up
to eight decimals; money supports two decimals. Edit to update units or a price.

The panel shows recorded cost, manually valued total and unrealized difference.
Each holding shows its price date. Prices are entered by you; they are not live
quotes. Holdings represent your current entered positions, not a historical
month-by-month portfolio. This tool does not connect a broker, execute trades,
calculate taxes or recommend securities.

Example: 2.5 units at a recorded cost of 100 and a manual price of 110 produces
cost **250**, value **275**, and an unrealized difference of **25**.

## Privacy and limits

Finance records are stored in Bob's existing local SQLite database for this
Windows workspace. They are not automatically placed in chat, personal memory,
support summaries or model prompts. This is not an encrypted financial vault or
a biometric access boundary; people with access to your Windows workspace can
view the enabled tracker. Use Windows account protections for that workspace.

There is no bank login, bank notification scraping, payment execution, live-price
provider or financial-account synchronization. Entries and dated prices are
manual. Suggestions are arithmetic and category observations based on what you
entered, not personalized investment recommendations.

## Quick test using sample records

- Enable Finance, choose your currency, set a budget of 1,000.
- Add a Food expense of 25.50. Verify expense 25.50 and remaining budget 974.50.
- Preview a purchase of 50. Verify 924.50 remains and no extra transaction appears.
- Edit the expense to 30. Verify remaining budget becomes 970.
- Add income 100 and a transfer 50. Verify net recorded cash flow is 70 and the
  transfer does not change that figure.
- Add the portfolio example above. Edit its price to 120: value becomes 300,
  unrealized difference 50.
- Hide and re-enable the widget. Verify records remain. Restart Bob and verify
  persistence. Delete the sample records and remove the sample budget when done.
