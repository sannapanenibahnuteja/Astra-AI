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

    def feed(self, clean, probability, speaking=False, settling=False):
        rms = float(np.sqrt(np.mean(clean * clean)))
        threshold = max(.0002,
                        min(.01, self.noise * 2.5),
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
            if sum(onset) >= 8 and speech and (not speaking or rms < .002 or span >= 12):
                self.started = True
                self.speech_peak = min(.1, rms)
                self.voiced = sum(onset)
                self.frames = list(self.preroll)
                self.preroll.clear()
                interrupt = True
        else:
            self.frames.append(clean.copy())
            if speech:
                self.speech_peak = max(self.speech_peak * .99, min(.1, rms))
            self.voiced += int(speech)
            self.silence = 0 if speech else self.silence + 1
            pause = natural_pause_ms(self.quiet_frames * 10, self.voiced * .01) // 10 if self.adaptive else self.quiet_frames
            if self.silence >= pause or len(self.frames) >= 2000:
                audio = np.concatenate(self.frames) if self.voiced >= 8 else None
                self.frames = []
                self.started = False
                self.streak = self.silence = self.voiced = 0
                self.speech_peak = 0.
                self.onset.clear()
                return interrupt, audio, rms
        return interrupt, None, rms


class DuplexAudio:
    def __init__(self, on_interrupt, on_status):
        from pywebrtc_audio import AudioProcessor
        import webrtcvad
        self.vad = webrtcvad.Vad(2)
        self.processor = AudioProcessor(sample_rate=RATE, echo_cancellation=True,
                                        noise_suppression=True, auto_gain_control=False)
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
        self.interruptions = self.completed_turns = 0
        self.raw_rms = self.clean_rms = 0.
        self.stream = None
        self.detector = TurnDetector()
        self.verify_interrupt = None
        self.turn_serial = 0
        self.interrupt_checked = False
        self._interrupt_lock = threading.Lock()
        self.last_interrupted_serial = -1
        self.pending_verifications = 0
        self._verification_lock = threading.Lock()
        self.microphone_calibration = {}
        self.input_gain = 1.
        self.speaker_processor = None
        self.speaker_frames = []
        self.speaker_preroll = deque(maxlen=90)
        self.worker = threading.Thread(target=self._work, daemon=True)

    def _verified_interrupt(self, audio, serial):
        try: accepted = bool(self.verify_interrupt and self.verify_interrupt(audio))
        except Exception: accepted = False
        if accepted: self._interrupt_verified(serial)

    def _interrupt_verified(self, serial):
        # A full, confidently matched request may succeed after the early
        # partial speaker check failed. It must still interrupt this turn.
        if not hasattr(self,'_interrupt_lock'): self._interrupt_lock = threading.Lock()
        with self._interrupt_lock:
            if self.closed.is_set() or serial != self.turn_serial or getattr(self,'last_interrupted_serial',-1) == serial:
                return
            self.last_interrupted_serial = serial
            self.interruptions += 1
        self.cancel_playback()
        self.on_interrupt()

    def _check_focus_interrupt(self, audio):
        if self.interrupt_checked: return
        self.interrupt_checked = True
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
        try: accepted=bool(self.verify_interrupt and self.verify_interrupt(speaker))
        except Exception: accepted=False
        if accepted:
            if isinstance(audio,CapturedTurn) and audio.serial is not None:
                self._interrupt_verified(audio.serial)
            self.on_status(voice_notice='')
            self._queue_turn(audio)
        else:
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
        from desktop.microphone import gain_for
        self.input_gain = gain_for(self.microphone_calibration, 'Windows WASAPI:' + inputs['name'])
        if 'stereo mix' in inputs['name'].lower():
            raise RuntimeError('Select a real microphone instead of Stereo Mix in Windows Sound settings.')
        self.stream = sd.Stream(device=device, samplerate=RATE, blocksize=BLOCK,
                                channels=(1, min(2, outputs['max_output_channels'])),
                                dtype='float32', latency='low', callback=self._audio)
        self.worker.start()
        try:
            self.stream.start()
        except Exception:
            self.close()
            raise
        self.on_status(aec='active', input_device=inputs['name'], output_device=outputs['name'])

    def _audio(self, incoming, outgoing, frames, timing, status):
        outgoing.fill(0)
        with self.lock:
            count = min(frames, len(self.samples) - self.position)
            if count:
                outgoing[:count] = self.samples[self.position:self.position + count, None]
                self.position += count
                self.echo_until = time.monotonic() + .4
            if self.position >= len(self.samples):
                self.play_done.set()
        if status:
            self.error = 'Audio stream lost synchronization. Restart the voice conversation.'
            return
        try:
            delay = max(0, min(500, round((timing.outputBufferDacTime - timing.inputBufferAdcTime) * 1000)))
            self.blocks.put_nowait((incoming[:, 0].copy(), outgoing[:, 0].copy(), delay))
        except queue.Full:
            self.error = 'Audio processing fell behind. Restart the voice conversation.'

    def _work(self):
        try:
            while not self.closed.is_set():
                if self.error:
                    raise RuntimeError(self.error)
                try:
                    near, far, delay = self.blocks.get(timeout=.1)
                except queue.Empty:
                    continue
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
                # Allow the filter to converge at the start of a playback burst.
                settling = speaking and now - self.play_started < .35
                was_started = self.detector.started
                interrupt, audio, rms = self.detector.feed(
                    clean, .99 if speech else 0., speaking, settling)
                if self.verify_interrupt is not None:
                    if interrupt:
                        self.speaker_frames = list(self.speaker_preroll)[-len(self.detector.frames):]
                    elif was_started:
                        self.speaker_frames.append(speaker_block.copy())
                self.on_status(level=min(1, rms * 15), output_level=min(1, float(np.sqrt(np.mean(far * far))) * 10))
                if interrupt:
                    self.turn_serial += 1
                    self.interrupt_checked = False
                    if self.verify_interrupt is None:
                        self.interruptions += 1
                        self.cancel_playback()
                        self.on_interrupt()
                if self.verify_interrupt is not None and self.detector.started and self.detector.voiced >= 160:
                    self._check_focus_interrupt(np.concatenate(self.speaker_frames))
                if audio is not None:
                    if self.verify_interrupt is not None:
                        speaker_audio = np.concatenate(self.speaker_frames)
                        self.speaker_frames = []
                        self._check_focus_interrupt(speaker_audio)
                        self._submit_focused_turn(CapturedTurn(audio,speaker_audio,self.turn_serial))
                    else: self._queue_turn(audio)
        except Exception as exc:
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
                return self.utterances.get(timeout=.05)
            except queue.Empty:
                if time.monotonic() >= deadline and not self.detector.started and not self.pending_verifications:
                    return None
        return None

    def discard(self):
        while True:
            try:
                self.utterances.get_nowait()
            except queue.Empty:
                break

    def close(self):
        self.closed.set()
        self.cancel_playback()
        if self.stream:
            self.stream.stop()
            self.stream.close()
        if self.worker.is_alive() and self.worker is not threading.current_thread():
            self.worker.join(timeout=1)
