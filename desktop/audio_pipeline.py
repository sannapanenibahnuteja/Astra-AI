"""Replaceable audio stages and lightweight, explicitly heuristic quality estimates."""
from collections import deque
from dataclasses import dataclass
from typing import Protocol
import math
import numpy as np

DEFAULT_AUDIO = {'audio_streaming_preview':True, 'audio_fast_barge_in':True,
                 'audio_noise_level':1, 'audio_array_delays':[], 'audio_group_mode':False,
                 'audio_pause_learning':True, 'voice_pause_profiles':{}}


def recognition_samples(audio):
    """48 kHz mono -> 16 kHz with a small anti-alias FIR, no extra runtime."""
    positions=np.arange(-30,31)
    kernel=np.sinc(positions/3)*np.hamming(61)
    kernel/=kernel.sum()
    return np.convolve(np.asarray(audio,dtype=np.float32),kernel,mode='same')[::3].astype(np.float32)


def validate_options(values):
    for key in ('audio_streaming_preview','audio_fast_barge_in','audio_group_mode','audio_pause_learning'):
        if key in values and type(values[key]) is not bool:raise ValueError('Invalid audio preference.')
    if 'audio_noise_level' in values and (type(values['audio_noise_level']) is not int or values['audio_noise_level'] not in (0,1,2)):
        raise ValueError('Choose light, moderate, or stronger noise suppression.')
    if 'audio_array_delays' in values:
        delays=values['audio_array_delays']
        if not isinstance(delays,list) or len(delays)>8 or len(delays)==1 or any(type(v) is not int or not 0<=v<=240 for v in delays):
            raise ValueError('Array delays require two to eight synchronized channels, each from 0 to 240 samples.')
    if 'voice_pause_profiles' in values:
        profiles=values['voice_pause_profiles']
        if not isinstance(profiles,dict) or len(profiles)>8:raise ValueError('Invalid learned pause profiles.')
        for key,row in profiles.items():
            if not isinstance(key,str) or len(key)>128 or not isinstance(row,dict) or set(row)!={'count','mid_pause_ms'}:
                raise ValueError('Invalid learned pause profile.')
            if type(row['count']) is not int or not 0<=row['count']<=1000 or type(row['mid_pause_ms']) not in (float,int) or not math.isfinite(row['mid_pause_ms']) or not 150<=row['mid_pause_ms']<=1800:
                raise ValueError('Invalid learned pause statistics.')


class AudioStage(Protocol):
    stream_delay_ms:int
    def process(self,near:np.ndarray,far:np.ndarray)->np.ndarray: ...


class TargetSpeakerExtractor(Protocol):
    """An installed extractor must return aligned mono float32 at the input rate."""
    def extract(self,audio:np.ndarray,rate:int,profile_id:str)->np.ndarray: ...


class WebRTCStage:
    def __init__(self,rate=48000,suppress=True,level=1):
        from pywebrtc_audio import AudioProcessor
        self.native=AudioProcessor(sample_rate=rate,echo_cancellation=True,noise_suppression=suppress,
                                   ns_level=level,auto_gain_control=False)
    @property
    def stream_delay_ms(self):return self.native.stream_delay_ms
    @stream_delay_ms.setter
    def stream_delay_ms(self,value):self.native.stream_delay_ms=value
    def process(self,near,far):return self.native.process(near,far)


class Beamformer:
    """Optional calibrated delay-and-sum. No invented microphone geometry."""
    def __init__(self,delays=None):
        self.delays=list(delays or []);self.channels=len(self.delays) or 1
        self.history=[np.zeros(delay,np.float32) for delay in self.delays]

    def process(self,frames):
        frames=np.asarray(frames,dtype=np.float32)
        if not self.delays:return frames[:,0] if frames.ndim==2 else frames
        if frames.ndim!=2 or frames.shape[1]!=self.channels:raise ValueError('The configured microphone array channels are unavailable.')
        aligned=[]
        for index,delay in enumerate(self.delays):
            combined=np.concatenate([self.history[index],frames[:,index]])
            aligned.append(combined[:len(frames)])
            self.history[index]=combined[-delay:].copy() if delay else np.empty(0,np.float32)
        return np.mean(aligned,axis=0,dtype=np.float32)


class EnvironmentMonitor:
    """Signal heuristics, not a trained cafe/car/music or emotion classifier."""
    def __init__(self,rate=48000):
        self.rate=rate;self.quiet=deque(maxlen=200);self.tick=0
        self.current={'environment':'unknown','snr_db':None,'clipping_fraction':0.,'noise_rms':0.}

    def observe(self,raw,clean,speech,playing):
        self.tick+=1
        if self.tick%5:return self.current
        clean=clean-float(np.mean(clean));rms=float(np.sqrt(np.mean(clean*clean)))
        if not speech and not playing:self.quiet.append(rms)
        noise=float(np.percentile(self.quiet,40)) if self.quiet else 0.
        snr=None if len(self.quiet)<4 else round(float(np.clip(10*np.log10(max(rms*rms-noise*noise,1e-12)/max(noise*noise,1e-12)),-20,60)),1)
        spectrum=np.abs(np.fft.rfft(clean*np.hanning(len(clean))))**2
        total=float(np.sum(spectrum))+1e-12
        low=float(np.sum(spectrum[np.fft.rfftfreq(len(clean),1/self.rate)<250]))/total
        crest=float(np.max(np.abs(clean)))/max(rms,1e-9)
        environment=('speech' if speech else 'impulsive_noise' if crest>8 and rms>.0005 else
                     'low_frequency_noise' if low>.7 and rms>.0004 else
                     'steady_noise' if rms>.001 else 'quiet')
        self.current={'environment':environment,'snr_db':snr,'noise_rms':round(noise,6),
                      'clipping_fraction':round(float(np.mean(np.abs(raw)>=.995)),4)}
        return self.current


class SourceSelector:
    """Quality-driven source choice for explicitly registered/consented sources."""
    def __init__(self):self.current=None;self.candidate=None;self.streak=0
    def choose(self,sources,at_boundary=True):
        eligible={key:row for key,row in sources.items() if row.get('consented') and row.get('stable')}
        if self.current not in eligible:self.current=None
        if not eligible:return self.current
        def score(row):return row.get('snr_db',-20)-100*row.get('clipping',0)-.02*row.get('latency_ms',0)
        best=max(eligible,key=lambda key:score(eligible[key]))
        if self.current is None:
            if at_boundary:self.current=best
            return self.current
        if not at_boundary or best==self.current or score(eligible[best])-score(eligible.get(self.current,{}))<3:
            self.candidate=None;self.streak=0;return self.current
        self.streak=self.streak+1 if self.candidate==best else 1;self.candidate=best
        if self.streak>=3:self.current=best;self.streak=0
        return self.current


@dataclass
class PreviewFrame:
    serial:int
    audio:np.ndarray
    speaker:np.ndarray
    captured_at:float


def validate_extraction(original,extracted):
    result=np.asarray(extracted,dtype=np.float32)
    if result.ndim!=1 or len(result)!=len(original) or not np.isfinite(result).all():
        raise ValueError('The target-speaker extractor returned unaligned or invalid audio.')
    return np.clip(result,-1,1)
