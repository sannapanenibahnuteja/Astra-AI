import { useEffect, useState } from 'react';
import { Check, ChevronRight, Copy, RefreshCw, Settings2 } from 'lucide-react';
import './welcome.css';

const examples = [
  ['Your first action', 'Open calculator', 'Check that the window actually opens.'],
  ['A useful memory', 'Remember that I prefer concise explanations', 'Review or delete the saved fact in Memory.'],
  ['A little less effort', 'Open YouTube', 'Use a website even without a desktop app.'],
  ['Think together', 'Help me plan a focused morning', 'Local conversation uses the model selected in Settings.'],
];

export default function WelcomePanel({ invoke, onSettings, prepareCommand }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  async function refresh() {
    setLoading(true); setError(''); setCopied(false);
    try {
      const result = await invoke('setup_readiness');
      if (!result?.checks) throw new Error();
      setReport(result);
    }
    catch { setError('Could not check setup. Launch Bob.exe, then try again.'); }
    finally { setLoading(false); }
  }
  useEffect(() => {
    let alive = true;
    invoke('setup_readiness').then(result => {
      if (!alive) return;
      if (result?.checks) setReport(result);
      else setError('Could not check setup. Launch Bob.exe, then try again.');
    });
    return () => { alive = false; };
  }, [invoke]); // One on-demand check; no background polling.

  return <div className="page-content welcome-page">
    <div className="eyebrow">YOUR STARTING POINT</div>
    <h1>Less setup.<br /><span>More possibility.</span></h1>
    <p className="welcome-intro">Make Bob yours, check the essentials, then try something useful.</p>
    <section className="glass-card welcome-health" aria-busy={loading}>
      <div className="welcome-heading"><div><h2>Ready when you are</h2><p aria-live="polite">{loading ? 'Checking setup…' : report ? `${report.ready_count} of ${report.required_count} essentials available` : 'Check your local setup'}</p></div>
        <button className="secondary-button" onClick={refresh} disabled={loading}><RefreshCw size={15} />Check again</button></div>
      {error && <p role="alert">{error}</p>}
      <div className="welcome-checks">{report?.checks.map(check => <div className="welcome-check" key={check.id}>
        <span className={`welcome-state ${check.state}`} aria-label={check.state}>{check.state === 'ready' ? <Check size={15} /> : '·'}</span>
        <div><h3>{check.title} <small>{check.state === 'attention' ? 'Needs setup' : check.state === 'optional' ? 'Optional' : 'Available'}</small></h3><p>{check.detail}</p></div>
      </div>)}</div>
      <div className="welcome-actions"><button className="primary-button" onClick={onSettings}><Settings2 size={15} />Open settings</button>
        <button className="secondary-button" disabled={!report || loading} onClick={async () => {
          try { const ok = await invoke('copy_text', report.support_summary); if (!ok) throw new Error(); setCopied(true); }
          catch { setError('Could not copy the setup summary. Try again.'); }
        }}><Copy size={15} />{copied ? 'Copied' : 'Copy setup summary'}</button></div>
      <p className="welcome-note">Checks query devices and files; they do not record audio or run tasks. The copied summary includes only check states—no chats, memory, credentials or device names. Available does not guarantee a successful live test.</p>
    </section>
    <section aria-label="First tasks"><h2>Make your first minute count</h2><p>Choose a request to review it in the composer. You decide when to send.</p>
      <div className="welcome-examples">{examples.map(([title, command, detail]) => <button key={title} aria-label={`Try ${title}`} className="glass-card" onClick={() => prepareCommand(command)}><span>{title}<ChevronRight size={16} /></span><strong>“{command}”</strong><p>{detail}</p></button>)}</div>
    </section>
    <p className="welcome-note">Bob runs on your PC. Ollama and a downloaded conversation model are required for local chat. Phone calls and optional cloud voices need separate provider accounts and may cost extra. Daily routines run while Bob and your PC stay awake. Review personal facts in Memory at any time.</p>
  </div>;
}
