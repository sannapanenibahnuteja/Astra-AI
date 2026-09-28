"""Bounded Windows automation using visible windows and accessibility controls."""
import json
import re
import time
from contextlib import contextmanager

ACTIONS = {'brightness', 'brightness_up', 'brightness_down', 'list_windows', 'focus_window',
           'minimize_window', 'maximize_window', 'restore_window', 'close_window',
           'inspect_window', 'click_control', 'type_text', 'press_key'}
CONFIRM = {'close_window', 'click_control'}
KEYS = {'enter':'{ENTER}', 'tab':'{TAB}', 'escape':'{ESC}', 'backspace':'{BACKSPACE}',
        'up':'{UP}', 'down':'{DOWN}', 'left':'{LEFT}', 'right':'{RIGHT}',
        'page up':'{PGUP}', 'page down':'{PGDN}', 'home':'{HOME}', 'end':'{END}',
        'ctrl+a':'^a', 'ctrl+c':'^c', 'ctrl+v':'^v', 'ctrl+z':'^z', 'ctrl+s':'^s',
        'ctrl+f':'^f', 'ctrl+l':'^l', 'ctrl+t':'^t', 'ctrl+w':'^w', 'ctrl+tab':'^{TAB}',
        'shift+tab':'+{TAB}', 'alt+left':'%{LEFT}', 'alt+right':'%{RIGHT}', 'f5':'{F5}'}

@contextmanager
def com_thread():
    import pythoncom
    pythoncom.CoInitialize()
    try: yield
    finally: pythoncom.CoUninitialize()


def validate(action, target, window=''):
    if action not in ACTIONS or not isinstance(target, str) or len(target)>4000:
        raise ValueError('Invalid Windows action.')
    if not isinstance(window, str) or len(window)>250:
        raise ValueError('Choose a window by its title or application name.')
    if action=='brightness' and (not target.isdigit() or not 0<=int(target)<=100):
        raise ValueError('Brightness must be between 0 and 100 percent.')
    if action=='press_key':
        target=target.lower().replace('control','ctrl').strip()
        if target not in KEYS:
            target=re.sub(r'\s+(?:plus\s+|and\s+)?', '+', target)
        if target not in KEYS:
            raise ValueError('That keyboard shortcut is not supported.')
    if action in {'type_text','click_control'} and not target.strip():
        raise ValueError('Specify the text or visible control label.')
    if action in {'brightness','brightness_up','brightness_down','list_windows'}:
        window = ''
    confirm = action in CONFIRM or (action=='press_key' and target in {'enter','ctrl+s','ctrl+v','ctrl+w'}) or (action=='type_text' and '\n' in target)
    return {'action':action, 'target':target, 'window':window, 'confirm':confirm}


def window_inventory():
    import win32gui
    import win32process
    import psutil
    items=[]
    def visit(handle, _):
        if win32gui.IsWindowVisible(handle):
            title=win32gui.GetWindowText(handle)
            if title and title not in ('Program Manager',):
                try: name=psutil.Process(win32process.GetWindowThreadProcessId(handle)[1]).name()
                except (psutil.Error, OSError): name=''
                items.append({'handle':handle,'title':title,'process':name})
    win32gui.EnumWindows(visit,None)
    return items


def find_window(query, timeout=5):
    query=query.lower().strip()
    if not query: raise ValueError('Name the application or window first, for example “switch to Notepad”.')
    deadline=time.monotonic()+timeout
    while True:
        items=window_inventory()
        exact=[w for w in items if w['title'].lower()==query]
        matches=exact or [w for w in items if query in w['title'].lower() or query==w['process'].lower().removesuffix('.exe')]
        if len(matches)==1:return matches[0]
        if len(matches)>1:raise ValueError('Several windows match. Use the exact title: '+ '; '.join(w['title'] for w in matches[:6]))
        if time.monotonic()>=deadline:raise ValueError(f'No visible window matches {query}. Open it first or say “list windows”.')
        time.sleep(.15)


