"""Session-scoped WASAPI playback/capture with a shared WebRTC AEC reference.

The audio callback only copies bounded blocks. DSP, speech detection and callbacks
run on a worker, never on PortAudio's real-time thread. No audio is saved to disk.
"""
from collections import deque
import queue
import threading
import time
import logging

import numpy as np

RATE = 48000
BLOCK = RATE // 100


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


class TurnDetector:
    """Bounded utterance buffer with pre-roll and sustained-speech interruption."""
    def __init__(self):
        self.preroll = deque(maxlen=60)
        self.frames = []
        self.streak = self.silence = self.voiced = 0
        self.noise = .0001
        self.onset = deque(maxlen=15)
        self.speech_peak = 0.
        self.started = False

    def feed(self, clean, probability, speaking=False, settling=False):
        rms = float(np.sqrt(np.mean(clean * clean)))
        threshold = max(.0002, min(.01, self.noise * 2.5), self.speech_peak * .08 if self.started else 0)
        speech = probability >= .80 and rms >= threshold and not settling
        if not speaking and not speech:
            self.noise = .98 * self.noise + .02 * min(rms, .004)
        interrupt = False
        if not self.started:
            self.preroll.append(clean.copy())
            self.onset.append(bool(speech))
            self.streak = self.streak + 1 if speech else 0
            if sum(self.onset) >= 8 and speech:
                self.started = True
                self.speech_peak = min(.1, rms)
                self.voiced = sum(self.onset)
                self.frames = list(self.preroll)
                self.preroll.clear()
                interrupt = True
        else:
            self.frames.append(clean.copy())
            if speech:
                self.speech_peak = max(self.speech_peak * .99, min(.1, rms))
            self.voiced += int(speech)
            self.silence = 0 if speech else self.silence + 1
            if self.silence >= 55 or len(self.frames) >= 2000:
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
        self.worker = threading.Thread(target=self._work, daemon=True)

    def start(self):
        import sounddevice as sd
        # Resolve the current Windows defaults in WASAPI, rather than MME aliases.
        host = next(h for h in sd.query_hostapis() if h['name'] == 'Windows WASAPI')
        device = (host['default_input_device'], host['default_output_device'])
        if min(device) < 0:
            raise RuntimeError('A Windows microphone and speaker are required.')
        inputs, outputs = [sd.query_devices(d) for d in device]
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
                clean = self.processor.process(near, far)
                self.raw_rms = float(np.sqrt(np.mean(near * near)))
                self.clean_rms = float(np.sqrt(np.mean(clean * clean)))
                # Normalize only the VAD input. Keep AEC/reference and captured
                # audio at their original scale; do not amplify the echo path.
                vad_gain = min(8., max(1., .015 / max(self.clean_rms, .0001)))
                pcm = ((clean * vad_gain).clip(-1, 1) * 32767).astype('<i2').tobytes()
                speech = self.vad.is_speech(pcm, RATE)
                now = time.monotonic()
                speaking = now < self.echo_until
                # Allow the filter to converge at the start of a playback burst.
                settling = speaking and now - self.play_started < .35
                interrupt, audio, rms = self.detector.feed(
                    clean, .99 if speech else 0., speaking, settling)
                self.on_status(level=min(1, rms * 15))
                if interrupt:
                    self.interruptions += 1
                    logging.info('Voice speech onset: raw_rms=%.6f clean_rms=%.6f playback=%s', self.raw_rms, self.clean_rms, speaking)
                    self.cancel_playback()
                    self.on_interrupt()
                if audio is not None:
                    self.completed_turns += 1
                    logging.info('Voice utterance complete: seconds=%.2f queued=%s', len(audio)/RATE, self.utterances.qsize())
                    try:
                        self.utterances.put_nowait(audio)
                    except queue.Full:
                        # Keep earlier requests; don't execute an unbounded backlog.
                        self.on_status(error='Please wait for Bob to finish processing your request.')
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
            self.play_started = time.monotonic()
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
                if time.monotonic() >= deadline and not self.detector.started:
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
