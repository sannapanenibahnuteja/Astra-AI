"""Local Ollama intent dry-run. Prints plans; never executes native actions."""
import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from desktop.runtime import SYSTEM, VOICE_PLAN, VOICE_PROTOCOL
from desktop.transport import ChatConnection

cases = [
    ('It is a bit too loud, bring it down a little.', [('volume_down','')]),
    ('Get YouTube up and bring the volume to twenty percent.', [('open','youtube'),('volume','20')]),
    ('I am done with every YouTube page. Close all of them.', [('edge_close_tabs','youtube')]),
    ('Do not open YouTube. Just tell me what it is.', []),
]
results=[]
for text, expected in cases:
    payload={'model':'qwen3:8b','stream':True,'think':False,'keep_alive':'5m',
             'options':{'num_ctx':8192,'num_predict':512,'temperature':0},'format':VOICE_PLAN,
             'messages':[{'role':'system','content':VOICE_PROTOCOL+SYSTEM+'\nInterpret spoken meaning. Some available apps: calculator, notepad. Keep answers short.'},{'role':'user','content':text}]}
    start=time.monotonic(); calls=[]; reply=''
    for chunk in ChatConnection('http://127.0.0.1:11434/api/chat',payload,threading.Event()).stream():
        if chunk.get('error'): raise RuntimeError(chunk['error'])
        calls.extend(chunk.get('message',{}).get('tool_calls',[])); reply+=chunk.get('message',{}).get('content','')
    if reply.strip():
        plan=json.loads(reply); calls=[{'function':{'name':'windows_action','arguments':a}} for a in plan['actions']]; reply=plan['reply']
    actions=[(c.get('function',{}).get('arguments',{}).get('action'),c.get('function',{}).get('arguments',{}).get('target','').casefold()) for c in calls]
    passed=actions==expected
    result={'transcript':text,'passed':passed,'actions':calls,'reply':reply,'seconds':round(time.monotonic()-start,2),'native_actions_executed':False}
    results.append(result); print(json.dumps(result),flush=True)
Path('.cache/semantic-voice-ollama.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
if not all(r['passed'] for r in results): raise SystemExit('Some local-model intent cases did not match; inspect results before release.')
