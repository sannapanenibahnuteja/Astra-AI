"""Bounded installed-executable discovery; never executes a registry command line."""
import os
import re
import time
from pathlib import Path

_registry_cache=None
_scan_cache=None

EXCLUDE=re.compile(r'uninstall|unins\d*|setup|installer|updat(?:e|er)|crash|helper|repair|service|redist',re.I)

def executable(raw):
    value=os.path.expandvars(str(raw).strip())
    match=re.match(r'^"([^"\r\n]+\.exe)"(?:,.*)?$',value,re.I)
    if match:value=match[1]
    else:
        value=re.sub(r',-?\d+$','',value)
        if not value.lower().endswith('.exe'):return None
    path=Path(value)
    return path if path.is_absolute() and path.is_file() and path.suffix.lower()=='.exe' else None

def registry_apps():
    global _registry_cache
    if _registry_cache and time.monotonic()-_registry_cache[0]<60:return dict(_registry_cache[1])
    apps={}
    try:import winreg
    except ImportError:return apps
    for hive in (winreg.HKEY_CURRENT_USER,winreg.HKEY_LOCAL_MACHINE):
        for view in (winreg.KEY_WOW64_64KEY,winreg.KEY_WOW64_32KEY):
            for branch in ('App Paths','Uninstall'):
                name='Software\\Microsoft\\Windows\\CurrentVersion\\'+branch
                try:root=winreg.OpenKey(hive,name,0,winreg.KEY_READ|view)
                except OSError:continue
                with root:
                    for index in range(min(4096,winreg.QueryInfoKey(root)[0])):
                        try:
                            subname=winreg.EnumKey(root,index)
                            with winreg.OpenKey(root,subname) as sub:
                                raw=winreg.QueryValueEx(sub,'' if branch=='App Paths' else 'DisplayIcon')[0]
                                path=executable(raw)
                                if not path or EXCLUDE.search(path.stem):continue
                                label=path.stem
                                if branch=='Uninstall':
                                    try:label=winreg.QueryValueEx(sub,'DisplayName')[0]
                                    except OSError:pass
                                if not EXCLUDE.search(label):apps.setdefault(str(label).lower(),('exe',str(path)))
                                apps.setdefault(path.stem.lower(),('exe',str(path)))
                        except OSError:continue
    _registry_cache=(time.monotonic(),dict(apps))
    return apps

def scan_programs(roots=None,budget=2.0):
    global _scan_cache
    cached=roots is None
    if cached and _scan_cache and time.monotonic()-_scan_cache[0]<300:return dict(_scan_cache[1])
    roots=roots if roots is not None else [os.environ.get('ProgramFiles'),os.environ.get('ProgramFiles(x86)'),str(Path(os.environ.get('LOCALAPPDATA',''))/'Programs')]
    deadline=time.monotonic()+budget;apps={};count=0
    for raw in roots:
        if not raw:continue
        root=Path(raw)
        if not root.is_dir():continue
        for folder,dirs,files in os.walk(root,followlinks=False):
            if time.monotonic()>deadline or count>20000:
                if cached:_scan_cache=(time.monotonic(),dict(apps))
                return apps
            relative=Path(folder).relative_to(root)
            dirs[:]=[name for name in dirs if not EXCLUDE.search(name) and not Path(folder,name).is_symlink()] if len(relative.parts)<3 else []
            for name in files:
                count+=1
                if name.lower().endswith('.exe') and not EXCLUDE.search(name):
                    path=Path(folder,name)
                    apps.setdefault(path.stem.lower(),('exe',str(path)))
    if cached:_scan_cache=(time.monotonic(),dict(apps))
    return apps
