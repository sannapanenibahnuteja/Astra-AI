"""Create a portable ZIP containing only distributable app assets, never user data."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
root=Path(__file__).resolve().parents[1]
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--release-dir',default=str(root/'dist'));args=parser.parse_args()
release=Path(args.release_dir).resolve()
shutil.copy2(root/'README.md',release/'README.md')
shutil.copy2(root/'docs/USER-MANUAL.md',release/'Bob-User-Manual.md')
shutil.copy2(root/'docs/PHONE-SETUP.md',release/'Phone-Setup.md')
shutil.copy2(root/'docs/RELEASE-0.10.5.md',release/'Release-Notes.md')
files=[release/'Phone-Setup.md',release/'Bob.exe',release/'README.md',release/'Bob-User-Manual.md',release/'Release-Notes.md']
for path in files:
 if not path.is_file(): raise RuntimeError(f'Missing release asset: {path}')
with ZipFile(release/'Bob-Windows-x64.zip','w',ZIP_DEFLATED,compresslevel=5) as archive:
 for path in files: archive.write(path,path.relative_to(release))
print('Created', release/'Bob-Windows-x64.zip')
