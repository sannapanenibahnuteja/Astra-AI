"""Private phone audio: bounded local decoding, Whisper, and offline Windows TTS."""
import base64
import io
import tempfile
from pathlib import Path
from desktop.voice import BASE
from desktop.speech_output import spoken_text

RENDER = BASE + r'''
$cfg = [Console]::In.ReadToEnd() | ConvertFrom-Json
$voice = [System.Speech.Synthesis.SpeechSynthesizer]::new()
try {
 $voice.SetOutputToWaveFile([string]$cfg.path)
 $voice.Rate = [int]$cfg.rate
 if ($cfg.voice) { $voice.SelectVoice([string]$cfg.voice) }
 $voice.Speak([string]$cfg.text)
} finally { $voice.Dispose() }
'''


def transcribe(voice, encoded):
    if not isinstance(encoded,str) or len(encoded)>2_800_000: raise ValueError('Record up to twenty seconds at a time.')
    try: raw=base64.b64decode(encoded,validate=True)
    except Exception: raise ValueError('Invalid audio.') from None
    if not raw or len(raw)>2_000_000: raise ValueError('Audio is empty or too large.')
    if not voice._operation.acquire(blocking=False): raise ValueError('Bob is using the microphone. Stop the desktop voice conversation first.')
    voice._cancel.clear(); voice._pause_wake()
    try:
        import av
        import numpy as np
        chunks=[]; count=0
        with av.open(io.BytesIO(raw)) as container:
            resampler=av.AudioResampler(format='s16',layout='mono',rate=16000)
            for frame in container.decode(audio=0):
                if voice._cancel.is_set(): raise ValueError('Voice stopped.')
                for resampled in resampler.resample(frame):
                    array=resampled.to_ndarray().flatten();count+=len(array)
                    if count>480000: raise ValueError('Audio exceeds thirty seconds.')
                    chunks.append(array)
        if not chunks: raise ValueError('No audio found.')
        audio=np.concatenate(chunks).astype(np.float32)/32768.0
        return voice.transcribe(audio)
    finally:
        voice._update(phase='idle');voice._operation.release()


def render(voice, text, rate=0):
    if not isinstance(text,str) or not 0<len(text)<=5000: raise ValueError('Invalid speech text.')
    if not voice._operation.acquire(blocking=False): raise ValueError('Bob is busy speaking or listening.')
    voice._cancel.clear();voice._speech_interrupted.clear();voice._pause_wake();voice._update(phase='speaking')
    try:
        options=dict(getattr(voice,'voice_options',{}))
        root=getattr(voice,'config_root',None)
        if root and options.get('voice_provider','auto')!='windows':
            from desktop.speech_output import neural_audio
            try:
                data=neural_audio(spoken_text(text),root,options.get('neural_voice',''),rate)
                if voice._cancel.is_set(): raise ValueError('Voice stopped.')
                if data: return base64.b64encode(data).decode()
            except Exception:
                voice._update(error='Neural phone voice unavailable; using Windows speech.')
        data=voice._speech_worker().render(spoken_text(text),rate,options.get('windows_voice',''),voice._cancel,voice._speech_interrupted)
        if not data or voice._cancel.is_set(): raise ValueError('Voice stopped.')
        return base64.b64encode(data).decode()
    finally:
        voice._update(phase='idle');voice._operation.release()
