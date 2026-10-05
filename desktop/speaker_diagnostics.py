"""Validate packaged speaker inference using generated speech, no user microphone."""
import base64
import io
import tempfile
import wave
import numpy as np
from desktop.voice import RENDER
from desktop.speaker import SpeakerProfile


def verify(runtime):
    encoded = runtime._voice._run(RENDER, {'text':'Hello Bob. This is a generated test of local speaker recognition. My voice profile should match the same recorded sentence.', 'rate':0}, 30)
    with wave.open(io.BytesIO(base64.b64decode(encoded))) as wav:
        rate = wav.getframerate()
        if wav.getsampwidth() != 2: raise RuntimeError('Unsupported diagnostic speech format.')
        audio = np.frombuffer(wav.readframes(wav.getnframes()), dtype='<i2').astype(np.float32)/32768
        if wav.getnchannels() > 1: audio = audio.reshape(-1,wav.getnchannels()).mean(axis=1)
    with tempfile.TemporaryDirectory(prefix='speaker-test-', dir=runtime._store.root) as root:
        profile = SpeakerProfile(root)
        try:
            for _ in range(3): profile.enroll('Generated fixture', audio, rate)
            result = profile.identify(audio, rate)
            restored = SpeakerProfile(root)
            try:
                reloaded = restored.identify(audio, rate)
                restored.clear()
                return {'version':runtime.bootstrap()['version'], 'same_fixture_match':result['state']=='matched',
                        'similarity':result.get('similarity'), 'encrypted_reload_match':reloaded['state']=='matched',
                        'deleted':not restored.path.exists(), 'user_microphone_used':False,
                        'note':'Generated identical-sample packaging check; not a live-user accuracy test.'}
            finally: restored.close()
        finally: profile.close()
