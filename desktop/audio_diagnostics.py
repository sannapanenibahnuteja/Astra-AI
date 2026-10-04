"""Safe packaged audio check: no transcription, Windows commands or saved audio."""
import base64
import time

import numpy as np

from desktop.duplex_audio import RATE, BLOCK, wav_samples
from desktop.voice import Voice, RENDER


def verify():
    from pywebrtc_audio import AudioProcessor
    rng = np.random.default_rng(42)
    far = rng.normal(0, .08, RATE * 5).astype(np.float32)
    near = np.concatenate([np.zeros(2880, np.float32), far[:-2880] * .6])
    ap = AudioProcessor(sample_rate=RATE, echo_cancellation=True,
                        noise_suppression=True, stream_delay_ms=60)
    clean = np.concatenate([ap.process(near[i:i+BLOCK], far[i:i+BLOCK])
                            for i in range(0, len(far), BLOCK)])
    reduction = float(10 * np.log10(np.mean(near[-RATE:] ** 2) / max(1e-15, np.mean(clean[-RATE:] ** 2))))
    assert reduction >= 10, 'Echo cancellation did not suppress the simulated echo.'
    voice = Voice()
    interrupts = []
    voice.on_interrupt = lambda: interrupts.append(True)
    result = {'simulated_echo_reduction_db': round(reduction, 1)}
    try:
        encoded = voice._run(RENDER, {'text': 'Bob echo cancellation audio test.', 'rate': 0}, 30)
        data = base64.b64decode(encoded, validate=True)
        result['windows_speech_samples'] = len(wav_samples(data))
        voice.session(True)
        engine = voice._ensure_duplex()
        if engine is None:
            raise RuntimeError(voice.status()['error'])
        engine.play(data, voice._cancel)
        time.sleep(.6)
        if engine.error:
            raise RuntimeError(engine.error)
        result.update(voice.status())
        result['detected_interruptions'] = len(interrupts)
        result['ok'] = True
    finally:
        voice.close()
    return result
