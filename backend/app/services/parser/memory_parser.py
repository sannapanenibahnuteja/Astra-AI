FILLER_WORDS = {
    "i",
    "my",
    "please",
    "can",
    "could",
    "would",
    "you",
    "me",
    "that",
    "this",
}

COMMAND_WORDS = {
    "remember",
    "recall",
}


def parse_memory(text: str):

    text = text.strip().lower()

    words = text.split()

    # Remove conversational prefixes
    while words and words[0] in FILLER_WORDS:
        words.pop(0)

    # Remove command words
    while words and words[0] in COMMAND_WORDS:
        words.pop(0)

    # Remove filler again (e.g. "remember my bike")
    while words and words[0] in FILLER_WORDS:
        words.pop(0)

    if not words:
        return None, None

    key = words[0]

    value = " ".join(words[1:]).strip()

    if value.startswith("is "):
        value = value[3:]

    return key, value