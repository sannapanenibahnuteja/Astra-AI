from app.services.intents import detect_intent


def get_intent(message: str):

    """
    Returns the user's intent.

    Example:

    'restart my pc'
        -> restart

    'reboot windows'
        -> restart

    'kill the computer'
        -> shutdown
    """

    return detect_intent(message)