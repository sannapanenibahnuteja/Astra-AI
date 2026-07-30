import os
import ctypes
import subprocess


def _run(command, success_message):

    try:

        subprocess.Popen(command, shell=True)

        return {
            "success": True,
            "message": success_message,
        }

    except Exception as e:

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

        ctypes.windll.powrprof.SetSuspendState(
            False,
            True,
            False,
        )

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
    return _run(
        r'explorer "%USERPROFILE%\Downloads"',
        "Opening Downloads.",
    )


def open_documents():
    return _run(
        r'explorer "%USERPROFILE%\Documents"',
        "Opening Documents.",
    )


def open_desktop():
    return _run(
        r'explorer "%USERPROFILE%\Desktop"',
        "Opening Desktop.",
    )


def open_pictures():
    return _run(
        r'explorer "%USERPROFILE%\Pictures"',
        "Opening Pictures.",
    )


def open_music():
    return _run(
        r'explorer "%USERPROFILE%\Music"',
        "Opening Music.",
    )


def open_videos():
    return _run(
        r'explorer "%USERPROFILE%\Videos"',
        "Opening Videos.",
    )


def open_recycle_bin():
    return _run(
        r'explorer shell:RecycleBinFolder',
        "Opening Recycle Bin.",
    )