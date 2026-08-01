import re

# Common aliases for popular applications
COMMON_ALIASES = {
    # Browsers
    "chrome": [
        "chrome", "google chrome", "browser", "internet", "web browser"
    ],
    "edge": [
        "edge", "microsoft edge", "browser", "internet", "web browser"
    ],
    "firefox": [
        "firefox", "mozilla", "mozilla firefox", "browser"
    ],
    "brave": [
        "brave", "brave browser", "browser"
    ],
    "opera": [
        "opera", "opera browser", "browser"
    ],

    # Communication
    "whatsapp": [
        "whatsapp", "whats app", "chat", "messaging", "message app"
    ],
    "telegram": [
        "telegram", "tg", "messenger"
    ],
    "discord": [
        "discord", "voice chat", "gaming chat"
    ],
    "slack": [
        "slack", "work chat", "team chat"
    ],
    "teams": [
        "teams", "microsoft teams", "meeting"
    ],
    "zoom": [
        "zoom", "meeting", "video call"
    ],

    # Music / Media
    "spotify": [
        "spotify", "music", "music player", "songs"
    ],
    "vlc": [
        "vlc", "video player", "media player"
    ],
    "windows media player": [
        "media player", "windows media player"
    ],

    # Development
    "visual studio code": [
        "visual studio code",
        "vs code",
        "vscode",
        "code",
        "editor"
    ],
    "visual studio": [
        "visual studio", "vs", "ide"
    ],
    "cursor": [
        "cursor", "cursor ai"
    ],
    "pycharm": [
        "pycharm", "python ide"
    ],
    "intellij": [
        "intellij", "idea", "java ide"
    ],
    "android studio": [
        "android studio", "android ide"
    ],
    "eclipse": [
        "eclipse", "java editor"
    ],
    "netbeans": [
        "netbeans"
    ],
    "jupyter": [
        "jupyter", "notebook"
    ],

    # AI
    "chatgpt": [
        "chatgpt", "gpt", "openai"
    ],
    "claude": [
        "claude", "anthropic"
    ],
    
    "copilot": [
        "copilot", "github copilot"
    ],

    # Gaming
    "steam": [
        "steam", "games", "game launcher"
    ],
    "epic games": [
        "epic", "epic games", "epic launcher"
    ],
    "riot client": [
        "riot", "riot games"
    ],
    "minecraft": [
        "minecraft", "mc"
    ],
    "ea": [
        "ea app", "ea"
    ],
    "battle.net": [
        "battle net", "battlenet", "blizzard"
    ],

    # Adobe
    "photoshop": [
        "photoshop", "ps", "photo editor"
    ],
    "illustrator": [
        "illustrator", "ai", "vector editor"
    ],
    "premiere": [
        "premiere", "premiere pro", "video editor"
    ],
    "after effects": [
        "after effects", "ae"
    ],
    "acrobat": [
        "acrobat", "pdf"
    ],

    # Office
    "word": [
        "word", "microsoft word", "document"
    ],
    "excel": [
        "excel", "spreadsheet"
    ],
    "powerpoint": [
        "powerpoint", "ppt", "presentation"
    ],
    "outlook": [
        "outlook", "mail", "email"
    ],
    "onenote": [
        "onenote", "notes"
    ],

    # Windows
    "notepad": [
        "notepad", "text editor"
    ],
    "notepad++": [
        "notepad++", "notepad plus plus"
    ],
    "calculator": [
        "calculator", "calc"
    ],
    "paint": [
        "paint", "mspaint", "drawing"
    ],
    "terminal": [
        "terminal", "cmd", "command prompt", "powershell"
    ],
    "powershell": [
        "powershell"
    ],
    "command prompt": [
        "cmd", "command prompt"
    ],
    "file explorer": [
        "file explorer", "explorer", "files", "file manager"
    ],
    "settings": [
        "settings", "windows settings"
    ],
    "control panel": [
        "control panel"
    ],
    "task manager": [
        "task manager", "process manager"
    ],
    "registry editor": [
        "registry", "regedit"
    ],
    "device manager": [
        "device manager"
    ],

    # Utilities
    "obs": [
        "obs", "obs studio", "streaming", "screen recorder"
    ],
    "7-zip": [
        "7zip", "7 zip", "archive"
    ],
    "winrar": [
        "winrar", "rar", "archive"
    ],
    "paint.net": [
        "paint.net", "paint net"
    ],
}


def generate_aliases(app_name: str):
    """
    Generate aliases for an application.
    """

    name = app_name.lower().strip()

    aliases = {name}

    # Split into words
    words = re.findall(r"[a-z0-9+.#-]+", name)

    # Add cleaned name
    aliases.add(" ".join(words))

    # Remove common company words
    ignored = {
        "microsoft",
        "google",
        "adobe",
        "corporation",
        "desktop",
        "launcher",
        "application",
        "inc",
        "ltd",
    }

    filtered = [w for w in words if w not in ignored]

    if filtered:
        aliases.add(" ".join(filtered))

    # Individual words
    for word in filtered:
        if len(word) > 2:
            aliases.add(word)

    # Add predefined aliases
    for app, extra_aliases in COMMON_ALIASES.items():
        if app in name:
            aliases.update(extra_aliases)

    return sorted(aliases)