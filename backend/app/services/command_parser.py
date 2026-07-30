from dataclasses import dataclass
from typing import Optional

from app.services.voice_preprocessor import preprocess

from app.services.parser.actions import ACTIONS
from app.services.parser.targets import TARGETS
from app.services.parser.constants import NUMBER_WORDS
from app.services.parser.matcher import match_alias


@dataclass
class ParsedCommand:
    action: Optional[str] = None
    target: Optional[str] = None
    value: Optional[str] = None
    query: Optional[str] = None
    raw: str = ""


def parse_command(text: str) -> ParsedCommand:

    import os

    print("\n================ PARSER DEBUG ================")
    print("FILE:", os.path.abspath(__file__))
    print("INPUT:", repr(text))

    text = preprocess(text)

    print("PREPROCESSED:", repr(text))

    action = match_alias(text, ACTIONS)
    target = match_alias(text, TARGETS)

    print("MATCHED ACTION:", action)
    print("MATCHED TARGET:", target)

    cmd = ParsedCommand(raw=text)
    cmd.action = action
    cmd.target = target

    # -------------------------------------------------
    # SEARCH
    # search youtube for music
    # -------------------------------------------------

    if cmd.action == "search":

        if cmd.target:

            query = text

            query = query.replace("search", "", 1)
            query = query.replace(cmd.target, "", 1)

            for word in (
                "for",
                "on",
                "about",
                "of",
            ):
                query = query.replace(word, "", 1)

            cmd.query = query.strip()

    # -------------------------------------------------
    # OPEN
    # open epic games
    # open visual studio code
    # -------------------------------------------------

    elif cmd.action == "open":

        if cmd.target is None:

            target = text

            target = target.replace("open", "", 1).strip()

            if target:
                cmd.target = target

    # -------------------------------------------------
    # CLOSE
    # close chrome
    # close epic games
    # -------------------------------------------------

    elif cmd.action == "close":

        if cmd.target is None:

            target = text

            target = target.replace("close", "", 1).strip()

            if target:
                cmd.target = target

    # -------------------------------------------------
    # NUMBER EXTRACTION
    # -------------------------------------------------

    words = text.split()

    for i, word in enumerate(words):

        if word.isdigit():

            cmd.value = word
            break

        if word in NUMBER_WORDS:

            cmd.value = str(NUMBER_WORDS[word])
            break

    # -------------------------------------------------
    # Brightness
    # -------------------------------------------------

    if (
        cmd.action == "set_brightness"
        and cmd.target is None
    ):
        cmd.target = "brightness"

    # -------------------------------------------------
    # Volume
    # -------------------------------------------------

    if (
        cmd.action in {
            "volume_up",
            "volume_down",
            "mute",
            "unmute",
        }
        and cmd.target is None
    ):
        cmd.target = "volume"

    # -------------------------------------------------
    # Window
    # -------------------------------------------------

    if (
        cmd.action in {
            "minimize",
            "maximize",
            "restore",
            "snap_left",
            "snap_right",
        }
        and cmd.target is None
    ):
        cmd.target = "window"

    print("FINAL CMD:", cmd)
    print("=============================================\n")

    return cmd