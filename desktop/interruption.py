"""Conservative, local interruption intent; never dispatches commands."""
import re


def reply_stop_control(text):
    value=re.sub(r"[^a-z0-9'\s]",' ',str(text).casefold())
    value=re.sub(r'\s+',' ',value).strip()
    value=re.sub(r'^(?:(?:hey|okay|ok) )?bob\s+','',value)
    value=re.sub(r'^(?:actually |please |can you |could you |would you )+','',value)
    return value in {'stop','stop talking','stop speaking','stop responding','stop that','wait','hold on',
                     'quiet','be quiet',"that's enough",'that is enough','let me speak','let me finish','listen to me'}


def intended_interruption(text, confidence=0., needs_review=True, require_trigger=False):
    if needs_review or confidence < .80:return False
    if require_trigger:
        from desktop.voice_triggers import explicit_interrupt_trigger,split_wake,session_stop
        if not explicit_interrupt_trigger(text):return False
        if session_stop(text):return True
        wake,payload=split_wake(text)
        if wake and not payload:return True
    value=re.sub(r"[^a-z0-9'\s]",' ',str(text).casefold())
    value=re.sub(r'\s+',' ',value).strip()
    if not value or len(value.split())>64:return False
    # Recognizer boilerplate and fillers are not conversational permission.
    if re.search(r'\b(thanks? for watching|subscribe|subtitles|inaudible|unintelligible)\b',value):return False
    addressed=bool(re.match(r'^(?:(?:hey|okay|ok) )?bob\b',value))
    if addressed:value=re.sub(r'^(?:(?:hey|okay|ok) )?bob\s*','',value)
    value=re.sub(r'^please\s+','',value)
    controls={'stop','stop talking','stop speaking','stop that','wait','hold on','quiet','be quiet',
              'shorter','make it shorter','make that shorter','skip that','skip that part',
              "that's enough",'that is enough','let me speak','let me finish','listen to me',
              'i have a question','just the answer','just give me the answer','never mind','cancel','cancel that','stop listening',
              'just give me the short version','give me the short version','keep it short','stop responding'}
    if value in controls:return True
    repair=bool(re.match(r'^(?:actually|wait|no i meant|no i mean|instead)\b',value))
    if repair:value=re.sub(r'^(?:actually|wait|no i meant|no i mean|instead)\s*','',value)
    value=re.sub(r'^(?:please |can you |could you |would you )+','',value)
    if value in controls:return True
    if repair and re.fullmatch(r'(?:next )?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today|\d{1,2}(?: (?:am|pm|percent))?)',value):return True
    # An address/correction plus a meaningful request form is required. Random
    # narration or a name alone cannot stop playback. Tool validation is later.
    if not (addressed or repair):return False
    return bool(re.match(r'^(?:open|close|play|pause|resume|show|find|search|set|change|turn|move|type|write|read|explain|tell|remind|remember|cancel|stop|switch|repeat|summarize|summarise|give)\s+\S+',value)
                or re.match(r'^(?:what|why|how|when|where|who)\s+\S+',value))
