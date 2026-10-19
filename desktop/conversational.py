"""Local conversational policy. Predictions are data, never tool authorization."""
from collections import Counter, deque
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import re
import threading
import time


class AttentionState(str, Enum):
    IDLE='IDLE'
    POSSIBLE_ATTENTION='POSSIBLE_ATTENTION'
    ATTENDING='ATTENDING'
    USER_SPEAKING='USER_SPEAKING'
    WAITING_FOR_FOLLOWUP='WAITING_FOR_FOLLOWUP'
    ASSISTANT_SPEAKING='ASSISTANT_SPEAKING'
    INTERRUPTED='INTERRUPTED'
    DISENGAGING='DISENGAGING'


def semantic_hint(text):
    value=str(text).strip().lower().rstrip('.!?')
    domain=next((name for name,pattern in {
        'calendar':r'\b(calendar|schedule|meeting|appointment)\b',
        'mail':r'\b(email|inbox|message)\b', 'files':r'\b(file|folder|document|project)\b',
        'media':r'\b(music|video|youtube|play|pause)\b',
        'device':r'\b(volume|brightness|wifi|bluetooth|window|monitor)\b',
    }.items() if re.search(pattern,value)), 'conversation')
    incomplete=bool(re.search(r'\b(and|or|but|because|with|to|at|for|the|a|my|actually|wait|uh|um|i mean)$',value)
                    or re.fullmatch(r'(i want to|can you|could you|i would like to)(?: \w+)?',value))
    return {'domain':domain, 'complete':not incomplete, 'pause_ms':1800 if incomplete else 650,
            'speculative':True, 'may_execute':False}


class AttentionEngine:
    def __init__(self, clock=time.monotonic):
        self.clock=clock; self.state=AttentionState.IDLE; self.last_interaction=0.
        self.active=False; self.awaiting_answer=False; self.score=0.; self.reason='inactive'
        self.lock=threading.RLock()

    def activate(self):
        with self.lock:
            self.active=True; self.last_interaction=self.clock();self.state=AttentionState.ATTENDING

    def transition(self,state):
        with self.lock: self.state=AttentionState(state)

    def disengage(self):
        with self.lock:
            self.active=False;self.awaiting_answer=False;self.score=0.;self.state=AttentionState.IDLE

    def evaluate(self,text,asr_confidence,speaker=None,require_saved=False,noisy=False):
        """Heuristic attention score, not a calibrated probability or identity score."""
        text=str(text).strip(); folded=text.lower()
        with self.lock:
            if not self.active: return {'accept':False,'score':0.,'reason':'inactive'}
            matched=(speaker or {}).get('state')=='matched'
            if require_saved and not matched:
                self.score=0.;self.reason='speaker_unverified'
                return {'accept':False,'score':0.,'reason':self.reason}
            addressed=bool(re.match(r'^(?:(?:hey|okay|ok)\s+)?bob\b',folded))
            social=bool(re.search(r'\b(?:he said|she said|they said|on (?:the )?tv|ask bob|talking to (?:him|her|them))\b',folded))
            # Mentioning Bob in a conversation about Bob is not an address.
            if social and not addressed:
                self.score=.15;self.reason='likely_other_conversation'
                return {'accept':False,'score':self.score,'reason':self.reason}
            recent=self.clock()-self.last_interaction<60
            micro=bool(re.fullmatch(r'(yes|no|later|tomorrow|actually \w+|the (?:first|second|third) one|that one|there|him|same as before)[.!?]*',folded))
            direct=bool(re.match(r'^(?:bob[, ]+)?(?:please |can you |could you )?(open|close|play|pause|set|show|tell|explain|remember|cancel|stop|quiet|listen|what|why|how|who|when|where|is|are)\b',folded))
            score=.30+.22*matched+.14*recent+.24*addressed+.12*direct+.18*(self.awaiting_answer and micro)
            score+=.10*max(0.,min(1.,float(asr_confidence)))
            if noisy:score-=.06
            self.score=round(min(1.,score),3)
            accepted=self.score>=(.57 if noisy else .50)
            self.reason='directed_turn' if accepted else 'attention_uncertain'
            if accepted:
                self.last_interaction=self.clock();self.state=AttentionState.ATTENDING
            else:self.state=AttentionState.POSSIBLE_ATTENTION
            return {'accept':accepted,'score':self.score,'reason':self.reason}

    def snapshot(self):
        with self.lock:return {'state':self.state.value,'score':self.score,'reason':self.reason,'awaiting_answer':self.awaiting_answer}


