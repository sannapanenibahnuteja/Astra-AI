"""Verify the packaged UIA backend against the dedicated disposable fixture."""
import argparse,json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop import windows
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--exe',default=str(root/'dist/release-0.7/Bob.exe'));args=parser.parse_args()
fixture=subprocess.Popen([sys.executable,str(root/'scripts/window-fixture.py')],creationflags=subprocess.CREATE_NO_WINDOW)
try:
 windows.find_window('Bob Automation Verification',timeout=15)
 result=root/'.cache/window-fixture-result.json'
 if result.exists():result.unlink()
 completed=subprocess.run([str(Path(args.exe).resolve()),'--windows-test','--data-dir',str(root/'.cache/packaged-windows-v06')],timeout=35)
 assert completed.returncode==0,completed.returncode
 saved=json.loads(result.read_text())
 assert saved['text']=='Hello + {Bob}',saved
 print((root/'.cache/packaged-windows-v06/windows-test.json').read_text())
 print('Packaged automation verified:',saved)
finally:
 try:windows.execute('close_window','Bob Automation Verification')
 except Exception:fixture.terminate()
 fixture.wait(timeout=10)
