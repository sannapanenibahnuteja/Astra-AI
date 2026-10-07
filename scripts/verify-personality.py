"""Text-only local tone demo. No memories, microphone, tools or native actions."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
from desktop.personality import style

parser=argparse.ArgumentParser()
parser.add_argument('--model',default='qwen3:8b')
args=parser.parse_args()
results={}
with httpx.Client(timeout=90,trust_env=False) as client:
    for key in ('funny','serious'):
        response=client.post('http://127.0.0.1:11434/api/chat',json={
            'model':args.model,'stream':False,'think':False,
            'messages':[{'role':'system','content':style({'personality_preset':key})},
                        {'role':'user','content':'I have thirty browser tabs open and cannot focus. Give me one short sentence of advice, in your current personality.'}],
            'options':{'num_predict':80,'num_ctx':4096},
        })
        response.raise_for_status()
        results[key]=response.json()['message']['content']
print(json.dumps(results,ensure_ascii=False,indent=2))
