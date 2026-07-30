from dataclasses import dataclass


@dataclass
class Intent:
    name: str
    phrases: list[str]


INTENTS = [

    Intent(
        "shutdown",
        [
            "shutdown",
            "shut down",
            "turn off computer",
            "turn off pc",
            "power off",
            "switch off",
            "kill the computer",
            "shut everything down"
        ]
    ),

    Intent(
        "restart",
        [
            "restart",
            "reboot",
            "restart windows",
            "reboot my machine"
        ]
    ),

    Intent(
        "sleep",
        [
            "sleep",
            "go to sleep",
            "put the pc to sleep",
            "put computer to sleep"
        ]
    ),

    Intent(
        "hibernate",
        [
            "hibernate",
            "hibernate computer",
            "save power mode"
        ]
    ),

    Intent(
        "lock",
        [
            "lock",
            "lock pc",
            "lock computer",
            "lock screen",
            "secure my pc"
        ]
    ),

    Intent(
        "logout",
        [
            "logout",
            "log out",
            "sign out"
        ]
    ),

    Intent(
        "volume_up",
        [
            "increase volume",
            "raise volume",
            "turn it up",
            "louder"
        ]
    ),

    Intent(
        "volume_down",
        [
            "decrease volume",
            "lower volume",
            "turn it down",
            "quieter"
        ]
    ),

    Intent(
        "mute",
        [
            "mute",
            "silence",
            "mute audio"
        ]
    ),

    Intent(
        "unmute",
        [
            "unmute",
            "turn sound back on",
            "sound on"
        ]
    ),

    Intent(
        "close_window",
        [
            "close",
            "close it",
            "close this",
            "close window",
            "close application",
            "exit",
            "quit"
        ]
    ),

    Intent(
        "minimize_window",
        [
            "minimize",
            "minimize it",
            "hide window"
        ]
    ),

    Intent(
        "maximize_window",
        [
            "maximize",
            "maximize it",
            "fullscreen",
            "full screen"
        ]
    ),

    Intent(
        "restore_window",
        [
            "restore",
            "restore it",
            "restore window"
        ]
    ),

]


def detect_intent(text: str):

    text = text.lower().strip()

    best_match = None
    longest = 0

    for intent in INTENTS:

        for phrase in intent.phrases:

            if phrase in text and len(phrase) > longest:
                longest = len(phrase)
                best_match = intent.name

    return best_match