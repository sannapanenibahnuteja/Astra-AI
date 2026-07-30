import os
import subprocess


WINDOWS_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "mspaint": "mspaint.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "powershell": "powershell.exe",
    "windows powershell": "powershell.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "taskmgr": "taskmgr.exe",
    "registry editor": "regedit.exe",
    "regedit": "regedit.exe",
    "control panel": "control.exe",
    "settings": "ms-settings:",
    "device manager": "devmgmt.msc",
    "disk management": "diskmgmt.msc",
    "services": "services.msc",
    "event viewer": "eventvwr.msc",
    "system configuration": "msconfig.exe",
    "system information": "msinfo32.exe",
}


def launch_builtin(name: str) -> bool:

    name = name.lower().strip()

    if name not in WINDOWS_APPS:
        return False

    command = WINDOWS_APPS[name]

    try:

        if command.startswith("ms-settings:"):
            os.startfile(command)

        elif command.endswith(".msc"):
            subprocess.Popen(["mmc", command])

        else:
            subprocess.Popen(command)

        return True

    except Exception as e:
        print(e)
        return False