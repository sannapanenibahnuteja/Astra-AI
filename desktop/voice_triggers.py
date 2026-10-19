"""Explicit trigger phrases; payload after the prefix is preserved verbatim."""
import re

WAKE_PHRASES=('hey bob','okay bob','ok bob')


def split_wake(text):
    match=re.match(r'^\s*(?:hey|okay|ok)[\s,]+bob\b[\s,.:!?-]*',str(text),re.I)
    return (True,str(text)[match.end():].strip()) if match else (False,str(text))


def session_stop(text):
    return bool(re.fullmatch(r'\s*(?:stop listening|stop voice|go to sleep)[.!?]*\s*',str(text),re.I))


def explicit_interrupt_trigger(text):
    from desktop.interruption import reply_stop_control
    wake,payload=split_wake(text)
    if wake:return True
    if session_stop(text):return True
    # Keep this explicit, addressed reply control for compatibility. A bare
    # "stop", "actually" or "shorter" is not a trigger.
    return bool(re.match(r'^\s*bob\b',str(text),re.I) and reply_stop_control(text))
