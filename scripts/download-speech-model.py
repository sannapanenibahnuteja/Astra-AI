"""Download the local English speech model for development and release packaging."""
from pathlib import Path
from huggingface_hub import snapshot_download
root=Path(__file__).resolve().parents[1]
snapshot_download('Systran/faster-whisper-small.en', local_dir=root/'dist/models/whisper-small.en',
                  allow_patterns=['config.json','model.bin','tokenizer.json','vocabulary.txt'])
