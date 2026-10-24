"""Allowlisted local transcription assets; runtime never downloads models."""
from pathlib import Path
import sys

MODELS = {
    'small.en': ('whisper-small.en', 'Whisper Small English · faster', 'vocabulary.txt'),
    'distil-large-v3': ('whisper-distil-large-v3', 'Distil-Whisper Large v3 · higher capacity', 'vocabulary.json'),
}


def path_for(identity):
    if not isinstance(identity, str) or identity not in MODELS:
        raise ValueError('Choose a supported transcription model.')
    folder, _, vocabulary = MODELS[identity]
    roots = ([Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent)), Path(sys.executable).parent]
             if getattr(sys, 'frozen', False) else [Path(__file__).resolve().parents[1] / 'dist'])
    for root in roots:
        candidate = root / 'models' / folder
        if all((candidate / name).is_file() for name in ('model.bin', 'config.json', 'tokenizer.json', vocabulary)):
            return candidate
    raise RuntimeError('Selected speech model is incomplete. Install a Bob release containing that model.')


def options():
    rows = []
    for identity, (_, label, _) in MODELS.items():
        try:
            path_for(identity)
            installed = True
        except RuntimeError:
            installed = False
        rows.append({'id': identity, 'label': label, 'installed': installed})
    return rows
