export default function ConversationControls({ draft, setDraft }) {
  return <div>
    <div className="field-grid">
      <label>Conversation mode<select value={draft.conversation_mode || 'balanced'} onChange={e => setDraft({ ...draft, conversation_mode: e.target.value })}>
        <option value="balanced">Balanced · natural and practical</option><option value="fast">Fast · answer first</option><option value="tutor">Tutor · examples and explanations</option><option value="calm">Calm · one step at a time</option>
      </select></label>
      <label>Pause before taking a turn<select value={draft.turn_pause_ms || 650} onChange={e => setDraft({ ...draft, turn_pause_ms: Number(e.target.value) })}>
        <option value={450}>Quick · 0.45 seconds</option><option value={650}>Natural · 0.65 seconds</option><option value={1200}>Patient · 1.2 seconds</option><option value={1800}>Thinking time · 1.8 seconds</option>
      </select></label>
    </div>
    <label className="toggle-row">Speak replies as they arrive<input type="checkbox" checked={draft.stream_voice ?? true} onChange={e => setDraft({ ...draft, stream_voice: e.target.checked })} /></label>
    <p className="field-help">Explanations start speaking at sentence boundaries. Action results are spoken after execution. Interrupt normally with “Actually, open calculator” or “Shorter”. Say “Give me more time to think” for longer pauses. Modes change wording; they do not add driving sensors or alter action permissions.</p>
    <label>Names and pronunciation hints<textarea rows={2} maxLength={1000} value={draft.voice_vocabulary || ''} onChange={e => setDraft({ ...draft, voice_vocabulary: e.target.value })} placeholder="Bhanu, Sannapaneni, Hyderabad, my project names" /></label>
    <p className="field-help">Hints help the English recognizer with names and terms. They are not voice training or automatic rewrites of your dictation. Edit or remove them at any time, then save settings.</p>
  </div>;
}
