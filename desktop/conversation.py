"""Explicit conversation preferences and conservative pending-intent repairs."""
import re
from datetime import datetime, timedelta

MODES = {
    'balanced': 'Keep a natural conversational pace. Be brief unless detail helps.',
    'fast': 'Give the useful answer first in one or two short sentences. Avoid tangents.',
    'tutor': 'Explain step by step with a concrete example. Ask one useful learning question.',
    'calm': 'Use calm, simple wording and small steps. Avoid overwhelming the user.',
}
REPLY_EDITS = {'shorter','keep it short','make that shorter','skip that part','just the answer','summarize that','summarise that'}


def preference(text):
    from desktop.intent import normalize
    text=normalize(text).lower()
    match=re.fullmatch(r'(?:switch to|use|enter|go into) (balanced|fast|tutor|calm)(?: mode)?',text)
    if match: return {'conversation_mode':match[1]}
    if text in ('give me more time to think','let me finish speaking','wait longer before answering'):
        return {'turn_pause_ms':1800}
    if text in ('respond faster','take turns faster'): return {'turn_pause_ms':450}
    return None


def repair_pending(text, steps, reminders):
    """Only edit one unexecuted numeric or reminder-time slot, then reapprove."""
    match=re.fullmatch(r'(?:no[, ]+)?(?:actually[, ]+|i meant |make (?:that|it) |change (?:that|it) to )(.+?)[.!?]*',text.strip(),re.I)
    if not match: return None
    replacement=match[1].strip()
    if re.match(r'^(?:open|close|send|delete|move|set|create|call|remind|cancel)\b',replacement,re.I): return None
    if len(steps)!=1:
        return {'question':'Which pending step should I change? Say the corrected request, or “cancel”.'}
    step=dict(steps[0]); action=step['action']
    if action in ('volume','brightness'):
        from desktop.devices import number_words
        raw=number_words(re.sub(r'\s*(?:percent|%)$','',replacement.lower()))
        if raw.isdigit() and 0<=int(raw)<=100:
            step.update(target=str(int(raw)),confirm=True)
            step.pop('description',None)
            return {'steps':[step]}
        return {'question':'What percentage should I use, from zero to one hundred?'}
    if action=='reminder_add':
        due=datetime.fromtimestamp(float(step['value']))
        day=re.fullmatch(r'(?:on )?(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow)(?: instead)?',replacement.lower())
        if day:
            now=datetime.now()
            date=(now+timedelta(days=1)).date() if day[1]=='tomorrow' else (now+timedelta(days=(['monday','tuesday','wednesday','thursday','friday','saturday','sunday'].index(day[1])-now.weekday())%7)).date()
            corrected=datetime.combine(date,due.time())
            if corrected<=now: corrected+=timedelta(days=7)
            step['value']=str(corrected.timestamp())
        else:
            clock=re.fullmatch(r'(?:at )?(\d{1,2})(?::(\d{2}))?\s*(am|pm)',replacement.lower())
            if not clock or not 1<=int(clock[1])<=12 or int(clock[2] or 0)>59:
                return {'question':'Which day or time should I use? For a time, include AM or PM.'}
            corrected=due.replace(hour=int(clock[1])%12+(12 if clock[3]=='pm' else 0),minute=int(clock[2] or 0))
            step['value']=str(corrected.timestamp())
        step=reminders.validate(step)
        step['confirm']=True
        return {'steps':[step]}
    return {'question':'Say the corrected request in full, or “cancel”. I haven’t executed the pending action.'}


def can_stream(text):
    """Only stream explanatory replies; action results are spoken after execution."""
    from desktop.intent import normalize
    text=normalize(text).lower()
    return bool(re.match(r'^(?:explain|tell me about|teach me|why\b|what is\b|how does\b)',text)) and not re.search(r'\b(?:open|close|send|delete|move|change|set|buy|book|create|schedule|call)\b',text)


def repair_utterance(text):
    """An explicit replacement action wins; never alter quoted text or dictation."""
    if any(mark in text for mark in ('"',"'",'`')): return text
    if not re.match(r'^(?:open|launch|close|set (?:the )?(?:volume|brightness))\b',text,re.I): return text
    match=re.search(r'[, ]+(?:no[, ]+(?:actually[, ]+)?|wait[, ]+(?:actually|instead)[, ]+)(.+)$',text,re.I)
    if match and re.match(r'^(?:open|launch|close|set (?:the )?(?:volume|brightness))\b',match[1],re.I): return match[1]
    return text


def success_claim(text):
    verbs=r'opened|closed|launched|sent|deleted|moved|changed|set|scheduled|connected|disconnected|typed|created|turned'
    return bool(re.search(r"\bI(?:'ve| have)? (?:successfully )?(?:"+verbs+r')\b',text,re.I) or
                re.match(r'^(?:Done[,:.! ]+|Successfully )?(?:'+verbs+r')\b',text,re.I) or
                re.search(r'\b(?:all|the) (?:tabs|windows|apps) (?:are|were|have been) (?:successfully )?closed\b',text,re.I))
