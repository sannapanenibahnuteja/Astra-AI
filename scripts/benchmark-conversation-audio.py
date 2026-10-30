"""Repeatable local synthetic SNR benchmark; no mic, tool calls or downloads."""
import argparse
import json
from pathlib import Path
import sys
import threading
import time
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop.voice import Voice
from desktop.duplex_audio import wav_samples
from desktop.audio_pipeline import recognition_samples
from desktop.voice_model_diagnostics import errors
from desktop.reliability import percentiles


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='.cache/conversation-snr-benchmark.json')
    parser.add_argument('--model',choices=['small.en','distil-large-v3'],default='small.en')
    args=parser.parse_args()
    voice=Voice();voice.transcription_model=args.model
    rng=np.random.default_rng(4207)
    rows=[]
    phrases=['Hey Bob, open the calculator.','Hey Bob, please stop talking.',
             'Hey Bob, set the volume to fifty percent.']
    try:
        for index,phrase in enumerate(phrases):
            wav=voice._speech_worker().render(phrase,0,'',threading.Event(),threading.Event())
            clean=recognition_samples(wav_samples(wav))
            noise=rng.normal(0,1,len(clean)).astype(np.float32)
            # Fixed broadband + low-frequency hum; not a real cafe or car.
            noise+=np.sin(np.arange(len(clean))*2*np.pi*90/16000).astype(np.float32)
            for snr in (None,20,10,5,0,-5):
                audio=clean.copy()
                if snr is not None:
                    scale=np.sqrt(np.mean(clean*clean)/max(np.mean(noise*noise),1e-12))*10**(-snr/20)
                    audio=np.clip(audio+noise*scale,-.999,.999)
                start=time.monotonic();result=voice.transcribe(audio)
                wrong,total=errors(phrase,result['text'])
                rows.append({'phrase_id':index,'snr_db':snr,'decode_ms':round((time.monotonic()-start)*1000,1),
                    'word_errors':wrong,'reference_words':total,'wer':round(wrong/max(total,1),3),
                    'needs_review':result['needs_review'],'text_present':bool(result['text']),
                    'scope':'Generated speech; no speaker identity, intent or executed-action accuracy measured.'})
        report={'seed':4207,'model':args.model,'microphone_used':False,'actions_executed':0,
                'latency_ms':percentiles([r['decode_ms'] for r in rows]),'trials':rows,
                'limitations':'Synthetic Windows speech plus seeded noise/hum. Not live accent, overlap, room or physical latency acceptance.'}
        path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(str(path.resolve()))
    finally:voice.close()


if __name__=='__main__':main()
