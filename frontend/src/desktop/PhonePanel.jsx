import { useEffect, useState } from 'react';

export default function PhonePanel({ invoke, setNotice }) {
  const [state, setState] = useState({ enabled: false });
  const [address, setAddress] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => { invoke('mobile_status').then(value => value && setState(value)); }, []);
  async function enable() {
    setBusy(true);
    try { const result = await invoke('enable_mobile', address.trim()); if (result) setState(result); }
    finally { setBusy(false); }
  }
  return <section className="glass-card settings-section">
    <h2>Phone &amp; reminders</h2>
    <p className="field-help">Keep Bob with you through a private mobile webpage. Your PC must stay awake with Bob running. Mobile access stays off until you enable it, and must be enabled again after restarting Bob.</p>
    <label>Private Tailscale HTTPS address<input value={address} onChange={e => setAddress(e.target.value)} placeholder="https://your-pc.your-tailnet.ts.net" /></label>
    <p className="field-help">Install Tailscale on your PC and phone, sign into the same network, then run <code>tailscale serve --bg http://127.0.0.1:8787</code> on your PC. Paste its HTTPS address above. Leave blank for a local PC-only preview. No router port forwarding is needed.</p>
    <button type="button" className="secondary-button" disabled={busy} onClick={enable}>{state.enabled ? 'Create a new pairing link' : 'Enable mobile access'}</button>
    {state.enabled && <><button type="button" className="secondary-button" onClick={async () => { const result = await invoke('disable_mobile'); if (result) setState(result); }}>Disable &amp; revoke links</button><label>Private pairing link — keep it secret<input readOnly value={state.url} onFocus={e => e.target.select()} /></label><p className="field-help">Open this link on your phone while connected to Tailscale. Anyone with the link and access to your private network can control Bob. Creating a new link revokes the old one. {state.remote_ready ? '' : 'This localhost link works only on this PC.'}</p></>}
    <h3>Reminders that stay saved</h3><p className="field-help">Say “remind me in ten minutes to take a break”, “show my reminders”, or “cancel reminder” followed by its ID. Local reminders show a desktop notification and speak when Bob is free.</p>
    <h3>Private voice conversation</h3><p className="field-help">Open the paired phone page and start a private voice conversation. Phone audio goes to Whisper on your PC; replies use offline Windows speech and return over the private connection. No carrier call or cloud speech service is used. Phone reminders sound while the page is open and audio is enabled; Bob cannot ring a locked phone or a closed browser. Say “call me in ten minutes to take a break” to schedule a phone-page alert.</p>
    <h3>Optional neural desktop voice</h3><p className="field-help">For a more natural voice, configure an Azure Speech resource in neural-voice.json and set enabled to true. This sends spoken reply text to Microsoft and may incur charges. The Windows voice remains the offline fallback. Phone-webpage replies use your phone's speech engine.</p>
    <button type="button" className="secondary-button" onClick={async () => { const path = await invoke('neural_voice_setup'); if (path) { setNotice(`Neural voice configuration: ${path}`); await invoke('open_data_folder'); } }}>Create neural voice configuration</button>
  </section>;
}
