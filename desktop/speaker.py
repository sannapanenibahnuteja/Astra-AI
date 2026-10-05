"""Optional local speaker recognition. Identification, never authorization."""
import json
import sys
import threading
from pathlib import Path
import numpy as np

MODEL = '3dspeaker_speech_eres2net_sv_en_voxceleb_16k.onnx'
THRESHOLD = .65  # Cosine similarity, not a probability; needs live-user testing.


def prepare_audio(audio, rate):
    """Bound work and trim silence without removing gaps within words."""
    audio = np.asarray(audio, dtype=np.float32).flatten()
    if not isinstance(rate, (int, float)) or not 8000 <= rate <= 192000 or not np.isfinite(audio).all():
        raise ValueError('Invalid speaker audio.')
    rate = int(rate)
    audio = audio[:rate*20]
    if len(audio) < rate*1.2:
        raise ValueError('Say a longer sentence so Bob can recognize your voice.')
    if float(np.mean(np.abs(audio) >= .995)) > .02:
        raise ValueError('Microphone audio is clipping. Lower the input level and try again.')
    audio = audio - float(np.mean(audio))
    width = int(rate*.02)
    blocks = audio[:len(audio)//width*width].reshape(-1,width)
    levels = np.sqrt(np.mean(blocks*blocks,axis=1))
    peak = float(np.max(levels))
    active = np.flatnonzero(levels > max(.0005,peak*.08))
    seconds = len(active)*.02
    if seconds < 1:
        raise ValueError('Not enough clear speech. Speak closer to the microphone.')
    # Stationary broadband hiss is unsuitable for enrollment or matching.
    power = np.mean(np.abs(np.fft.rfft(blocks[:400]*np.hanning(width),axis=1))**2,axis=0)[1:]
    flatness = float(np.exp(np.mean(np.log(power+1e-12)))/(np.mean(power)+1e-12))
    if flatness > .8:
        raise ValueError('Too much broadband noise. Reduce background noise and try again.')
    start = max(0,int(active[0])*width-int(rate*.12))
    end = min(len(audio),(int(active[-1])+1)*width+int(rate*.12),start+rate*8)
    # Normalize softly for microphone gain variation; never amplify silence.
    trimmed = audio[start:end]
    rms = float(np.sqrt(np.mean(trimmed*trimmed)))
    trimmed = np.clip(trimmed*min(4.,max(.25,.05/max(rms,.0001))),-.98,.98)
    return np.ascontiguousarray(trimmed), seconds


def unit(vector):
    vector = np.asarray(vector, dtype=np.float32).flatten()
    norm = float(np.linalg.norm(vector))
    if not len(vector) or not np.isfinite(vector).all() or norm < 1e-6:
        raise ValueError('Voice sample could not produce a usable speaker profile.')
    return vector / norm


class SpeakerProfile:
    def __init__(self, root):
        self.path = Path(root) / 'voice-profile.dat'
        self._lock = threading.RLock()
        self._model = None
        self._timer = None
        self._draft = []
        self._name = ''
        self._profile = None
        self._error = ''
        self.threshold = THRESHOLD
        if self.path.exists():
            try:
                import win32crypt
                _, data = win32crypt.CryptUnprotectData(self.path.read_bytes(), None, None, None, 0)
                profile = json.loads(data)
                if profile['model'] != MODEL: raise ValueError('Profile model changed; enroll again.')
                profile['vector'] = unit(profile['vector'])
                if 'templates' in profile:
                    profile['templates'] = [unit(v) for v in profile['templates']]
                    if len(profile['templates']) != 3 or any(len(v) != len(profile['vector']) for v in profile['templates']):
                        raise ValueError('Invalid voice templates.')
                self._profile = profile
            except Exception:
                self._error = 'Could not read your voice profile. Delete it and enroll again.'

    def status(self):
        with self._lock:
            return {'enrolled':bool(self._profile), 'name':self._profile['name'] if self._profile else '',
                    'samples':len(self._draft), 'required':3, 'error':self._error}

    def clear(self):
        with self._lock:
            self.path.unlink(missing_ok=True)
            self._profile = None; self._draft = []; self._name = ''; self._error = ''
            self.close()
            return self.status()

    def close(self):
        with self._lock:
            if self._timer: self._timer.cancel()
            self._model = None

    def embedding(self, audio, rate):
        import sherpa_onnx
        audio, _ = prepare_audio(audio, rate)
        with self._lock:
            if self._timer: self._timer.cancel()
            try:
                if self._model is None:
                    root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1] / 'dist'))
                    path = root / 'models' / 'speaker' / MODEL
                    if not path.is_file(): raise RuntimeError('Speaker model missing. Install the latest complete Bob release.')
                    config = sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=str(path), num_threads=1, provider='cpu')
                    if not config.validate(): raise RuntimeError('Speaker model configuration is invalid.')
                    self._model = sherpa_onnx.SpeakerEmbeddingExtractor(config)
                stream = self._model.create_stream()
                stream.accept_waveform(sample_rate=rate, waveform=np.ascontiguousarray(audio[:rate*20]))
                stream.input_finished()
                if not self._model.is_ready(stream): raise ValueError('Voice sample is too short.')
                return unit(self._model.compute(stream))
            finally:
                self._timer = threading.Timer(60, self.close)
                self._timer.daemon = True; self._timer.start()

    def enroll(self, name, audio, rate):
        name = str(name).strip()
        if not name or len(name) > 80: raise ValueError('Enter your name, up to 80 characters.')
        with self._lock:
            if self._profile: raise ValueError('Delete the saved profile before enrolling again.')
            _, seconds = prepare_audio(audio,rate)
            if seconds < 3: raise ValueError('Enrollment needs at least three seconds of clear speech. Read the whole sentence.')
            vector = self.embedding(audio, rate)
            if self._name != name: self._draft = []; self._name = name
            if self._draft and min(float(v @ vector) for v in self._draft) < THRESHOLD:
                raise ValueError('This sample differs from the earlier samples. Try again in a quiet room.')
            self._draft.append(vector)
            if len(self._draft) >= 3:
                profile = {'name':name, 'model':MODEL, 'vector':unit(np.mean(self._draft, axis=0)).tolist(),
                           'templates':[v.tolist() for v in self._draft]}
                import win32crypt
                encrypted = win32crypt.CryptProtectData(json.dumps(profile).encode(), 'Bob voice profile', None, None, None, 0)
                temporary = self.path.with_suffix('.tmp')
                temporary.write_bytes(encrypted); temporary.replace(self.path)
                profile['vector'] = unit(profile['vector'])
                profile['templates'] = list(self._draft)
                self._profile = profile; self._draft = []; self._error = ''
            return self.status()

    def identify(self, audio, rate):
        with self._lock:
            if not self._profile: return {'state':'not_enrolled'}
            try:
                _, seconds = prepare_audio(audio,rate)
                vector = self.embedding(audio, rate)
                score = float(self._profile['vector'] @ vector)
                threshold = self.threshold + (.07 if seconds < 2 else 0)
                templates = self._profile.get('templates', [])
                votes = sum(float(v @ vector) >= threshold-.04 for v in templates)
                matched = score >= threshold and (not templates or votes >= 2)
                return {'state':'matched' if matched else 'unknown', 'name':self._profile['name'] if matched else '',
                        'similarity':round(score,3), 'threshold':round(threshold,3), 'speech_seconds':round(seconds,2)}
            except ValueError as error:
                return {'state':'uncertain', 'name':'', 'message':str(error)}
            except Exception:
                return {'state':'unavailable', 'name':'', 'message':'Speaker recognition unavailable; your command can still be transcribed.'}