RECOVERY = {
    'INTENT_UNCERTAIN':('clarify','I could not validate that request. Specify the missing target or correct the words on screen.'),
    'ASR_UNCERTAIN':('review','Check the words on screen; correct only the part I missed.'),
    'SPEAKER_UNCERTAIN':('silent','I could not confidently match the voice. Try a longer phrase or Test voice match.'),
    'TOOL_FAILED':('report','The action failed. Check its result before trying again.'),
    'NETWORK_FAILED':('local','The model is unavailable. Local listening still works; no action will be replayed.'),
    'AUDIO_DEVICE_FAILED':('restart','Check Windows Sound input, then restart voice conversation.'),
    'TTS_FAILED':('text','The reply is on screen. Check your output device or choose another voice.'),
    'MULTIPLE_SPEAKERS_AMBIGUOUS':('silent','Please speak one at a time.'),
    'NO_SPEECH_DETECTED':('listen','I did not detect enough speech.'),
    'ACTION_REQUIRES_CONFIRMATION':('confirm','Confirm the pending action or say cancel.'),
}


class QualityMetrics:
    """Bounded RAM-only aggregates; text used for repetition is hashed per session."""
    def __init__(self):
        self.counts=Counter();self.timings={};self.last={};self.lock=threading.RLock()

    def event(self,name,amount=1):
        with self.lock:self.counts[name]+=amount

    def timing(self,name,milliseconds):
        with self.lock:self.timings.setdefault(name,deque(maxlen=64)).append(max(0.,float(milliseconds)))

    def utterance(self,scope,text):
        value=re.sub(r'^(?:i said|as i said|i asked)[, ]+','',text.strip().lower())
        digest=hashlib.blake2s(value.encode()).hexdigest()
        with self.lock:
            old=self.last.get(scope)
            if old and old[0]==digest and time.monotonic()-old[1]<120:self.counts['user_repetitions']+=1
            self.last[scope]=(digest,time.monotonic())
            if len(self.last)>32:self.last.pop(next(iter(self.last)))
            self.counts['user_turns']+=1
            if re.search(r'\b(actually|i mean|make that|no,|wait,)\b',text,re.I):self.counts['corrections']+=1

    def snapshot(self):
        with self.lock:
            return {'counts':dict(self.counts),'latency_ms':{key:{'samples':len(values),'mean':round(sum(values)/len(values),1),'max':round(max(values),1)} for key,values in self.timings.items()},
                    'unmeasured':['false_activation_rate','missed_activation_rate'],
                    'note':'Activation error rates need labeled trials; counters are not accuracy percentages.'}


@dataclass
class ResponsePlan:
    should_speak:bool=True
    response_mode:str='CONCISE'
    requires_confirmation:bool=False
    can_interrupt:bool=True
    preferred_output:str='both'
    max_spoken_sentences:int=3
    rate_delta:int=0
    privacy:str='normal'


def response_plan(mode='balanced',request='',public=False):
    value=request.lower().strip()
    if mode in ('silent','meeting') or re.fullmatch(r"(?:go )?quiet|don't speak|do not speak|text only",value):
        return ResponsePlan(False,'ULTRA_SHORT',preferred_output='text',max_spoken_sentences=0)
    if mode=='public' or public:return ResponsePlan(True,'CONCISE',max_spoken_sentences=1,privacy='public')
    if mode=='driving':return ResponsePlan(True,'DRIVING',max_spoken_sentences=2,rate_delta=-1)
    if mode=='tutor' or re.search(r'\b(explain more|give me the details|in detail|step by step)\b',value):
        return ResponsePlan(True,'TUTOR' if mode=='tutor' else 'DETAILED',max_spoken_sentences=10,rate_delta=-1)
    if mode=='fast' or value in ('shorter','just tell me the answer','just the answer','keep it short'):
        return ResponsePlan(True,'ULTRA_SHORT',max_spoken_sentences=1)
    if mode=='bedtime':return ResponsePlan(True,'CONCISE',max_spoken_sentences=2,rate_delta=-1)
    return ResponsePlan()


class SpeechBudget:
    def __init__(self,plan):self.plan=plan;self.sentences=0;self.words=0;self.lock=threading.Lock()

    def take(self,text):
        from desktop.speech_output import spoken_text
        with self.lock:
            if not self.plan.should_speak:return ''
            if self.plan.privacy=='public':
                if self.sentences:return ''
                self.sentences=1
                return 'The details are on screen.'
            # Modes shape the model's answer, never silently truncate the
            # text already shown. Privacy/text-only modes remain explicit.
            return spoken_text(text)


@dataclass
class SessionContext:
    active_goal:str=''
    recent_entities:list=field(default_factory=list)
    options:list=field(default_factory=list)
    pending_question:str=''
    decisions:list=field(default_factory=list)
    interrupted_response:str=''
    tool_context:dict=field(default_factory=dict)
    mode:str='balanced'

    def compact(self):
        return {'active_goal':self.active_goal[:240], 'recent_entities':self.recent_entities[-8:],
                'recent_options':self.options[:8], 'pending_question':self.pending_question[:240],
                'recent_decisions':self.decisions[-5:], 'interrupted_response':self.interrupted_response[-1200:],
                'tool_context':self.tool_context,'conversation_mode':self.mode}


