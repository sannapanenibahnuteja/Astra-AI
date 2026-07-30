from app.services.context_manager import context

APP_ALIASES = {
    "browser": "chrome",
    "google chrome": "chrome",
    "music": "spotify",
    "player": "spotify",
    "code": "vscode",
    "visual studio": "vscode",
    "editor": "vscode",
    "files": "explorer",
    "file manager": "explorer",
}

FOLDER_ALIASES = {
    "downloads": "downloads",
    "download": "downloads",
    "documents": "documents",
    "document": "documents",
    "desktop": "desktop",
    "pictures": "pictures",
    "photos": "pictures",
    "images": "pictures",
    "music": "music",
    "videos": "videos",
}


def resolve(parsed):

    # Already resolved by parser
    if parsed.target:

        if parsed.target in APP_ALIASES:
            parsed.target = APP_ALIASES[parsed.target]

        elif parsed.target in FOLDER_ALIASES:
            parsed.target = FOLDER_ALIASES[parsed.target]

        return parsed

    # -------- Context --------

    if parsed.action in ("close", "focus"):

        if context.last_app:
            parsed.target = context.last_app

    elif parsed.action == "open":

        if context.last_folder:
            parsed.target = context.last_folder

    elif parsed.action in ("volume_up", "volume_down"):

        parsed.target = "system"

    return parsed