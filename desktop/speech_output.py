"""Speakable text and optional, explicitly configured Azure neural speech."""
import json
import re
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape


def spoken_text(text):
    text = re.sub(r'```[\s\S]*?```', 'I’ve put the code in the chat.', str(text))
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'^\s*(?:#{1,6}|[-*])\s+', '', text, flags=re.M)
    return text.replace('**','').replace('`','').strip()[:5000]


def neural_audio(text, root, voice_override='', rate=0):
    path = root/'neural-voice.json'
    if not path.exists(): return None
    cfg = json.loads(path.read_text(encoding='utf-8'))
    if cfg.get('enabled') is not True: return None
    region, voice = cfg.get('region',''), voice_override or cfg.get('voice','en-IN-PrabhatNeural')
    if not re.fullmatch(r'[a-z0-9]+',region) or not re.fullmatch(r'[A-Za-z0-9-]+',voice) or not cfg.get('key'):
        raise ValueError('Configure the Azure Speech region, voice and key in neural-voice.json.')
    locale='-'.join(voice.split('-')[:2])
    speed=max(-40,min(40,int(rate)*8))-3
    ssml = '<speak version="1.0" xml:lang="'+locale+'"><voice name="'+voice+'"><prosody rate="'+str(speed)+'%">'+escape(text)+'</prosody></voice></speak>'
    request = Request(f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1',data=ssml.encode(),headers={
        'Ocp-Apim-Subscription-Key':cfg['key'], 'Content-Type':'application/ssml+xml',
        'X-Microsoft-OutputFormat':'riff-24khz-16bit-mono-pcm','User-Agent':'BobDesktop'})
    try:
        with urlopen(request,timeout=20) as response: data=response.read(16_000_001)
    except Exception: raise RuntimeError('Neural voice is unavailable. Check Azure Speech credentials, region and connectivity.') from None
    if len(data)>16_000_000 or not data.startswith(b'RIFF'): raise RuntimeError('Unexpected neural speech response.')
    return data
