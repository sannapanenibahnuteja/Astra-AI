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

def model_path():
    if getattr(sys, 'frozen', False):
        roots = [Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent)), Path(sys.executable).parent]
    else:
        roots = [Path(__file__).resolve().parents[1] / 'dist']
    required = ('model.bin', 'config.json', 'tokenizer.json', 'vocabulary.txt')
    for root in roots:
        candidate = root / 'models' / 'whisper-small.en'
        if all((candidate / name).is_file() for name in required):
            return candidate
    raise RuntimeError('The bundled speech model is incomplete. Download the latest Bob.exe again.')


def transcript_result(segments):
    segments = list(segments)
    accepted = [s for s in segments if s.no_speech_prob < .65 and s.avg_logprob > -1.2]
    text = ' '.join(s.text.strip() for s in accepted).strip()
    words = [w.probability for s in accepted for w in (s.words or [])]
    confidence = float(sum(words) / len(words)) if words else 0.0
    # Never automatically execute marginal recognition. Scores are heuristic, not guarantees.
    review = bool(text) and (confidence < .65 or any(s.avg_logprob < -.7 for s in accepted)
                            or any(probability < .25 for probability in words))
    return {'text': text, 'confidence': round(confidence, 3), 'needs_review': review, 'language': 'en'}


class Voice:
    def __init__(self):
        self._lock = threading.RLock()
        self._operation = threading.Lock()
        self._model_lock = threading.Lock()
        self._process = None
        self._wake_process = None
        self._cancel = threading.Event()
        self._closed = threading.Event()
        self._hold = False
        self._enabled = False
        self._thread = None
        self._callback = None
        self._model = None
        self._release = None
        self._duplex = None
        self._duplex_failed = False
        self._duplex_lock = threading.RLock()
        self._speech_interrupted = threading.Event()
        self.on_interrupt = None
        self.speaker = None
        self.speaker_enabled = False
        self.last_speaker = {'state':'not_enrolled'}
        self._state = {'phase': 'idle', 'level': 0, 'wake': 'off', 'error': '', 'aec': 'off'}

    def status(self):
        with self._lock:
            value = dict(self._state)
        engine = self._duplex
        value['pending_audio'] = bool(engine and (not engine.utterances.empty() or engine.detector.started))
        if engine:
            value.update(recording_command=bool(engine.detector.started), captured_seconds=round(len(engine.detector.frames)*.01,2),
                         interruptions=engine.interruptions, completed_turns=engine.completed_turns,
                         raw_rms=round(engine.raw_rms,6), clean_rms=round(engine.clean_rms,6))
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
        self._hold = bool(active)
        if active:
            self._pause_wake()
        else:
            with self._duplex_lock:
                if self._duplex:
                    self._duplex.close()
                    self._duplex = None
                self._duplex_failed = False
            self._update(aec='off')
        return True

    def _barge_in(self):
        self._speech_interrupted.set()
        with self._lock:
            if self._process and self._process.poll() is None:
                self._process.terminate()
        if self.on_interrupt:
            self.on_interrupt()

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
                engine = DuplexAudio(self._barge_in, self._update)
                engine.start()
                self._duplex = engine
                return engine
            except Exception as exc:
                if engine:
                    engine.close()
                self._duplex_failed = True
                self._update(aec='unavailable', error='Hands-free interruption unavailable; using turn-by-turn voice. ' + str(exc)[:200])
                return None

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
        self._cancel.set()
        if self._duplex:
            self._duplex.cancel_playback()
            self._duplex.discard()
        with self._lock:
            if self._process and self._process.poll() is None:
                self._process.terminate()
        return True

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

    def transcribe(self, audio):
        from faster_whisper import WhisperModel
        with self._model_lock:
            if self._release:
                self._release.cancel()
            if self._model is None:
                path = model_path()
                self._update(phase='loading')
                self._model = WhisperModel(str(path), device='cpu', compute_type='int8', cpu_threads=2, num_workers=1, local_files_only=True)
            self._update(phase='transcribing', level=0)
            try:
                segments, _ = self._model.transcribe(audio, language='en', beam_size=5, vad_filter=True,
                    condition_on_previous_text=False, word_timestamps=True, temperature=0,
                    vad_parameters={'min_silence_duration_ms': 500})
                return transcript_result(segments)
            finally:
                self._release = threading.Timer(60, self._unload)
                self._release.daemon = True
                self._release.start()

    def _unload(self):
        with self._model_lock:
            self._model = None

    def _neural_render(self, text, config_root):
        from desktop.speech_output import neural_audio
        result = queue.Queue(maxsize=1)
        def render():
            try:
                result.put((neural_audio(text, config_root), None))
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

    def _recognize_speaker(self, result, audio, rate, enrollment):
        if self._cancel.is_set(): return {'text':'', 'confidence':0}
        if self.speaker and (self.speaker_enabled or enrollment is not None):
            if enrollment is not None:
                return {'enrollment':self.speaker.enroll(enrollment, audio, rate)}
            self.last_speaker = self.speaker.identify(audio, rate)
            result['speaker'] = dict(self.last_speaker)
            self._update(speaker=self.last_speaker)
        return result

    def listen(self, language='en-US', phrases=None, enrollment=None):
        self.last_speaker = {'state':'disabled' if not self.speaker_enabled else 'uncertain'}
        engine = self._ensure_duplex()
        if engine:
            with self._operation:
                self._cancel.clear()
                self._update(phase='listening')
                try:
                    audio = engine.receive(self._cancel)
                    if audio is None or self._cancel.is_set():
                        return {'text': '', 'confidence': 0, 'needs_review': False}
                    import numpy as np
                    original_audio = audio
                    rms = float(np.sqrt(np.mean(audio * audio)))
                    audio = audio * min(8., max(1., .035 / max(rms, .0001)))
                    pcm = (audio.clip(-1, 1) * 32767).astype('<i2')
                    buffer = io.BytesIO()
                    with wave.open(buffer, 'wb') as wav:
                        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(48000)
                        wav.writeframes(pcm.tobytes())
                    buffer.seek(0)
                    result = {} if enrollment is not None else self.transcribe(buffer)
                    # Use original capture for quality checks, before transcription gain.
                    result = self._recognize_speaker(result, original_audio, 48000, enrollment)
                    logging.info('Voice transcription finished: text_present=%s confidence=%.3f review=%s', bool(result.get('text')), result.get('confidence',0), result.get('needs_review',False))
                    return {'text': '', 'confidence': 0} if self._cancel.is_set() else result
                finally:
                    self._update(phase='idle', level=0)
        import numpy as np
        import sounddevice as sd
        if not self._operation.acquire(blocking=False):
            raise RuntimeError('Voice is already busy. Stop the current voice operation first.')
        self._cancel.clear()
        self._pause_wake()
        self._update(phase='listening', error='')
        try:
            # WASAPI/PortAudio uses the Windows default input. Record at its native rate.
            device = sd.query_devices(kind='input')
            rate = int(device['default_samplerate'])
            chunk = int(rate * .05)
            frames, preroll = [], []
            started = False
            voiced = silence = elapsed = 0.0
            with sd.InputStream(samplerate=rate, channels=1, dtype='float32', blocksize=chunk) as stream:
                ambient, _ = stream.read(chunk * 6)
                noise = float(np.sqrt(np.mean(ambient * ambient)))
                threshold = max(.003, min(.025, noise * 2.5))
                # Cue only after the input device is ready. It is outside captured frames.
                import winsound
                winsound.Beep(880, 90)
                stream.read(chunk * 3)
                while elapsed < 20 and not self._cancel.is_set():
                    audio, _ = stream.read(chunk)
                    rms = float(np.sqrt(np.mean(audio * audio)))
                    self._update(level=min(1, rms * 15))
                    elapsed += .05
                    speech = rms > threshold
                    if not started:
                        preroll.append(audio.copy())
                        preroll = preroll[-6:]
                        if speech:
                            started = True
                            frames.extend(preroll)
                        elif elapsed > 8:
                            break
                    else:
                        frames.append(audio.copy())
                    if started:
                        if speech:
                            voiced += .05
                            silence = 0
                        else:
                            silence += .05
                        if silence > .85:
                            break
            if self._cancel.is_set() or voiced < .2 or not frames:
                return {'text': '', 'confidence': 0, 'needs_review': False}
            pcm = (np.clip(np.concatenate(frames), -1, 1) * 32767).astype(np.int16)
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav:
                wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate); wav.writeframes(pcm.tobytes())
            buffer.seek(0)
            result = {} if enrollment is not None else self.transcribe(buffer)
            result = self._recognize_speaker(result, np.concatenate(frames), rate, enrollment)
            return {'text': '', 'confidence': 0} if self._cancel.is_set() else result
        except sd.PortAudioError as exc:
            raise RuntimeError('Cannot access your microphone. Set the correct Windows default input and allow microphone access for desktop apps. ' + str(exc)) from exc
        finally:
            self._update(phase='idle', level=0)
            self._operation.release()

    def speak(self, text, rate, config_root=None):
        with self._operation:
            self._cancel.clear()
            self._speech_interrupted.clear()
            self._pause_wake()
            self._update(phase='speaking')
            try:
                from desktop.speech_output import spoken_text
                text = spoken_text(text)
                engine = self._ensure_duplex()
                if engine and (not engine.utterances.empty() or engine.detector.started):
                    return False
                data = None
                if config_root:
                    try:
                        data = self._neural_render(text, config_root)
                        if self._cancel.is_set() or self._speech_interrupted.is_set(): return False
                    except Exception:
                        self._update(error='Neural voice unavailable; using the Windows voice. Check neural-voice.json.')
                if self._cancel.is_set() or self._speech_interrupted.is_set(): return False
                if not data:
                    encoded = self._run(RENDER, {'text': text[:5000], 'rate': int(rate)}, 180)
                    if not encoded: return False
                    data = base64.b64decode(encoded, validate=True)
                if self._cancel.is_set() or self._speech_interrupted.is_set(): return False
                if engine:
                    engine.play(data, self._cancel, self._speech_interrupted)
                else:
                    import sounddevice as sd
                    with wave.open(io.BytesIO(data)) as audio:
                        if audio.getsampwidth()!=2: raise RuntimeError('Unsupported speech audio format.')
                        with sd.RawOutputStream(samplerate=audio.getframerate(),channels=audio.getnchannels(),dtype='int16') as output:
                            while not self._cancel.is_set():
                                chunk=audio.readframes(int(audio.getframerate() * .02))
                                if not chunk: break
                                output.write(chunk)
                return not self._cancel.is_set() and not self._speech_interrupted.is_set()
            finally:
                self._update(phase='idle')
