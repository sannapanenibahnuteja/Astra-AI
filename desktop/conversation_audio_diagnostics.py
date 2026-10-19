"""Deterministic native DSP checks. No microphone, personal profile or network."""
import time
import numpy as np
from desktop.audio_pipeline import WebRTCStage
from desktop.duplex_audio import RATE, BLOCK, TurnDetector


def verify():
    random=np.random.default_rng(41)
    far=random.normal(0,.06,RATE*6).astype(np.float32)
    near=np.r_[np.zeros(2880,np.float32),far[:-2880]*.6]
    stage=WebRTCStage(suppress=False);stage.stream_delay_ms=60
    times=[];output=[]
    for offset in range(0,len(far),BLOCK):
        started=time.perf_counter()
        output.append(stage.process(near[offset:offset+BLOCK],far[offset:offset+BLOCK]))
        times.append((time.perf_counter()-started)*1000)
    clean=np.concatenate(output)
    reduction=float(10*np.log10(np.mean(near[-RATE:]**2)/max(1e-15,np.mean(clean[-RATE:]**2))))
    # Separately exercise the configurable suppression stage, with exact blocks.
    for level in (0,1,2):
        denoiser=WebRTCStage(level=level)
        for _ in range(30):
            processed=denoiser.process(random.normal(0,.003,BLOCK).astype(np.float32),np.zeros(BLOCK,np.float32))
            assert len(processed)==BLOCK and np.isfinite(processed).all()
    detector=TurnDetector();detector.quiet_frames=65;detector.adaptive=True
    signal=np.full(BLOCK,.02,np.float32)
    onset=None
    for index in range(40):
        interrupted,_,_=detector.feed(signal,.99,True,False)
        if interrupted:onset=(index+1)*10
    endpoint=None
    for index in range(180):
        _,audio,_=detector.feed(np.zeros(BLOCK,np.float32),0)
        if audio is not None:endpoint=(index+1)*10;break
    assert reduction>=10 and onset is not None and endpoint is not None
    return {'passed':True,'frame_ms':10,'sample_rate':RATE,
            'native_aec_reduction_db':round(reduction,1),'dsp_frame_p95_ms':round(float(np.percentile(times,95)),3),
            'dsp_frame_max_ms':round(max(times),3),'controlled_vad_onset_ms':onset,
            'controlled_short_turn_endpoint_ms':endpoint,'suppression_levels_exercised':[0,1,2],
            'microphone_used':False,'scope':'Seeded simulated echo and controlled VAD input; not live speech accuracy or end-to-end interruption latency.'}
