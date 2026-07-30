from rapidfuzz import fuzz


def match_alias(text: str, aliases_dict: dict, threshold: int = 90):
    """
    Returns the best matching key from an alias dictionary.

    Matching priority:
    1. Exact alias match
    2. Alias contained in text
    3. Highest fuzzy score
    """

    text = text.lower().strip()

    # ---------------------------------
    # 1. Exact match
    # ---------------------------------

    for key, aliases in aliases_dict.items():
        for alias in aliases:

            alias = alias.lower().strip()

            if text == alias:
                return key

    # ---------------------------------
    # 2. Alias contained in sentence
    # ---------------------------------

    for key, aliases in aliases_dict.items():
        for alias in aliases:

            alias = alias.lower().strip()

            if alias in text:
                return key

    # ---------------------------------
    # 3. Best fuzzy match
    # ---------------------------------

    best_key = None
    best_score = 0

    for key, aliases in aliases_dict.items():

        for alias in aliases:

            score = fuzz.ratio(alias.lower(), text)

            if score > best_score:
                best_score = score
                best_key = key

    if best_score >= threshold:
        return best_key

    return None