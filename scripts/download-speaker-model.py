"""Download the pinned official speaker model for offline Bob releases."""
import hashlib
from pathlib import Path
from urllib.request import urlretrieve

name = '3dspeaker_speech_eres2net_sv_en_voxceleb_16k.onnx'
root = Path(__file__).resolve().parents[1] / 'dist/models/speaker'
root.mkdir(parents=True, exist_ok=True)
temporary = root / (name + '.tmp')
urlretrieve('https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-recongition-models/' + name, temporary)
if hashlib.sha256(temporary.read_bytes()).hexdigest() != 'c59158379255ad66e161679cca6af8d52d51e389e3224ab7d7a7baae295c2db5':
    temporary.unlink()
    raise RuntimeError('Speaker model checksum mismatch.')
temporary.replace(root / name)
print('Downloaded verified speaker model:', root / name)
