import { useEffect, useState } from 'react';
import { Mic } from 'lucide-react';

export default function MicrophonePanel({ invoke, busy, setNotice, setDraft }) {
  const [device, setDevice] = useState(null);
  const [stage, setStage] = useState('');
  const [noiseReady, setNoiseReady] = useState(false);
  const [progress, setProgress] = useState({ level: 0, seconds: 0 });
  useEffect(() => { let alive = true; invoke('microphone_status').then(value => { if (alive) setDevice(value); }); return () => { alive = false; }; }, [invoke]);
  useEffect(() => {
    if (!stage) return;
    let alive = true;
    const timer = setInterval(async () => {
      const value = await invoke('voice_status');
      if (alive && value) setProgress({ level: value.level || 0, seconds: value.calibration_seconds || 0 });
    }, 100);
    return () => { alive = false; clearInterval(timer); };
  }, [stage, invoke]);
  async function measure(next) {
    setStage(next); setProgress({ level: 0, seconds: 0 });
    try {
      const result = await invoke('calibrate_microphone', next);
      if (result?.cancelled) { setNotice('Calibration cancelled. Your previous calibration is kept.'); return; }
      if (result?.noise_ready) { setNoiseReady(true); setNotice('Room noise measured. Click Record my normal voice and speak for ten seconds.'); }
      if (result?.profile) {
        setDraft(previous => ({ ...previous, microphone_calibration: result.profile }));
        setDevice({ name: result.profile.name, calibrated: true, gain: result.profile.gain });
        setNoiseReady(false); setNotice('Microphone calibrated and saved. Now record your three voice samples at your normal speaking volume.');
      }
    } finally { setStage(''); }
  }
  return <section className="glass-card settings-section"><div className="settings-title"><Mic size={21} /><div><h2>Calibrate my microphone</h2><p>Match listening to your laptop microphone and room.</p></div></div>
    <p>{device?.name || 'Checking the Windows default microphone…'}{device?.calibrated ? ` · calibrated · ${device.gain}× input gain` : ' · not calibrated for this input'}</p>
    <p className="field-help">Stop voice conversation first. Step 1: stay quiet for three seconds. Step 2: speak normally for ten seconds at your usual distance. Only device levels are saved; audio is discarded. Repeat after changing microphones or rooms.</p>
    <button type="button" className="secondary-button" disabled={busy || !!stage} onClick={() => measure('noise')}>Measure room noise</button>
    <button type="button" className="secondary-button" disabled={busy || !!stage || !noiseReady} onClick={() => measure('speech')}>Record my normal voice</button>
    {stage && <div role="status"><p>{stage === 'noise' ? 'Stay quiet — measuring room noise' : 'Speak now — tell Bob about your day'} · {progress.seconds.toFixed(1)} / {stage === 'noise' ? 3 : 10} seconds</p><meter aria-label="Calibration microphone level" min={0} max={1} value={progress.level} style={{ width: '100%' }} /><button type="button" className="text-button" onClick={() => invoke('stop_voice')}>Cancel calibration</button></div>}
  </section>;
}
