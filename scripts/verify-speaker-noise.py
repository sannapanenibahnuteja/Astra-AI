"""Real local model with public synthetic speech; no microphone or native actions."""
import base64
import io
import json
import tempfile
import wave
from pathlib import Path
import numpy as np
from desktop.voice import Voice, RENDER
from desktop.voice_choices import installed
from desktop.speaker import SpeakerProfiles

voices=installed()
if not voices: raise RuntimeError('No Windows synthesis voices available for this test.')
voice=Voice()
sentences=[
    'Hello Bob, I would like you to recognize my normal speaking voice while I tell you about my plans and the things I enjoy doing every day.',
    'I work on several projects and I like having a helpful assistant who understands my preferences and remembers the important details from our conversations.',
    'This is another natural sentence with different words and sounds, recorded at a normal pace so the speaker profile has enough useful information.',
    'Please help me prepare for the afternoon and tell me which tasks I should finish first before I take a break and have something to eat.'
]
def speech(text, name):
    encoded=voice._run(RENDER,{'text':text,'voice':name,'rate':0},30)
    with wave.open(io.BytesIO(base64.b64decode(encoded))) as wav:
        samples=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype(np.float32)/32768
        rate=wav.getframerate()
        if wav.getnchannels()>1: samples=samples.reshape(-1,wav.getnchannels()).mean(axis=1)
    return samples,rate
Path('.cache').mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir='.cache',prefix='speaker-noise-') as folder:
    bank=SpeakerProfiles(folder)
    try:
        fixtures=[speech(text,voices[0]['id']) for text in sentences]
        for audio,rate in fixtures[:3]: bank.enroll('Synthetic saved voice',audio,rate)
        audio,rate=fixtures[3]
        clean=bank.identify(audio,rate,select=False)
        rms=float(np.sqrt(np.mean(audio*audio)))
        noisy=np.clip(audio+np.random.default_rng(7).normal(0,rms/np.sqrt(10),len(audio)).astype(np.float32),-.98,.98)
        noise_match=bank.identify(noisy,rate,select=False)
        result={'user_microphone_used':False,'native_actions_executed':False,'clean_held_out_match':clean['state']=='matched',
                'added_broadband_noise_snr_db':10,'noisy_held_out_match':noise_match['state']=='matched',
                'note':'Synthetic speech is a model check, not proof of real-user or overlapping-speech accuracy.'}
        if len(voices)>1:
            other,other_rate=speech(sentences[3],voices[1]['id'])
            result['unregistered_synthetic_voice_rejected']=bank.identify(other,other_rate,select=False)['state']!='matched'
        Path('.cache/speaker-noise-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps(result))
        assert result['clean_held_out_match']
    finally:
        bank.close(); voice.close()
