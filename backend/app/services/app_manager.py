import os
import win32gui
import win32con
import subprocess
import psutil
import pygetwindow as gw

from rapidfuzz import fuzz
from app.services.app_registry import registry
from app.services.windows_apps import launch_builtin



print(win32gui.GetForegroundWindow())
PROCESS_NAMES = {
    "chrome": ["chrome.exe", "msedge.exe"],
    "edge": ["msedge.exe"],
    "firefox": ["firefox.exe"],
    "spotify": ["spotify.exe"],
    "discord": ["discord.exe"],
    "steam": ["steam.exe"],
    "notepad": ["notepad.exe"],
    "calculator": ["calculator.exe", "calculatorapp.exe", "calc.exe"],
    "vscode": ["code.exe"],
    "cursor": ["cursor.exe"],
    "telegram": ["telegram.exe"],
    "whatsapp": ["whatsapp.exe"],
    "obs": ["obs64.exe"],
}


WINDOW_ALIASES = {
    "chrome": ["edge", "microsoft edge"],
    "edge": ["edge", "microsoft edge"],
    "firefox": ["firefox"],
    "spotify": ["spotify"],
    "discord": ["discord"],
    "steam": ["steam"],
    "notepad": ["notepad"],
    "calculator": ["calculator"],
    "vscode": ["visual studio code", "vs code", "code"],
    "explorer": [
        "file explorer",
        "explorer",
        "downloads",
        "documents",
        "desktop",
    ],
    "cursor": ["cursor"],
    "telegram": ["telegram"],
    "whatsapp": ["whatsapp"],
    "obs": ["obs"],
}


def _find_process(process_names):

    process_names = [p.lower() for p in process_names]

    for proc in psutil.process_iter(["pid", "name"]):

        try:

            name = proc.info["name"]

            if not name:
                continue

            if name.lower() in process_names:
                return proc

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return None


def is_running(app_name):

    aliases = PROCESS_NAMES.get(app_name.lower())

    if not aliases:
        return False

    return _find_process(aliases) is not None


def close_app(app_name):

    aliases = PROCESS_NAMES.get(app_name.lower())

    if not aliases:
        return False

    aliases = [a.lower() for a in aliases]

    found = False

    for proc in psutil.process_iter(["pid", "name"]):

        try:

            name = proc.info["name"]

            if not name:
                continue

            if name.lower() not in aliases:
                continue

            found = True

            try:
                proc.terminate()
                proc.wait(timeout=3)

            except Exception:

                try:
                    proc.kill()
                except Exception:
                    pass

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return found


def get_running_apps():

    running = []

    for app, aliases in PROCESS_NAMES.items():

        if _find_process(aliases):
            running.append(app)

    return sorted(set(running))


def focus_window(app_name):

    app_name = app_name.lower()

    search_terms = WINDOW_ALIASES.get(app_name, [app_name])

    for window in gw.getAllWindows():

        try:

            if not window.title:
                continue

            title = window.title.lower()

            if any(term in title for term in search_terms):

                print(f"Matched window: {window.title}")

                if window.isMinimized:
                    print("Restoring...")
                    window.restore()

                try:
                    hwnd = window._hWnd
                    print(f"HWND: {hwnd}")

                    # Restore window
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    print("ShowWindow OK")

                    # Bring window to top
                    win32gui.BringWindowToTop(hwnd)

                    # Best effort: SetForegroundWindow may fail
                    try:
                        win32gui.SetForegroundWindow(hwnd)
                        print("SetForegroundWindow OK")
                    except Exception as e:
                        print(f"SetForegroundWindow warning: {repr(e)}")

                    print("Focused successfully")
                    return True

                except Exception as e:
                    print("Focus failed:", repr(e))
                    return False

        except Exception as e:
            print("Window iteration error:", repr(e))

    print("No matching window found.")
    return False


def close_active_window():

    try:

        win = gw.getActiveWindow()

        if not win:
            return False

        win.close()

        return True

    except Exception:
        return False


MATCH_THRESHOLD = 75


def find_app(query: str):
    query = query.lower().strip()

    apps = registry.all()

    # Exact name
    if query in apps:
        return apps[query]

    # Exact alias
    for app in apps.values():
        aliases = app.get("aliases", [])

        if query in aliases:
            return app

    # Fuzzy search
    best_score = 0
    best_match = None

    for app in apps.values():
        candidates = [app["name"].lower()]
        candidates.extend(app.get("aliases", []))

        for candidate in candidates:
            score = fuzz.ratio(query, candidate.lower())

            if score > best_score:
                best_score = score
                best_match = app

    if best_score >= MATCH_THRESHOLD:
        return best_match

    return None


def launch_app(app):
    print(f">>> LAUNCH_APP({app}) <<<")

    app = app.lower().strip()

    # Built-in Windows apps
    if launch_builtin(app):
        print(f"Launched built-in app: {app}")
        return True

    # Installed applications
    app_info = find_app(app)

    if not app_info:
        print("Application not found.")
        return False

    try:

        # -------------------------------
        # Microsoft Store (AppX/MSIX) Apps
        # -------------------------------
        if app_info.get("type") == "store":

            appid = app_info.get("appid")

            if not appid:
                print("Store app has no AppID.")
                return False

            subprocess.Popen(
                [
                    "explorer.exe",
                    f"shell:AppsFolder\\{appid}"
                ]
            )

            print(f"Launching Store app: {app_info['name']}")
            return True

        # -------------------------------
        # Traditional EXE Applications
        # -------------------------------
        path = app_info.get("path")

        if not path:
            print("Application has no executable path.")
            return False

        if not os.path.exists(path):
            print(f"Executable not found: {path}")
            return False

        subprocess.Popen(path)

        print(f"Launching {app_info['name']}")
        return True

    except Exception as e:
        print(f"Launch failed: {e}")
        return False


def get_active_window():

    try:

        win = gw.getActiveWindow()

        if win:
            return win.title

    except Exception:
        pass

    return None