from app.services.astra_brain import brain


PRONOUNS = {

    "it",
    "them",
    "that",
    "those",
    "this",
    "these",

}


def resolve_context(message: str) -> str:

    """
    Replace pronouns like 'it' or 'them'
    with whatever Astra currently knows
    from the conversation.
    """

    text = message.lower()

    # -------------------------
    # UPDATES
    # -------------------------

    if brain.last_subject == "updates":

        if "them" in text:
            return text.replace("them", "updates")

        if "they" in text:
            return text.replace("they", "updates")

        if "it" in text:
            return text.replace("it", "update")

    # -------------------------
    # FILES
    # -------------------------

    if brain.last_file:

        if "it" in text:

            return text.replace(
                "it",
                brain.last_file
            )

    # -------------------------
    # APPS
    # -------------------------

    if brain.last_app:

        if "it" in text:

            return text.replace(
                "it",
                brain.last_app
            )

    return text


def update_context(message: str):

    text = message.lower()

    # -------------------------

    if "update" in text:

        brain.set_subject("updates")

    # -------------------------

    if "youtube" in text:

        brain.set_app("youtube")

    elif "google" in text:

        brain.set_app("google")

    elif "github" in text:

        brain.set_app("github")

    # -------------------------

    if ".pdf" in text:

        brain.set_file(text)