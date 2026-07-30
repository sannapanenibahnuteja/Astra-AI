import re

FILLER_WORDS = {
    "please",
    "could",
    "would",
    "can",
    "will",
    "you",
    "jarvis",
    "astra",
    "assistant",
    "for",
    "me",
    "just",
    "kindly",
    "hey",
    "hi",
    "hello",
    "um",
    "uh",
    "like",
    "actually",
    "simply",
    "maybe",
    "now",
    "right",
}

REPLACEMENTS = {

    # ---------- OPEN ----------
    "launch": "open",
    "start": "open",
    "run": "open",
    "fire up": "open",
    "boot": "open",
    "bring up": "open",
    "load": "open",

    # ---------- CLOSE ----------
    "quit": "close",
    "exit": "close",
    "terminate": "close",
    "kill": "close",

    # ---------- FOCUS ----------
    "switch to": "focus",
    "switch over to": "focus",
    "switch back to": "focus",
    "go to": "focus",
    "bring to front": "focus",

    # ---------- VOLUME ----------
    "turn up": "volume up",
    "increase volume": "volume up",
    "increase the volume": "volume up",
    "raise the volume": "volume up",

    "turn down": "volume down",
    "decrease volume": "volume down",
    "lower volume": "volume down",
    "lower the volume": "volume down",

    # ---------- SYSTEM ----------
    "power off": "shutdown",
    "turn off": "shutdown",
    "switch off": "shutdown",

    "reboot": "restart",

    # ---------- BROWSER ----------
    "reload": "refresh",
    "refresh page": "refresh",
}


def preprocess(text: str) -> str:

    text = text.lower()

    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # Replace only complete phrases/words
    for old, new in sorted(REPLACEMENTS.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"\b" + re.escape(old) + r"\b"
        text = re.sub(pattern, new, text)

    # Remove filler words
    words = [w for w in text.split() if w not in FILLER_WORDS]

    text = " ".join(words)

    # Collapse spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text