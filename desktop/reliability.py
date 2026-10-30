"""Local reliability policy: measured timings, explicit targets, no guessed scores."""
from collections import deque
import math
import re
import threading
import time

# Targets, never advertised as measured guarantees. None = workload dependent.
BUDGETS = {
    'audio_capture_latency':(30,'Driver callback to DSP worker; excludes physical microphone latency.'),
    'audio_processing_latency':(10,'One 10 ms frame on the DSP worker.'),
    'vad_latency':(150,'First detected speech evidence to capture onset.'),
    'speaker_detection_latency':(200,'Completed-turn speaker verification processing.'),
    'asr_partial_latency':(300,'Capture onset to first published provisional transcript.'),
    'endpoint_latency':(500,'Last VAD speech frame to endpoint; not semantic ground truth.'),
    'intent_latency':(150,'Final request routing/planning; workload dependent.'),
    'tool_dispatch_latency':(100,'Validated action dispatch; not completion time.'),
    'llm_first_token_latency':(600,'Model request sent to first output; model dependent.'),
    'tts_first_chunk_latency':(300,'Text chunk submitted to first rendered PCM.'),
    'audio_output_latency':(100,'Driver-reported output buffering estimate, not measured sound.'),
    'total_turn_latency':(900,'Speech endpoint to first playback submission; not physical audibility.'),
}


def latency_report(*snapshots):
    observed={}
    for snapshot in snapshots:observed.update(snapshot.get('latency_ms',{}))
    return {name:{'target_ms':target,'definition':definition,
                  'observed':observed.get(name),
                  'status':('unmeasured' if name not in observed else
                            'within_target' if observed[name].get('p95',float('inf'))<=target else 'above_target')}
            for name,(target,definition) in BUDGETS.items()}


class TurnTrace:
    """Bounded metadata-only event replay; no transcript, name, path or tool args.

    This is observational: it cannot dispatch, retry, roll back or cancel tools.
    Replaying a trace validates ordering, never repeats real actions.
    """
    NEXT={'IDLE':{'CAPTURING'},'CAPTURING':{'VERIFYING','RECOVERY','CANCELLED'},
          'VERIFYING':{'TRANSCRIBING','RECOVERY','CANCELLED'},
          'TRANSCRIBING':{'READY','RECOVERY','CANCELLED'},
          'READY':{'CAPTURING','IDLE'},'RECOVERY':{'CAPTURING','IDLE'},
          'CANCELLED':{'CAPTURING','IDLE'}}
    def __init__(self,clock=time.monotonic):
        self.clock=clock;self.state='IDLE';self.events=deque(maxlen=128)
        self.lock=threading.Lock();self.sequence=0

    def transition(self,state,reason=''):
        if state not in self.NEXT:raise ValueError('Unknown capture state')
        # Reasons are fixed codes, never caller text.
        if reason not in ('','idle','no_words','speaker_rejected','cancelled','device_failed'):
            raise ValueError('Unknown capture reason')
        with self.lock:
            if state==self.state:return True
            allowed=state in self.NEXT[self.state]
            self.sequence+=1
            self.events.append({'sequence':self.sequence,'at':round(self.clock(),3),
                'from':self.state,'to':state,'valid':allowed,'reason':reason})
            if allowed:self.state=state
            return allowed

    def snapshot(self):
        with self.lock:return {'state':self.state,'events':[dict(v) for v in self.events]}

    @classmethod
    def replay(cls,events):
        if not isinstance(events,list) or len(events)>128:raise ValueError('Invalid trace')
        valid=True;last=None
        for event in events:
            before,after=event.get('from'),event.get('to')
            if before not in cls.NEXT or after not in cls.NEXT:raise ValueError('Invalid state')
            valid=valid and (last is None or before==last) and after in cls.NEXT[before] and event.get('valid') is True
            last=after
        return {'passed':valid,'events':len(events),'actions_executed':0}


def percentiles(values):
    rows=sorted(float(v) for v in values if math.isfinite(float(v)) and float(v)>=0)
    if not rows:return {}
    def percentile(p):return round(rows[max(0,math.ceil(p*len(rows))-1)],1)
    return {'p50':percentile(.50),'p90':percentile(.90),'p95':percentile(.95),'p99':percentile(.99)}


class ExpectedReply:
    """One narrow same-speaker answer after an explicit assistant question."""
    PATTERNS={
        'confirmation':r'(?:yes|yes please|no|cancel|correct|go ahead)',
        'time':r'(?:at )?(?:\d{1,2}(?::\d{2})?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)(?: (?:thirty|fifteen|forty five))?(?: ?(?:am|pm)| in the (?:morning|evening|afternoon))?',
        'day':r'(?:today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)(?: (?:morning|evening|afternoon))?',
        'option':r'(?:the )?(?:first|second|third|fourth|\d)(?: one)?',
    }
    def __init__(self,clock=time.monotonic):
        self.clock=clock;self.lock=threading.Lock();self.kind='';self.owner='';self.until=0.
    def clear(self):
        with self.lock:self.until=0.
    def arm(self,question,owner):
        text=question.strip().lower()
        kind=('confirmation' if re.search(r'\b(?:say .?yes|should i|want me to|shall i)\b',text) else
              'time' if re.search(r'\b(?:what|which) time\b',text) else
              'day' if re.search(r'\b(?:what|which) (?:day|date)\b',text) else
              'option' if re.search(r'\bwhich (?:one|option)\b',text) else '')
        with self.lock:
            self.kind=kind;self.owner=owner or '';self.until=self.clock()+12 if kind and owner else 0.
    def accepts(self,result):
        with self.lock:
            if (self.clock()>=self.until or not self.kind or not self.owner
                    or result.get('confidence',0)<.80 or result.get('needs_review',True)
                    or result.get('speaker',{}).get('state')!='matched'
                    or result.get('speaker',{}).get('profile_id')!=self.owner):return False
            text=result.get('text','').strip().lower().rstrip('.!?')
            if not re.fullmatch(self.PATTERNS[self.kind],text):return False
            self.until=0.;return True
