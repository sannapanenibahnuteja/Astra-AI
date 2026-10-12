"""Public synthetic requests only. No native execution or personal data."""
import json
import threading
import time
from pathlib import Path
from desktop.runtime import VOICE_PLAN, VOICE_PROTOCOL, SYSTEM
from desktop.transport import ChatConnection
from desktop.automations import voice_plan

cases=[
    ('Can you recognize me by my voice?',False),
    ('Set up a daily routine called Morning at 8 AM: open YouTube and set volume to 35 percent.',True),
]
results=[]
for text,automation in cases:
    payload={'model':'qwen3:8b','stream':True,'think':False,'tools':[], 'format':VOICE_PLAN,
        'options':{'num_ctx':4096,'num_predict':512,'temperature':0},
        'messages':[{'role':'system','content':VOICE_PROTOCOL+SYSTEM+'\nBob supports optional local voice identification in Settings → Recognize my voice. It is approximate personalization, not authentication. It is currently disabled; no profile has matched. Never claim voice identification is unsupported.'},{'role':'user','content':text}]}
    started=time.monotonic(); content=''
    for chunk in ChatConnection('http://127.0.0.1:11434/api/chat',payload,threading.Event()).stream():
        content+=chunk.get('message',{}).get('content','')
    plan=json.loads(content)
    print(json.dumps(plan),flush=True)
    if automation:
        assert len(plan['actions'])==1 and plan['actions'][0]['action']=='automation_create'
        routine=voice_plan(plan['actions'][0])['routine']
        assert routine['name'].lower()=='morning' and routine['schedule']=='08:00' and len(routine['steps'])==2
    else:
        assert not plan['actions']
        assert 'recogn' in plan['reply'].lower() and ('disabled' in plan['reply'].lower() or 'setting' in plan['reply'].lower() or 'optional' in plan['reply'].lower())
    results.append({'request':text,'passed':True,'plan':plan,'seconds':round(time.monotonic()-started,2),'native_actions_executed':False})
Path('.cache/ollama-01029.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results))
