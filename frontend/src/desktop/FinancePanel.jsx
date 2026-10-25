import { useEffect, useState } from 'react';
import { ChevronRight, Pencil, RefreshCw, Trash2, Wallet, X } from 'lucide-react';
import './finance.css';

function today() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
const transactionDraft = () => ({ day: today(), kind: 'expense', amount: '', category: 'Other', description: '' });
const holdingDraft = () => ({ name: '', units: '', cost: '', price: '', price_date: today() });
const money = (value, currency = 'INR') => new Intl.NumberFormat(undefined, { style: 'currency', currency }).format(value / 100);

export function FinanceWidget({ invoke, open }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    let alive = true;
    invoke('finance_snapshot').then(value => { if (alive) setData(value); });
    return () => { alive = false; };
  }, [invoke]);
  return <button className="finance-widget" onClick={open} aria-label="Open Finance widget">
    <span className="finance-widget-icon"><Wallet size={18} /></span>
    <span><small>YOUR MONEY · MANUAL TRACKER</small><strong>{data?.enabled ? `${money(data.expense, data.currency)} recorded · ${data.month}` : 'Your finance overview'}</strong></span>
    <span className="finance-widget-budget">{data?.remaining != null ? `${money(data.remaining, data.currency)} budget left` : 'Budgets & portfolio'}<ChevronRight size={16} /></span>
  </button>;
}

