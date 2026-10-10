"""Verify accepted voice approval closes only an owned disposable test window."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from desktop import windows
parser=argparse.ArgumentParser();parser.add_argument('--exe');args=parser.parse_args()
folder=root/'.cache'/('confirmation-packaged' if args.exe else 'confirmation-source');folder.mkdir(parents=True,exist_ok=True)
fixture=subprocess.Popen([sys.executable,str(root/'scripts/window-fixture.py')],creationflags=subprocess.CREATE_NO_WINDOW)
try:
    import win32process,psutil
    item=windows.find_window('Bob Automation Verification',timeout=15)
    owned={fixture.pid,*[p.pid for p in psutil.Process(fixture.pid).children(recursive=True)]}
    assert win32process.GetWindowThreadProcessId(item['handle'])[1] in owned,'Fixture must belong to this test'
    command=[str(Path(args.exe).resolve())] if args.exe else [sys.executable,'-m','desktop.main']
    result=subprocess.run([*command,'--confirmation-test','--data-dir',str(folder)],timeout=40)
    assert result.returncode==0,result.returncode
    data=json.loads((folder/'confirmation-test.json').read_text())
    assert data['passed'] and data['approval_executed'] and data['native_window_closed'],data
    print(json.dumps(data))
finally:
    if fixture.poll() is None: fixture.terminate()
    fixture.wait(timeout=10)
