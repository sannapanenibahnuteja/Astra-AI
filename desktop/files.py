"""Explicit file operations and Explorer context, with reversible deletion only."""
import os
from pathlib import Path
import re
import shutil
from desktop.windows import com_thread

ACTIONS = {'file_list', 'file_find', 'file_open', 'file_properties', 'file_mkdir',
           'file_copy', 'file_move', 'file_rename', 'file_recycle', 'explorer_selection'}
REFERENCES = {'it', 'that', 'that file', 'those', 'those files', 'these files', 'them', 'the selected files', 'selected files'}
FOLDERS = {'desktop':'Desktop', 'documents':'Personal', 'downloads':'{374DE290-123F-4565-9164-39C4925E467B}',
           'pictures':'My Pictures', 'music':'My Music', 'videos':'My Video'}
EXECUTABLE = {'.exe','.com','.bat','.cmd','.ps1','.vbs','.vbe','.js','.jse','.wsf','.wsh','.msi','.scr','.lnk','.url','.hta','.reg','.cpl','.msc'}


def known_folder(name):
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders') as key:
        return Path(os.path.expandvars(winreg.QueryValueEx(key, FOLDERS[name])[0])).resolve()


def path_for(value, context):
    value = value.strip()
    quoted = value.startswith('"') and value.endswith('"')
    value = value.strip('"')
    if not quoted:
        value = re.sub(r'^(?:the )?(?:file|folder)\s+', '', value, flags=re.I)
        source = re.fullmatch(r'(.+?) (?:from|in) (.+)', value, re.I)
        if source:
            folder = path_for(source[2], context)
            return path_for(str(folder / source[1].strip('"')), {})
    alias = value.lower().removeprefix('my ').removeprefix('the ')
    if alias in FOLDERS:
        return known_folder(alias)
    if alias in ('here', 'this folder', 'that folder', 'current folder', '.'):
        if not context.get('last_folder'): raise ValueError('Name a folder first, or say “use selected files” while Explorer is active.')
        return Path(context['last_folder']).resolve()
    value = os.path.expandvars(os.path.expanduser(value))
    if value.startswith(('\\\\', '\\?\\', '\\.\\')):
        raise ValueError('Use a local drive path; network and device paths are not supported for file operations.')
    path = Path(value)
    if not path.is_absolute():
        if not context.get('last_folder'): raise ValueError('Give a full path or first say “list files in Downloads”.')
        path = Path(context['last_folder']) / path
    # Reject NTFS alternate streams, device names and ambiguous relative drives.
    if ':' in str(path)[2:] or any(p.rstrip(' .').upper().split('.')[0] in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]} for p in path.parts[1:]):
        raise ValueError('That is not a regular local file path.')
    if any(p.endswith((' ', '.')) for p in path.parts[1:] if p not in ('.','..')):
        raise ValueError('Paths ending in spaces or dots are ambiguous on Windows.')
    for part in (path, *path.parents):
        if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
            raise ValueError('File operations through symbolic links or junctions are excluded.')
    return path.resolve()


def protect(path, destructive=False):
    for key in ('SystemRoot', 'PROGRAMFILES', 'PROGRAMFILES(X86)', 'PROGRAMDATA', 'LOCALAPPDATA', 'APPDATA'):
        base = os.environ.get(key)
        if base and path.is_relative_to(Path(base).resolve()):
            raise ValueError('System, application and private app-data folders are excluded from file changes.')
    if path == Path(path.anchor) or path == Path.home().resolve():
        raise ValueError('A drive root or user-profile root cannot be changed.')
    if destructive and any(path == known_folder(name) for name in FOLDERS):
        raise ValueError('A standard personal folder cannot itself be moved, renamed or recycled. Choose items inside it.')


def parse(text):
    rules = [
        ('file_list', r'(?:list|show) (?:files|items|folders)(?: in (.+))?'),
        ('file_find', r'(?:find|search for) (?:files? )?(.+?) in (.+)'),
        ('file_mkdir', r'(?:create|make) (?:a |the )?(?:new )?folder (.+?) in (.+)'),
        ('file_copy', r'copy (.+?) to (.+)'), ('file_move', r'move (.+?) to (.+)'),
        ('file_rename', r'rename (.+?) to (.+)'),
        ('file_recycle', r'(?:delete|recycle|send to (?:the )?recycle bin) (.+)'),
        ('file_properties', r'(?:show|get) (?:the )?properties (?:of|for) (.+)'),
        ('file_open', r'open (?:file|folder) (.+)'),
    ]
    if text.lower() in ('use selected files', 'show selected files', 'what files are selected'):
        return {'action':'explorer_selection', 'target':''}
    for action, pattern in rules:
        match = re.fullmatch(pattern, text, re.I)
        if match:
            command = {'action':action, 'target':match[1] or 'current folder'}
            if len(match.groups()) > 1: command['destination'] = match[2]
            return command
    return None


