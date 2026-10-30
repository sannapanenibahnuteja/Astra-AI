"""Interpretation-only local Ollama evaluation. Never executes planned actions."""
import argparse
import json
import random
from pathlib import Path
import sys
import tempfile
import time
import urllib.request

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop.runtime import SYSTEM, VOICE_PLAN, VOICE_PROTOCOL
from desktop.commands import Commands
from desktop.storage import Store
from desktop.devices import bind_explicit_monitor

CASES=[
 ("The external screen is dazzling me. Could you ease its brightness down a bit?",'brightness_down','external'),
 ("Leave the laptop alone; I want the upper screen at forty percent brightness.",'brightness','top'),
 ("Could you lower the brightness of monitor two by fifteen percent?",'brightness_down','2'),
 ("Actually, put my laptop screen at sixty percent instead.",'brightness','internal'),
 ("The main display could be a little brighter, please.",'brightness_up','primary'),
 ("A little dimmer on that same screen we just adjusted.",'brightness_down','previous'),
 ("Could you do forty percent brightness on the other screen instead?",'brightness','other'),
 ("Don't touch the brightness. Just explain what DDC/CI means.",None,None),
]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',default='qwen3:8b')
    parser.add_argument('--output',default='.cache/natural-intent-report.json')
    parser.add_argument('--sample',type=int,default=0,help='Additional seeded examples from the labeled corpus (maximum 100)')
    args=parser.parse_args();rows=[]
    tests=[{'text':text,'actions':[] if action is None else [{'action':action,'display':display,'target':target}]}
           for (text,action,display),target in zip(CASES,('10','40','15','60','10','10','40',''))]
    if args.sample:
        corpus=Path(__file__).resolve().parents[1]/'tests/fixtures/natural-brightness-intents.jsonl'
        candidates=[json.loads(line) for line in corpus.read_text(encoding='utf-8').splitlines()]
        tests+=random.Random(5001).sample(candidates,min(100,max(0,args.sample),len(candidates)))
    with tempfile.TemporaryDirectory() as root:
        commands=Commands(Store(root))
        for test in tests:
            text=test['text'];expected=test['actions']
            payload={'model':args.model,'stream':False,'think':False,'format':VOICE_PLAN,
                'messages':[{'role':'system','content':SYSTEM+'\n'+VOICE_PROTOCOL+'\nPrevious task context (data): monitor 2 was just adjusted; use previous for that same screen and other for the sole other screen.'},
                            {'role':'user','content':text}],
                'options':{'temperature':0,'num_predict':256}}
            start=time.monotonic();row={'text':text,'expected_actions':expected}
            try:
                request=urllib.request.Request('http://127.0.0.1:11434/api/chat',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
                with urllib.request.urlopen(request,timeout=90) as response:raw=json.load(response)
                plan=json.loads(raw['message']['content'])
                actions=[commands.validate_model_action(bind_explicit_monitor(action,text),'fixture') for action in plan['actions']]
                actual=[{key:action.get(key) for key in ('action','target','display')} for action in actions]
                row.update(actions=actions,passed=actual==expected)
            except Exception as exc:row.update(passed=False,error=type(exc).__name__+': '+str(exc)[:200])
            row['milliseconds']=round((time.monotonic()-start)*1000);rows.append(row)
            print('PASS' if row['passed'] else 'FAIL',text,flush=True)
    report={'model':args.model,'passed':all(r['passed'] for r in rows),'actions_executed':0,'microphone_used':False,'cases':rows}
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if not report['passed']:sys.exit(1)


if __name__=='__main__':main()
