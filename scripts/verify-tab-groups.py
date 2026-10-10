"""Live closure across two disposable Edge windows; never selects personal tabs."""
import json
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop import windows,tab_tasks
from desktop.runtime import Runtime
from desktop.web_launch import edge_path
marker='BobQA-'+uuid.uuid4().hex[:8]
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body=('<title>'+marker+' YouTube '+self.path+'</title><h1>Disposable test page</h1>').encode()
        self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(body)
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
root=Path(__file__).resolve().parents[1]
profile=root/'.cache'/marker
handles=[]
try:
    for path in ('one','two'):
        subprocess.Popen([edge_path(),'--user-data-dir='+str(profile),'--no-first-run','--no-default-browser-check','--new-window',f'http://127.0.0.1:{server.server_port}/{path}'],creationflags=subprocess.CREATE_NO_WINDOW)
        deadline=time.monotonic()+20
        while time.monotonic()<deadline:
            owned=[w for w in windows.window_inventory() if w['process']=='msedge.exe' and marker in w['title']]
            if len(owned)==len(handles)+1: handles=[w['handle'] for w in owned];break
            time.sleep(.2)
        else: raise RuntimeError('Disposable Edge windows did not appear')
    actual=tab_tasks.inventory()
    owned=[r for r in actual if r['handle'] in handles and marker in r['title']]
    assert len(owned)==2, 'Both live tabs must be accessible'
    with tempfile.TemporaryDirectory(dir=root/'.cache') as folder:
        runtime=Runtime(folder);identity=runtime.new_conversation()
        def send(text):
            job=runtime.start_chat(identity,text)
            deadline=time.monotonic()+20
            while time.monotonic()<deadline:
                result=runtime.poll_chat(job)
                if result['done']: return result
                time.sleep(.02)
            raise RuntimeError('Closure timed out')
        # Only fixture inventory is exposed to this live execution; close_one is native.
        with patch.object(tab_tasks,'inventory',return_value=owned),patch('desktop.runtime.ChatConnection',side_effect=AssertionError('Routine command reached model')):
            waiting=send('I said close all you tube.')
            assert not waiting['error'] and '2 selected' in waiting['text'],waiting
        with patch.object(tab_tasks,'inventory',side_effect=AssertionError('Approval must retain selection')):
            result=send('yes')
            assert not result['error'] and 'Closed 2' in result['text'],result
        assert not any(r['handle'] in handles for r in tab_tasks.inventory()), 'Selected fixture tabs remained'
        print(json.dumps({'passed':True,'native_closed_tabs':2,'windows':2,'routine_model_calls':0}))
finally:
    import win32gui,win32con
    for row in windows.window_inventory():
        if marker in row['title'] and row['process']=='msedge.exe': win32gui.PostMessage(row['handle'],win32con.WM_CLOSE,0,0)
    server.shutdown()