export default function FinancePanel({ enabled, invoke, setSettings }) {
  const [month, setMonth] = useState(today().slice(0, 7));
  const [data, setData] = useState(null);
  const [tab, setTab] = useState('activity');
  const [draft, setDraft] = useState(transactionDraft);
  const [holding, setHolding] = useState(holdingDraft);
  const [budget, setBudget] = useState('');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const [remove, setRemove] = useState(null);
  const [purchase, setPurchase] = useState('');
  const [estimate, setEstimate] = useState(null);

  async function load() {
    const result = await invoke('finance_snapshot', month);
    if (!result?.enabled) { setError('Could not load Finance. Check that the widget is enabled.'); return false; }
    setData(result); setBudget((result.budget / 100).toFixed(2)); setEstimate(null); setError('');
    return true;
  }
  useEffect(() => {
    if (!enabled) return;
    let alive = true;
    invoke('finance_snapshot', month).then(result => {
      if (!alive) return;
      if (result?.enabled) { setData(result); setBudget((result.budget / 100).toFixed(2)); setEstimate(null); setError(''); }
      else setError('Could not load Finance. Try Refresh.');
    });
    return () => { alive = false; };
  }, [enabled, invoke, month]);

  async function act(method, ...args) {
    setPending(true); setError('');
    try {
      const result = await invoke(method, ...args);
      if (result == null) { setError('Change was not saved. Review the message above and try again.'); return false; }
      await load();
      return true;
    } finally { setPending(false); }
  }
  async function toggle() {
    setPending(true);
    try {
      const settings = await invoke('finance_toggle', !enabled);
      if (settings) { setSettings(settings); if (enabled) { setData(null); setEstimate(null); } }
    } finally { setPending(false); }
  }
  const format = value => money(value, data?.currency || 'INR');
  return <div className="page-content finance-page">
    <div className="eyebrow">A LITTLE CLARITY FOR YOUR MONEY</div>
    <div className="finance-heading"><div><h1>Your money.<br /><span>In perspective.</span></h1><p>Transactions, monthly limits and a portfolio you control.</p></div>
      <label className="finance-switch">Show Finance widget<input type="checkbox" checked={!!enabled} disabled={pending} onChange={toggle} /></label></div>
    <p className="field-help">Optional and off by default. Records stay in this Windows workspace; switching off hides them without deletion. No bank connection, live prices, trades or automatic uploads to an AI model.</p>
    {!enabled ? <section className="glass-card finance-off"><Wallet size={30} /><h2>A calmer view of your finances.</h2><p>Turn on the widget to start a manual ledger, set a monthly budget, and track holdings with dated prices. It also appears in your conversation workspace.</p><button className="primary-button" disabled={pending} onClick={toggle}>Enable Finance widget</button></section> : <>
      <div className="finance-toolbar"><div className="finance-tabs" role="group" aria-label="Finance views"><button aria-pressed={tab === 'activity'} onClick={() => setTab('activity')}>Activity</button><button aria-pressed={tab === 'portfolio'} onClick={() => setTab('portfolio')}>Portfolio</button></div>
        {tab === 'activity' && <label>Finance month<input type="month" value={month} disabled={pending} onChange={e => { if (e.target.value) { setMonth(e.target.value); setData(null); setRemove(null); setDraft({ ...transactionDraft(), day: e.target.value === today().slice(0, 7) ? today() : e.target.value + '-01' }); } }} /></label>}
        <button className="secondary-button" disabled={pending} onClick={async () => { setPending(true); try { await load(); } finally { setPending(false); } }}><RefreshCw size={15} />Refresh finance</button></div>
      {error && <p className="finance-error" role="alert">{error}</p>}
      {!data ? <p role="status">Loading your overview…</p> : <>
        <label className="finance-currency">Ledger currency<select value={data.currency} disabled={pending || data.currency_locked} onChange={async e => {
          const value = e.target.value;
          if (await act('finance_currency', value)) setSettings(current => ({ ...current, finance_currency: value }));
        }}>{['INR', 'USD', 'EUR', 'GBP'].map(currency => <option key={currency}>{currency}</option>)}</select><small>{data.currency_locked ? 'Locked while any finance records or budgets exist. No currency conversion.' : 'Choose before your first record.'}</small></label>
        {tab === 'activity' ? <>
          <div className="finance-stats">{[['Recorded income', data.income], ['Recorded expenses', data.expense], ['Net cash flow', data.net], ['Budget remaining', data.remaining]].map(([label, value]) => <div className="glass-card" key={label}><small>{label}</small><strong>{value == null ? 'Not set' : format(value)}</strong></div>)}</div>
          <p className="field-help">Net cash flow uses entered income minus expenses, not your bank balance. Transfers are excluded: {format(data.transfers)} recorded.</p>
          <div className="finance-grid"><section className="glass-card finance-card"><h2>A plan for this month</h2>
            <form onSubmit={async e => { e.preventDefault(); await act('finance_budget', month, budget); }}><label>Monthly spending budget<input type="number" min="0" max="100000000" step="0.01" required value={budget} onChange={e => setBudget(e.target.value)} /></label><button className="secondary-button" disabled={pending}>Save budget</button></form><p className="field-help">Enter zero to remove this month’s budget.</p>
            {data.daily_guide != null && <div className="finance-daily"><strong>{format(data.daily_guide)}</strong><span>daily budget guide across {data.days_left} remaining days, including today</span></div>}
            <ul className="finance-insights">{data.insights.map(insight => <li key={insight}>{insight}</li>)}</ul>
            <h3>Before you spend</h3><form onSubmit={e => { e.preventDefault();
              if (!/^\d+(\.\d{1,2})?$/.test(purchase) || Number(purchase) <= 0 || Number(purchase) > 100000000) { setError('Enter a positive purchase amount with at most two decimals.'); return; }
              setError(''); setEstimate(Math.round(Number(purchase) * 100));
            }}><label>Planned purchase amount<input type="number" min="0.01" max="100000000" step="0.01" required value={purchase} onChange={e => { setPurchase(e.target.value); setEstimate(null); }} /></label><button className="secondary-button">Check purchase</button></form>
            {estimate != null && <p className="finance-purchase" role="status">{data.remaining == null ? 'Set a budget first to see how this purchase changes it.' : `This would leave ${format(data.remaining - estimate)} in your entered monthly budget${data.remaining - estimate < 0 ? ' — over budget' : ''}.`} This is a preview; no transaction was saved.</p>}
          </section><section className="glass-card finance-card"><h2>{draft.id ? 'Edit transaction' : 'Record a transaction'}</h2>
            <form className="finance-form" onSubmit={async e => { e.preventDefault(); if (await act('finance_transaction', draft)) setDraft(transactionDraft()); }}>
              <div className="finance-fields"><label>Transaction date<input type="date" required value={draft.day} onChange={e => setDraft({ ...draft, day: e.target.value })} /></label><label>Transaction type<select value={draft.kind} onChange={e => setDraft({ ...draft, kind: e.target.value })}>{['expense', 'income', 'transfer'].map(kind => <option key={kind}>{kind}</option>)}</select></label></div>
              <label>Transaction amount<input type="number" min="0.01" max="100000000" step="0.01" required value={draft.amount} onChange={e => setDraft({ ...draft, amount: e.target.value })} /></label>
              <label>Transaction description<input maxLength={180} required value={draft.description} placeholder="Coffee, salary, a weekend trip…" onChange={e => setDraft({ ...draft, description: e.target.value })} /></label>
              <label>Transaction category<select value={draft.category} onChange={e => setDraft({ ...draft, category: e.target.value })}>{data.categories.map(category => <option key={category}>{category}</option>)}</select></label>
              <div className="finance-actions"><button className="primary-button" disabled={pending}>{draft.id ? 'Update transaction' : 'Add transaction'}</button>{draft.id && <button type="button" className="secondary-button" onClick={() => setDraft(transactionDraft())}>Cancel transaction edit</button>}</div>
            </form></section></div>
          {data.category_totals.length > 0 && <section className="glass-card finance-card"><h2>Where it went</h2>{data.category_totals.map(row => <div className="finance-category" key={row.category}><span>{row.category}</span><progress value={row.amount} max={data.expense} aria-label={`${row.category} spending share`} /><strong>{format(row.amount)}</strong></div>)}</section>}
          <section className="glass-card finance-card"><div className="finance-section-title"><h2>Transactions</h2><small>{data.transactions.length} of {data.transaction_count} · newest 250 shown; totals include all</small></div>
            {!data.transactions.length ? <p className="field-help">No records in this month. Add one above or choose another month.</p> : <div className="finance-table"><table><thead><tr><th>Date</th><th>Description</th><th>Type / category</th><th>Amount</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{data.transactions.map(row => <tr key={row.id}><td>{row.day}</td><td>{row.description}</td><td>{row.kind} · {row.category}</td><td>{format(row.amount)}</td><td><button disabled={pending} aria-label={`Edit transaction ${row.description}`} onClick={() => setDraft({ ...row, amount: (row.amount / 100).toFixed(2) })}><Pencil size={14} /></button><button disabled={pending} aria-label={`Delete transaction ${row.description}`} onClick={() => setRemove({ kind: 'transaction', id: row.id })}><Trash2 size={14} /></button></td></tr>)}</tbody></table></div>}
          </section>
        </> : <>
          <div className="finance-stats">{[['Recorded cost', data.portfolio.cost], ['Manual valuation', data.portfolio.value], ['Unrealized difference', data.portfolio.gain]].map(([label, value]) => <div className="glass-card" key={label}><small>{label}</small><strong>{format(value)}</strong></div>)}</div>
          <section className="glass-card finance-card"><h2>{holding.id ? 'Edit holding' : 'Build your portfolio'}</h2><p className="field-help">Enter your positions and dated prices. This is a manual snapshot, not a brokerage connection or investment recommendation.</p>
            <form className="finance-form" onSubmit={async e => { e.preventDefault(); if (await act('finance_holding', holding)) setHolding(holdingDraft()); }}>
              <label>Holding name<input required maxLength={80} placeholder="An asset or fund you own" value={holding.name} onChange={e => setHolding({ ...holding, name: e.target.value })} /></label>
              <div className="finance-fields">{[['units', 'Holding units', '0.00000001'], ['cost', 'Average cost per unit', '0.01'], ['price', 'Manual price per unit', '0.01']].map(([key, label, step]) => <label key={key}>{label}<input type="number" min={key === 'units' ? step : '0'} step={step} required value={holding[key]} onChange={e => setHolding({ ...holding, [key]: e.target.value })} /></label>)}<label>Manual price date<input type="date" required value={holding.price_date} onChange={e => setHolding({ ...holding, price_date: e.target.value })} /></label></div>
              <div className="finance-actions"><button className="primary-button" disabled={pending}>{holding.id ? 'Update holding' : 'Add holding'}</button>{holding.id && <button type="button" className="secondary-button" onClick={() => setHolding(holdingDraft())}>Cancel holding edit</button>}</div>
            </form></section>
          <section className="glass-card finance-card"><h2>Your holdings</h2>{!data.holdings.length ? <p className="field-help">No holdings yet. Add one to begin tracking.</p> : <div className="finance-table"><table><thead><tr><th>Asset / units</th><th>Price dated</th><th>Recorded cost</th><th>Manual value</th><th>Difference</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{data.holdings.map(row => <tr key={row.id}><td>{row.name}<small>{row.units} units</small></td><td>{row.price_date}</td><td>{format(row.cost_total)}</td><td>{format(row.value)}</td><td>{format(row.gain)}</td><td><button disabled={pending} aria-label={`Edit holding ${row.name}`} onClick={() => setHolding({ id: row.id, name: row.name, units: row.units, cost: (row.cost / 100).toFixed(2), price: (row.price / 100).toFixed(2), price_date: row.price_date })}><Pencil size={14} /></button><button disabled={pending} aria-label={`Delete holding ${row.name}`} onClick={() => setRemove({ kind: 'holding', id: row.id })}><Trash2 size={14} /></button></td></tr>)}</tbody></table></div>}</section>
        </>}
        {remove && <div className="finance-remove" role="group" aria-label="Confirm finance removal"><span>Remove this recorded {remove.kind}? This changes only Bob’s tracker.</span><button className="secondary-button" disabled={pending} onClick={async () => { if (await act('finance_delete', remove.kind, remove.id)) { setRemove(null); setDraft(transactionDraft()); setHolding(holdingDraft()); } }}>Remove finance record</button><button className="secondary-button" disabled={pending} onClick={() => setRemove(null)}><X size={14} />Keep record</button></div>}
      </>}
    </>}
  </div>;
}