def validate(command):
    action = command.get('action')
    if action not in ACTIONS: raise ValueError('Unsupported file operation.')
    result = {key:command.get(key, '') for key in ('action','target','destination')}
    if any(not isinstance(v,str) or len(v)>2048 or '\x00' in v for v in result.values()):
        raise ValueError('Invalid file target.')
    if action != 'explorer_selection' and not result['target']: raise ValueError('Name a file or folder.')
    if action in ('file_copy','file_move','file_rename','file_mkdir','file_find') and not result['destination']:
        raise ValueError('Name the destination folder or new name.')
    result['confirm'] = action in ('file_move','file_rename','file_recycle')
    return result


def sources(target, context):
    if target.lower() in REFERENCES:
        selected = context.get('last_files', [])
        if not selected: raise ValueError('No remembered file selection. First find files or say “use selected files” in Explorer.')
        if target.lower() in ('it','that','that file') and len(selected) != 1:
            raise ValueError(f'{len(selected)} items are remembered. Name one file, or say “those files” for all of them.')
        return [path_for(p, context) for p in selected]
    return [path_for(target, context)]


def prepare(command, context):
    """Resolve before asking for approval, so 'yes' never targets a new selection."""
    command = validate(command)
    action = command['action']
    if action in ('file_copy','file_move','file_rename','file_recycle'):
        paths = sources(command['target'], context)
        if len(paths)>50: raise ValueError('Choose at most 50 items for a file operation.')
        if action == 'file_rename' and len(paths) != 1: raise ValueError('Rename one explicitly named file at a time.')
        for path in paths:
            if not path.exists(): raise ValueError(f'File no longer exists: {path}')
            protect(path, destructive=action != 'file_copy')
        if any(a != b and a.is_relative_to(b) for a in paths for b in paths):
            raise ValueError('Choose either a folder or its children, not both in the same operation.')
        command['paths'] = [str(p) for p in paths]
        command['identities'] = [(p.stat().st_ino, p.stat().st_mtime_ns, p.stat().st_size) for p in paths]
        command['target'] = ', '.join(command['paths'])
        if action == 'file_rename':
            name = command['destination'].strip('"')
            if not name or Path(name).name != name or any(c in name for c in '<>:"/\\|?*') or name in ('.','..'):
                raise ValueError('A new name must be a single file or folder name.')
            destinations = [path_for(str(paths[0].parent / name), context)]
        elif action in ('file_copy','file_move'):
            folder = path_for(command['destination'], context)
            if not folder.is_dir(): raise ValueError('The destination must be an existing folder.')
            destinations = [folder / p.name for p in paths]
        else:
            destinations = []
        for src, dst in zip(paths, destinations):
            protect(dst)
            if dst.exists(): raise ValueError(f'Nothing was changed: {dst} already exists. Choose another name or folder.')
            if dst.is_relative_to(src): raise ValueError('A folder cannot be placed inside itself.')
            if action in ('file_move','file_rename') and src.drive.lower() != dst.drive.lower():
                raise ValueError('For a transfer between drives, copy first, verify the copies, then recycle the originals.')
        if len(set(destinations)) != len(destinations): raise ValueError('Two files would have the same destination name.')
        command['destinations'] = [str(p) for p in destinations]
        command['description'] = action.removeprefix('file_').replace('recycle','send to the Recycle Bin') + ' ' + '; '.join(command['paths'])
        if destinations: command['description'] += ' → ' + '; '.join(command['destinations'])
    return command


def explorer_selection(preferred_handle=None):
    import win32gui
    import win32com.client
    with com_thread():
        foreground = preferred_handle or win32gui.GetForegroundWindow()
        candidates = []
        for window in win32com.client.Dispatch('Shell.Application').Windows():
            try:
                if int(window.HWND) == foreground and Path(window.FullName).name.lower() == 'explorer.exe':
                    candidates.append(window)
            except Exception: continue
        if len(candidates) != 1: raise ValueError('Bring the desired File Explorer window to the front and select its files first.')
        document = candidates[0].Document
        folder = document.Folder.Self.Path
        selected = [item.Path for item in document.SelectedItems()]
        if len(selected)>50: raise ValueError('Select at most 50 items.')
        if not Path(folder).is_dir(): raise ValueError('Open a local folder in Explorer first.')
        return folder, selected


def _bounded_tree(path):
    count, total = 0, 0
    def check(item):
        nonlocal count, total
        if item.is_symlink() or (hasattr(item,'is_junction') and item.is_junction()):
            raise ValueError('Linked files and junctions are excluded from bulk operations.')
        count += 1
        total += item.stat().st_size if item.is_file() else 0
        if count>2000 or total>1_073_741_824:
            raise ValueError('This operation exceeds 2,000 items or 1 GB. Use File Explorer for larger transfers.')
    check(path)
    if path.is_dir():
        for root, folders, names in os.walk(path, followlinks=False):
            for name in folders + names: check(Path(root) / name)


