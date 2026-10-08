import { useEffect, useState } from 'react';
import ConversationControls from './ConversationControls';
import VoicePicker from './VoicePicker';

const labels = {
  humor: ['Humor / funny', 'Light wit without forcing a joke into every reply.'],
  seriousness: ['Seriousness', 'Higher values prioritize focus and keep humor rare.'],
  discretion: ['Discretion', 'Avoid volunteering private details. This controls wording, not security settings.'],
  honesty: ['Honesty / candor', 'Gentle to frank feedback. Bob must stay truthful at every level.'],
};
const fallback = { humor: 40, seriousness: 50, discretion: 70, honesty: 70 };

export default function PersonalityPanel({ draft, setDraft, invoke }) {
  const [profiles, setProfiles] = useState([]);
  useEffect(() => { let alive = true; invoke('personality_options').then(data => { if (alive && data) setProfiles(data); }); return () => { alive = false; }; }, []);
  const selected = profiles.find(item => item.key === (draft.personality_preset || 'balanced'));
  const values = { ...(selected?.traits || fallback), ...(draft.personality_traits || {}) };
  return <div>
    <VoicePicker draft={draft} setDraft={setDraft} invoke={invoke} />
    <ConversationControls draft={draft} setDraft={setDraft} />
    <label>Personality<select value={draft.personality_preset || 'balanced'} onChange={e => setDraft({ ...draft, personality_preset: e.target.value, personality_traits: {} })}>{profiles.length ? profiles.map(item => <option key={item.key} value={item.key}>{item.label}</option>) : <option value={draft.personality_preset || 'balanced'}>Loading personalities…</option>}</select></label>
    <div className="field-grid">{Object.entries(labels).map(([key, [label, help]]) => <label key={key}>{label} · {values[key]}<input type="range" min="0" max="100" step="5" value={values[key]} onChange={e => setDraft({ ...draft, personality_traits: { ...(draft.personality_traits || {}), [key]: Number(e.target.value) } })} /><small className="field-help">{help}</small></label>)}</div>
    <button type="button" className="text-button" onClick={() => setDraft({ ...draft, personality_traits: {} })}>Reset traits to this personality</button>
    <p className="field-help">Save settings to apply. Say “Be funnier”, “Be serious”, “Be discreet”, “Be more honest”, or “Set your humor to 80” to change style during conversation. Serious topics and action confirmations stay clear.</p>
  </div>;
}
