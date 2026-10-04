"""Opt-in exact dictation regression using only a new disposable Notepad tab."""
from pathlib import Path
import subprocess
import sys
import time
import uuid

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from desktop import windows

path=root/'.cache'/('bob-dictation-'+uuid.uuid4().hex[:8]+'.txt')
path.parent.mkdir(exist_ok=True)
path.write_text('',encoding='utf-8')
subprocess.Popen(['notepad.exe',str(path)])
item=windows.find_window(path.name,timeout=15)
try:
    text='Hello, Bob! Keep A+B = {value}.'
    print(windows.execute('type_text',text,item['title']))
    windows.execute('press_key','ctrl+s',path.name)
    time.sleep(1)
    actual=path.read_text(encoding='utf-8-sig')
    assert actual==text,repr(actual)
    print('Actual Notepad exact dictation passed.')
finally:
    # Close only our tab, never the user's other documents or entire app.
    windows.execute('press_key','ctrl+w',path.name)