def execute(command, context):
    action = command['action']
    if action == 'explorer_selection':
        folder, selected = explorer_selection(command.get('explorer_handle'))
        context.update(last_folder=folder, last_files=selected)
        return f'Working in {folder}. Selected {len(selected)} items:\n' + '\n'.join(selected)
    if action in ('file_copy','file_move','file_rename','file_recycle'):
        # Recheck frozen paths without re-resolving conversational references.
        paths = [path_for(p, {}) for p in command['paths']]
        destinations = [path_for(p, {}) for p in command['destinations']]
        for path, expected in zip(paths, command['identities']):
            protect(path, destructive=action != 'file_copy')
            stat = path.stat()
            if (stat.st_ino, stat.st_mtime_ns, stat.st_size) != tuple(expected):
                raise ValueError('A source changed since this operation was proposed. Ask again to review the current files.')
            _bounded_tree(path)
        for dst in destinations:
            protect(dst)
            if dst.exists(): raise ValueError(f'{dst} now exists. No files were changed.')
        completed = []
        try:
            for i, src in enumerate(paths):
                if action == 'file_recycle':
                    from send2trash import send2trash
                    send2trash(str(src))
                    if src.exists(): raise RuntimeError('Windows did not confirm recycling the item.')
                elif action == 'file_copy':
                    dst = destinations[i]
                    if src.is_dir(): shutil.copytree(src, dst, dirs_exist_ok=False)
                    else:
                        # Exclusive create prevents accidental overwrite if a file appears meanwhile.
                        with src.open('rb') as reader, dst.open('xb') as writer: shutil.copyfileobj(reader, writer)
                        shutil.copystat(src, dst)
                    if not dst.exists(): raise RuntimeError('Destination was not created.')
                else:
                    dst = destinations[i]
                    # Windows rename never overwrites. Cross-volume moves need Explorer.
                    if src.drive.lower() != dst.drive.lower(): raise ValueError('Use copy, verify, then recycle for a transfer between drives.')
                    src.rename(dst)
                    if src.exists() or not dst.exists(): raise RuntimeError('Windows did not confirm the move.')
                completed.append(str(src))
        except Exception as exc:
            raise RuntimeError(f'Completed {len(completed)} of {len(paths)} items. Stopped at {paths[len(completed)]}: {exc}. Check both folders before retrying.') from exc
        context['last_files'] = [str(p) for p in destinations]
        if destinations: context['last_folder'] = str(destinations[0].parent)
        verb = {'file_copy':'Copied','file_move':'Moved','file_rename':'Renamed','file_recycle':'Sent to the Recycle Bin'}[action]
        return f'{verb}: ' + ', '.join(p.name for p in destinations or paths) + '.'
    if action == 'file_mkdir':
        folder = path_for(command['destination'], context)
        name = command['target'].strip('"')
        if Path(name).name != name or any(c in name for c in '<>:"/\\|?*') or name in ('.','..',''):
            raise ValueError('Choose a single new folder name.')
        path = path_for(str(folder / name), context)
        protect(path)
        path.mkdir(exist_ok=False)
        context.update(last_folder=str(folder), last_files=[str(path)])
        return f'Created {path}.'
    if action == 'file_find':
        folder = path_for(command['destination'], context)
        if not folder.is_dir(): raise ValueError('Choose an existing folder.')
        found, scanned = [], 0
        for root, dirs, names in os.walk(folder, followlinks=False):
            dirs[:] = [n for n in dirs if n not in ('.git','node_modules','venv','.venv') and not (Path(root)/n).is_symlink() and not (Path(root)/n).is_junction()]
            for name in dirs + names:
                scanned += 1
                if command['target'].strip('"').lower() in name.lower(): found.append(str(Path(root)/name))
                if len(found)>=50 or scanned>=5000: break
            if len(found)>=50 or scanned>=5000: break
        context.update(last_folder=str(folder), last_files=found)
        return f'Found {len(found)} matching items (limit: 50 results / 5,000 entries scanned):\n' + ('\n'.join(found) or 'No matches.')
    if action == 'file_list':
        folder = path_for(command['target'], context)
        if not folder.is_dir(): raise ValueError('Choose an existing folder.')
        # Keep selection explicit: listing a folder does not select all its contents.
        from itertools import islice
        items = sorted(islice(folder.iterdir(), 101), key=lambda p:(not p.is_dir(),p.name.lower()))
        context.update(last_folder=str(folder), last_files=[])
        return f'In {folder} (up to 100 items):\n' + '\n'.join(('[folder] ' if p.is_dir() else '')+p.name for p in items[:100])
    paths = sources(command['target'], context)
    if len(paths)!=1: raise ValueError('Name one item to open or inspect.')
    path = paths[0]
    if not path.exists(): raise ValueError('That item no longer exists.')
    if action == 'file_properties':
        stat = path.stat()
        from datetime import datetime
        size = 'Contents size not calculated' if path.is_dir() else f'{stat.st_size:,} bytes'
        return f'{path}\nType: {"folder" if path.is_dir() else "file"}. Size: {size}. Modified: {datetime.fromtimestamp(stat.st_mtime):%Y-%m-%d %H:%M}.'
    if not path.is_dir() and path.suffix.lower() in EXECUTABLE:
        raise ValueError('Launching scripts, installers and shortcuts through file commands is excluded. Use a named Start-menu app.')
    os.startfile(str(path))
    context.update(last_folder=str(path if path.is_dir() else path.parent), last_files=[str(path)])
    return f'Asked Windows to open {path.name}. I have not verified the app or folder view.'
