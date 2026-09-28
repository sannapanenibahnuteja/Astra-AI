"""Opt-in integration check against the local Ollama; never executes OS tools."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from desktop.runtime import Runtime

runtime = Runtime('.cache/ollama-verification')
identity = runtime.new_conversation()
runtime.save_settings({'keep_alive': '30s'})
results = []
planned = []
runtime._commands.execute = lambda step, identity: planned.append(step) or ('Verified ' + step['action'] + ' ' + step['target'])
for message in ('My test project is called Moon Garden. Reply in one short sentence.',
                'What is my test project called? Reply with just its name.',
                'Could you bring up a calculator and reduce the volume to twenty percent?'):
    start = time.monotonic()
    job = runtime.start_chat(identity, message)
    while True:
        result = runtime.poll_chat(job)
        if result['done']:
            break
        if time.monotonic() - start > 90:
            runtime.cancel_chat()
            raise RuntimeError('Ollama integration check timed out')
        time.sleep(.1)
    results.append({'message': message, 'seconds': round(time.monotonic() - start, 2), **result})
    print(json.dumps(results[-1], ensure_ascii=True), flush=True)
Path('.cache/ollama-verification/results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
assert not any(r['error'] for r in results), 'An Ollama response failed'
assert 'moon garden' in results[1]['text'].lower(), 'Conversation context was not recalled'
assert 'calculator' in results[2]['text'].lower() and any(p['action']=='volume' for p in planned), 'Natural action planning was not returned'
