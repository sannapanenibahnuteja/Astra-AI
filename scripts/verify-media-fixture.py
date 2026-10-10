"""Verify native transport only on a silent disposable Edge media session."""
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop import browser,windows
from desktop.web_launch import edge_path
root=Path(__file__).resolve().parents[1]
server=subprocess.Popen([sys.executable,str(root/'scripts/verify-media.py'),'--serve'],creationflags=subprocess.CREATE_NO_WINDOW)
handle=None
try:
    import urllib.request
    for _ in range(40):
        try:
            with urllib.request.urlopen('http://127.0.0.1:8793',timeout=1) as response:
                if b'Bob Playback Verification' in response.read(): break
        except OSError: time.sleep(.2)
    else: raise RuntimeError('Silent media fixture server failed')
    subprocess.Popen([edge_path(),'--user-data-dir='+str(root/'.cache/media-verification-profile'),'--no-first-run','--no-default-browser-check','--new-window','http://127.0.0.1:8793'],creationflags=subprocess.CREATE_NO_WINDOW)
    item=windows.find_window('Bob Playback Verification',timeout=20);handle=item['handle']
    for _ in range(30):
        if 'Play silent fixture' in browser.execute({'action':'edge_inspect','target':''},{},handle): break
        time.sleep(.2)
    else: raise RuntimeError('Media fixture accessibility tree was not ready')
    browser.execute({'action':'edge_click','target':'Play silent fixture'}, {},handle)
    time.sleep(2)
    result=subprocess.run([sys.executable,str(root/'scripts/verify-media.py'),'--verify'],timeout=40,capture_output=True,text=True)
    if result.returncode: raise RuntimeError(result.stderr)
    print('Native silent media fixture: pause, seek and resume verified.')
finally:
    if handle:
        import win32gui,win32con
        win32gui.PostMessage(handle,win32con.WM_CLOSE,0,0)
    server.terminate();server.wait(timeout=10)
