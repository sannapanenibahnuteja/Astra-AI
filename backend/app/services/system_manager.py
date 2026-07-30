import os
import ctypes
import subprocess
import screen_brightness_control as sbc

USER_HOME = os.path.expanduser("~")


def _open_folder(folder_name, display_name):
    path = os.path.join(USER_HOME, folder_name)
    return _run(f'explorer "{path}"', f"Opening {display_name}.")


def _run(command, success_message):

    print("=" * 60)
    print(f"[SYSTEM] Executing: {command}")

    try:

        process = subprocess.Popen(
            command,
            shell=True
        )

        print(f"[SYSTEM] Process ID: {process.pid}")
        print("[SYSTEM] Command launched successfully.")
        print("=" * 60)

        return {
            "success": True,
            "message": success_message,
        }

    except Exception as e:

        print("[SYSTEM ERROR]", e)
        print("=" * 60)

        return {
            "success": False,
            "message": str(e),
        }


# ---------------- POWER ----------------

def shutdown():
    return _run("shutdown /s /t 0", "Shutting down your PC.")


def restart():
    return _run("shutdown /r /t 0", "Restarting your PC.")


def hibernate():
    return _run("shutdown /h", "Hibernating your PC.")


def logout():
    return _run("shutdown /l", "Signing you out.")


def sleep():

    try:
        ctypes.windll.powrprof.SetSuspendState(False, True, False)
        return {
            "success": True,
            "message": "Putting your PC to sleep.",
        }
    
    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }


def lock():

    try:

        ctypes.windll.user32.LockWorkStation()

        return {
            "success": True,
            "message": "Locking your PC.",
        }
    
    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }
    # ---------------- BRIGHTNESS ----------------

def set_brightness(level):

    try:

        level = max(0, min(100, int(level)))

        sbc.set_brightness(level)

        return {
            "success": True,
            "message": f"Brightness set to {level}%.",
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }


def brightness_up(step=10):

    try:

        current = sbc.get_brightness()

        if isinstance(current, list):
            current = current[0]

        level = min(100, current + step)

        sbc.set_brightness(level)

        return {
            "success": True,
            "message": f"Brightness set to {level}%.",
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }


def brightness_down(step=10):

    try:

        current = sbc.get_brightness()

        if isinstance(current, list):
            current = current[0]

        level = max(0, current - step)

        sbc.set_brightness(level)

        return {
            "success": True,
            "message": f"Brightness set to {level}%.",
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }


# ---------------- WINDOWS ----------------

def open_task_manager():
    return _run("start taskmgr", "Opening Task Manager.")


def open_control_panel():
    return _run("control", "Opening Control Panel.")


def open_settings():
    return _run("start ms-settings:", "Opening Settings.")


def open_file_explorer():
    return _run("start explorer", "Opening File Explorer.")


# ---------------- FOLDERS ----------------

def open_downloads():
    return _run("explorer shell:Downloads", "Opening Downloads.")

def open_documents():
    return _run("explorer shell:Personal", "Opening Documents.")

def open_desktop():
    return _run("explorer shell:Desktop", "Opening Desktop.")

def open_pictures():
    return _run("explorer shell:My Pictures", "Opening Pictures.")

def open_music():
    return _run("explorer shell:My Music", "Opening Music.")

def open_videos():
    return _run("explorer shell:My Video", "Opening Videos.")

def open_recycle_bin():
    return _run("explorer shell:RecycleBinFolder", "Opening Recycle Bin.")


def open_recycle_bin():
    return _run(r'explorer shell:RecycleBinFolder', "Opening Recycle Bin.")


# ==========================================================
# COMPATIBILITY FUNCTIONS FOR SYSTEM HANDLER
# ==========================================================

def open_folder(name):
    folders = {
        "desktop": open_desktop,
        "downloads": open_downloads,
        "documents": open_documents,
        "pictures": open_pictures,
        "music": open_music,
        "videos": open_videos,
        "recycle bin": open_recycle_bin,
    }

    func = folders.get(name.lower())

    if not func:
        return False

    result = func()

    return result.get("success", False)
def open_cmd():
    return _run("start cmd", "Opening Command Prompt.")


def open_powershell():
    return _run("start powershell", "Opening PowerShell.")


def open_terminal():
    return _run("start wt", "Opening Windows Terminal.")


def open_system(name):
    systems = {
        "settings": open_settings,
        "control panel": open_control_panel,
        "task manager": open_task_manager,
        "explorer": open_file_explorer,
        "file explorer": open_file_explorer,
            "cmd": open_cmd,
    "command prompt": open_cmd,

    "powershell": open_powershell,
    "power shell": open_powershell,

    "terminal": open_terminal,
    "windows terminal": open_terminal,
        
    }

    func = systems.get(name.lower())

    if not func:
        return False

    result = func()

    return result.get("success", False)