import json
import os
import subprocess
from pathlib import Path

import pythoncom
from win32com.client import Dispatch

from app.services.app_registry import registry


START_MENU_LOCATIONS = [
    Path(os.environ["PROGRAMDATA"])
    / "Microsoft"
    / "Windows"
    / "Start Menu"
    / "Programs",

    Path(os.environ["APPDATA"])
    / "Microsoft"
    / "Windows"
    / "Start Menu"
    / "Programs",
]


def resolve_shortcut(shortcut_path):
    """
    Resolve a Windows .lnk shortcut to its target executable.
    """

    try:
        pythoncom.CoInitialize()

        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))

        target = shortcut.Targetpath

        if target and os.path.exists(target):
            return target

        return None

    except Exception as e:
        print(f"Failed to resolve {shortcut_path}: {e}")
        return None


def scan_start_menu():
    """
    Scan the Windows Start Menu for installed applications.
    """

    discovered = 0

    for start_menu in START_MENU_LOCATIONS:

        if not start_menu.exists():
            continue

        for shortcut in start_menu.rglob("*.lnk"):

            name = shortcut.stem.lower()

            if registry.exists(name):
                continue

            target = resolve_shortcut(shortcut)

            if not target:
                continue

            registry.register(
                name,
                {
                    "name": shortcut.stem,
                    "type": "exe",
                    "path": target,
                },
            )

            discovered += 1

    print(f"✓ Found {discovered} Start Menu applications.")


def scan_store_apps():
    """
    Scan Microsoft Store (AppX/MSIX) applications.
    """

    try:

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-StartApps | ConvertTo-Json -Depth 2"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if result.returncode != 0:
            print("Failed to scan Microsoft Store apps.")
            return

        if not result.stdout.strip():
            return

        apps = json.loads(result.stdout)

        if isinstance(apps, dict):
            apps = [apps]

        discovered = 0

        for app in apps:

            name = app.get("Name", "").strip()
            appid = app.get("AppID", "").strip()

            if not name or not appid:
                continue

            key = name.lower()

            if registry.exists(key):
                continue

            registry.register(
                key,
                {
                    "name": name,
                    "type": "store",
                    "appid": appid,
                },
            )

            discovered += 1

        print(f"✓ Found {discovered} Microsoft Store applications.")

    except Exception as e:
        print(f"Store app scan failed: {e}")


def scan_apps():
    """
    Scan every supported application source.
    """

    scan_start_menu()
    scan_store_apps()