import { useEffect, useState } from 'react';
import SpeechModelPanel from './SpeechModelPanel';

export default function AudioIntelligencePanel({ draft, setDraft, invoke }) {
  const [status, setStatus] = useState(null);
  const [voice, setVoice] = useState(null);
  useEffect(() => {
    let alive = true;
    const refresh = async () => {
      const [policy, audio] = await Promise.all([invoke('conversation_status'), invoke('voice_status')]);
      if (alive) { setStatus(policy); setVoice(audio); }
    };
    refresh();
    const timer = setInterval(refresh, 2000);
    return () => { alive = false; clearInterval(timer); };
  }, [invoke]);
  const toggle = (key, label, help, fallback = true) => <div key={key}>
    <label className="toggle-row">{label}<input type="checkbox" checked={draft[key] ?? fallback} onChange={e => { const checked = e.target.checked; setDraft(current => ({ ...current, [key]: checked })); }} /></label>
    <p className="field-help">{help}</p>
  </div>;
  return <section className="glass-card settings-section" aria-label="Conversational audio">
    <div className="settings-title"><div><h2>Conversational audio</h2><p>Local processing, natural turns, visible diagnostics.</p></div></div>
    <SpeechModelPanel draft={draft} setDraft={setDraft} invoke={invoke} />
    {toggle('audio_wake_phrase_only', 'Require Hey Bob for each voice request', 'Recommended. Say “Hey Bob” or “Okay Bob” before each new request or interruption. A wake phrase by itself arms the next request for eight seconds; clicking Voice also arms one request. “Bob, stop” stops a reply; “Stop listening” ends the session. Ordinary chatter and bare “actually” or “shorter” do not interrupt. Saved-voice matching is still required during replies.')}
    {toggle('audio_verified_interruptions', 'Allow verified voice interruptions', 'Requires sustained speech confirmed by a separate local neural detector, your saved voice, and a completed confident request such as “Hey Bob, please stop talking”. During replies, “Hey Bob” alone does not stop playback. Provisional words cannot stop or lower the reply. Off disables voice interruptions entirely. Matching is approximate; completed-speech verification adds delay.')}
    {!draft.speaker_enabled && (draft.audio_verified_interruptions ?? true) && <p className="field-help">Enable Recognize my voice and select your enrolled profile to use voice interruptions. Until then, Bob keeps speaking; the Stop button still works.</p>}
    <p className="field-help">Sound-only playback lowering is disabled. Live provisional captions pause during replies to reduce CPU contention; the microphone and final interruption recognition remain active.</p>
    {toggle('audio_streaming_preview', 'Live provisional captions', 'Incremental local Whisper previews help captions and detect unfinished thoughts. Final transcription alone reaches commands. Uses extra CPU while speaking; disable for lighter operation.')}
    {toggle('audio_pause_learning', 'Learn my speaking pauses', 'Learns only from accepted, confident requests by a matched profile after activation checks. Stores small pause statistics, never recordings or transcripts. It cannot change neural model weights, identity thresholds or interruption rules. Patient or Thinking time takes priority; forget learned pauses below.')}
    {toggle('audio_group_mode', 'Group attention filter', 'Adds a conservative check for speech directed at Bob. Use Recognize my voice and focused listening for primary-user preference. Overlapping voices cannot reliably be separated.', false)}
    <div className="field-grid"><label>Noise suppression<select value={draft.audio_noise_level ?? 1} onChange={e => { const value = Number(e.target.value); setDraft(current => ({ ...current, audio_noise_level: value })); }}>
      <option value={0}>Light · preserve detail</option><option value={1}>Moderate · recommended</option><option value={2}>Stronger · noisy room</option>
    </select></label><label>Action autonomy<select value={draft.autonomy_level ?? 3} onChange={e => { const value = Number(e.target.value); setDraft(current => ({ ...current, autonomy_level: value })); }}>
      <option value={0}>0 · answer and inspect only</option><option value={1}>1 · suggest changes</option><option value={2}>2 · confirm changes</option><option value={3}>3 · automatic low-risk actions</option><option value={4}>4 · trusted routines, same safety checks</option>
    </select></label></div>
    <p className="field-help">Save settings. Noise processing and captions restart with the next voice conversation. Native confirmations still apply to sensitive actions at every level. Camera attention and overlapping-speaker extraction are unavailable. Microphone arrays require calibrated channel delays; a laptop microphone remains supported.</p>
    <div className="connection-banner" role="status">
      {voice?.aec === 'active' ? '10 ms frames · echo cancellation active' : 'Start a voice conversation to inspect live audio'}
      <br />Environment: {voice?.environment || 'not measured'} · estimated SNR: {voice?.snr_db == null ? 'not measured' : `${voice.snr_db} dB`}
      <br />Attention: {status?.attention?.state || 'IDLE'} · playback ducks: {voice?.playback_ducks || 0}
    </div>
    <p className="field-help">Signal labels and attention scores are heuristics. Latencies below are observed processing times, not recognition accuracy or a guarantee.</p>
    {Object.entries(status?.quality?.latency_ms || {}).map(([key, row]) => <p className="field-help" key={key}>{key.replaceAll('_', ' ')}: {Math.round(row.mean)} ms average · {row.samples} samples</p>)}
    {Object.entries(status?.audio_quality?.latency_ms || {}).map(([key, row]) => <p className="field-help" key={key}>{key.replaceAll('_', ' ')}: {Math.round(row.mean)} ms average · {row.samples} samples</p>)}
    <p className="field-help">Actions completed: {status?.quality?.counts?.actions_completed || 0} · tool failures: {status?.quality?.counts?.tool_failures || 0} · verified interruptions: {status?.quality?.counts?.verified_interruptions || 0}</p>
    <button type="button" className="text-button" onClick={async () => setStatus(await invoke('reset_conversation_metrics'))}>Reset session diagnostics</button>
    <button type="button" className="text-button" onClick={() => setDraft(current => ({ ...current, voice_pause_profiles: {} }))}>Forget learned speaking pauses</button>
  </section>;
}
