import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop.runtime import Runtime
runtime=Runtime('.cache/complex-plan')
id=runtime.new_conversation()
executed=[]
runtime._commands.execute=lambda step,identity: executed.append(step) or 'Verified plan.'
job=runtime.start_chat(id,'Could you open Notepad, type Good morning Bob into it, maximize that window and set brightness to forty percent?',True)
for _ in range(1200):
 result=runtime.poll_chat(job)
 if result['done']:break
 time.sleep(.1)
else:runtime.cancel_chat();raise RuntimeError('Planner timed out')
print(json.dumps(result))
plans=executed or runtime._pending.get(id,[])
print(json.dumps(plans))
assert not result['error'],result
assert {p['action'] for p in plans}>={'open','type_text','maximize_window','brightness'},plans
assert any(p['action']=='brightness' and p['target']=='40' for p in plans)
assert any(p['action']=='type_text' and p['target']=='Good morning Bob' for p in plans),plans
runtime._pending.clear()
