# Run from repository root: python -m PyInstaller desktop/Bob.spec
from pathlib import Path
from PyInstaller.utils.hooks import collect_all
root = Path(SPECPATH).parent
speech_data, speech_binaries, speech_imports = collect_all('faster_whisper')
ct_data, ct_binaries, ct_imports = collect_all('ctranslate2')
aec_data, aec_binaries, aec_imports = collect_all('pywebrtc_audio')
speaker_data, speaker_binaries, speaker_imports = collect_all('sherpa_onnx')
speaker_model = root / 'dist/models/speaker/3dspeaker_speech_eres2net_sv_en_voxceleb_16k.onnx'
if not speaker_model.is_file(): raise RuntimeError('Run scripts/download-speaker-model.py before building Bob.')
speaker_data += [(str(speaker_model), 'models/speaker')]
speaker_data += [(str(root / 'assets/3D-Speaker-LICENSE.txt'), 'licenses')]
model_root = root / 'dist/models/whisper-small.en'
model_files = ['config.json', 'model.bin', 'tokenizer.json', 'vocabulary.txt']
for name in model_files:
    if not (model_root / name).is_file():
        raise RuntimeError('Run scripts/download-speech-model.py before building Bob.')
model_data = [(str(model_root / name), 'models/whisper-small.en') for name in model_files]
a = Analysis([str(root / 'desktop/main.py')], pathex=[str(root)],
             binaries=speech_binaries + ct_binaries + aec_binaries + speaker_binaries, datas=[(str(root / 'frontend/dist'), 'frontend/dist')] + model_data + speech_data + ct_data + aec_data + speaker_data,
             hiddenimports=['webview.platforms.edgechromium', 'pystray._win32', 'PIL.Image', 'PIL.ImageDraw', 'pywinauto.controls.uia_controls', 'pywinauto.controls.hwndwrapper', 'webrtcvad', '_webrtcvad'] + speech_imports + ct_imports + aec_imports + speaker_imports,
             hookspath=[str(root / 'desktop/hooks')], hooksconfig={}, runtime_hooks=[],
             excludes=['PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'tkinter'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='Bob',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=False, disable_windowed_traceback=False, icon=str(root / 'assets/bob.ico'))
