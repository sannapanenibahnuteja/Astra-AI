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
    def __init__(self, root, filename='voice-profile.dat'):
        self.path = Path(root) / filename
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
            if seconds < 2.5: raise ValueError('That recording was too short. Speak naturally for five to ten seconds; the example wording does not have to match.')
            vector = self.embedding(audio, rate)
            if self._name != name: self._draft = []; self._name = name
            if self._draft and float(unit(np.mean(self._draft, axis=0)) @ vector) < .50:
                raise ValueError('This sample differs from the earlier samples. Try again in a quiet room.')
            self._draft.append(vector)
            if len(self._draft) >= 3:
                consistency = min(float(a @ b) for i,a in enumerate(self._draft) for b in self._draft[i+1:])
                profile = {'name':name, 'model':MODEL, 'balanced_threshold':max(.55,min(THRESHOLD,consistency-.10)), 'vector':unit(np.mean(self._draft, axis=0)).tolist(),
                           'templates':[v.tolist() for v in self._draft]}
                import win32crypt
                encrypted = win32crypt.CryptProtectData(json.dumps(profile).encode(), 'Bob voice profile', None, None, None, 0)
                temporary = self.path.with_suffix('.tmp')
                temporary.write_bytes(encrypted); temporary.replace(self.path)
                profile['vector'] = unit(profile['vector'])
                profile['templates'] = list(self._draft)
                self._profile = profile; self._draft = []; self._error = ''
            return self.status()

    def identify(self, audio, rate, _vector=None, _seconds=None):
        with self._lock:
            if not self._profile: return {'state':'not_enrolled'}
            try:
                if _vector is None:
                    _, seconds = prepare_audio(audio,rate)
                    vector = self.embedding(audio, rate)
                else:
                    vector, seconds = _vector, _seconds
                score = float(self._profile['vector'] @ vector)
                # Keep Strict fixed. Balanced adapts to verified enrollment
                # variation, with a floor and template consensus, never one
                # weak sample or an automatic match for short speech.
                templates = self._profile.get('templates', [])
                consistency = min((float(a @ b) for i,a in enumerate(templates) for b in templates[i+1:]),default=THRESHOLD+.10)
                calibrated = self._profile.get('balanced_threshold', max(.55,min(THRESHOLD,consistency-.10)))
                if not isinstance(calibrated,(int,float)) or not np.isfinite(calibrated): calibrated=THRESHOLD
                threshold = (max(.55,min(self.threshold,calibrated)) if self.threshold <= THRESHOLD else self.threshold) + (.07 if seconds < 2 else 0)
                votes = sum(float(v @ vector) >= threshold-.04 for v in templates)
                matched = score >= threshold and (not templates or votes >= 2)
                return {'state':'matched' if matched else 'unknown', 'name':self._profile['name'] if matched else '',
                        'similarity':round(score,3), 'threshold':round(threshold,3), 'speech_seconds':round(seconds,2)}
            except ValueError as error:
                return {'state':'uncertain', 'name':'', 'message':str(error)}
            except Exception:
                return {'state':'unavailable', 'name':'', 'message':'Speaker recognition unavailable; your command can still be transcribed.'}


class SpeakerProfiles:
    """One shared extractor, encrypted profiles, conservative multi-user selection."""
    def __init__(self, root):
        self.root=Path(root); self.lock=threading.RLock()
        self.extractor=SpeakerProfile(root)
        self.profiles={'legacy':self.extractor} if self.extractor._profile else {}
        for path in sorted(self.root.glob('voice-user-*.dat')):
            profile=SpeakerProfile(root,path.name)
            if profile._profile: self.profiles[path.stem]=profile
        self.threshold=THRESHOLD; self.draft=None; self.active=None

    def status(self):
        with self.lock:
            current=self.draft or self.profiles.get(self.active) or next(iter(self.profiles.values()),self.extractor)
            result=current.status()
            result['profiles']=[{'id':key,'name':p._profile['name'],'personality':p._profile.get('personality','inherit')} for key,p in self.profiles.items()]
            result['active']=self.active
            return result

    def enroll(self,name,audio,rate):
        import uuid
        with self.lock:
            if self.draft is None:
                if len(self.profiles)>=8: raise ValueError('Up to eight voice profiles are supported. Delete an unused profile first.')
                if any(p._profile['name'].casefold()==str(name).strip().casefold() for p in self.profiles.values()):
                    raise ValueError('That name already has a profile. Use a different name, or delete only that profile to record it again.')
                self.draft=SpeakerProfile(self.root,'voice-user-'+uuid.uuid4().hex+'.dat')
                self.draft.embedding=self.extractor.embedding
            result=self.draft.enroll(name,audio,rate)
            if result['enrolled']:
                self.profiles[self.draft.path.stem]=self.draft
                self.draft=None
            return {**self.status(),'name':result['name']}

    def identify(self,audio,rate):
        with self.lock:
            if not self.profiles: return {'state':'not_enrolled'}
            try:
                _,seconds=prepare_audio(audio,rate)
                vector=self.extractor.embedding(audio,rate)
                ranked=[]
                for key,profile in self.profiles.items():
                    profile.threshold=self.threshold
                    result=profile.identify(audio,rate,_vector=vector,_seconds=seconds)
                    ranked.append((result.get('similarity',-1),key,result))
                ranked.sort(key=lambda x:x[0],reverse=True)
                score,key,result=ranked[0]
                if result['state']=='matched' and (len(ranked)<2 or score-ranked[1][0]>=.04):
                    changed=self.active!=key
                    self.active=key
                    return {**result,'profile_id':key,'profile_changed':changed}
                return {**result,'state':'uncertain' if result['state']=='matched' else result['state'],'name':'',
                        'message':'No clear voice match. The active profile was not changed. Try a longer sentence.'}
            except ValueError as error:
                return {'state':'uncertain','name':'','message':str(error)}
            except Exception:
                return {'state':'unavailable','name':'','message':'Voice matching is unavailable. Commands can still be used.'}

    def preferences(self,identity):
        with self.lock:
            profile=self.profiles.get(identity)
            return {'personality_preset':profile._profile['personality'],'personality_traits':{}} if profile and profile._profile.get('personality') else {}

    def personalize(self,identity,personality):
        from desktop.personality import PRESETS
        if personality not in PRESETS and personality!='inherit': raise ValueError('Choose an available personality.')
        with self.lock:
            profile=self.profiles.get(identity)
            if not profile: raise ValueError('Voice profile not found.')
            import win32crypt
            data={**profile._profile,'personality':personality}
            if personality=='inherit': data.pop('personality',None)
            data['vector']=data['vector'].tolist()
            data['templates']=[v.tolist() for v in data.get('templates',[])]
            encrypted=win32crypt.CryptProtectData(json.dumps(data).encode(),'Bob voice profile',None,None,None,0)
            temp=profile.path.with_suffix('.tmp'); temp.write_bytes(encrypted); temp.replace(profile.path)
            if personality=='inherit': profile._profile.pop('personality',None)
            else: profile._profile['personality']=personality
            return self.status()

    def clear(self,identity=None):
        with self.lock:
            if identity is None:
                for profile in self.profiles.values(): profile.clear()
                self.profiles={}; self.active=None
                if self.draft: self.draft.clear()
                self.draft=None; self.extractor.clear()
            else:
                if identity not in self.profiles: raise ValueError('Voice profile not found.')
                self.profiles.pop(identity).clear()
                if self.active==identity: self.active=None
            return self.status()

    def close(self):
        with self.lock:
            self.extractor.close()
            for profile in self.profiles.values(): profile.close()
            if self.draft: self.draft.close()
