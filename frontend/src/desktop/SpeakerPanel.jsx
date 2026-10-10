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
  const [ready, setReady] = useState(false);
  const [match, setMatch] = useState(null);
  const [adding, setAdding] = useState(false);
  useEffect(() => { let alive = true; invoke('speaker_status').then(value => { if (alive && value) setProfile(value); }); return () => { alive = false; }; }, [invoke]);
  useEffect(() => {
    if (!recording) return;
    let alive = true;
    const timer = setInterval(async () => {
      const status = await invoke('voice_status');
      if (alive) setReady(status?.phase === 'listening');
    }, 250);
    return () => { alive = false; clearInterval(timer); };
  }, [recording, invoke]);
  async function record() {
    setReady(false); setRecording(true); setNotice('Wait for Listening, then speak naturally for five to ten seconds. The example words do not have to match.');
    try {
      const value = await invoke('enroll_speaker', name);
      if (value) { setProfile(value); if (value.enrolled) setAdding(false); setNotice(value.enrolled ? `Voice profile saved for ${value.name}.` : `Sample ${value.samples} of 3 captured.`); }
    } finally { setRecording(false); }
  }
  return <section className="glass-card settings-section"><div className="settings-title"><Mic size={21} /><div><h2>Recognize my voice</h2><p>Three spoken samples. Matching runs locally on your PC.</p></div></div>
    <label className="toggle-row"><span>Recognize my voice · optional</span><input type="checkbox" checked={!!draft.speaker_enabled} onChange={e => setDraft({ ...draft, speaker_enabled: e.target.checked })} /></label><p className="field-help">Off by default. Save settings to apply. Turning this off keeps your profile but stops matching; use Delete to erase it.</p>
    <label>Matching sensitivity<select value={draft.speaker_match_mode || 'balanced'} onChange={e => setDraft({ ...draft, speaker_match_mode: e.target.value })}><option value="balanced">Balanced</option><option value="strict">Strict · fewer matches</option></select></label><p className="field-help">Use Strict if Bob mistakes another voice for yours. Save settings before testing.</p>
    {profile.enrolled && <><button type="button" className="secondary-button" disabled={busy || recording} onClick={async () => { setReady(false); setRecording(true); setMatch(null); setNotice('Say a new sentence for five seconds, then pause. Nothing you say here will execute.'); try { const value = await invoke('test_speaker'); if (value) setMatch(value); } finally { setRecording(false); } }}><Mic size={16} />{recording ? 'Listening…' : 'Test voice match'}</button>{match && <p role="status">{match.state === 'matched' ? `Recognized as ${match.name}` : match.message || 'No confident match. Try a longer sentence in a quiet room.'}{typeof match.similarity === 'number' && <small> · similarity {match.similarity.toFixed(2)} / cutoff {match.threshold.toFixed(2)} (not a probability)</small>}</p>}</>}
    {(profile.profiles || []).map(user => <div key={user.id} className="field-grid"><label>{profile.active === user.id ? 'Active: ' : ''}{user.name}<select disabled={busy || recording} value={user.personality} onChange={async e => { const value = await invoke('personalize_speaker', user.id, e.target.value); if (value) setProfile(value); }}><option value="inherit">Use main personality</option><option value="balanced">Balanced</option><option value="friend">Friendly</option><option value="funny">Funny</option><option value="serious">Serious</option><option value="butler">Witty butler</option><option value="engineer">Precise engineer</option><option value="discreet">Discreet</option><option value="coach">Coach</option><option value="explorer">Explorer</option><option value="candid">Candid</option></select></label><button type="button" className="text-button" disabled={busy || recording} onClick={async () => { const value = await invoke('forget_speaker', user.id); if (value) { setProfile(value); setMatch(null); setNotice('That voice profile was deleted. Saved conversations remain available.'); } }}><Trash2 size={14} />Delete {user.name}'s voice</button></div>)}
    {profile.enrolled && !adding ? <button type="button" className="secondary-button" disabled={busy || recording || (profile.profiles?.length || 0) >= 8} onClick={() => { setAdding(true); setName(''); setProfile({ ...profile, samples: 0 }); }}>Add another person</button> : <><label>Your name<input maxLength={80} value={name} disabled={recording} onChange={e => setName(e.target.value)} placeholder="Your preferred name" /></label><p className="field-help">Sample {Math.min(profile.samples + 1, 3)} of 3. Speak normally for five to ten seconds in a quiet room, then pause.</p><blockquote>{phrases[Math.min(profile.samples, 2)]}</blockquote><button type="button" className="secondary-button" disabled={busy || recording || !name.trim()} onClick={record}><Mic size={16} />{recording ? (ready ? 'Listening… speak naturally' : 'Preparing microphone…') : 'Record sample'}</button></>}
    <p className="field-help">A clear voice match resumes that person's conversation and uses their personality. An uncertain match keeps the current profile. Profiles are personalization, not a login or privacy barrier on a shared PC. Existing general memories stay in the general workspace.</p>
    {profile.error && <p role="status">{profile.error}</p>}
    {recording && <p role="status">{ready ? 'Listening — speak normally, then pause for two seconds.' : 'Preparing microphone — wait before speaking.'}</p>}
    <p className="field-help">The sentences are suggestions, not a reading test. Bob matches the sound of your voice without checking spelling or grammar. Brief pauses are allowed. Only encrypted voice features are saved, not recordings. Short phrases can be uncertain. This identifies a likely speaker; it does not lock other people out or approve sensitive actions.</p>
    <button type="button" className="text-button" disabled={busy || recording} onClick={async () => { const value = await invoke('forget_speaker'); if (value) { setProfile(value); setNotice('Voice profile and pending samples deleted.'); } }}><Trash2 size={14} />Delete voice profile / restart enrollment</button>
  </section>;
}
