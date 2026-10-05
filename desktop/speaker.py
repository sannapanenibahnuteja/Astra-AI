"""Optional local speaker recognition. Identification, never authorization."""
import json
import sys
import threading
from pathlib import Path
import numpy as np

MODEL = '3dspeaker_speech_eres2net_sv_en_voxceleb_16k.onnx'
THRESHOLD = .65  # Cosine similarity, not a probability; needs live-user testing.


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
        if self.path.exists():
            try:
                import win32crypt
                _, data = win32crypt.CryptUnprotectData(self.path.read_bytes(), None, None, None, 0)
                profile = json.loads(data)
                if profile['model'] != MODEL: raise ValueError('Profile model changed; enroll again.')
                profile['vector'] = unit(profile['vector'])
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
        audio = np.asarray(audio, dtype=np.float32).flatten()
        if not np.isfinite(audio).all() or not 8000 <= rate <= 192000:
            raise ValueError('Invalid speaker audio.')
        if len(audio) / rate < 2:
            raise ValueError('Say a full sentence for at least two seconds.')
        # Exclude near-silence from the minimum useful speech duration check.
        blocks = audio[:len(audio)//int(rate*.02)*int(rate*.02)].reshape(-1, int(rate*.02))
        levels = np.sqrt(np.mean(blocks * blocks, axis=1))
        if float(np.sum(levels > max(.0005, float(np.max(levels))*.08)))*.02 < 1.5:
            raise ValueError('Not enough clear speech. Speak closer to the microphone.')
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
            vector = self.embedding(audio, rate)
            if self._name != name: self._draft = []; self._name = name
            if self._draft and float(unit(np.mean(self._draft, axis=0)) @ vector) < THRESHOLD:
                raise ValueError('This sample differs from the earlier samples. Try again in a quiet room.')
            self._draft.append(vector)
            if len(self._draft) >= 3:
                profile = {'name':name, 'model':MODEL, 'vector':unit(np.mean(self._draft, axis=0)).tolist()}
                import win32crypt
                encrypted = win32crypt.CryptProtectData(json.dumps(profile).encode(), 'Bob voice profile', None, None, None, 0)
                temporary = self.path.with_suffix('.tmp')
                temporary.write_bytes(encrypted); temporary.replace(self.path)
                profile['vector'] = unit(profile['vector'])
                self._profile = profile; self._draft = []; self._error = ''
            return self.status()

    def identify(self, audio, rate):
        with self._lock:
            if not self._profile: return {'state':'not_enrolled'}
            try:
                score = float(self._profile['vector'] @ self.embedding(audio, rate))
                matched = score >= THRESHOLD
                return {'state':'matched' if matched else 'unknown', 'name':self._profile['name'] if matched else '',
                        'similarity':round(score,3)}
            except ValueError as error:
                return {'state':'uncertain', 'name':'', 'message':str(error)}
            except Exception:
                return {'state':'unavailable', 'name':'', 'message':'Speaker recognition unavailable; your command can still be transcribed.'}
