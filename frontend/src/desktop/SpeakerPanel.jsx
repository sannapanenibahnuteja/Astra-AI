import { useEffect, useState } from 'react';
import { Mic, Trash2 } from 'lucide-react';

const phrases = [
  'Hello Bob. This is my voice. I would like you to recognize me when we talk. I am speaking at my normal pace about my day and the things I enjoy.',
  'I use this computer for my work and my projects. Help me plan a good day and keep track of the projects I am working on.',
  'We can have a natural conversation. Remember my voice and call me by my name. I would like you to understand my normal speaking style without needing exact command words.',
];

export default function SpeakerPanel({ invoke, busy, setNotice, draft, setDraft }) {
  const [profile, setProfile] = useState({ samples: 0, enrolled: false });
  const [name, setName] = useState('');
  const [recording, setRecording] = useState(false);
  const [ready, setReady] = useState(false);
  const [enrolling, setEnrolling] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [mic, setMic] = useState({ level: 0, name: '' });
  const [cancelled, setCancelled] = useState(false);
  const [match, setMatch] = useState(null);
  const [adding, setAdding] = useState(false);
  const [updating, setUpdating] = useState(null);
  useEffect(() => { let alive = true; invoke('speaker_status').then(value => { if (alive && value) setProfile(value); }); return () => { alive = false; }; }, [invoke]);
  useEffect(() => {
    if (!recording) return;
    let alive = true;
    const timer = setInterval(async () => {
      const status = await invoke('voice_status');
      if (alive) { setReady(status?.phase === 'listening'); setSeconds(status?.enrollment_seconds || 0); setMic({ level: status?.level || 0, name: status?.input_device || '' }); }
    }, 250);
    return () => { alive = false; clearInterval(timer); };
  }, [recording, invoke]);
  async function record() {
    setReady(false); setSeconds(0); setCancelled(false); setEnrolling(true); setRecording(true); setNotice('Wait for Listening, then read at your own pace. Click Finish sample when done. Exact wording does not matter.');
    try {
      const value = await invoke('enroll_speaker', name, updating);
      if (value?.cancelled) setNotice('Recording cancelled. Earlier accepted samples are kept.');
      else if (value) { setProfile(value); if (value.enrolled) { setAdding(false); setUpdating(null); } setNotice(value.enrolled ? `Voice profile saved for ${value.name}.` : `Sample ${value.samples} of 3 captured.`); }
    } finally { setRecording(false); setEnrolling(false); }
  }
  return <section className="glass-card settings-section"><div className="settings-title"><Mic size={21} /><div><h2>Recognize my voice</h2><p>Three varied samples of eight to twelve seconds each. Matching runs locally on your PC.</p></div></div>
    <label className="toggle-row"><span>Recognize my voice · optional</span><input type="checkbox" checked={!!draft.speaker_enabled} onChange={e => setDraft({ ...draft, speaker_enabled: e.target.checked })} /></label><p className="field-help">Off by default. When enabled, only enrolled voices can issue voice commands or interrupt. Without a confident match, Bob ignores the utterance. Save settings to apply; turning this off permits ordinary voice input again.</p>
    <label>Focused listening<select value={draft.speaker_focus || '*'} onChange={e => setDraft({ ...draft, speaker_focus: e.target.value, ...(e.target.value ? { speaker_enabled: true } : {}) })}><option value="*">Saved voices only · recommended</option>{(profile.profiles || []).map(user => <option key={user.id} value={user.id}>Focus on {user.name}</option>)}{draft.speaker_focus && draft.speaker_focus !== '*' && !(profile.profiles || []).some(user => user.id === draft.speaker_focus) && <option value={draft.speaker_focus}>Selected profile unavailable · choose another or turn off</option>}</select></label><p className="field-help">Enrol in a quiet room first. Choose all saved voices or one person, then save. A confident enrolled match is required for commands and interruptions. Verification adds about 1.6 seconds of speech before an interruption; short or overlapping voices can be ignored. Speak normally near your microphone. This does not separate overlapping speakers or authenticate a person.</p>
    <label>Matching sensitivity<select value={draft.speaker_match_mode || 'balanced'} onChange={e => setDraft({ ...draft, speaker_match_mode: e.target.value })}><option value="balanced">Balanced</option><option value="strict">Strict · fewer matches</option></select></label><p className="field-help">Use Strict if Bob mistakes another voice for yours. Save settings before testing.</p>
    {profile.enrolled && <><button type="button" className="secondary-button" disabled={busy || recording} onClick={async () => { setReady(false); setCancelled(false); setRecording(true); setMatch(null); setNotice('Say a new sentence for five seconds, then pause. Nothing you say here will execute.'); try { const value = await invoke('test_speaker'); if (value) setMatch(value); } finally { setRecording(false); } }}><Mic size={16} />{recording ? 'Listening…' : 'Test voice match'}</button>{match && <p role="status">{match.state === 'matched' ? `Recognized as ${match.name}` : match.message || 'No confident match. Try a longer sentence in a quiet room.'}{typeof match.similarity === 'number' && <small> · similarity {match.similarity.toFixed(2)} / cutoff {match.threshold.toFixed(2)} (not a probability)</small>}</p>}</>}
    {typeof profile.speech_seconds === 'number' && <p className="field-help">Usable speech captured: {profile.speech_seconds.toFixed(1)} seconds. Each new sample needs at least four seconds of clear speech; aim for 15–30 seconds across all three samples.</p>}
    {(profile.profiles || []).map(user => <div key={user.id} className="field-grid"><label>{profile.active === user.id ? 'Active: ' : ''}{user.name}<select disabled={busy || recording} value={user.personality} onChange={async e => { const value = await invoke('personalize_speaker', user.id, e.target.value); if (value) setProfile(value); }}><option value="inherit">Use main personality</option><option value="balanced">Balanced</option><option value="friend">Friendly</option><option value="funny">Funny</option><option value="serious">Serious</option><option value="butler">Witty butler</option><option value="engineer">Precise engineer</option><option value="discreet">Discreet</option><option value="coach">Coach</option><option value="explorer">Explorer</option><option value="candid">Candid</option></select></label><button type="button" className="secondary-button" disabled={busy || recording || !!updating} onClick={() => { setUpdating(user.id); setAdding(true); setName(user.name); setProfile({ ...profile, enrolled: false, samples: 0 }); setNotice('Record three new samples. Your existing profile and memories remain until all three are accepted.'); }}>Re-record {user.name}</button><button type="button" className="text-button" disabled={busy || recording || !!updating} onClick={async () => { const value = await invoke('forget_speaker', user.id); if (value) { setProfile(value); setMatch(null); setNotice('That voice profile was deleted. Saved conversations remain available.'); } }}><Trash2 size={14} />Delete {user.name}'s voice</button></div>)}
    {profile.enrolled && !adding ? <button type="button" className="secondary-button" disabled={busy || recording || (profile.profiles?.length || 0) >= 8} onClick={() => { setAdding(true); setUpdating(null); setName(''); setProfile({ ...profile, samples: 0 }); }}>Add another person</button> : <><label>Your name<input maxLength={80} value={name} disabled={recording || !!updating} onChange={e => setName(e.target.value)} placeholder="Your preferred name" /></label><p className="field-help">Sample {Math.min(profile.samples + 1, 3)} of 3. Read at your own pace in a quiet room, then click Finish sample. You have up to 60 seconds.</p><blockquote>{phrases[Math.min(profile.samples, 2)]}</blockquote><button type="button" className="secondary-button" disabled={busy || recording || !name.trim()} onClick={record}><Mic size={16} />{recording ? (ready ? 'Listening… speak naturally' : 'Preparing microphone…') : 'Record sample'}</button></>}
    {updating && <button type="button" className="text-button" disabled={recording} onClick={async () => { const value = await invoke('cancel_speaker_enrollment'); if (value) { setProfile(value); setUpdating(null); setAdding(false); setNotice('Re-recording cancelled. The saved profile and memories are unchanged.'); } }}>Cancel re-recording</button>}
    <p className="field-help">A clear voice match resumes that person's conversation and uses their personality. An uncertain match uses a separate conversation; focused listening ignores it. Profiles are personalization, not a login or privacy barrier on a shared PC. Existing general memories stay in the general workspace.</p>
    {profile.error && <p role="status">{profile.error}</p>}
    {recording && <><p className="field-help">{mic.name || 'Windows default microphone'}</p><meter aria-label="Enrollment microphone level" min={0} max={1} value={mic.level} style={{ width: '100%' }} /><p role="status">{cancelled ? 'Cancelling recording…' : ready ? (enrolling ? `Listening · ${Math.floor(seconds)} / 60 seconds. Take pauses freely, then click Finish sample.` : 'Listening — speak normally, then pause for two seconds.') : 'Preparing or processing sample — please wait.'}</p>{enrolling && <button type="button" className="secondary-button" disabled={!ready || cancelled} onClick={() => invoke('finish_enrollment')}>Finish sample</button>}<button type="button" className="text-button" disabled={cancelled} onClick={async () => { setCancelled(true); await invoke('stop_voice'); }}>Cancel recording</button></>}
    <p className="field-help">The sentences are suggestions, not a reading test. Bob matches the sound of your voice without checking spelling or grammar. During enrollment, pauses do not end the recording. Finish sample saves it; Cancel recording discards it. Recording ends automatically at 60 seconds. Only encrypted voice features are saved, not recordings. Short phrases can be uncertain. This identifies a likely speaker; it does not lock other people out or approve sensitive actions.</p>
    <button type="button" className="text-button" disabled={busy || recording} onClick={async () => { const value = await invoke('forget_speaker'); if (value) { setProfile(value); setNotice('Voice profile and pending samples deleted.'); } }}><Trash2 size={14} />Delete voice profile / restart enrollment</button>
  </section>;
}
