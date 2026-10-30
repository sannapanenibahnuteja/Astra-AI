"""Session-scoped WASAPI playback/capture with a shared WebRTC AEC reference.

The audio callback only copies bounded blocks. DSP, speech detection and callbacks
run on a worker, never on PortAudio's real-time thread. No audio is saved to disk.
"""
from collections import deque
from dataclasses import dataclass
import queue
import threading
import time
import logging

import numpy as np

RATE = 48000
BLOCK = RATE // 100


@dataclass
class CapturedTurn:
    audio: np.ndarray
    speaker: np.ndarray
    serial: int | None = None
    pauses: tuple = ()
    ended_at: float = 0.
    interruption_ready: bool | None = None
    requires_authorization: bool = False
    recognition: dict | None = None
    room_mode: str | None = None


class InterruptionGate:
    """Separate capture sensitivity from permission to stop a spoken reply.

    Require sustained, above-floor speech, even if the capture VAD hangs over
    after a click. A quiet room must not make arbitrary tiny sounds eligible.
    """
    def __init__(self, minimum_rms=.0008):
        self.minimum_rms=minimum_rms
        self.frames = deque(maxlen=32)
        self.gap = 0
        self.ready = False

    def feed(self, rms, speech, noise=.0001, settling=False):
        if settling:
            self.reset()
            return False
        eligible = speech and rms >= max(self.minimum_rms, min(.012, noise * 4))
        self.gap = 0 if eligible else self.gap + 1
        if self.gap >= 9:
            self.reset()
            return False
        self.frames.append(bool(eligible))
        if len(self.frames) >= 24 and sum(self.frames) >= 20 and eligible:
            self.ready = True
        return self.ready

    def reset(self):
        self.frames.clear()
        self.gap = 0
        self.ready = False


def completed_speech_candidate(strict_ready, voiced_frames, total_frames, room_mode='balanced'):
    """Nominate completed speech for neural/identity/intent checks, never stop.

    The strict short window can miss consonants or quiet words. A full utterance
    can supply the same sustained evidence across gaps; clicks cannot accumulate
    across separate turns. Every nominated turn still needs all final checks.
    """
    quiet=room_mode=='quiet'
    return bool(strict_ready or (voiced_frames >= (35 if quiet else 45) and total_frames > 0
                                and voiced_frames / total_frames >= (.22 if quiet else .25)))


def wav_samples(data, target_rate=RATE):
    import io
    import wave
    with wave.open(io.BytesIO(data), 'rb') as audio:
        if audio.getsampwidth() != 2:
            raise RuntimeError('Speech playback requires 16-bit PCM audio.')
        rate, channels = audio.getframerate(), audio.getnchannels()
        samples = np.frombuffer(audio.readframes(audio.getnframes()), dtype='<i2')
        samples = samples.reshape(-1, channels).mean(axis=1).astype(np.float32) / 32768
    if rate != target_rate and len(samples):
        length = round(len(samples) * target_rate / rate)
        samples = np.interp(np.arange(length) * rate / target_rate,
                            np.arange(len(samples)), samples).astype(np.float32)
    return np.ascontiguousarray(samples)


def acoustic_speech(clean):
    """Reject isolated impulses and broadband hiss before speech onset."""
    centered = clean - float(np.mean(clean))
    rms = float(np.sqrt(np.mean(centered * centered)))
    if rms < .00002 or float(np.max(np.abs(centered))) > rms * 12:
        return False
    power = np.abs(np.fft.rfft(centered * np.hanning(len(centered))))[1:] ** 2
    flatness = np.exp(np.mean(np.log(power + 1e-12))) / (np.mean(power) + 1e-12)
    return bool(flatness < .5)


def natural_pause_ms(base, voiced_seconds):
    """Natural mode: quick short answers, breathing room for longer thoughts."""
    if base != 650: return base
    if voiced_seconds < .6: return 450
    if voiced_seconds >= 2.5: return 950
    return 650


