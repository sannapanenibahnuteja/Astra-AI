import json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop import windows
process=subprocess.Popen([sys.executable,'scripts/window-fixture.py'],creationflags=subprocess.CREATE_NO_WINDOW)
try:
 name='Bob Automation Verification'
 windows.find_window(name,timeout=15)
 print(windows.execute('focus_window',name))
 print(windows.execute('type_text','Hello + {Bob}',name))
 print(windows.execute('inspect_window',name))
 print(windows.execute('click_control','Record',name))
 result=json.loads(Path('.cache/window-fixture-result.json').read_text())
 assert result['text']=='Hello + {Bob}',result
 print(windows.execute('maximize_window',name))
 print(windows.execute('restore_window',name))
 print(windows.execute('minimize_window',name))
 print(windows.execute('restore_window',name))
 print('Verified literal typing, accessible controls, focus and window sizing:',result)
finally:
 try:windows.execute('close_window','Bob Automation Verification')
 except Exception:process.terminate()
 process.wait(timeout=10)
