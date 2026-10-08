"""Generated-speech speaker-stop -> endpoint -> Whisper -> action-plan check.

No microphone capture, saved audio, or Windows actions. The far-end playback is
stopped after onset, as in the real duplex loop, and its delayed echo is retained.
"""
import base64
import io
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import webrtcvad
from pywebrtc_audio import AudioProcessor
from desktop.voice import Voice, RENDER
from desktop.duplex_audio import RATE, BLOCK, TurnDetector, wav_samples, acoustic_speech
from desktop.commands import parse

voice = Voice()
def render(text):
    return wav_samples(base64.b64decode(voice._run(RENDER, {'text': text, 'rate': 0}, 30)))

try:
    far = render('This is Bob speaking through the speakers. I can explain how the audio system works while you interrupt me with another request. The echo canceller separates our voices using the playback reference. It works locally on your computer.')
    far = np.pad(far, (0, (-len(far)) % BLOCK))
    user = render('Actually, open calculator.')
    for gain in (0., .5, .1):
        played = far.copy()
        processor = AudioProcessor(sample_rate=RATE, echo_cancellation=True,
                                   noise_suppression=True, stream_delay_ms=60)
        detector, vad = TurnDetector(), webrtcvad.Vad(2)
        detector.quiet_frames=65  # Runtime's Natural pause setting.
        cutoff, results = None, []
        for i in range(0, len(far), BLOCK):
            near = np.zeros(BLOCK, np.float32)
            echo = i - 2880
            if echo >= 0:
                near += played[echo:echo + BLOCK] * .6
            start, end = max(i, RATE * 5), min(i + BLOCK, RATE * 5 + len(user))
            if end > start:
                near[start-i:end-i] += user[start-RATE*5:end-RATE*5] * gain
            clean = processor.process(near, played[i:i+BLOCK])
            rms = float(np.sqrt(np.mean(clean * clean)))
            boost = min(8., max(1., .015 / max(rms, .0001)))
            speech = vad.is_speech(((clean * boost).clip(-1, 1) * 32767).astype('<i2').tobytes(), RATE) and acoustic_speech(clean)
            onset, audio, _ = detector.feed(clean, .99 if speech else 0., cutoff is None)
            if onset and cutoff is None:
                cutoff = i
                played[i+BLOCK:] = 0
            if audio is not None:
                rms = float(np.sqrt(np.mean(audio * audio)))
                audio = audio * min(8., max(1., .035 / max(rms, .0001)))
                buffer = io.BytesIO()
                with wave.open(buffer, 'wb') as wav:
                    wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(RATE)
                    wav.writeframes((audio.clip(-1, 1) * 32767).astype('<i2').tobytes())
                buffer.seek(0)
                result = voice.transcribe(buffer)
                plan = parse(result['text'])
                print({'gain':gain, 'onset_seconds':cutoff/RATE, 'ended_seconds':i/RATE,
                       'transcription':result, 'plan':plan})
                results.append((result, plan))
        if gain == 0:
            assert cutoff is None and not results, 'Bob speech echo triggered an interruption'
            print('Bob-only echo: no interruption')
        else:
            assert any(plan and plan['action']=='open' and plan['target']=='calculator'
                       and not result['needs_review'] for result,plan in results), 'The complete interruption did not reach a reliable Calculator action plan'
finally:
    voice.close()
