"""Generated-speech model checks for the separate echo-cancelled speaker path."""
import json,runpy,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pywebrtc_audio import AudioProcessor
namespace=runpy.run_path('scripts/verify-speaker-noise.py')
bank=namespace['bank'];audio,rate=namespace['fixtures'][3]
rate48=48000
samples=np.interp(np.arange(round(len(audio)*rate48/rate))*rate/rate48,np.arange(len(audio)),audio).astype(np.float32)
results={}
try:
    for label,suppression in [('speaker_path',False),('transcription_path',True)]:
        processor=AudioProcessor(sample_rate=rate48,echo_cancellation=True,noise_suppression=suppression,auto_gain_control=False)
        blocks=[processor.process(samples[i:i+480],np.zeros(480,np.float32)) for i in range(0,len(samples)//480*480,480)]
        matched=bank.identify(np.concatenate(blocks),rate48,select=False)
        results[label]={'matched':matched['state']=='matched','similarity':matched.get('similarity'),'threshold':matched.get('threshold')}
    from desktop.speaker import prepare_audio
    active,_=prepare_audio(samples,rate48)
    short=np.concatenate([np.zeros(4800,np.float32),active[:int(rate48*.85)],np.zeros(4800,np.float32)])
    short_result=bank.identify(short,rate48,select=False)
    results['short_speech']={k:v for k,v in short_result.items() if k in ('state','similarity','threshold','speech_seconds')}
    rng=np.random.default_rng(11)
    far=rng.normal(0,.08,rate48*5).astype(np.float32)
    near=np.concatenate([np.zeros(2880,np.float32),far[:-2880]*.6])
    processor=AudioProcessor(sample_rate=rate48,echo_cancellation=True,noise_suppression=False,auto_gain_control=False,stream_delay_ms=60)
    cleaned=np.concatenate([processor.process(near[i:i+480],far[i:i+480]) for i in range(0,len(far),480)])
    if 'other' in namespace:
        other=namespace['other'];other_rate=namespace['other_rate']
        other48=np.interp(np.arange(round(len(other)*rate48/other_rate))*other_rate/rate48,np.arange(len(other)),other).astype(np.float32)
        unknown_processor=AudioProcessor(sample_rate=rate48,echo_cancellation=True,noise_suppression=False,auto_gain_control=False)
        unknown=np.concatenate([unknown_processor.process(other48[i:i+480],np.zeros(480,np.float32)) for i in range(0,len(other48)//480*480,480)])
        results['unregistered_voice_rejected_on_speaker_path']=bank.identify(unknown,rate48,select=False)['state']!='matched'
        assert results['unregistered_voice_rejected_on_speaker_path']
    results['speaker_echo_reduction_db']=round(float(10*np.log10(np.mean(near[-rate48:]**2)/max(1e-15,np.mean(cleaned[-rate48:]**2)))),1)
    results['user_microphone_used']=False
    results['scope']='Generated speech and simulated echo; not live-user accuracy.'
    Path('.cache/speaker-path-0.10.36.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results))
    assert results['speaker_path']['matched']
    assert results['speaker_echo_reduction_db']>=10
finally:bank.close()
