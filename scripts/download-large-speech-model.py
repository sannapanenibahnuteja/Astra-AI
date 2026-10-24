"""Optional pinned higher-capacity English ASR; about 1.5 GB on disk."""
from pathlib import Path
from huggingface_hub import snapshot_download

root = Path(__file__).resolve().parents[1]
snapshot_download('Systran/faster-distil-whisper-large-v3',
                  revision='c3058b475261292e64a0412df1d2681c06260fab',
                  local_dir=root/'dist/models/whisper-distil-large-v3',
                  allow_patterns=['config.json','model.bin','tokenizer.json',
                                  'vocabulary.json','preprocessor_config.json','README.md'])
