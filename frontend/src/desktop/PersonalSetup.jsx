import { useEffect, useRef, useState } from 'react';
import { Sparkles } from 'lucide-react';

const questions = [
  ['preferred name', 'What should I call you?', 'Your preferred name'],
  ['communication style', 'How do you like me to respond?', 'Brief and warm, thoughtful, playful…'],
  ['ongoing projects', 'What are you working on?', 'A project you want me to keep in mind'],
  ['daily priorities', 'What matters in your everyday routine?', 'Your priorities or preferences'],
];
export default function PersonalSetup({ invoke, onDone }) {
  const [values, setValues] = useState({});
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const dialog = useRef(null);
  useEffect(() => {
    const before = document.activeElement;
    dialog.current?.querySelector('input,button')?.focus();
    return () => before?.focus();
  }, []);
  async function finish(details) {
    setSaving(true);
    try { const data = await invoke('personal_setup', details); if (data) onDone(data); }
    finally { setSaving(false); }
  }
  const current = questions[step];
  function trap(event) {
    if (event.key !== 'Tab') return;
    const targets = [...dialog.current.querySelectorAll('input,button:not(:disabled)')];
    const index = targets.indexOf(document.activeElement);
    if (event.shiftKey && index <= 0) { event.preventDefault(); targets.at(-1)?.focus(); }
    else if (!event.shiftKey && index === targets.length - 1) { event.preventDefault(); targets[0]?.focus(); }
  }
  return <div className="setup-backdrop"><section ref={dialog} onKeyDown={trap} className="glass-card personal-setup" role="dialog" aria-modal="true" aria-labelledby="setup-title"><Sparkles size={28} /><div className="eyebrow">LET’S GET ACQUAINTED · {Math.min(step + 1, 5)} / 5</div><h2 id="setup-title">{current ? current[1] : 'Here’s what I’ll remember.'}</h2><p>Optional. Only the details you choose to save become memory. Review or delete them in Memory. These go to your active voice profile, or the general workspace.</p>{current ? <label key={current[0]}>{current[0]}<input autoFocus maxLength={1000} value={values[current[0]] || ''} onChange={e => setValues({ ...values, [current[0]]: e.target.value })} placeholder={current[2]} onKeyDown={e => { if (e.key === 'Enter') setStep(step + 1); }} /></label> : <dl>{Object.entries(values).filter(([, v]) => v.trim()).map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}{!Object.values(values).some(v => v.trim()) && <p>No personal facts selected.</p>}</dl>}<div className="routine-toolbar">{step > 0 && <button className="secondary-button" disabled={saving} onClick={() => setStep(step - 1)}>Back</button>}{current ? <button className="primary-button" onClick={() => setStep(step + 1)}>{values[current[0]]?.trim() ? 'Continue' : 'Skip question'}</button> : <button className="primary-button" disabled={saving} onClick={() => finish(values)}>{saving ? 'Saving…' : 'Save selected memories'}</button>}<button className="text-button" disabled={saving} onClick={() => finish({})}>Skip setup</button></div></section></div>;
}
