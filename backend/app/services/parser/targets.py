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

    "event viewer": [
        "event viewer",
    ],

    "device manager": [
        "device manager",
    ],

    "disk management": [
        "disk management",
        "disk manager",
    ],

    "terminal": [
        "terminal",
        "windows terminal",
    ],


}
FOLDER_TARGETS = {

    "desktop": [
        "desktop",
    ],

    "documents": [
        "documents",
        "document",
        "my documents",
    ],

    "downloads": [
        "downloads",
        "download",
        "downloads folder",
        "download folder",
    ],

    "pictures": [
        "pictures",
        "picture",
        "photos",
        "photo",
        "images",
    ],

    "videos": [
        "videos",
        "video",
    ],

    "music": [
        "music",
        "songs",
        "music folder",
    ],

    "recycle bin": [
        "recycle bin",
        "trash",
        "bin",
        "recycling bin",
    ],
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
WINDOW_TARGETS = {

    "window": ["window"],

    "current window": [
        "current window",
    ],

    "active window": [
        "active window",
    ],

    "brightness": [
    "brightness",
    "screen brightness",
    "display brightness",
    "screen",
    "display",
],

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

TARGETS = {
    **APP_TARGETS,
    **WINDOWS_TARGETS,
    **WEBSITE_TARGETS,
    **FOLDER_TARGETS,
    **WINDOW_TARGETS,
}