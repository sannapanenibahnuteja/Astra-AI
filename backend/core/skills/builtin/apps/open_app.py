"""
Open Application Skill
"""

import subprocess
import platform

from core.skills.base.skill import Skill


class OpenAppSkill(Skill):

    def __init__(self):

        super().__init__()

        self.name = "open_app"

        self.description = "Open installed applications"

    def execute(self, app_name: str):

        app = app_name.lower().strip()

        windows_apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe"
        }

        if platform.system() != "Windows":
            return {
                "success": False,
                "response": "Only Windows is supported right now."
            }

        if app not in windows_apps:
            return {
                "success": False,
                "response": f"{app} is not supported yet."
            }

        subprocess.Popen(windows_apps[app])

        return {
            "success": True,
            "response": f"Opening {app}..."
        }