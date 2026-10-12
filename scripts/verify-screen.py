"""Screen awareness/control against our disposable app, never a user window."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from desktop import windows

parser = argparse.ArgumentParser()
parser.add_argument('--exe')
parser.add_argument('--data-dir', default=str(root / '.cache/screen-01026-source'))
args = parser.parse_args()
fixture = subprocess.Popen([sys.executable, str(root / 'scripts/window-fixture.py')], creationflags=subprocess.CREATE_NO_WINDOW)
try:
    windows.find_window('Bob Automation Verification', timeout=15)
    record = root / '.cache/window-fixture-result.json'
    if record.exists(): record.unlink()
    launch = [args.exe] if args.exe else [sys.executable, '-m', 'desktop.main']
    subprocess.run(launch + ['--screen-test', '--data-dir', args.data_dir], cwd=root, check=True, timeout=40)
    for _ in range(50):
        if record.exists(): break
        time.sleep(.1)
    assert record.exists(), 'The actual app did not receive the control activation'
    data = json.loads((Path(args.data_dir) / 'screen-test.json').read_text())
    assert data['passed']
    print(json.dumps(data))
finally:
    try: windows.execute('close_window', 'Bob Automation Verification')
    except Exception: fixture.terminate()
    fixture.wait(timeout=10)
