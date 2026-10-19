"""Deterministic native DSP checks. No microphone, personal profile or network."""
import time
import numpy as np
from desktop.audio_pipeline import WebRTCStage
from desktop.duplex_audio import RATE, BLOCK, TurnDetector, InterruptionGate


def verify():
    from desktop.interruption import intended_interruption
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
    gate=InterruptionGate()
    tiny_rejected=not any(gate.feed(.0003,True,noise=0) for _ in range(300))
    gate.reset()
    click_rejected=not any(gate.feed(.03 if index<5 else .0001,True) for index in range(100))
    gate.reset();speech_gate=None
    for index in range(40):
        voiced=index%5!=0
        if gate.feed(.002 if voiced else .0001,voiced):speech_gate=(index+1)*10;break
    assert tiny_rejected and click_rejected and speech_gate is not None and speech_gate<=300
    intent_rejections=all(not intended_interruption(text,.99,False) for text in
        ('blah blah','Bob banana','thanks for watching','open youtube','Bob do not stop'))
    directed_accepted=intended_interruption('Bob stop',.95,False) and intended_interruption('Actually open calculator',.95,False)
    uncertain_rejected=not intended_interruption('Bob stop',.6,False)
    assert intent_rejections and directed_accepted and uncertain_rejected
    wake_guard=all(not intended_interruption(text,.99,False,require_trigger=True) for text in ('Shorter','Actually open calculator','Bob open YouTube','blah blah'))
    wake_guard=wake_guard and all(intended_interruption(text,.99,False,require_trigger=True) for text in ('Hey Bob','Hey Bob open calculator','Bob please stop talking','Stop listening'))
    assert wake_guard
    return {'passed':True,'frame_ms':10,'sample_rate':RATE,
            'native_aec_reduction_db':round(reduction,1),'dsp_frame_p95_ms':round(float(np.percentile(times,95)),3),
            'dsp_frame_max_ms':round(max(times),3),'controlled_vad_onset_ms':onset,
            'controlled_short_turn_endpoint_ms':endpoint,'suppression_levels_exercised':[0,1,2],
            'quiet_false_vad_rejected':tiny_rejected,'brief_click_rejected':click_rejected,
            'controlled_speech_interruption_gate_ms':speech_gate,
            'gibberish_and_undirected_rejected':intent_rejections,'directed_controls_accepted':directed_accepted,
            'uncertain_interrupt_words_rejected':uncertain_rejected,
            'wake_phrase_policy_passed':wake_guard,
            'microphone_used':False,'scope':'Seeded simulated echo and controlled VAD input; not live speech accuracy or end-to-end interruption latency.'}
