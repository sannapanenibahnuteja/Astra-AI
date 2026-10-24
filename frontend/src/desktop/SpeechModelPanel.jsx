import { useEffect, useState } from 'react';

export default function SpeechModelPanel({ draft, setDraft, invoke }) {
  const [models, setModels] = useState([]);
  useEffect(() => {
    let alive = true;
    invoke('transcription_models').then(rows => { if (alive && rows) setModels(rows); });
    return () => { alive = false; };
  }, [invoke]);
  return <div>
    <label>Speech recognition model<select value={draft.transcription_model || 'small.en'} onChange={e => setDraft(current => ({ ...current, transcription_model: e.target.value }))}>
      {!models.length && <option value={draft.transcription_model || 'small.en'}>Current model · checking installed models</option>}
      {models.map(model => <option key={model.id} value={model.id} disabled={!model.installed}>{model.label}{!model.installed ? ' · not installed' : ''}</option>)}
    </select></label>
    <p className="field-help">Small English uses less memory. Distil-Whisper Large v3 is a larger English model (756 million parameters); it may improve transcription but can take longer on a CPU. End your voice conversation, choose a model and Save settings. Runtime recognition stays local; changing this does not retrain your saved voice or your LLM. Both models use the same mandatory noise and interruption checks.</p>
  </div>;
}
