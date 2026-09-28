"""Opt-in native integration in a disposable Edge profile; no personal tabs."""
import json
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from desktop import browser, windows

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'<title>Bob Edge Verification</title><h1>Bob test page</h1><label>Test message<input aria-label="Test message"></label><button onclick="document.getElementById(\'result\').textContent=\'Button worked\'">Test action</button><p id="result">Ready</p>'
        self.send_response(200); self.send_header('Content-Type','text/html'); self.end_headers(); self.wfile.write(body)
    def log_message(self, *args): pass

server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
exe=Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')
profile=ROOT/'.cache/edge-verification-profile'
subprocess.Popen([str(exe),'--user-data-dir='+str(profile),'--no-first-run','--no-default-browser-check','--new-window',f'http://127.0.0.1:{server.server_port}'],creationflags=subprocess.CREATE_NO_WINDOW)
handle=None
try:
    for _ in range(80):
        matches=[w for w in windows.window_inventory() if w['process']=='msedge.exe' and w['title'].startswith('Bob Edge Verification')]
        if len(matches)==1: handle=matches[0]['handle']; break
        time.sleep(.25)
    if not handle: raise RuntimeError('Disposable Edge fixture did not appear.')
    context={}; results=[]
    def run(action,target='',value=''):
        time.sleep(.25)
        result=browser.execute({'action':action,'target':target,'value':value},context,handle)
        results.append(result); return result
    observed=run('edge_inspect')
    for _ in range(10):
        if 'Test message' in observed: break
        time.sleep(.5)
        observed=run('edge_inspect')
    assert 'Test message' in observed, observed
    run('edge_fill','Test message','Hello + Bob ^ 50%')
    run('edge_click','Test action')
    assert 'Button worked' in run('edge_inspect')
    run('edge_tabs')
    run('edge_find','Bob test page')
    run('edge_shortcut','escape')
    run('edge_shortcut','new tab')
    time.sleep(.5)
    run('edge_select_tab','Bob Edge Verification')
    print(json.dumps({'passed':True,'checks':len(results)},indent=2))
finally:
    if handle:
        import win32gui, win32con
        win32gui.PostMessage(handle,win32con.WM_CLOSE,0,0)
    server.shutdown()
