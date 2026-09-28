"""Bounded Windows PowerShell speech check; uses a WAV, never records the mic."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from desktop.voice import Voice, BASE

folder = Path('.cache/native-speech').resolve()
folder.mkdir(parents=True, exist_ok=True)
script = BASE + r'''
$cfg = [Console]::In.ReadToEnd() | ConvertFrom-Json
$info = [System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers() | Select-Object -First 1
if (!$info) { throw 'No recognizer installed' }
$voice = [System.Speech.Synthesis.SpeechSynthesizer]::new()
try {
  $voice.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::NotSet, [System.Speech.Synthesis.VoiceAge]::NotSet, 0, $info.Culture)
  $voice.SetOutputToWaveFile($cfg.path)
  $voice.Speak('Open calculator')
} finally { $voice.Dispose() }
$engine = [System.Speech.Recognition.SpeechRecognitionEngine]::new($info)
try {
  $engine.LoadGrammar([System.Speech.Recognition.DictationGrammar]::new())
  $choices = [System.Speech.Recognition.Choices]::new([string[]]@('open calculator', 'yes', 'cancel'))
  $builder = [System.Speech.Recognition.GrammarBuilder]::new($choices)
  $builder.Culture = $info.Culture
  $engine.LoadGrammar([System.Speech.Recognition.Grammar]::new($builder))
  $engine.SetInputToWaveFile($cfg.path)
  $result = $engine.Recognize([TimeSpan]::FromSeconds(10))
  if (!$result) { throw 'No speech recognized' }
  @{text=$result.Text; confidence=$result.Confidence; language=$info.Culture.Name} | ConvertTo-Json -Compress
} finally { $engine.Dispose() }
'''
print(Voice()._run(script, {'path': str(folder / 'sample.wav')}, 25))
