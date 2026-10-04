"""Payload-preserving conversational aliases for the low-latency command path."""
import re
from difflib import SequenceMatcher

PHRASES = {
    'volume up': ('make it louder', 'make the sound louder', 'turn the sound up', 'increase the audio', 'a little louder'),
    'volume down': ('make it quieter', 'make the sound quieter', 'turn the sound down', 'lower the audio', 'a little quieter'),
    'brightness up': ('make the screen brighter', 'brighten the screen', 'a little brighter'),
    'brightness down': ('make the screen dimmer', 'dim the screen', 'a little dimmer'),
    'list windows': ('show my apps', 'show running apps', 'what apps are open', 'show all open applications'),
}


def dictation(text):
    """Recognize explicit Notepad dictation before normalizing its literal payload."""
    text = re.sub(r"^(?:(?:hey|okay|ok)\s+)?bob\b[, ]*", '', text.strip(), flags=re.I)
    text = re.sub(r"^(?:(?:could|can|would|will) you(?: please)?|please|i want you to)\s+", '', text, flags=re.I)
    patterns = [r'(?:type|write|put)\s+(.+?)\s+(?:into|in)\s+(?:the\s+)?(?:note\s*pad)(?:\s+window)?[.!?]*$',
                r'(?:in\s+note\s*pad[, ]+|(?:type|write)\s+(?:in|into)\s+note\s*pad[:, ]+)(.+)$']
    for pattern in patterns:
        match = re.fullmatch(pattern, text, re.I | re.S)
        if match:
            payload = match[1]
            if len(payload)>1 and payload[0]==payload[-1] and payload[0] in ('"',"'"):
                payload=payload[1:-1]
            return {'action':'type_text','target':payload,'window':'Notepad'}
    return None


def phrase_intent(text):
    """Fuzz only bounded, non-destructive phrases, with separation by intent."""
    folded = text.casefold()
    scores = []
    for command, phrases in PHRASES.items():
        if folded in phrases: return command, False
        scores.append((max(SequenceMatcher(None, folded, p).ratio() for p in phrases), command))
    scores.sort(reverse=True)
    if scores[0][0] >= .87 and scores[0][0] - scores[1][0] >= .10:
        return scores[0][1], True
    return None, False


def normalize(text):
    text = re.sub(r'\s+', ' ', text.strip()).rstrip('.!?')
    text = text.replace('’', "'")
    text = re.sub(r'^(swich|swtich|opne|opem|maximise|minimise)\b',
                  lambda m: {'swich':'switch','swtich':'switch','opne':'open','opem':'open','maximise':'maximize','minimise':'minimize'}[m[0].lower()],text,flags=re.I)
    prefixes = [r"(?:(?:hey|okay|ok)\s+)?bob\b[, ]*",
                r"(?:please|kindly|just)\s+",
                r"(?:could|can|would|will) you(?: please| kindly)?\s+",
                r"(?:i(?:'d| would) like you to|i want you to|i need you to|would you mind|can you help me)\s+"]
    for _ in range(5):
        before = text
        for prefix in prefixes:
            text = re.sub('^' + prefix, '', text, flags=re.I)
        if before == text: break
    text = re.sub(r'[, ]+please$', '', text, flags=re.I)
    # Only rewrite the command prefix, never the content of a dictation/query/path.
    aliases = [(r'(?:pull up|fire up|bring up|opening|launching) ', 'open '),
               (r'(?:jump to|bring me to|take me to|switch over to) ', 'switch to '),
               (r'(?:jot down|write a note saying) ', 'note '),
               (r'(?:look online for|search the internet for) ', 'search for '),
               (r'(?:bump up|crank up) ', 'increase '),
               (r'(?:dial down|tone down) ', 'lower ')]
    for pattern, replacement in aliases:
        if re.match(pattern, text, re.I):
            text = re.sub('^' + pattern, replacement, text, count=1, flags=re.I)
            break
    return text.strip()
