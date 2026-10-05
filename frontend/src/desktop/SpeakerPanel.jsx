import { useEffect, useState } from 'react';
import { Mic, Trash2 } from 'lucide-react';

const phrases = [
  'Hello Bob. This is my voice. I would like you to recognize me when we talk.',
  'I use this computer for my work and my projects. Help me plan a good day.',
  'We can have a natural conversation. Remember my voice and call me by my name.',
];

export default function SpeakerPanel({ invoke, busy, setNotice, draft, setDraft }) {
  const [profile, setProfile] = useState({ samples: 0, enrolled: false });
  const [name, setName] = useState('');
  const [recording, setRecording] = useState(false);
  const [match, setMatch] = useState(null);
  useEffect(() => { let alive = true; invoke('speaker_status').then(value => { if (alive && value) setProfile(value); }); return () => { alive = false; }; }, []);
  async function record() {
    setRecording(true); setNotice('Read the sentence aloud, then pause. This sample will not execute commands.');
    try {
      const value = await invoke('enroll_speaker', name);
      if (value) { setProfile(value); setNotice(value.enrolled ? `Voice profile saved for ${value.name}.` : `Sample ${value.samples} of 3 captured.`); }
    } finally { setRecording(false); }
  }
  return <section className="glass-card settings-section"><div className="settings-title"><Mic size={21} /><div><h2>Recognize my voice</h2><p>Three spoken samples. Matching runs locally on your PC.</p></div></div>
    <label className="toggle-row"><span>Recognize my voice · optional</span><input type="checkbox" checked={!!draft.speaker_enabled} onChange={e => setDraft({ ...draft, speaker_enabled: e.target.checked })} /></label><p className="field-help">Off by default. Save settings to apply. Turning this off keeps your profile but stops matching; use Delete to erase it.</p>
    <label>Matching sensitivity<select value={draft.speaker_match_mode || 'balanced'} onChange={e => setDraft({ ...draft, speaker_match_mode: e.target.value })}><option value="balanced">Balanced</option><option value="strict">Strict · fewer matches</option></select></label><p className="field-help">Use Strict if Bob mistakes another voice for yours. Save settings before testing.</p>
    {profile.enrolled && <><button type="button" className="secondary-button" disabled={busy || recording} onClick={async () => { setRecording(true); setMatch(null); setNotice('Say a new sentence for five seconds, then pause. Nothing you say here will execute.'); try { const value = await invoke('test_speaker'); if (value) setMatch(value); } finally { setRecording(false); } }}><Mic size={16} />{recording ? 'Listening…' : 'Test voice match'}</button>{match && <p role="status">{match.state === 'matched' ? `Recognized as ${match.name}` : match.message || 'No confident match. Try a longer sentence in a quiet room.'}{typeof match.similarity === 'number' && <small> · similarity {match.similarity.toFixed(2)} / cutoff {match.threshold.toFixed(2)} (not a probability)</small>}</p>}</>}
    {profile.enrolled ? <p>Saved voice profile: <strong>{profile.name}</strong></p> : <><label>Your name<input maxLength={80} value={name} disabled={recording} onChange={e => setName(e.target.value)} placeholder="Your preferred name" /></label><p className="field-help">Sample {Math.min(profile.samples + 1, 3)} of 3. Speak normally for five to ten seconds in a quiet room, then pause.</p><blockquote>{phrases[Math.min(profile.samples, 2)]}</blockquote><button type="button" className="secondary-button" disabled={busy || recording || !name.trim()} onClick={record}><Mic size={16} />{recording ? 'Listening… read the sentence now' : 'Record sample'}</button></>}
    {profile.error && <p role="status">{profile.error}</p>}
    <p className="field-help">Only encrypted voice features are saved, not recordings. Short phrases can be uncertain. This identifies a likely speaker; it does not lock other people out or approve sensitive actions.</p>
    <button type="button" className="text-button" disabled={busy || recording} onClick={async () => { const value = await invoke('forget_speaker'); if (value) { setProfile(value); setNotice('Voice profile and pending samples deleted.'); } }}><Trash2 size={14} />Delete voice profile / restart enrollment</button>
  </section>;
}
