"""Packaged speaker inference with varied generated speech, never microphone audio."""
import base64
import io
import tempfile
import wave
import numpy as np
from desktop.voice import RENDER
from desktop.speaker import SpeakerProfiles


def verify(runtime):
    def speech(text):
        encoded=runtime._voice._run(RENDER, {'text':text,'rate':0},30)
        with wave.open(io.BytesIO(base64.b64decode(encoded))) as wav:
            rate=wav.getframerate()
            if wav.getsampwidth()!=2: raise RuntimeError('Unsupported diagnostic speech format.')
            audio=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype(np.float32)/32768
            if wav.getnchannels()>1: audio=audio.reshape(-1,wav.getnchannels()).mean(axis=1)
        return audio,rate
    phrases=[
        'Hello Bob. This is my voice. I would like you to recognize me when we talk.',
        'I use this computer for my work and my projects. Help me plan a good day.',
        'We can have a natural conversation. Remember my voice and call me by my name.',
        'Could you tell me what time it is and help me prepare for the afternoon?'
    ]
    fixtures=[speech(text) for text in phrases]
    with tempfile.TemporaryDirectory(prefix='speaker-test-',dir=runtime._store.root) as root:
        profiles=SpeakerProfiles(root)
        try:
            for audio,rate in fixtures[:3]: profiles.enroll('Generated fixture',audio,rate)
            result=profiles.identify(*fixtures[0])
            different=profiles.identify(*fixtures[3])
            restored=SpeakerProfiles(root)
            try:
                reloaded=restored.identify(*fixtures[3])
                restored.clear()
                return {'version':runtime.bootstrap()['version'],'same_fixture_match':result['state']=='matched',
                        'different_phrase_match':different['state']=='matched','similarity':different.get('similarity'),
                        'threshold':different.get('threshold'),'encrypted_reload_match':reloaded['state']=='matched',
                        'deleted':not list(restored.root.glob('voice-user-*.dat')),'user_microphone_used':False,
                        'note':'Varied synthetic speech validates the model and profile path, not live-user accuracy.'}
            finally: restored.close()
        finally: profiles.close()
