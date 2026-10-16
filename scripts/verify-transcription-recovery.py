"""Known public synthetic command recordings; no microphone, profiles or actions."""
import json
import sys
import time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from faster_whisper.audio import decode_audio
from desktop.voice import Voice

root=Path('.cache/voice-fixtures')
voice=Voice()
results=[]
try:
    for index in range(5):
        samples=decode_audio(str(root/f'{index}.wav'),sampling_rate=16000)
        for name,gain in [('normal',1.),('quiet',.08)]:
            start=time.monotonic()
            result=voice.transcribe(samples*gain)
            results.append({'fixture':index,'variant':name,'text':result['text'],'confidence':result['confidence'],'review':result['needs_review'],'seconds':round(time.monotonic()-start,2)})
    silence=voice.transcribe(np.zeros(16000*2,np.float32))
    hiss=voice.transcribe(np.random.default_rng(5).normal(0,.01,16000*2).astype(np.float32))
    output={'commands':results,'decoded':sum(bool(row['text']) for row in results),'total':len(results),'silence_empty':not silence['text'],'hiss_empty':not hiss['text'],'scope':'Real local Whisper with generated Windows speech fixtures; no live microphone or speaker filtering.'}
    Path('.cache/transcription-recovery-0.10.34.json').write_text(json.dumps(output,indent=2))
    print(json.dumps(output,indent=2))
finally:
    voice.close()
