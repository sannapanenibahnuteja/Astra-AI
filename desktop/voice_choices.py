"""Public voice choices; credentials stay in the private Azure configuration."""
import json
import subprocess
from desktop.voice import BASE, Voice

NEURAL = [
    {'id':'en-US-AndrewMultilingualNeural','label':'Andrew · American English · male'},
    {'id':'en-US-AvaMultilingualNeural','label':'Ava · American English · female'},
    {'id':'en-US-BrianMultilingualNeural','label':'Brian · American English · male'},
    {'id':'en-US-EmmaMultilingualNeural','label':'Emma · American English · female'},
]

def installed():
    script = BASE + " $v=[System.Speech.Synthesis.SpeechSynthesizer]::new(); try { @($v.GetInstalledVoices() | Where-Object Enabled | ForEach-Object { @{id=$_.VoiceInfo.Name;label=($_.VoiceInfo.Name+' · '+$_.VoiceInfo.Culture.Name+' · '+$_.VoiceInfo.Gender)} }) | ConvertTo-Json -Compress } finally { $v.Dispose() }"
    process = Voice._spawn(script, stdin=subprocess.DEVNULL)
    try:
        output, error = process.communicate(timeout=15)
        if process.returncode: raise RuntimeError('Windows voice inventory unavailable.')
        rows = json.loads(output or '[]')
        return rows if isinstance(rows,list) else [rows]
    except subprocess.TimeoutExpired:
        process.kill(); process.communicate()
        raise RuntimeError('Windows voice inventory timed out.') from None

def ready(root):
    try:
        cfg=json.loads((root/'neural-voice.json').read_text(encoding='utf-8'))
        return cfg.get('enabled') is True and bool(cfg.get('key')) and bool(cfg.get('region'))
    except (OSError,ValueError): return False

def validate(values):
    if 'voice_provider' in values and values['voice_provider'] not in ('auto','windows','azure'):
        raise ValueError('Choose automatic, Windows or Azure speech.')
    if 'neural_voice' in values and values['neural_voice'] not in ('',*[v['id'] for v in NEURAL]):
        raise ValueError('Choose an available neural voice.')
    if 'windows_voice' in values:
        name=values['windows_voice']
        if not isinstance(name,str) or (name and name not in [v['id'] for v in installed()]):
            raise ValueError('Choose an installed Windows voice.')

def selection(settings):
    return {key:settings.get(key,default) for key,default in
            [('voice_provider','auto'),('windows_voice',''),('neural_voice','')]}
