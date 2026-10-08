"""Launching a process is not proof that an application window opened."""
from pathlib import Path
import re
import time
from desktop import windows

ALIASES={'calculator':{'calculator.exe','calculatorapp.exe'},'notepad':{'notepad.exe'},
         'microsoft edge':{'msedge.exe'},'edge':{'msedge.exe'},'windows terminal':{'windowsterminal.exe'}}


def wait_for_app(target,path='',timeout=2):
    expected=set(ALIASES.get(target.lower(),()))
    if str(path).lower().endswith('.exe'): expected.add(Path(path).name.lower())
    elif str(path).lower().endswith('.lnk'):
        try:
            with windows.com_thread():
                import win32com.client
                resolved=win32com.client.Dispatch('WScript.Shell').CreateShortcut(str(path)).TargetPath
                if resolved.lower().endswith('.exe'): expected.add(Path(resolved).name.lower())
        except Exception: pass
    deadline=time.monotonic()+timeout
    while True:
        for row in windows.window_inventory():
            if row['process'].lower() in expected or (not expected and re.search(r'\b'+re.escape(target)+r'\b',row['title'],re.I)):
                return row
        if time.monotonic()>=deadline: return None
        time.sleep(.1)