def execute(action, target, window='', cancel=None):
    command=validate(action,target,window)
    target=command['target']
    if cancel and cancel.is_set():raise RuntimeError('Task stopped.')
    if action.startswith('brightness'):
        with com_thread():
            import screen_brightness_control as sbc
            try:
                current=sbc.get_brightness()
                if not current:raise RuntimeError('No supported display found.')
                for index, old in enumerate(current):
                    level=int(target) if action=='brightness' else max(0,min(100,old+(10 if action=='brightness_up' else -10)))
                    sbc.set_brightness(level,display=index)
                actual=sbc.get_brightness()
                return 'Display brightness: '+', '.join(f'{v}%' for v in actual)+'.'
            except Exception as exc:
                raise RuntimeError('Windows could not control this display’s brightness. External monitors may need DDC/CI enabled. '+str(exc)[:180]) from exc
    if action=='list_windows':
        return 'Open windows:\n'+'\n'.join('- '+w['title'] for w in window_inventory()[:40])
    item=find_window(window or (target if action.endswith('_window') else ''))
    import win32gui
    import win32con
    handle=item['handle']
    if action in {'minimize_window','maximize_window','restore_window'}:
        code={'minimize_window':win32con.SW_MINIMIZE,'maximize_window':win32con.SW_MAXIMIZE,'restore_window':win32con.SW_RESTORE}[action]
        win32gui.ShowWindow(handle,code)
        state=win32gui.GetWindowPlacement(handle)[1]
        if action=='maximize_window' and state!=win32con.SW_SHOWMAXIMIZED:raise RuntimeError('This window did not maximize.')
        if action=='minimize_window' and not win32gui.IsIconic(handle):raise RuntimeError('This window did not minimize.')
        return f"{action.split('_')[0].capitalize()}d {item['title']}."
    if action=='close_window':
        win32gui.PostMessage(handle,win32con.WM_CLOSE,0,0)
        return 'Requested closure of '+item['title']+'. Any save dialog remains for your choice.'
    with com_thread():
        from pywinauto import Desktop
        wrapper=Desktop(backend='uia').window(handle=handle).wrapper_object()
        if action=='inspect_window':
            controls=[]
            for node in wrapper.descendants(depth=5)[:400]:
                info=node.element_info
                if node.is_visible() and node.is_enabled() and info.name and not getattr(info,'is_password',False):
                    controls.append({'name':info.name[:150],'type':info.control_type})
                if len(controls)>=60:break
            return json.dumps({'window':item['title'],'controls':controls},ensure_ascii=False)
        if action=='focus_window':
            if win32gui.IsIconic(handle):wrapper.restore()
            wrapper.set_focus()
            if win32gui.GetForegroundWindow()!=handle:raise RuntimeError('Windows prevented Bob from switching focus.')
            return 'Switched to '+item['title']+'.'
        if item['process'].lower() in {'cmd.exe','powershell.exe','pwsh.exe','windowsterminal.exe','regedit.exe'}:
            raise ValueError('Text and control automation is not available for shells or Registry Editor.')
        wrapper.set_focus()
        if win32gui.GetForegroundWindow()!=handle:raise RuntimeError('The target window is not focused. No input was sent.')
        if action=='click_control':
            matches=[node for node in wrapper.descendants(depth=5)[:400] if node.is_visible() and node.is_enabled() and node.element_info.name.casefold()==target.casefold()]
            if len(matches)!=1:raise ValueError('The control label is missing or ambiguous. Say “inspect window” with its title to see current controls.')
            node=matches[0]
            if getattr(node.element_info,'is_password',False):raise ValueError('Password controls are excluded.')
            if hasattr(node,'invoke'):node.invoke()
            elif hasattr(node,'select'):node.select()
            else:raise ValueError('This control does not expose an accessible invoke/select action.')
            return f'Activated “{target}” in {item["title"]}.'
        from pywinauto.keyboard import send_keys
        if action=='press_key':
            send_keys(KEYS[target.lower()],pause=.03)
            return f'Sent {target} to {item["title"]}.'
        if action=='type_text':
            from pywinauto.uia_defines import IUIA
            focused=IUIA().iuia.GetFocusedElement()
            if focused.CurrentIsPassword or focused.CurrentControlType not in (50004,50030):
                raise ValueError('Focus an editable text field in the target application before dictating text.')
            # Literal characters only: spoken text can never become send_keys syntax.
            escaped=''.join({'{':'{{}', '}':'{}}', '+':'{+}', '^':'{^}', '%':'{%}', '~':'{~}', '(':'{(}', ')':'{)}'}.get(c,c) for c in target)
            send_keys(escaped,with_spaces=True,with_newlines=True,pause=.005,vk_packet=True)
            return f'Typed the requested text into {item["title"]}.'
    raise ValueError('Unsupported Windows action.')