class TurnDetector:
    """Bounded utterance buffer with pre-roll and sustained-speech interruption."""
    def __init__(self):
        self.preroll = deque(maxlen=90)
        self.frames = []
        self.streak = self.silence = self.voiced = 0
        self.noise = .0001
        self.onset = deque(maxlen=15)
        self.speech_peak = 0.
        self.started = False
        self.quiet_frames = 55
        self.adaptive = False
        self.semantic_pause_ms = 0
        self.pauses = []
        self.last_pauses = ()
        self.last_voiced = 0
        self.last_silence = 0
        self.last_onset_ms = 0
        self.room_mode = 'balanced'

    def feed(self, clean, probability, speaking=False, settling=False):
        rms = float(np.sqrt(np.mean(clean * clean)))
        quiet=self.room_mode=='quiet'
        threshold = max(.00012 if quiet else .0002,
                        min(.01, self.noise * (1.8 if quiet else 2.5)),
                        self.speech_peak * .08 if self.started else 0)
        speech = probability >= .80 and rms >= threshold and not settling
        # Do not learn residual playback echo as the room's noise floor.
        # After onset, continue learning quiet frames so residual noise cannot
        # restart an utterance immediately after its endpoint.
        if not speech and not settling and (not speaking or self.started):
            self.noise = .98 * self.noise + .02 * min(rms, .004)
        interrupt = False
        if not self.started:
            self.preroll.append(clean.copy())
            self.onset.append(bool(speech))
            self.streak = self.streak + 1 if speech else 0
            onset = list(self.onset)[-15:]
            # Demand a longer speech span during playback, rather than more
            # voiced frames: quiet consonants need gaps without losing words.
            span = len(onset) - onset.index(True) if any(onset) else 0
            if sum(onset) >= 8 and speech and (not speaking or span >= 12):
                self.last_onset_ms=span*10
                self.started = True
                self.speech_peak = min(.1, rms)
                self.voiced = sum(onset)
                self.frames = list(self.preroll)
                self.preroll.clear()
                interrupt = True
        else:
            self.frames.append(clean.copy())
            if speech:
                if 15 <= self.silence <= 250: self.pauses.append(self.silence * 10)
                self.speech_peak = max(self.speech_peak * .99, min(.1, rms))
            self.voiced += int(speech)
            self.silence = 0 if speech else self.silence + 1
            pause = natural_pause_ms(self.quiet_frames * 10, self.voiced * .01) // 10 if self.adaptive else self.quiet_frames
            pause = max(pause, min(180, self.semantic_pause_ms // 10))
            if self.silence >= pause or len(self.frames) >= 2000:
                audio = np.concatenate(self.frames) if self.voiced >= 8 else None
                self.last_pauses = tuple(self.pauses[-20:])
                self.last_voiced = self.voiced
                self.last_silence = self.silence
                self.pauses = []
                self.semantic_pause_ms = 0
                self.frames = []
                self.started = False
                self.streak = self.silence = self.voiced = 0
                self.speech_peak = 0.
                self.onset.clear()
                return interrupt, audio, rms
        return interrupt, None, rms


class DuplexAudio:
    def __init__(self, on_interrupt, on_status, options=None):
        from desktop.audio_pipeline import DEFAULT_AUDIO, WebRTCStage, Beamformer, EnvironmentMonitor, AdaptiveRoom
        import webrtcvad
        self.options = {**DEFAULT_AUDIO, **(options or {})}
        quiet=self.options['audio_room_mode']=='quiet'
        self.vad = webrtcvad.Vad(2)
        self.interrupt_vad = webrtcvad.Vad(3)
        self.interruption_gate = InterruptionGate()
        self.turn_interruption_ready = False
        self.turn_started_during_playback = False
        self.processor = WebRTCStage(RATE, level=self.options['audio_noise_level'])
        self.beamformer = Beamformer(self.options['audio_array_delays'])
        self.environment = EnvironmentMonitor(RATE)
        self.adaptive_room = AdaptiveRoom(prefer_quiet=quiet)
        self.turn_room_mode = 'balanced'
        self.preview = None
        self.last_preview = 0.
        self.duck_until = 0.
        self.duck_gain = 1.
        self.ducks = 0
        self.check_pending = False
        self.check_attempts = 0
        self.on_interrupt, self.on_status = on_interrupt, on_status
        self.blocks = queue.Queue(maxsize=50)
        self.utterances = queue.Queue(maxsize=2)
        self.closed = threading.Event()
        self.play_done = threading.Event()
        self.play_done.set()
        self.lock = threading.Lock()
        self.samples = np.empty(0, dtype=np.float32)
        self.position = 0
        self.play_started = self.echo_until = 0.
        self.error = ''
        self.stream_glitches = 0
        self._glitch_times = deque(maxlen=20)
        self.interruptions = self.completed_turns = 0
        self.rejected_acoustic_turns = 0
        self.raw_rms = self.clean_rms = 0.
        self.stream = None
        self.detector = TurnDetector()
        self.verify_interrupt = None
        self.authorize_interrupt = None
        self.response_active = lambda: False
        self.turn_requires_authorization = False
        self.turn_serial = 0
        self.interrupt_checked = False
        self._interrupt_lock = threading.Lock()
        self.last_interrupted_serial = -1
        self.acknowledged_serial = -1
        self.pending_verifications = 0
        self.delivery_pending = False
        self.metrics = None
        self.last_callback_at = 0.
        self.dsp_frames = 0
        self._verification_lock = threading.Lock()
        self.microphone_calibration = {}
        self.input_gain = 1.
        self.speaker_processor = None
        self.speaker_frames = []
        self.speaker_preroll = deque(maxlen=90)
        self.worker = threading.Thread(target=self._work, daemon=True)

    def _verified_interrupt(self, audio, serial):
        try:
            authorize=getattr(self,'authorize_interrupt',None)
            if authorize and isinstance(audio,CapturedTurn) and audio.requires_authorization:
                # An incomplete decode can hallucinate an address/control from
                # a click or echo. Only the completed-turn path may stop TTS.
                accepted=False
            else:accepted = bool(self.verify_interrupt and self.verify_interrupt(audio))
        except Exception: accepted = False
        if accepted: self._interrupt_verified(serial)
        elif serial == self.turn_serial:
            self.duck_until = 0.
        self.check_pending = False

    def _interrupt_verified(self, serial, authorized=False):
        # A full, confidently matched request may succeed after the early
        # partial speaker check failed. It must still interrupt this turn.
        if not hasattr(self,'_interrupt_lock'): self._interrupt_lock = threading.Lock()
        if getattr(self,'authorize_interrupt',None) is not None and not authorized:return False
        with self._interrupt_lock:
            if self.closed.is_set() or serial != self.turn_serial or getattr(self,'last_interrupted_serial',-1) == serial:
                return False
            self.last_interrupted_serial = serial
            self.interruptions += 1
        try:accepted=self.on_interrupt() is not False
        except Exception:
            logging.exception('Interruption commit callback failed; playback retained')
            accepted=False
        if not accepted:
            with self._interrupt_lock:
                if self.last_interrupted_serial==serial:self.last_interrupted_serial=self.acknowledged_serial
                self.interruptions-=1
            return False
        self.cancel_playback()
        logging.info('Completed interruption authorized: serial=%s',serial)
        return True

    def _check_focus_interrupt(self, audio):
        if self.interrupt_checked or self.check_pending: return
        self.interrupt_checked = True
        self.check_pending = True
        self.check_attempts += 1
        threading.Thread(target=self._verified_interrupt,args=(audio,self.turn_serial),daemon=True,name='bob-speaker-check').start()

    def _queue_turn(self, audio):
        if self.closed.is_set(): return
        try:
            self.utterances.put_nowait(audio)
            self.completed_turns += 1
        except queue.Full:
            self.on_status(error='Please wait for Bob to finish processing your request.')

    def _deliver_focused_turn(self, audio):
        # Do not let background conversations fill the two-command queue
        # while Bob is speaking and prevent the real user's next request.
        speaker = audio.speaker if isinstance(audio,CapturedTurn) else audio
        try:
            authorize=getattr(self,'authorize_interrupt',None)
            if isinstance(audio,CapturedTurn) and authorize and self.response_active():
                audio.requires_authorization=True
            strict=isinstance(audio,CapturedTurn) and audio.requires_authorization
            if strict:
                if audio.interruption_ready is not True:return
                accepted=bool(audio.serial==self.turn_serial and not self.closed.is_set()
                              and self.authorize_interrupt and self.authorize_interrupt(audio,False))
                if audio.serial!=self.turn_serial or self.closed.is_set():return
            else:accepted=bool(self.verify_interrupt and self.verify_interrupt(speaker))
        except Exception: accepted=False
        if accepted:
            if (isinstance(audio,CapturedTurn) and audio.serial is not None and audio.interruption_ready is not False
                    and (audio.requires_authorization or not getattr(self,'authorize_interrupt',None))):
                committed=self._interrupt_verified(audio.serial,authorized=audio.requires_authorization)
                if audio.requires_authorization and not committed:return
            self.on_status(voice_notice='')
            self._queue_turn(audio)
        else:
            if isinstance(audio,CapturedTurn) and audio.serial == self.turn_serial:
                self.duck_until = 0.
            if not (isinstance(audio,CapturedTurn) and audio.requires_authorization):
                self.on_status(voice_notice='Speech captured, but the saved-voice filter could not match it. Say a longer sentence or test your profile in Settings.')

    def _verify_turn(self, audio):
        try:
            self._deliver_focused_turn(audio)
        finally:
            with self._verification_lock:
                self.pending_verifications -= 1

    def _submit_focused_turn(self, audio):
        with self._verification_lock:
            # Bound inference work instead of spawning an unbounded backlog.
            if self.pending_verifications >= 2:
                self.on_status(voice_notice='Voice matching is busy. Please wait a moment before speaking again.')
                return
            self.pending_verifications += 1
        threading.Thread(target=self._verify_turn,args=(audio,),daemon=True,name='bob-speaker-turn').start()

    def start(self):
        import sounddevice as sd
        # Resolve the current Windows defaults in WASAPI, rather than MME aliases.
        host = next(h for h in sd.query_hostapis() if h['name'] == 'Windows WASAPI')
        device = (host['default_input_device'], host['default_output_device'])
        if min(device) < 0:
            raise RuntimeError('A Windows microphone and speaker are required.')
        inputs, outputs = [sd.query_devices(d) for d in device]
        from desktop.microphone import gain_for,interruption_floor
        if inputs['max_input_channels'] < self.beamformer.channels:
            raise RuntimeError('The selected microphone does not expose the configured synchronized array channels. Clear the array calibration or choose its input device.')
        self.input_gain = gain_for(self.microphone_calibration, 'Windows WASAPI:' + inputs['name'])
        self.interruption_gate.minimum_rms=interruption_floor(self.microphone_calibration,'Windows WASAPI:'+inputs['name'])
        if self.options['audio_room_mode']=='quiet':
            self.interruption_gate.minimum_rms=max(.0006,self.interruption_gate.minimum_rms*.65)
        if 'stereo mix' in inputs['name'].lower():
            raise RuntimeError('Select a real microphone instead of Stereo Mix in Windows Sound settings.')
        if outputs['max_output_channels'] < 1:
            raise RuntimeError('The selected Windows speaker has no output channels.')
        # Explicit shared-mode conversion avoids driver-dependent format choices.
        # Retry only these same WASAPI endpoints with a more tolerant buffer;
        # never silently select WDM-KS, a loopback input or another microphone.
        errors=[]
        for latency in ('low', 'high'):
            candidate=None
            try:
                shared=sd.WasapiSettings(exclusive=False, auto_convert=True)
                candidate=sd.Stream(device=device, samplerate=RATE, blocksize=BLOCK,
                    channels=(self.beamformer.channels, min(2, outputs['max_output_channels'])),
                    dtype='float32', latency=latency, extra_settings=(shared,shared), callback=self._audio)
                candidate.start()
                self.stream=candidate
                break
            except Exception as exc:
                errors.append(type(exc).__name__)
                if candidate is not None:
                    try:candidate.close()
                    except Exception:pass
        if self.stream is None:
            raise RuntimeError('Windows could not open the selected WASAPI microphone and speakers in shared mode. '
                               'Check microphone permissions, close apps using exclusive audio, and reconnect the audio device. '
                               'No alternate microphone was selected. ('+', '.join(errors)+')')
        self.worker.start()
        self.on_status(aec='active', input_device=inputs['name'], output_device=outputs['name'], audio_buffer=latency)

    def _audio(self, incoming, outgoing, frames, timing, status):
        self.last_callback_at=time.monotonic()
        outgoing.fill(0)
        with self.lock:
            count = min(frames, len(self.samples) - self.position)
            if count:
                outgoing[:count] = self.samples[self.position:self.position + count, None]
                target = .18 if time.monotonic() < self.duck_until else 1.
                gain = np.linspace(self.duck_gain, target, count, dtype=np.float32)
                outgoing[:count] *= gain[:,None]
                self.duck_gain = target
                self.position += count
                self.echo_until = time.monotonic() + .4
            if self.position >= len(self.samples):
                self.play_done.set()
        if status:
            # A single recoverable PortAudio under/overflow is not speech and
            # must not cancel playback. Preserve the exact emitted reference
            # and continue; repeated failures surface as a device error.
            self.stream_glitches+=1
            now=time.monotonic()
            self._glitch_times.append(now)
            if len(self._glitch_times)==20 and now-self._glitch_times[0]<2:
                self.error = 'Repeated audio driver dropouts. Restart the voice conversation or choose a stable audio device.'
                return
        try:
            delay = max(0, min(500, round((timing.outputBufferDacTime - timing.inputBufferAdcTime) * 1000)))
            self.blocks.put_nowait((incoming.copy(), outgoing[:, 0].copy(), delay,self.last_callback_at))
        except queue.Full:
            self.error = 'Audio processing fell behind. Restart the voice conversation.'

    def _work(self):
        try:
            while not self.closed.is_set():
                if self.error:
                    raise RuntimeError(self.error)
                try:
                    near, far, delay, *captured_at = self.blocks.get(timeout=.1)
                except queue.Empty:
                    if self.stream is not None and self.last_callback_at and time.monotonic()-self.last_callback_at>3:
                        raise RuntimeError('Microphone audio stopped arriving. Check Windows Sound input, then restart Voice. No command was submitted.')
                    continue
                processing_started=time.monotonic()
                self.dsp_frames+=1
                if self.metrics is not None and captured_at and self.dsp_frames%10==0:
                    self.metrics.timing('audio_capture_latency',(processing_started-captured_at[0])*1000)
                near = self.beamformer.process(near)
                self.processor.stream_delay_ms = delay
                clean = np.clip(self.processor.process(near, far)*self.input_gain, -.999, .999)
                if self.verify_interrupt is not None:
                    if self.speaker_processor is None:
                        from pywebrtc_audio import AudioProcessor
                        # Enrollment is not noise-suppressed. Keep the speaker
                        # characteristics close to that input while cancelling
                        # playback echo on this synchronized reference too.
                        self.speaker_processor = AudioProcessor(sample_rate=RATE, echo_cancellation=True,
                            noise_suppression=False, auto_gain_control=False)
                    self.speaker_processor.stream_delay_ms = delay
                    speaker_block = np.clip(self.speaker_processor.process(near,far)*self.input_gain,-.999,.999)
                    self.speaker_preroll.append(speaker_block.copy())
                self.raw_rms = float(np.sqrt(np.mean(near * near)))
                self.clean_rms = float(np.sqrt(np.mean(clean * clean)))
                # Normalize only the VAD input. Keep AEC/reference and captured
                # audio at their original scale; do not amplify the echo path.
                now = time.monotonic()
                speaking = now < self.echo_until
                vad_gain = min(8., max(1., .015 / max(self.clean_rms, .0001)))
                pcm = ((clean * vad_gain).clip(-1, 1) * 32767).astype('<i2').tobytes()
                speech = self.vad.is_speech(pcm, RATE) and acoustic_speech(clean)
                room_mode=self.adaptive_room.observe(self.clean_rms,speech,speaking,
                    bool(np.any(np.abs(near)>=.995)))
                # Freeze sensitivity per utterance, including its final neural
                # check. Noise cannot switch a partly captured turn to Quiet.
                if not self.detector.started:
                    self.turn_room_mode=room_mode
                    self.detector.room_mode=room_mode
                    self.vad.set_mode(1 if room_mode=='quiet' else 2)
                    self.interrupt_vad.set_mode(2 if room_mode=='quiet' else 3)
                # Allow the filter to converge at the start of a playback burst.
                settling = speaking and now - self.play_started < .35
                # The command recognizer boosts quiet input up to 8x. Do not
                # reuse that boost to authorize stopping the current reply.
                strict_pcm = (clean.clip(-1,1)*32767).astype('<i2').tobytes()
                strict_speech = speech and self.interrupt_vad.is_speech(strict_pcm,RATE)
                interruption_ready = self.interruption_gate.feed(self.clean_rms,strict_speech,self.detector.noise,settling)
                was_started = self.detector.started
                # Keep ownership across the endpoint -> verifier/queue handoff.
                # detector.started becomes False before a completed turn is
                # published; an expired idle timer must not split that turn.
                if was_started:self.delivery_pending=True
                interrupt, audio, rms = self.detector.feed(
                    clean, .99 if speech else 0., speaking, settling)
                if self.verify_interrupt is not None:
                    if interrupt:
                        self.speaker_frames = list(self.speaker_preroll)[-len(self.detector.frames):]
                    elif was_started:
                        self.speaker_frames.append(speaker_block.copy())
                self.on_status(level=min(1, rms * 15), output_level=min(1, float(np.sqrt(np.mean(far * far))) * 10))
                if interrupt:
                    self.delivery_pending=True
                    if self.metrics is not None:self.metrics.timing('vad_latency',self.detector.last_onset_ms)
                    self.turn_serial += 1
                    self.interrupt_checked = False
                    self.check_attempts = 0
                    self.duck_until = 0.
                    self.turn_interruption_ready = False
                    self.turn_started_during_playback = speaking
                    self.turn_requires_authorization = bool(self.authorize_interrupt and (speaking or self.response_active()))
                    self.last_preview = now
                    if self.preview: self.preview.begin(self.turn_serial)
                if self.detector.started and self.authorize_interrupt and (speaking or self.response_active()):
                    self.turn_requires_authorization=True
                if self.detector.started and interruption_ready:
                    self.turn_interruption_ready = True
                    if self.verify_interrupt is None and self.authorize_interrupt is None:self._interrupt_verified(self.turn_serial)
                if (self.options['audio_fast_barge_in'] and speaking and self.detector.started
                        and not self.turn_requires_authorization and self.turn_interruption_ready and not self.duck_until and self.check_attempts == 0):
                    self.duck_until = now + 1.2
                    self.ducks += 1
                if (not self.turn_requires_authorization and speaking and self.turn_interruption_ready and self.verify_interrupt is not None and self.detector.started and not self.check_pending
                        and self.check_attempts < 3 and self.detector.voiced >= (60,120,200)[self.check_attempts]):
                    self.interrupt_checked = False
                    if self.turn_requires_authorization:
                        clean_turn=np.concatenate(self.detector.frames)
                        who=np.concatenate(self.speaker_frames) if self.speaker_frames else clean_turn
                        self._check_focus_interrupt(CapturedTurn(clean_turn,who,self.turn_serial,interruption_ready=True,requires_authorization=True))
                    else:self._check_focus_interrupt(np.concatenate(self.speaker_frames))
                self.environment.observe(near, clean, speech, speaking)
                self.environment.current['listening_sensitivity']=self.turn_room_mode
                if self.metrics is not None and self.dsp_frames%10==0:
                    self.metrics.timing('audio_processing_latency',(time.monotonic()-processing_started)*1000)
                if self.preview and self.detector.started and now-self.last_preview >= 1.5:
                    from desktop.audio_pipeline import PreviewFrame
                    self.last_preview = now
                    frames=self.detector.frames[-800:]
                    who=self.speaker_frames[-800:] if self.verify_interrupt else frames
                    self.preview.submit(PreviewFrame(self.turn_serial,np.concatenate(frames),np.concatenate(who),now))
                if audio is not None:
                    if self.metrics is not None:self.metrics.timing('endpoint_latency',self.detector.last_silence*10)
                    self.interruption_gate.reset()
                    if self.preview: self.preview.end(self.turn_serial)
                    self.on_status(partial_text='', partial_stable='')
                    if self.turn_requires_authorization:
                        self.turn_interruption_ready=completed_speech_candidate(
                            self.turn_interruption_ready,self.detector.last_voiced,len(audio)//BLOCK,self.turn_room_mode)
                    if (self.turn_started_during_playback or self.turn_requires_authorization) and not self.turn_interruption_ready:
                        self.rejected_acoustic_turns+=1
                        self.speaker_frames = []
                        self.delivery_pending=False
                        continue # An incidental sound is neither a barge-in nor a queued command.
                    if self.verify_interrupt is not None or self.turn_requires_authorization:
                        speaker_audio = np.concatenate(self.speaker_frames) if self.speaker_frames else audio
                        self.speaker_frames = []
                        self._submit_focused_turn(CapturedTurn(audio,speaker_audio,self.turn_serial,self.detector.last_pauses,now,self.turn_interruption_ready,self.turn_requires_authorization,room_mode=self.turn_room_mode))
                    else: self._queue_turn(CapturedTurn(audio,audio,self.turn_serial,self.detector.last_pauses,now,self.turn_interruption_ready))
                    self.delivery_pending=False
        except Exception as exc:
            self.delivery_pending=False
            self.error = str(exc)
            self.cancel_playback()
            self.on_status(aec='error', error=self.error)

    def play(self, data, cancel, interrupted=None):
        samples = wav_samples(data)
        with self.lock:
            if cancel.is_set() or (interrupted and interrupted.is_set()) or self.closed.is_set():
                return
            self.samples, self.position = samples, 0
            now=time.monotonic()
            # Keep the trained echo filter interruptible across streamed
            # sentence gaps; reconverge after a long idle interval.
            if not self.play_started or now-self.echo_until>2:
                self.play_started=now
            self.play_done.clear()
        while not self.play_done.wait(.02):
            if cancel.is_set() or (interrupted and interrupted.is_set()) or self.closed.is_set() or self.error:
                self.cancel_playback()
                break
        # Drain the last block through the physical speaker buffer.
        delay = self.stream.latency[1] if self.stream else 0
        if self.metrics is not None:self.metrics.timing('audio_output_latency',delay*1000)
        cancel.wait(min(.3, delay))
        if self.error:
            raise RuntimeError(self.error)

    def cancel_playback(self):
        with self.lock:
            self.samples = np.empty(0, dtype=np.float32)
            self.position = 0
            self.play_done.set()

    def receive(self, cancel, timeout=8):
        deadline = time.monotonic() + timeout
        while not cancel.is_set() and not self.closed.is_set():
            if self.error:
                raise RuntimeError(self.error)
            try:
                turn = self.utterances.get(timeout=.05)
                if isinstance(turn,CapturedTurn) and turn.serial is not None:
                    self.acknowledged_serial = max(self.acknowledged_serial,turn.serial)
                return turn
            except queue.Empty:
                busy=self.detector.started or self.pending_verifications or getattr(self,'delivery_pending',False)
                # Timeout means idle time, not total time since listen began.
                # Leave a complete grace interval for endpoint publication even
                # when speech began just before the original idle deadline.
                if busy:deadline=time.monotonic()+timeout
                if time.monotonic() >= deadline and not busy:
                    return None
        return None

    def discard(self):
        self.interruption_gate.reset()
        self.acknowledged_serial = max(self.acknowledged_serial,self.last_interrupted_serial)
        if self.preview: self.preview.end(self.turn_serial)
        self.on_status(partial_text='', partial_stable='')
        while True:
            try:
                self.utterances.get_nowait()
            except queue.Empty:
                break

    def close(self):
        self.closed.set()
        if self.preview: self.preview.close()
        self.cancel_playback()
        if self.stream:
            self.stream.stop()
            self.stream.close()
        if self.worker.is_alive() and self.worker is not threading.current_thread():
            self.worker.join(timeout=1)
