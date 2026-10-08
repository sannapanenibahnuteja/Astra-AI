import { useEffect, useState } from 'react';

export default function VoicePicker({ draft, setDraft, invoke }) {
  const [catalog, setCatalog] = useState({ windows: [], neural: [] });
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const refresh = () => invoke('voice_options').then(data => { if (data) setCatalog(data); });
  useEffect(() => { refresh().catch(() => setMessage('Voice list unavailable. Try again.')); }, []);
  const provider = draft.voice_provider || 'auto';
  const preview = async () => {
    setBusy(true); setMessage('Playing preview…');
    try {
      const played = await invoke('preview_voice', { voice_provider: provider, windows_voice: draft.windows_voice || '', neural_voice: draft.neural_voice || '', voice_rate: draft.voice_rate || 0 });
      setMessage(played === null ? 'Preview failed. Check the error notice above.' : played ? 'Preview finished. Save settings to use this voice.' : 'Preview stopped.');
    } catch (error) { setMessage(error.message || String(error)); }
    finally { setBusy(false); }
  };
  return <div>
    <label>Bob’s voice<select value={provider} onChange={e => setDraft({ ...draft, voice_provider: e.target.value })}>
      <option value="auto">Automatic · use configured Azure, otherwise Windows</option>
      <option value="azure">Azure neural · more natural speech · online</option>
      <option value="windows">Windows · installed voices · offline</option>
    </select></label>
    {provider !== 'windows' && <label>Natural voice<select value={draft.neural_voice || ''} onChange={e => setDraft({ ...draft, neural_voice: e.target.value })}>
      <option value="">Use voice from Azure configuration</option>
      {catalog.neural.map(v => <option key={v.id} value={v.id}>{v.label}</option>)}
    </select></label>}
    <label>{provider === 'windows' ? 'Offline voice' : 'Offline fallback voice'}<select value={draft.windows_voice || ''} onChange={e => setDraft({ ...draft, windows_voice: e.target.value })}>
      <option value="">Windows system default</option>
      {catalog.windows.map(v => <option key={v.id} value={v.id}>{v.label}</option>)}
    </select></label>
    <button type="button" className="text-button" disabled={busy} onClick={preview}>{busy ? 'Previewing…' : 'Listen to this voice'}</button>
    <button type="button" className="text-button" disabled={busy} onClick={() => refresh().catch(() => setMessage('Could not refresh voices.'))}>Refresh voices</button>
    <button type="button" className="text-button" disabled={busy} onClick={async () => { const path = await invoke('neural_voice_setup'); if (path) { setMessage(`Edit ${path}: enter your Azure Speech region and key, set enabled to true, then refresh voices.`); await invoke('open_data_folder'); } }}>Set up neural voice</button>
    <p className="field-help">{message || catalog.error || (catalog.azure_ready ? 'Azure configuration found. Preview to check connectivity and choose your favorite.' : 'Neural voices need Azure Speech: use “Set up neural voice”, fill in region and key, set enabled to true, then refresh. Twilio credentials do not enable Azure voices.')}</p>
    <p className="field-help">Azure sends reply text to Microsoft and may incur charges. Windows speech stays offline. Voice choice also applies to private phone webpage replies; carrier calls use the calling provider’s voice. Stop voice conversation before previewing.</p>
  </div>;
}
