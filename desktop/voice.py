"""Offline command transcription, constrained wake grammar and Windows speech output."""
import io
import base64
import json
import queue
import logging
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import wave
from collections import deque

BASE = "$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[Text.UTF8Encoding]::new(); Add-Type -AssemblyName System.Speech; "
SPEAK = BASE + r"""
$cfg = [Console]::In.ReadToEnd() | ConvertFrom-Json
$voice = [System.Speech.Synthesis.SpeechSynthesizer]::new()
try { $voice.Rate = $cfg.rate; $voice.Speak([string]$cfg.text) } finally { $voice.Dispose() }
"""
RENDER = BASE + r"""
$cfg = [Console]::In.ReadToEnd() | ConvertFrom-Json
$voice = [System.Speech.Synthesis.SpeechSynthesizer]::new()
$buffer = [IO.MemoryStream]::new()
try {
 $voice.Rate = $cfg.rate
 if ($cfg.voice) { $voice.SelectVoice([string]$cfg.voice) }
 $voice.SetOutputToWaveStream($buffer)
 $voice.Speak([string]$cfg.text)
 $voice.SetOutputToNull()
 [Console]::Write([Convert]::ToBase64String($buffer.ToArray()))
} finally { $voice.Dispose(); $buffer.Dispose() }
"""
WAKE = BASE + r"""
$info = [System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers() | Where-Object { $_.Culture.Name -like 'en-*' } | Select-Object -First 1
if (!$info) { throw 'Wake words require a Windows English Speech language pack. The microphone button still works without it.' }
$engine = [System.Speech.Recognition.SpeechRecognitionEngine]::new($info)
try {
 $choices = [System.Speech.Recognition.Choices]::new([string[]]@('hey bob','okay bob'))
 $builder = [System.Speech.Recognition.GrammarBuilder]::new($choices)
 $builder.Culture = $info.Culture
 $engine.LoadGrammar([System.Speech.Recognition.Grammar]::new($builder))
 $engine.SetInputToDefaultAudioDevice()
 [Console]::WriteLine('READY'); [Console]::Out.Flush()
 while ($true) {
  $result = $engine.Recognize([TimeSpan]::FromSeconds(3))
  if ($result -and $result.Confidence -ge 0.80) { [Console]::WriteLine('WAKE'); [Console]::Out.Flush(); break }
 }
} finally { $engine.Dispose() }
"""

def model_path(identity='small.en'):
    from desktop.speech_models import path_for
    return path_for(identity)


def transcript_result(segments):
    segments = list(segments)
    accepted = [s for s in segments if s.no_speech_prob < .65 and s.avg_logprob > -1.2]
    text = ' '.join(s.text.strip() for s in accepted).strip()
    words = [w.probability for s in accepted for w in (s.words or [])]
    confidence = float(sum(words) / len(words)) if words else 0.0
    # Never automatically execute marginal recognition. Scores are heuristic, not guarantees.
    review = bool(text) and (confidence < .65 or any(s.avg_logprob < -.7 for s in accepted)
                            or any(probability < .25 for probability in words))
    return {'text': text, 'confidence': round(confidence, 3), 'needs_review': review, 'language': 'en',
            'word_confidence_min': min(words) if words else 0.}


