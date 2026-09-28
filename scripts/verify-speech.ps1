$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$testFolder = Join-Path $PSScriptRoot '..\.cache\speech-test'
New-Item -ItemType Directory -Path $testFolder -Force | Out-Null
$waveFile = Join-Path (Resolve-Path $testFolder).Path 'sample.wav'
$recognizers = [System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers()
if (!$recognizers.Count) { throw 'No Windows speech recognizer installed.' }
$recognizerInfo = $recognizers[0]
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $voice.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::NotSet, [System.Speech.Synthesis.VoiceAge]::NotSet, 0, $recognizerInfo.Culture)
    $voice.SetOutputToWaveFile($waveFile)
    $voice.Speak('Open calculator')
} finally { $voice.Dispose() }
$recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine($recognizerInfo)
try {
    $recognizer.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
    $recognizer.SetInputToWaveFile($waveFile)
    $result = $recognizer.Recognize()
    if (!$result) { throw 'Speech recognition returned no text.' }
    @{ language=$recognizerInfo.Culture.Name; text=$result.Text; confidence=$result.Confidence } | ConvertTo-Json
} finally { $recognizer.Dispose() }
