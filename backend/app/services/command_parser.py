from dataclasses import dataclass
from typing import Optional
from rapidfuzz import fuzz

from app.services.voice_preprocessor import preprocess


@dataclass
class ParsedCommand:
    action: Optional[str] = None
    target: Optional[str] = None
    value: Optional[str] = None
    raw: str = ""


ACTIONS = {

    "open": [
        "open",
    ],

    "close": [
        "close",
    ],

    "focus": [
        "focus",
    ],

    "minimize": [
        "minimize",
    ],

    "maximize": [
        "maximize",
        "fullscreen",
    ],

    "restore": [
        "restore",
    ],

    "shutdown": [
        "shutdown",
    ],

    "restart": [
        "restart",
    ],

    "sleep": [
        "sleep",
    ],

    "hibernate": [
        "hibernate",
    ],

    "lock": [
        "lock",
    ],

    "mute": [
        "mute",
    ],

    "unmute": [
        "unmute",
    ],

    "volume_up": [
        "volume up",
    ],

    "volume_down": [
        "volume down",
    ],
}


APP_TARGETS = {

    "chrome": ["chrome", "google chrome"],
    "edge": ["edge", "microsoft edge"],
    "firefox": ["firefox"],
    "brave": ["brave"],
    "opera": ["opera"],

    "notepad": ["notepad"],
    "calculator": ["calculator", "calc"],
    "paint": ["paint", "mspaint"],

    "vscode": ["vscode", "vs code", "visual studio code"],
    "cursor": ["cursor"],

    "discord": ["discord"],
    "spotify": ["spotify"],
    "steam": ["steam"],
    "telegram": ["telegram"],
    "whatsapp": ["whatsapp", "whats app"],

    "word": ["word", "microsoft word"],
    "excel": ["excel"],
    "powerpoint": ["powerpoint", "power point"],

}
WINDOWS_TARGETS = {

    "explorer": ["explorer", "file explorer"],

    "settings": ["settings"],

    "cmd": ["cmd", "command prompt"],

    "powershell": [
        "powershell",
        "power shell",
        "windows powershell",
    ],

    "task manager": ["task manager"],

    "control panel": ["control panel"],

    "registry editor": [
        "registry editor",
        "regedit",
    ],

    "services": ["services"],

    "event viewer": ["event viewer"],

}

WEBSITE_TARGETS = {

    "google": ["google"],

    "gmail": [
        "gmail",
        "mail",
        "email",
    ],

    "youtube": ["youtube"],

    "github": ["github"],

    "chatgpt": [
        "chatgpt",
        "chat gpt",
    ],

    "reddit": ["reddit"],

    "linkedin": ["linkedin"],

    "facebook": ["facebook"],

    "instagram": ["instagram"],

    "twitter": [
        "twitter",
        "x",
    ],

}
FOLDER_TARGETS = {

    "desktop": ["desktop"],

    "documents": [
        "documents",
        "document",
    ],

    "downloads": [
        "downloads",
        "download folder",
    ],

    "pictures": [
        "pictures",
        "photos",
    ],

    "videos": ["videos"],

    "music": [
        "music",
        "music folder",
    ],

}
WINDOW_TARGETS = {

    "window": ["window"],

    "current window": [
        "current window",
    ],

    "active window": [
        "active window",
    ],

}
TARGETS = {
    **APP_TARGETS,
    **WINDOWS_TARGETS,
    **WEBSITE_TARGETS,
    **FOLDER_TARGETS,
    **WINDOW_TARGETS,
}

NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "twenty": "20",
    "thirty": "30",
    "forty": "40",
    "fifty": "50",
    "hundred": "100",
}


def fuzzy_contains(text: str, phrase: str, threshold: int = 90):

    if phrase in text:
        return True

    return fuzz.partial_ratio(text, phrase) >= threshold


def parse_command(text: str) -> ParsedCommand:

    text = preprocess(text)

    cmd = ParsedCommand(raw=text)

    # ---------- Action ----------

    for action, aliases in ACTIONS.items():

        for alias in aliases:

            if fuzzy_contains(text, alias):

                cmd.action = action
                break

        if cmd.action:
            break

    # ---------- Target ----------

    for target, aliases in TARGETS.items():

        for alias in aliases:

            if fuzzy_contains(text, alias):

                cmd.target = target
                break

        if cmd.target:
            break

    # ---------- Numbers ----------

    for word in text.split():

        if word.isdigit():

            cmd.value = word
            break

        if word in NUMBER_WORDS:

            cmd.value = NUMBER_WORDS[word]
            break

    print("=" * 60)
    print("RAW      :", text)
    print("ACTION   :", cmd.action)
    print("TARGET   :", cmd.target)
    print("VALUE    :", cmd.value)
    print("=" * 60)

    return cmd