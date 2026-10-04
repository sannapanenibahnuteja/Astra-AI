"""Opt-in native regression on owned windows/files; never places phone calls."""
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop import windows

root=Path(__file__).resolve().parents[1]
fixture=subprocess.Popen([sys.executable,str(root/'scripts/window-fixture.py')],creationflags=subprocess.CREATE_NO_WINDOW)
try:
    windows.find_window('Bob Automation Verification',timeout=15)
    monitors=windows.monitor_inventory()
    for index in range(1,len(monitors)+1):
        print(windows.execute('move_window',str(index),'Bob Automation Verification'))
    windows.execute('type_text','Hello, Bob! A+B = {value}.','Bob Automation Verification')
    windows.execute('click_control','Record','Bob Automation Verification')
    import json
    data=json.loads((root/'.cache/window-fixture-result.json').read_text())
    assert data['text']=='Hello, Bob! A+B = {value}.',data
    print('Literal typing verified; monitors:',len(monitors))
finally:
    try: windows.execute('close_window','Bob Automation Verification')
    except Exception: fixture.terminate()
    fixture.wait(timeout=10)
