"""Create a portable ZIP containing only distributable app assets, never user data."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
root=Path(__file__).resolve().parents[1]
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--release-dir',default=str(root/'dist'));parser.add_argument('--folder-only',action='store_true');args=parser.parse_args()
release=Path(args.release_dir).resolve()
archive_dir=release
if (release/'Bob'/'Bob.exe').is_file(): release=release/'Bob'
shutil.copy2(root/'README.md',release/'README.md')
shutil.copy2(root/'docs/USER-MANUAL.md',release/'Bob-User-Manual.md')
shutil.copy2(root/'docs/PHONE-SETUP.md',release/'Phone-Setup.md')
shutil.copy2(root/'docs/PHONE-SETUP.md',release/'PHONE-SETUP.md')
shutil.copy2(root/'assets/3D-Speaker-LICENSE.txt',release/'3D-Speaker-LICENSE.txt')
import re
version_source=(root/'desktop/runtime.py').read_text(encoding='utf-8')
version=re.search(r'"version": "([0-9.]+)"',version_source).group(1)
shutil.copy2(root/f'docs/RELEASE-{version}.md',release/'Release-Notes.md')
shutil.copy2(root/f'docs/RELEASE-{version}.md',release/f'RELEASE-{version}.md')
conversation_status=root/'docs/CONVERSATION-CAPABILITIES.md'
if conversation_status.exists():
 shutil.copy2(conversation_status,release/'Conversation-Capabilities.md')
 shutil.copy2(conversation_status,release/'CONVERSATION-CAPABILITIES.md')
files=[release/'Phone-Setup.md',release/'Bob.exe',release/'README.md',release/'Bob-User-Manual.md',release/'Release-Notes.md',release/'3D-Speaker-LICENSE.txt']
files.append(release/f'RELEASE-{version}.md')
files.append(release/'PHONE-SETUP.md')
if conversation_status.exists(): files.extend([release/'Conversation-Capabilities.md',release/'CONVERSATION-CAPABILITIES.md'])
for path in files:
 if not path.is_file(): raise RuntimeError(f'Missing release asset: {path}')
if (release/'_internal').is_dir():
 files += sorted(path for path in (release/'_internal').rglob('*') if path.is_file())
if args.folder_only:
 print('Ready to launch:',release/'Bob.exe')
 raise SystemExit(0)
with ZipFile(archive_dir/'Bob-Windows-x64.zip','w',ZIP_DEFLATED,compresslevel=5) as archive:
 for path in files: archive.write(path,path.relative_to(release))
print('Created', archive_dir/'Bob-Windows-x64.zip')