class Voice:
    def __init__(self):
        self._lock = threading.RLock()
        self._operation = threading.Lock()
        self._model_lock = threading.Lock()
        self._final_decoding = threading.Event()
        from desktop.audio_pipeline import DEFAULT_AUDIO
        from desktop.conversational import PauseModel, QualityMetrics
        self.audio_options = dict(DEFAULT_AUDIO)
        self.target_extractor = None # Explicitly installed plugin only; no fake separation.
        self.pause_model = PauseModel()
        self.metrics = QualityMetrics()
        self._process = None
        self._wake_process = None
        self._cancel = threading.Event()
        self._finish_enrollment = threading.Event()
        self._verified_samples = deque(maxlen=2)
        self.microphone_calibration = {}
        self._calibration_noise = None
        self._closed = threading.Event()
        self._hold = False
        self._enabled = False
        self._thread = None
        self._callback = None
        self._model = None
        self.transcription_model = 'small.en'
        self._release = None
        self._release_serial = 0
        self._warming = None
        self._duplex = None
        self._duplex_failed = False
        self._duplex_lock = threading.RLock()
        self._speech_interrupted = threading.Event()
        self.on_interrupt = None
        self.response_active = False
        self.interruption_owner = None
        self._interrupt_context = None
        self._interrupt_proofs = {}
        self._delivered_interrupts = {}
        self._wake_until = 0.
        self._wake_from_interruption = False
        self.speaker = None
        self.speaker_enabled = False
        self.speaker_focus = ''
        self.last_speaker = {'state':'not_enrolled'}
        self._tts = None
        self._state = {'phase': 'idle', 'level': 0, 'wake': 'off', 'error': '', 'aec': 'off'}

    def status(self):
        with self._lock:
            value = dict(self._state)
        engine = self._duplex
        value['pending_audio'] = bool(engine and (not engine.utterances.empty() or engine.detector.started or getattr(engine, 'pending_verifications', 0)))
        value['verification_pending'] = bool(engine and getattr(engine, 'pending_verifications', 0))
        if engine:
            value.update(recording_command=bool(engine.detector.started), captured_seconds=round(len(engine.detector.frames)*.01,2),
                         interruptions=engine.interruptions, completed_turns=engine.completed_turns,
                         raw_rms=round(engine.raw_rms,6), clean_rms=round(engine.clean_rms,6))
            value['audio_driver_glitches']=getattr(engine,'stream_glitches',0)
            if isinstance(getattr(engine,'options',None),dict):
                value.update(engine.environment.current, playback_ducks=engine.ducks,
                             audio_frame_ms=10, capture_rate=48000,
                             beamforming=bool(engine.options['audio_array_delays']))
        return value

    def _update(self, **values):
        with self._lock:
            self._state.update(values)

    @staticmethod
    def _spawn(script, stdin=subprocess.PIPE):
        executable = os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), r'System32\WindowsPowerShell\v1.0\powershell.exe')
        return subprocess.Popen([executable, '-NoProfile', '-NonInteractive', '-Command', script], stdin=stdin,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',
                                creationflags=subprocess.CREATE_NO_WINDOW)

    def _pause_wake(self):
        with self._lock:
            if self._wake_process and self._wake_process.poll() is None:
                self._wake_process.terminate()
            self._update(wake='paused' if self._enabled else 'off')

    def session(self, active):
        if active and not self._hold:self.arm_wake()
        if not active:self._wake_until=0.
        self._hold = bool(active)
        if active:
            self._pause_wake()
            root=getattr(self,'config_root',None)
            provider=getattr(self,'voice_options',{}).get('voice_provider','auto')
            if root and provider!='azure':
                from desktop.voice_choices import ready
                if provider=='windows' or not ready(root):
                    threading.Thread(target=self._warm_speech,daemon=True).start()
        else:
            with self._duplex_lock:
                if self._duplex:
                    self._duplex.close()
                    self._duplex = None
                self._duplex_failed = False
            self._update(aec='off')
            if self._model_lock.acquire(blocking=False):
                try:
                    if self._closed.is_set():
                        self._cancel_release()
                        self._model = None
                    elif self._model is not None:
                        self._defer_release()
                finally:
                    self._model_lock.release()
        return True

    def _speech_worker(self):
        from desktop.tts_worker import WindowsSpeech
        with self._lock:
            if self._tts is None: self._tts=WindowsSpeech(self._spawn)
            return self._tts

    def _warm_speech(self):
        try:
            if not self._closed.is_set():
                worker=self._speech_worker(); worker.warm()
                if self._closed.is_set() or not self._hold: worker.close()
        except Exception: pass  # Rendering retries and surfaces any real failure.

    def begin_response(self,context):
        with self._lock:
            self._interrupt_context=context
            self._interrupt_proofs.clear();self._delivered_interrupts.clear()

    def finish_response(self,context):
        with self._lock:
            if self._interrupt_context==context:
                self._interrupt_context=None
                self._interrupt_proofs.clear();self._delivered_interrupts.clear()

    def consume_interrupt(self,permit,context):
        # An opaque, one-use permit never crosses the public desktop API.
        if type(permit) is not object:return False
        with self._lock:
            missing=object()
            issued=self._delivered_interrupts.pop(permit,missing)
            return issued is not missing and issued==context and self._interrupt_context==context

    def _barge_in(self,engine=None):
        with self._lock:
            if engine is None or engine is not self._duplex:return False
            proof=self._interrupt_proofs.pop(engine.last_interrupted_serial,None)
            if (not proof or proof['context']!=self._interrupt_context
                    or proof['signature']!=self._speaker_signature()
                    or proof['owner']!=self._interruption_target()
                    or time.monotonic()-proof['at']>5):return False
            permit=proof['permit']
            self._delivered_interrupts[permit]=proof['context']
            while len(self._delivered_interrupts)>4:self._delivered_interrupts.pop(next(iter(self._delivered_interrupts)))
        if self.on_interrupt and self.on_interrupt(permit) is False:return False
        self._speech_interrupted.set()
        if self._tts:self._tts.interrupt()
        with self._lock:
            if self._process and self._process.poll() is None:self._process.terminate()
        return True

    def _ensure_duplex(self):
        if not self._hold or self._duplex_failed:
            return None
        with self._duplex_lock:
            if self._duplex:
                if self._duplex.error:
                    raise RuntimeError(self._duplex.error)
                return self._duplex
            engine = None
            try:
                from desktop.duplex_audio import DuplexAudio
                engine = DuplexAudio(lambda:self._barge_in(engine), self._update, self.audio_options)
                engine.microphone_calibration = dict(self.microphone_calibration)
                engine.verify_interrupt = self._focus_accept if self.speaker_enabled else None
                self.configure_interruptions(engine)
                engine.detector.quiet_frames = getattr(self,'turn_pause_ms',650)//10
                engine.detector.adaptive = True
                if self.audio_options['audio_streaming_preview']:
                    from desktop.streaming_asr import PreviewWorker
                    engine.preview = PreviewWorker(self._preview_decode, lambda frame,text,stable:self._preview_publish(engine,frame,text,stable))
                engine.start()
                self._duplex = engine
                return engine
            except Exception as exc:
                if engine:
                    engine.close()
                self._duplex_failed = True
                self._update(aec='unavailable', error='Hands-free interruption unavailable; using turn-by-turn voice. ' + str(exc)[:200])
                return None

    def configure_interruptions(self, engine):
        # No preference combination may fall back to sound-only interruption.
        # Turning interruptions off means off, never weaker verification.
        engine.authorize_interrupt = self._authorize_interrupt
        if isinstance(getattr(engine,'options',None),dict):engine.options['audio_fast_barge_in'] = False
        engine.response_active = lambda: self.response_active or self.status().get('phase')=='speaking'

    def arm_wake(self, from_interruption=False):
        self._wake_until=time.monotonic()+8
        self._wake_from_interruption=bool(from_interruption)
        self._update(wake_gate='armed')
        return True

    def wake_window_open(self):
        return time.monotonic()<self._wake_until and not self.response_active

    def filter_voice_trigger(self,result,armed=None):
        if not self.audio_options['audio_wake_phrase_only'] or not result.get('text') or result.get('ignored'):return result
        from desktop.voice_triggers import split_wake,session_stop
        from desktop.interruption import reply_stop_control
        wake,payload=split_wake(result['text'])
        reliable=result.get('confidence',0)>=.80 and not result.get('needs_review',True)
        if session_stop(result['text']) and reliable:
            self._wake_until=0.
            return {**result,'text':'stop listening'}
        if wake and reliable:
            if not payload:
                self.arm_wake(result.get('interrupted_reply',False))
                return {**result,'text':'','wake_triggered':True}
            self._wake_until=0.
            self._update(wake_gate='waiting')
            return {**result,'text':payload}
        # Runtime snapshots permission before capture/decode. A slow ASR must
        # not expire a command already spoken after an explicit activation.
        if (self.wake_window_open() if armed is None else armed) and not self.response_active:
            if self._wake_from_interruption and reply_stop_control(result['text']) and reliable:
                self._wake_until=0.
                return {**result,'text':'','interruption_control':'stop_reply'}
            if not result.get('needs_review') and result.get('confidence',0)>=.65:self._wake_until=0.
            return result
        self._update(wake_gate='waiting')
        return {**result,'text':'','ignored':True,'trigger_required':True}

    def _interruption_target(self):
        if not self.speaker_enabled or not self.speaker:return None
        target=self.speaker_focus if self.speaker_focus not in ('','*') else (self.interruption_owner or getattr(self.speaker,'active',None))
        return target if isinstance(target,str) and target else None

    def _decode_interruption(self, turn, partial):
        if self._cancel.is_set() or self._model is None:return None
        acquired=self._model_lock.acquire(blocking=False) if partial else self._model_lock.acquire(timeout=2)
        if not acquired:return None
        try:
            if self._model is None or self._cancel.is_set():return None
            import numpy as np
            from desktop.audio_pipeline import recognition_samples
            audio=recognition_samples(turn.audio[-48000*8:] if partial else turn.audio)
            rms=float(np.sqrt(np.mean(audio*audio)))
            audio=np.clip(audio*min(8.,max(1.,.035/max(rms,.0001))),-1,1)
            segments,_=self._model.transcribe(audio,language='en',beam_size=1 if partial else 3,
                vad_filter=True,word_timestamps=True,condition_on_previous_text=False,
                temperature=0,max_new_tokens=64 if partial else 256)
            return transcript_result(segments)
        finally:self._model_lock.release()

    def _authorize_interrupt(self, turn, partial=False):
        from desktop.interruption import intended_interruption
        if partial or not self.audio_options['audio_verified_interruptions'] or turn.interruption_ready is not True:
            return False
        owner=self._interruption_target()
        if not owner:
            self._update(interruption_state='blocked',interruption_reason='Enable saved-voice recognition and choose your voice to interrupt.')
            return False
        from desktop.voice_evidence import interruption_speech
        if not interruption_speech(turn.audio,self.audio_options['audio_room_mode']):
            self.metrics.event('interrupt_non_speech_rejected')
            self._update(interruption_state='ignored', interruption_reason='Reply continues: no clear spoken interruption.')
            return False
        signature=self._speaker_signature()
        context=self._interrupt_context
        match=self._match_speaker(turn.speaker,48000,owner)
        if (signature!=self._speaker_signature() or match.get('state')!='matched' or match.get('profile_id')!=owner):
            self.metrics.event('interrupt_speaker_rejected')
            self._update(interruption_state='ignored', interruption_reason='Reply continues: the selected saved voice did not match.')
            return False
        result=self._decode_interruption(turn,partial)
        if (not result or not intended_interruption(result.get('text',''),result.get('confidence',0),result.get('needs_review',True),
                                                   require_trigger=True)
                or result.get('word_confidence_min',result.get('confidence',0)) < .65
                or signature!=self._speaker_signature() or owner!=self._interruption_target() or context!=self._interrupt_context
                or self._cancel.is_set()):
            self.metrics.event('interrupt_intent_rejected')
            self._update(interruption_state='ignored',interruption_reason='Reply continues. Say “Hey Bob, please stop talking” in your saved voice.')
            return False
        with self._lock:
            self._verified_samples.append((turn.speaker,signature,dict(match)))
            self._interrupt_proofs[turn.serial]={'permit':object(),'context':context,'signature':signature,'owner':owner,'at':time.monotonic()}
            while len(self._interrupt_proofs)>4:self._interrupt_proofs.pop(next(iter(self._interrupt_proofs)))
        if not partial:turn.recognition={'result':result,'signature':signature,'profile':owner}
        self._update(interruption_state='accepted',interruption_reason='Saved voice and clear interruption matched.')
        self.metrics.event('interrupt_intent_accepted')
        return True

    def _preview_decode(self, frame):
        # Preview inference is disposable. Never load a model or wait behind
        # final recognition; never dispatch or select a user from partial text.
        if self.response_active or self.status().get('phase')=='speaking':return None
        if self._final_decoding.is_set() or self._cancel.is_set() or not self._hold or self._model is None:return None
        if self.speaker_enabled and not self._focus_accept(frame.speaker):return None
        if not self._model_lock.acquire(blocking=False):return None
        try:
            if self._final_decoding.is_set() or self._model is None:return None
            import numpy as np
            from desktop.audio_pipeline import recognition_samples
            audio=recognition_samples(frame.audio)
            segments,_=self._model.transcribe(audio,language='en',beam_size=1,vad_filter=True,
                hotwords=getattr(self,'vocabulary','') or None,condition_on_previous_text=False,
                temperature=0,max_new_tokens=48)
            return ' '.join(part.text.strip() for part in segments if part.no_speech_prob<.6 and part.avg_logprob> -1).strip()
        finally:self._model_lock.release()

    def _preview_publish(self, engine, frame, text, stable):
        from desktop.conversational import semantic_hint
        if engine.closed.is_set() or frame.serial != engine.turn_serial or not engine.detector.started:return
        if self.audio_options['audio_wake_phrase_only'] and time.monotonic()>=self._wake_until:
            from desktop.voice_triggers import split_wake
            if not split_wake(text)[0]:return
        hint=semantic_hint(stable or text)
        # Only an incomplete, fresh preview may extend a pause. It cannot
        # shorten the user's selected pause or authorize an operation.
        engine.detector.semantic_pause_ms=hint['pause_ms'] if not hint['complete'] else 0
        self._update(partial_text=text[:500],partial_stable=stable[:500],predicted_domain=hint['domain'])

    def configure(self, enabled):
        self._enabled = bool(enabled)
        if not enabled:
            self._pause_wake()
        return True

    def start(self, callback, enabled=True):
        self._callback = callback
        self.configure(enabled)
        if self._thread is None:
            self._thread = threading.Thread(target=self._wake_loop, daemon=True)
            self._thread.start()

    def _wake_loop(self):
        while not self._closed.wait(.25):
            if not self._enabled or self._hold or self._operation.locked():
                continue
            process = self._spawn(WAKE, stdin=subprocess.DEVNULL)
            with self._lock:
                self._wake_process = process
                if self._hold or not self._enabled or self._closed.is_set():
                    process.terminate()
            self._update(wake='starting')
            triggered = False
            for line in process.stdout:
                if line.strip().lstrip('\ufeff') == 'READY':
                    self._update(wake='ready', error='')
                elif line.strip() == 'WAKE':
                    triggered = True
            error = process.stderr.read()
            process.wait()
            with self._lock:
                if self._wake_process is process:
                    self._wake_process = None
            if triggered and self._enabled and not self._hold and not self._closed.is_set():
                self.session(True)
                try:
                    self._callback()
                except Exception as exc:
                    self._update(error=str(exc)[:400])
                    self.session(False)
            elif error and not self._hold and self._enabled:
                self._update(wake='error', error=error.strip()[:400])
                self._closed.wait(10)

    def stop(self):
        with self._lock:
            self._interrupt_proofs.clear();self._delivered_interrupts.clear()
        self._cancel.set()
        if self._tts: self._tts.close()
        if self._duplex:
            self._duplex.cancel_playback()
            self._duplex.discard()
        with self._lock:
            if self._process and self._process.poll() is None:
                self._process.terminate()
        return True

    def finish_enrollment(self):
        if not self.status().get('enrolling'):
            return False
        self._finish_enrollment.set()
        return True

    def microphone_status(self):
        import sounddevice as sd
        from desktop.microphone import input_device, gain_for
        _, device, key = input_device(sd)
        return {'name':device.get('name','Default microphone'),
                'calibrated': bool(self.microphone_calibration and self.microphone_calibration.get('device') == key),
                'gain': gain_for(self.microphone_calibration, key)}

    def calibrate_microphone(self, stage):
        import numpy as np
        import sounddevice as sd
        from desktop.microphone import input_device, rms_levels, calibration
        if stage not in ('noise','speech'): raise ValueError('Choose the room-noise or voice calibration step.')
        if not self._operation.acquire(blocking=False): raise ValueError('Stop the current voice operation before calibration.')
        self._cancel.clear(); self._pause_wake()
        self._update(phase='preparing', error='')
        try:
            index, device, key = input_device(sd)
            if stage == 'speech' and (not self._calibration_noise or self._calibration_noise[0] != key):
                raise ValueError('Measure room noise first. Repeat it if the microphone changed.')
            if stage == 'noise': self._calibration_noise = None
            rate = int(device['default_samplerate']); chunk = int(rate*.05)
            seconds = 3 if stage == 'noise' else 10
            frames = []
            with sd.InputStream(device=index, samplerate=rate, channels=1, dtype='float32', blocksize=chunk) as stream:
                self._update(phase='calibrating', microphone_stage=stage, calibration_seconds=0,
                             input_device=device.get('name','Default microphone'))
                for tick in range(seconds*20):
                    if self._cancel.is_set(): return {'cancelled': True}
                    block, overflowed = stream.read(chunk)
                    if overflowed: raise ValueError('Microphone capture fell behind. Close busy audio apps and retry calibration.')
                    frames.append(block.copy())
                    rms = float(np.sqrt(np.mean(block*block)))
                    self._update(level=min(1,rms*100), calibration_seconds=round((tick+1)*.05,1))
            audio = np.concatenate(frames)
            if self._cancel.is_set(): return {'cancelled': True}
            if stage == 'noise':
                noise = float(np.percentile(rms_levels(audio,rate),70))
                self._calibration_noise = (key,noise)
                return {'noise_ready':True,'name':device.get('name','Default microphone')}
            profile = calibration(key,device.get('name','Default microphone'),self._calibration_noise[1],audio,rate)
            self._calibration_noise = None
            return {'profile':profile}
        finally:
            self._update(phase='idle',level=0,microphone_stage='',calibration_seconds=0)
            self._operation.release()

    def close(self):
        self._closed.set()
        self.configure(False)
        self.stop()
        self.session(False)
        if self.speaker: self.speaker.close()

    def _run(self, script, data, timeout):
        process = self._spawn(script)
        with self._lock:
            self._process = process
        try:
            output, error = process.communicate(json.dumps(data), timeout=timeout)
            if process.returncode:
                if self._cancel.is_set() or self._speech_interrupted.is_set():
                    return ''
                raise RuntimeError(error.strip()[:600] or 'Speech stopped.')
            return output.lstrip('\ufeff').strip()
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise RuntimeError('Windows speech timed out. Check your default audio device.')
        finally:
            with self._lock:
                if self._process is process:
                    self._process = None

    def _load_model(self):
        from faster_whisper import WhisperModel
        if self._model is None:
            path = model_path() if self.transcription_model == 'small.en' else model_path(self.transcription_model)
            self._model = WhisperModel(str(path), device='cpu', compute_type='int8', cpu_threads=2, num_workers=1, local_files_only=True)

    def _cancel_release(self):
        if self._release: self._release.cancel()
        self._release_serial += 1

    def _defer_release(self):
        self._cancel_release()
        self._release = threading.Timer(180 if self._hold else 60, self._unload, args=(self._release_serial,))
        self._release.daemon = True
        self._release.start()

    def prepare_transcription(self):
        """Load only local model weights in the background; never opens the mic."""
        with self._lock:
            if self._closed.is_set() or (self._warming and self._warming.is_alive()): return False
            self._warming = threading.Thread(target=self._warm_transcription, daemon=True)
            self._warming.start()
        return True

    def _warm_transcription(self):
        with self._model_lock:
            if self._closed.is_set() or not self._hold: return
            self._cancel_release()
            try:
                self._load_model()
            except Exception:
                logging.exception('Local speech preload failed; normal capture will retry')
            finally:
                if self._closed.is_set(): self._model = None
                else: self._defer_release()

    def transcribe(self, audio):
        self._final_decoding.set()
        try:
            return self._transcribe_final(audio)
        finally:self._final_decoding.clear()

    def _transcribe_final(self, audio):
        with self._model_lock:
            self._cancel_release()
            if self._model is None: self._update(phase='loading')
            self._load_model()
            self._update(phase='transcribing', level=0)
            try:
                segments, _ = self._model.transcribe(audio, language='en', beam_size=5, vad_filter=True,
                    hotwords=getattr(self,'vocabulary','') or None,
                    condition_on_previous_text=False, word_timestamps=True, temperature=0,
                    vad_parameters={'threshold': .35, 'min_speech_duration_ms': 100,
                                    'min_silence_duration_ms': 500, 'speech_pad_ms': 200})
                result = transcript_result(segments)
                # Turn detection has already found speech. Silero can still
                # discard a quiet/short command; retry once, never on silence
                # or hiss and never after cancellation. Keep decoder confidence
                # and no-speech checks for the retry as well.
                if not result['text'] and not self._cancel.is_set():
                    retry = self._retry_audio(audio)
                    if retry is not None:
                        self._update(phase='transcribing')
                        segments, _ = self._model.transcribe(retry, language='en', beam_size=5, vad_filter=False,
                            hotwords=getattr(self,'vocabulary','') or None, condition_on_previous_text=False,
                            word_timestamps=True, temperature=0)
                        result = transcript_result(segments)
                        logging.info('Speech retry finished: text_present=%s review=%s', bool(result['text']), result['needs_review'])
                self._update(voice_notice='' if result['text'] else 'Speech was captured but no words were decoded. Check your input microphone and try again.')
                return result
            finally:
                if self._closed.is_set(): self._model = None
                else: self._defer_release()

    @staticmethod
    def _retry_audio(audio):
        if audio is None: return None
        import numpy as np
        from faster_whisper.audio import decode_audio
        from desktop.duplex_audio import acoustic_speech
        if hasattr(audio, 'seek'): audio.seek(0)
        samples = audio if isinstance(audio, np.ndarray) else decode_audio(audio, sampling_rate=16000)
        samples = np.asarray(samples, dtype=np.float32).flatten()[:16000*20]
        if not np.isfinite(samples).all(): return None
        frames = samples[:len(samples)//320*320].reshape(-1,320)
        voiced = sum(float(np.sqrt(np.mean(frame*frame))) >= .0004 and acoustic_speech(frame) for frame in frames)
        return samples if voiced >= 15 else None

    def _unload(self, serial=None):
        with self._model_lock:
            if serial is None or serial == self._release_serial:
                self._model = None

    def _neural_render(self, text, config_root, voice_override='', rate=0):
        from desktop.speech_output import neural_audio
        result = queue.Queue(maxsize=1)
        def render():
            try:
                result.put((neural_audio(text, config_root, voice_override, rate), None))
            except Exception as exc:
                result.put((None, exc))
        threading.Thread(target=render, daemon=True).start()
        while not self._cancel.is_set() and not self._speech_interrupted.is_set():
            try:
                data, error = result.get(timeout=.05)
                if error:
                    raise error
                return data
            except queue.Empty:
                continue
        return None

    def _match_speaker(self, audio, rate, target=None):
        profiles=getattr(self.speaker,'profiles',{})
        if target and isinstance(profiles,dict) and target in profiles:
            return self.speaker.identify_target(target,audio,rate)
        return self.speaker.identify(audio,rate,select=False)

    def _focus_accept(self, audio, rate=48000):
        if not self.speaker_enabled: return True
        if not self.speaker: return False
        signature = self._speaker_signature()
        target=self.speaker_focus if self.speaker_focus not in ('','*') else None
        match=self._match_speaker(audio,rate,target)
        if signature != self._speaker_signature():return False
        logging.info('Speaker check: state=%s speech_seconds=%s similarity=%s threshold=%s',
                     match.get('state'),match.get('speech_seconds'),match.get('similarity'),match.get('threshold'))
        accepted = match.get('state')=='matched' and (not self.speaker_focus or self.speaker_focus=='*' or match.get('profile_id')==self.speaker_focus)
        if accepted:
            with self._lock:
                self._verified_samples.append((audio, signature, dict(match)))
        return accepted

    def _speaker_signature(self):
        profiles = getattr(self.speaker, 'profiles', None)
        enrolled = tuple(sorted((key, id(value)) for key, value in profiles.items())) if isinstance(profiles, dict) else ()
        return (id(self.speaker), self.speaker_enabled, self.speaker_focus, getattr(self.speaker, 'threshold', None), enrolled)

    def _verified_match(self, audio):
        with self._lock:
            for index, item in enumerate(self._verified_samples):
                if item[0] is audio and item[1] == self._speaker_signature():
                    del self._verified_samples[index]
                    return item[2]
        return None

    def _recognize_speaker(self, result, audio, rate, enrollment, identity_test=False):
        if self._cancel.is_set(): return {'text':'', 'confidence':0}
        if self.speaker_enabled and not self.speaker and enrollment is None:
            return {'text':'','confidence':0,'needs_review':False,'ignored':True,'speaker':{'state':'unavailable','message':'Enroll your voice in Settings before using saved-voice listening.'}}
        if self.speaker and (self.speaker_enabled or enrollment is not None):
            if enrollment is not None:
                if isinstance(enrollment, dict):
                    return {'enrollment':self.speaker.enroll(enrollment['name'], audio, rate, identity=enrollment['identity'])}
                return {'enrollment':self.speaker.enroll(enrollment, audio, rate)}
            focus=(self.speaker_focus or '*') if self.speaker_enabled and not identity_test else ''
            self._update(phase='verifying')
            self.last_speaker = (self._verified_match(audio) or self._match_speaker(audio, rate, focus if focus!='*' else None)) if focus else self.speaker.identify(audio, rate)
            if focus:
                if self.last_speaker.get('state')!='matched' or (focus!='*' and self.last_speaker.get('profile_id')!=focus):
                    reason = self.last_speaker.get('message') or 'No confident saved-voice match.'
                    self.last_speaker={'state':'ignored','message':reason + ' Say a longer sentence, or test your voice profile in Settings.'}
                    self._update(speaker=self.last_speaker)
                    return {'text':'','confidence':0,'needs_review':False,'ignored':True,'speaker':dict(self.last_speaker)}
                self.speaker.active=self.last_speaker['profile_id']
            result['speaker'] = dict(self.last_speaker)
            self._update(speaker=self.last_speaker)
        return result

    def listen(self, language='en-US', phrases=None, enrollment=None, identity_test=False):
        self.last_speaker = {'state':'disabled' if not self.speaker_enabled else 'uncertain'}
        engine = None if enrollment is not None else self._ensure_duplex()
        if engine:
            with self._operation:
                self._cancel.clear()
                self._update(phase='listening')
                previous_pause = None
                if enrollment is not None or identity_test:
                    previous_pause = engine.detector.quiet_frames
                    engine.detector.quiet_frames = 180
                try:
                    audio = engine.receive(self._cancel)
                    if audio is None or self._cancel.is_set():
                        return {'text': '', 'confidence': 0, 'needs_review': False}
                    import numpy as np
                    from desktop.duplex_audio import CapturedTurn
                    original_audio = audio.speaker if isinstance(audio,CapturedTurn) else audio
                    captured=audio if isinstance(audio,CapturedTurn) else None
                    audio = audio.audio if isinstance(audio,CapturedTurn) else audio
                    result = self._recognize_speaker({}, original_audio, 48000, enrollment, identity_test)
                    if (self.target_extractor is not None and result.get('speaker',{}).get('state')=='matched'
                            and not identity_test and enrollment is None):
                        from desktop.audio_pipeline import validate_extraction
                        # A supplied extractor must preserve time alignment. It
                        # cannot replace identity proof or decide tool intent.
                        audio=validate_extraction(audio,self.target_extractor.extract(audio,48000,result['speaker']['profile_id']))
                    rms = float(np.sqrt(np.mean(audio * audio)))
                    audio = audio * min(8., max(1., .035 / max(rms, .0001)))
                    pcm = (audio.clip(-1, 1) * 32767).astype('<i2')
                    buffer = io.BytesIO()
                    with wave.open(buffer, 'wb') as wav:
                        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(48000)
                        wav.writeframes(pcm.tobytes())
                    buffer.seek(0)
                    # Check the denoised, original-level speech first. Background
                    # voices must not consume a Whisper request or reach chat.
                    if not result.get('ignored') and enrollment is None and not identity_test:
                        started=time.monotonic()
                        proof=captured.recognition if captured else None
                        if proof and proof['signature']==self._speaker_signature() and proof['profile']==result.get('speaker',{}).get('profile_id'):
                            result.update(proof['result'])
                            result['interrupted_reply']=True
                            from desktop.interruption import reply_stop_control
                            if reply_stop_control(result['text']):
                                # A verified "Bob, stop" controls this reply;
                                # never let an LLM reinterpret it as an app/media action.
                                result.update(text='',interruption_control='stop_reply')
                        else:result.update(self.transcribe(buffer))
                        self.metrics.timing('final_asr', (time.monotonic()-started)*1000)
                        if captured and captured.ended_at:self.metrics.timing('endpoint_to_transcript',(time.monotonic()-captured.ended_at)*1000)
                        # Keep only bounded pause metadata on this returned turn.
                        # Runtime learns after wake/attention validation, never
                        # from unaddressed speech or uncertain recognition.
                        if captured:result['_speaking_pauses']=list(captured.pauses[-20:])
                    logging.info('Voice transcription finished: text_present=%s confidence=%.3f review=%s', bool(result.get('text')), result.get('confidence',0), result.get('needs_review',False))
                    return {'text': '', 'confidence': 0} if self._cancel.is_set() else result
                finally:
                    if previous_pause is not None:
                        engine.detector.quiet_frames = previous_pause
                    self._update(phase='idle', level=0)
        import numpy as np
        import sounddevice as sd
        from desktop.duplex_audio import natural_pause_ms
        if not self._operation.acquire(blocking=False):
            raise RuntimeError('Voice is already busy. Stop the current voice operation first.')
        self._cancel.clear()
        self._finish_enrollment.clear()
        self._pause_wake()
        self._update(phase='preparing', error='', enrolling=enrollment is not None, enrollment_seconds=0)
        try:
            # WASAPI/PortAudio uses the Windows default input. Record at its native rate.
            from desktop.microphone import input_device, gain_for
            device_index, device, device_key = input_device(sd)
            gain = gain_for(self.microphone_calibration, device_key)
            self._update(input_device=device.get('name','Default microphone'))
            rate = int(device['default_samplerate'])
            chunk = int(rate * .05)
            frames, preroll = [], []
            started = False
            voiced = silence = elapsed = 0.0
            with sd.InputStream(device=device_index, samplerate=rate, channels=1, dtype='float32', blocksize=chunk) as stream:
                ambient, _ = stream.read(chunk * 6)
                noise = float(np.sqrt(np.mean(ambient * ambient)))
                threshold = max(.0002, min(.003, noise * 2.0))
                # Cue only after the input device is ready. It is outside captured frames.
                import winsound
                winsound.Beep(880, 90)
                stream.read(chunk * 3)
                self._update(phase='listening')
                # Manual enrollment captures immediately, including quiet words
                # and pauses. Acoustic quality is checked after Finish sample.
                if enrollment is not None: started = True
                # Enrollment is explicitly finished by the reader. Pauses and
                # hesitant reading must never use conversational endpointing.
                while elapsed < (60 if enrollment is not None else 20) and not self._cancel.is_set():
                    if enrollment is not None and self._finish_enrollment.is_set():
                        break
                    audio, overflowed = stream.read(chunk)
                    if overflowed: raise ValueError('Microphone capture fell behind. Please retry the recording.')
                    audio = np.clip(audio*gain, -.999, .999)
                    rms = float(np.sqrt(np.mean(audio * audio)))
                    self._update(level=min(1, rms * 15))
                    elapsed += .05
                    if enrollment is not None:
                        self._update(enrollment_seconds=round(elapsed, 1))
                    speech = rms > threshold
                    if not started:
                        preroll.append(audio.copy())
                        preroll = preroll[-6:]
                        if speech:
                            started = True
                            frames.extend(preroll)
                        elif elapsed > (30 if enrollment is not None else 8):
                            break
                    else:
                        frames.append(audio.copy())
                    if started:
                        if speech:
                            voiced += .05
                            silence = 0
                        else:
                            silence += .05
                        pause = 1800 if enrollment is not None or identity_test else natural_pause_ms(getattr(self,'turn_pause_ms',650), voiced)
                        if enrollment is None and silence >= pause/1000:
                            break
            if self._cancel.is_set() or (enrollment is None and voiced < .2) or not frames:
                return {'text': '', 'confidence': 0, 'needs_review': False}
            pcm = (np.clip(np.concatenate(frames), -1, 1) * 32767).astype(np.int16)
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav:
                wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate); wav.writeframes(pcm.tobytes())
            buffer.seek(0)
            self._update(phase='processing' if enrollment is not None else 'verifying')
            result = self._recognize_speaker({}, np.concatenate(frames), rate, enrollment, identity_test)
            if not result.get('ignored') and enrollment is None and not identity_test:
                result.update(self.transcribe(buffer))
            return {'text': '', 'confidence': 0} if self._cancel.is_set() else result
        except sd.PortAudioError as exc:
            raise RuntimeError('Cannot access your microphone. Set the correct Windows default input and allow microphone access for desktop apps. ' + str(exc)) from exc
        finally:
            self._update(phase='idle', level=0, enrolling=False, enrollment_seconds=0)
            self._operation.release()

    def speak(self, text, rate, config_root=None, voice_options=None):
        with self._operation:
            options = dict(voice_options if voice_options is not None else getattr(self,'voice_options',{}))
            self._cancel.clear()
            self._speech_interrupted.clear()
            self._pause_wake()
            self._update(phase='speaking')
            try:
                from desktop.speech_output import spoken_text
                text = spoken_text(text)
                engine = self._ensure_duplex()
                # Capture onset is provisional: a click may start the sensitive
                # detector without ever becoming a permitted interruption.
                if engine and engine.last_interrupted_serial > engine.acknowledged_serial:
                    return False
                from desktop.speech_output import speech_chunks
                for part in speech_chunks(text):
                    if self._cancel.is_set() or self._speech_interrupted.is_set():return False
                    data = None
                    if config_root and options.get('voice_provider','auto') != 'windows':
                        try:
                            data = self._neural_render(part, config_root, options.get('neural_voice',''), rate)
                            if not data and options.get('strict'): raise RuntimeError('Configure Azure Speech before previewing a neural voice.')
                            if self._cancel.is_set() or self._speech_interrupted.is_set(): return False
                        except Exception:
                            if options.get('strict'): raise RuntimeError('Azure preview failed. Configure Azure Speech and check the region, key and connectivity.') from None
                            self._update(error='Neural voice unavailable; using the Windows voice. Check neural-voice.json.')
                    if self._cancel.is_set() or self._speech_interrupted.is_set(): return False
                    if not data:
                        data = self._speech_worker().render(part,int(rate),options.get('windows_voice',''),self._cancel,self._speech_interrupted)
                        if not data: return False
                    if self._cancel.is_set() or self._speech_interrupted.is_set(): return False
                    if engine:
                        engine.play(data, self._cancel, self._speech_interrupted)
                    else:
                        import sounddevice as sd
                        with wave.open(io.BytesIO(data)) as audio:
                            if audio.getsampwidth()!=2: raise RuntimeError('Unsupported speech audio format.')
                            with sd.RawOutputStream(samplerate=audio.getframerate(),channels=audio.getnchannels(),dtype='int16') as output:
                                while not self._cancel.is_set() and not self._speech_interrupted.is_set():
                                    chunk=audio.readframes(int(audio.getframerate() * .02))
                                    if not chunk: break
                                    import numpy as np
                                    samples=np.frombuffer(chunk,dtype='<i2').astype(np.float32)/32768
                                    self._update(output_level=min(1,float(np.sqrt(np.mean(samples*samples)))*10))
                                    output.write(chunk)
                return not self._cancel.is_set() and not self._speech_interrupted.is_set()
            finally:
                self._update(phase='idle',output_level=0)
