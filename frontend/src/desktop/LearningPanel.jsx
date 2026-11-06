import { useEffect, useState } from 'react';

export default function LearningPanel({ draft, setDraft, invoke }) {
  const [status, setStatus] = useState(null);
  const [message, setMessage] = useState('');
  useEffect(() => { let alive = true; invoke('learning_status').then(value => { if (alive) setStatus(value); }); return () => { alive = false; }; }, [invoke]);
  const toggle = (key, label, help, fallback = false) => <div key={key}>
    <label className="toggle-row">{label}<input type="checkbox" checked={draft[key] ?? fallback} onChange={event => { const checked = event.target.checked; setDraft(current => ({ ...current, [key]: checked })); }} /></label>
    <p className="field-help">{help}</p>
  </div>;
  return <div>
    <h3>Conversation, learning and internet</h3>
    {toggle('web_enabled', 'Internet research', 'Bob can look up current questions and read public HTTPS pages. Search sends the current question to a public search engine; saved memories and microphone audio are not included. Answers show source links. Website text cannot authorize PC actions.')}
    {toggle('command_learning', 'Learn common voice requests', 'After a verified successful action, Bob can save a small local shortcut for this profile. Similar supported requests reuse the intent, execute it again and check the result. It never replays a saved “done” reply. Context-dependent and sensitive actions are excluded.')}
    {toggle('semantic_memory', 'Neural memory retrieval', 'Uses the local nomic-embed-text model in Ollama to find related saved facts. Install it with ollama pull nomic-embed-text. Existing lexical memory works if the model is unavailable. It does not train the chat model or upload memories to the web.')}
    {toggle('voice_expression', 'Expressive voice replies', 'Adds controlled changes to pacing and pitch. Auto uses cues in your words for a calm, warm or brighter delivery. Voice support varies; this expresses a conversational style, not feelings experienced by Bob.', true)}
    <label>Voice expression<select value={draft.voice_tone || 'auto'} onChange={event => setDraft(current => ({ ...current, voice_tone: event.target.value }))}>
      <option value="auto">Auto · respond to the conversation</option><option value="warm">Warm</option><option value="calm">Calm</option><option value="bright">Bright</option><option value="serious">Serious</option><option value="neutral">Neutral</option>
    </select></label>
    <p className="field-help">Save settings to apply. Use Listen to this voice under Voice &amp; personality to preview your selected delivery.</p>
    <details><summary>Learned commands · {status?.count || 0}</summary>
      <p className="field-help">{status?.scope || 'Current workspace'}. You can delete these shortcuts without deleting conversations or saved facts.</p>
      {(status?.commands || []).map(row => <p className="field-help" key={row.phrase}>{row.phrase} · used {row.uses} times</p>)}
      <button type="button" className="text-button" onClick={async () => { const value = await invoke('clear_learned_commands'); if (value) setStatus(value); }}>Clear learned commands</button>
      <button type="button" className="text-button" onClick={async () => { if (await invoke('clear_semantic_index')) setMessage('Neural index cleared. Saved facts remain in Memory and can be indexed again while enabled.'); }}>Clear neural memory index</button>
    </details>
    {message && <p className="field-help" role="status">{message}</p>}
  </div>;
}