class DialogueState:
    def __init__(self):self.sessions={};self.lock=threading.RLock()

    def session(self,identity):
        with self.lock:
            if identity not in self.sessions:
                if len(self.sessions)>=32:self.sessions.pop(next(iter(self.sessions)))
                self.sessions[identity]=SessionContext()
            return self.sessions[identity]

    def resolve(self,identity,text):
        state=self.session(identity);value=text.strip();folded=value.lower().rstrip('.!?')
        # Resolve only explicit ordered choices. Pronouns without an observed
        # unambiguous referent remain for the existing LLM/tool context.
        match=re.fullmatch(r'(?:the )?(first|second|third|fourth|fifth)(?: (?:one|option|place|file))?',folded)
        if match:
            index=['first','second','third','fourth','fifth'].index(match[1])
            if index<len(state.options):return value+' (the selected option is '+state.options[index]+')'
        if folded in ('same as before','do the same thing','do that again') and state.active_goal:
            return 'Repeat this earlier request: '+state.active_goal
        if folded in ('shorter','only the important ones','skip that part','continue','resume','explain more','give me the details'):
            if state.interrupted_response:return value+'\nPrevious interrupted answer (data): '+state.interrupted_response[-1200:]
        if re.fullmatch(r'(?:actually |i meant |make that )(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|\d.+)',folded) and state.active_goal:
            return 'Correction to my earlier request ('+state.active_goal+'): '+value
        return value

    def finish(self,identity,request,reply,mode='balanced'):
        state=self.session(identity);state.mode=mode
        micro=bool(re.fullmatch(r'(yes|no|later|tomorrow|that one|there|him|shorter|the \w+ one)[.!?]*',request.strip(),re.I))
        if not micro and not request.lower().startswith(('actually ','i meant ')):state.active_goal=request[:400]
        state.pending_question=reply[-240:] if reply.rstrip().endswith('?') else ''
        options=re.findall(r'^\s*\d+[.)]\s+(.+)$',reply,re.M)
        if options:state.options=[value[:240] for value in options[:8]]
        if reply and not state.pending_question:state.decisions=(state.decisions+[reply[:240]])[-5:]
        # Track explicit quoted names/paths as data, never execute their contents.
        entities=re.findall(r'"([^"\n]{1,120})"|\b([\w.-]+\.(?:pdf|docx|txt|xlsx))\b',request)
        for quoted,path in entities:
            value=quoted or path
            if value not in state.recent_entities:state.recent_entities.append(value)
        state.recent_entities=state.recent_entities[-8:]


class ActionLedger:
    """Process-local per-operation idempotency; failed actions never auto-retry."""
    def __init__(self):self.records={};self.lock=threading.RLock()

    def propose(self,key,action):
        with self.lock:
            if key not in self.records:
                if len(self.records)>=256:self.records.pop(next(iter(self.records)))
                self.records[key]={'state':'PROPOSED','action':action,'result':None}
            return self.records[key]

    def run(self,key,action,execute):
        with self.lock:
            record=self.propose(key,action)
            if record['state']=='SUCCEEDED':return record['result']
            if record['state'] in ('EXECUTING','FAILED','CANCELLED'):raise ValueError('This action is already running or finished; it will not be replayed.')
            record['state']='EXECUTING'
        try:result=execute()
        except Exception:
            with self.lock:record['state']='FAILED'
            raise
        with self.lock:record.update(state='SUCCEEDED',result=result)
        return result

    def snapshot(self):
        with self.lock:return [{'id':key,'action':v['action'],'state':v['state']} for key,v in list(self.records.items())[-16:]]

    def cancel(self,key):
        with self.lock:
            if key in self.records and self.records[key]['state'] in ('PROPOSED','CONFIRMED'):
                self.records[key]['state']='CANCELLED'

    def confirm(self,key):
        with self.lock:
            if self.records[key]['state']=='PROPOSED':self.records[key]['state']='CONFIRMED'


class PauseModel:
    def __init__(self,profiles=None):self.profiles=dict(profiles or {})

    def observe(self,profile,pauses):
        if not profile or not pauses:return
        valid=[min(1800,max(150,float(p))) for p in pauses if 150<=p<=2500]
        if not valid:return
        previous=self.profiles.get(profile,{'count':0,'mid_pause_ms':650.})
        previous={'count':min(1000,previous['count']+1),'mid_pause_ms':round(.9*previous['mid_pause_ms']+.1*sum(valid)/len(valid),1)}
        self.profiles[profile]=previous
        if len(self.profiles)>8:self.profiles.pop(next(iter(self.profiles)))

    def pause(self,profile,base):
        if base!=650 or profile not in self.profiles:return base
        return int(min(1400,max(650,self.profiles[profile]['mid_pause_ms']+200)))
