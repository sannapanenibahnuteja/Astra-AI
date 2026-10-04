"""Launch website requests explicitly in Edge; report only observable results."""
import os
from pathlib import Path
import subprocess
import time
from urllib.parse import urlparse
from desktop import windows


def edge_path():
    # Match an already running Edge variant/profile rather than a stale shortcut.
    import psutil
    import win32gui
    import win32process
    foreground = win32gui.GetForegroundWindow()
    items = sorted(windows.window_inventory(), key=lambda w: w['handle'] != foreground)
    for item in items:
        if item['process'].casefold() == 'msedge.exe':
            try:
                executable = Path(psutil.Process(win32process.GetWindowThreadProcessId(item['handle'])[1]).exe())
                if executable.is_file(): return str(executable)
            except (psutil.Error, OSError):
                pass
    for base in ('ProgramFiles(x86)', 'ProgramFiles', 'LOCALAPPDATA'):
        for variant in ('Edge', 'Edge Beta', 'Edge Dev'):
            executable = Path(os.environ.get(base, '')) / 'Microsoft' / variant / 'Application/msedge.exe'
            if executable.is_file(): return str(executable)
    return None


def visible_address(url, exclude=None):
    from pywinauto import Desktop
    requested = urlparse(url)
    def host(value): return (value or '').casefold().removeprefix('www.')
    with windows.com_thread():
        for item in windows.window_inventory():
            if item['process'].casefold() != 'msedge.exe': continue
            if item['handle'] in (exclude or set()): continue
            try:
                wrapper = Desktop(backend='uia').window(handle=item['handle']).wrapper_object()
                for control in wrapper.descendants(control_type='Edit', depth=12)[:12]:
                    if not control.is_visible() or getattr(control.element_info, 'is_password', False): continue
                    value = control.iface_value.CurrentValue
                    observed = urlparse(value if '://' in value else 'https://' + value)
                    if host(observed.hostname) == host(requested.hostname) and (not requested.path.strip('/') or observed.path.rstrip('/') == requested.path.rstrip('/')):
                        return item['handle']
            except Exception:
                continue
    return None


def open_website(url):
    executable = edge_path()
    label = urlparse(url).hostname or 'the website'
    if not executable:
        os.startfile(url)
        return 'Asked Windows to open ' + label + '. I cannot confirm the page opened.', None
    previous = {w['handle'] for w in windows.window_inventory()}
    process = subprocess.Popen([executable, '--new-window', url])
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        handle = visible_address(url, exclude=previous)
        if handle:
            return 'Opened ' + label + ' in Edge; its address is visible.', handle
        if process.poll() not in (None, 0):
            raise RuntimeError('Edge could not open the requested website.')
        time.sleep(.2)
    return 'Asked Edge to open ' + label + ', but I could not verify the page address.', None
