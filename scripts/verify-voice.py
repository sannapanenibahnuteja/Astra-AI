"""Generate known speech fixtures through Windows TTS; no microphone or actions."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from desktop.voice import Voice, BASE, WAKE
folder = Path('.cache/voice-fixtures').resolve()
folder.mkdir(parents=True, exist_ok=True)
phrases = ['Open calculator', 'What time is it', 'Remember that my favourite colour is blue', 'Search the web for pictures of mountains', 'Stop listening', 'Hey Bob', 'Okay Bob']
script = BASE + r'''
$cfg = [Console]::In.ReadToEnd() | ConvertFrom-Json
$voice = [System.Speech.Synthesis.SpeechSynthesizer]::new()
try {
 foreach ($item in $cfg.items) {
  $voice.SetOutputToWaveFile($item.path)
  $voice.Speak([string]$item.text)
  $voice.SetOutputToNull()
 }
} finally { $voice.Dispose() }
'''
items=[{'text': phrase, 'path':str(folder / f'{index}.wav')} for index, phrase in enumerate(phrases)]
voice=Voice()
voice._run(script, {'items':items}, 60)
(folder/'expected.json').write_text(json.dumps(items,indent=2))
print('Generated',len(items),'speech fixtures')
for item in items[-2:]:
 test = WAKE.replace('$engine.SetInputToDefaultAudioDevice()', "$engine.SetInputToWaveFile('"+item['path'].replace("'", "''")+"')")
 test=test.replace('while ($true)', 'for ($i=0; $i -lt 2; $i++)')
 print(item['text'], voice._run(test, {}, 20))
import wave
with wave.open(str(folder/'silence.wav'),'wb') as wav:
 wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(16000);wav.writeframes(b'\0\0'*16000*3)
