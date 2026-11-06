"""Replaceable, buffered local ASR core. Never dispatches commands or stores audio."""
from dataclasses import dataclass
import numpy as np


@dataclass
class PreparedAudio:
    samples: np.ndarray
    rms: float
    clipping: float
    seconds: float


def prepare(audio):
    from faster_whisper.audio import decode_audio
    if hasattr(audio,'seek'):audio.seek(0)
    samples=audio if isinstance(audio,np.ndarray) else decode_audio(audio,sampling_rate=16000)
    samples=np.asarray(samples,dtype=np.float32)
    if samples.ndim!=1 or not 1600<=len(samples)<=16000*31 or not np.isfinite(samples).all():
        raise ValueError('The captured audio is invalid or too short. Please repeat your request.')
    samples=samples.copy()
    clipping=float(np.mean(np.abs(samples)>=.995))
    samples-=float(np.mean(samples))
    rms=float(np.sqrt(np.mean(samples*samples)))
    gain=min(8.,max(1.,.035/max(rms,.0001)))
    samples=np.ascontiguousarray(np.clip(samples*gain,-.999,.999),dtype=np.float32)
    return PreparedAudio(samples,rms,clipping,len(samples)/16000)


def transcript_result(segments):
    segments=list(segments)
    accepted=[s for s in segments if s.no_speech_prob<.65 and s.avg_logprob>-1.2]
    text=' '.join(s.text.strip() for s in accepted).strip()
    words=[w.probability for s in accepted for w in (s.words or [])]
    confidence=float(sum(words)/len(words)) if words else 0.
    review=bool(text) and (confidence<.65 or any(s.avg_logprob<-.7 for s in accepted)
                          or any(p<.25 for p in words))
    return {'text':text,'confidence':round(confidence,3),'needs_review':review,
            'language':'en','word_confidence_min':min(words) if words else 0.}


class Recognizer:
    """Decode a single immutable 16 kHz buffer; one evidence-gated recovery pass."""
    def decode(self,model,audio,cancel,retry_gate,vocabulary='',room_mode='balanced',allow_retry=True):
        prepared=prepare(audio)
        if cancel.is_set():return {'text':'','confidence':0.,'needs_review':False,'capture_status':'cancelled'}
        options=dict(language='en',beam_size=5,hotwords=vocabulary or None,
                     condition_on_previous_text=False,word_timestamps=True,temperature=0)
        segments,_=model.transcribe(prepared.samples,vad_filter=True,
            vad_parameters={'threshold':.28 if room_mode=='quiet' else .35,
                            'min_speech_duration_ms':80,'min_silence_duration_ms':350,'speech_pad_ms':180},**options)
        result=transcript_result(segments)
        if allow_retry and not result['text'] and not cancel.is_set():
            retry=retry_gate(prepared.samples)
            if retry is not None:
                segments,_=model.transcribe(retry,vad_filter=False,**options)
                result=transcript_result(segments)
        if cancel.is_set():return {'text':'','confidence':0.,'needs_review':False,'capture_status':'cancelled'}
        if prepared.clipping>.10 and result['text']:result['needs_review']=True
        result['audio_quality']={'seconds':round(prepared.seconds,2),'rms':round(prepared.rms,6),
                                 'clipping_fraction':round(prepared.clipping,4)}
        if not result['text']:
            result.update(capture_status='no_words',retryable=True,
                message='I captured audio but could not decode the words. Please repeat your request; nothing was executed.')
        return result
