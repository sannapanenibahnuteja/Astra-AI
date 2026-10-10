"""Bounded Windows automation using visible windows and accessibility controls."""
import json
import re
import time
from contextlib import contextmanager

ACTIONS = {'brightness', 'brightness_up', 'brightness_down', 'list_windows', 'focus_window',
           'minimize_window', 'maximize_window', 'restore_window', 'close_window',
           'inspect_window', 'click_control', 'type_text', 'press_key', 'move_window', 'list_monitors'}
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


def accessible_descendants(wrapper, **criteria):
    """Handle UIA's detached-parent depth-filter race on changing browser trees."""
    try:
        return wrapper.descendants(**criteria)
    except AttributeError as error:
        if 'has_depth' not in str(error) or 'depth' not in criteria:
            raise
        # A disappearing ancestor breaks pywinauto's Python depth filter.
        # Fresh native UIA enumeration does not require traversing that parent.
        criteria = {key:value for key,value in criteria.items() if key != 'depth'}
        return wrapper.descendants(**criteria)


def validate(action, target, window=''):
    if action not in ACTIONS or not isinstance(target, str) or len(target)>4000:
        raise ValueError('Invalid Windows action.')
    if not isinstance(window, str) or len(window)>250:
        raise ValueError('Choose a window by its title or application name.')
    if action=='brightness' and (not target.isdigit() or not 0<=int(target)<=100):
        raise ValueError('Brightness must be between 0 and 100 percent.')
    if action=='move_window' and (not target.isdigit() or not 1<=int(target)<=16):
        raise ValueError('Choose a monitor number from “list monitors”.')
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


def monitor_inventory():
    import win32api
    items=[win32api.GetMonitorInfo(handle) for handle,_,_ in win32api.EnumDisplayMonitors()]
    items.sort(key=lambda m:(not bool(m['Flags'] & 1),m['Monitor'][0],m['Monitor'][1]))
    return items


def destination_rect(rect, work):
    left,top,right,bottom=work
    width=min(rect[2]-rect[0],right-left);height=min(rect[3]-rect[1],bottom-top)
    return left+(right-left-width)//2,top+(bottom-top-height)//2,width,height


class AmbiguousWindows(ValueError):
    def __init__(self, matches):
        self.matches=matches[:12]
        super().__init__('Several windows match. '+ '; '.join(f"{i}. {w['title']}" for i,w in enumerate(self.matches,1))+'. Say “close all those” or name one window. Closing a browser window closes its tabs too.')


def find_window(query, timeout=5):
    query=query.lower().strip()
    if not query: raise ValueError('Name the application or window first, for example “switch to Notepad”.')
    deadline=time.monotonic()+timeout
    while True:
        items=window_inventory()
        exact=[w for w in items if w['title'].lower()==query]
        matches=exact or [w for w in items if query in w['title'].lower() or query==w['process'].lower().removesuffix('.exe')]
        if len(matches)==1:return matches[0]
        if len(matches)>1:raise AmbiguousWindows(matches)
        if time.monotonic()>=deadline:raise ValueError(f'No visible window matches {query}. Open it first or say “list windows”.')
        time.sleep(.15)


def execute(action, target, window='', cancel=None, reference=None):
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
    if action=='list_monitors':
        return '\n'.join(f"Monitor {i}: {m['Device']}"+(' (primary)' if m['Flags'] & 1 else '')+f" — {m['Monitor']}" for i,m in enumerate(monitor_inventory(),1))
    if reference:
        if reference not in window_inventory(): raise ValueError('The selected window changed or closed. Refresh the window list.')
        item=reference
    else:
        item=find_window(window or (target if action.endswith('_window') else ''))
    import win32gui
    import win32con
    handle=item['handle']
    if action=='move_window':
        monitors=monitor_inventory();index=int(target)-1
        if index>=len(monitors): raise ValueError('That monitor is not connected. Say “list monitors”.')
        maximized=win32gui.GetWindowPlacement(handle)[1]==win32con.SW_SHOWMAXIMIZED
        win32gui.ShowWindow(handle,win32con.SW_RESTORE)
        x,y,width,height=destination_rect(win32gui.GetWindowRect(handle),monitors[index]['Work'])
        win32gui.SetWindowPos(handle,0,x,y,width,height,win32con.SWP_NOZORDER|win32con.SWP_NOACTIVATE)
        if maximized: win32gui.ShowWindow(handle,win32con.SW_MAXIMIZE)
        import win32api
        actual=win32api.GetMonitorInfo(win32api.MonitorFromWindow(handle,2))
        if actual['Device']!=monitors[index]['Device']: raise RuntimeError('Windows did not move the window to the requested monitor.')
        return f"Moved {item['title']} to monitor {target}."
    if action in {'minimize_window','maximize_window','restore_window'}:
        code={'minimize_window':win32con.SW_MINIMIZE,'maximize_window':win32con.SW_MAXIMIZE,'restore_window':win32con.SW_RESTORE}[action]
        win32gui.ShowWindow(handle,code)
        state=win32gui.GetWindowPlacement(handle)[1]
        if action=='maximize_window' and state!=win32con.SW_SHOWMAXIMIZED:raise RuntimeError('This window did not maximize.')
        if action=='minimize_window' and not win32gui.IsIconic(handle):raise RuntimeError('This window did not minimize.')
        return f"{action.split('_')[0].capitalize()}d {item['title']}."
    if action=='close_window':
        win32gui.PostMessage(handle,win32con.WM_CLOSE,0,0)
        for _ in range(20):
            if not win32gui.IsWindow(handle): return 'Closed '+item['title']+'.'
            time.sleep(.1)
        raise RuntimeError('The window is still open. Check for a save dialog or a blocked close request; I have not forced it closed.')
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
            if item['process'].lower()=='notepad.exe':
                editors=[n for n in wrapper.descendants(depth=12) if n.is_visible() and n.is_enabled()
                         and n.element_info.control_type in ('Edit','Document')
                         and not getattr(n.element_info,'is_password',False)
                         and not re.search(r'find|replace|search',n.element_info.name,re.I)]
                if len(editors)!=1: raise ValueError('Open one document in Notepad and close its Find/Replace panel before dictating.')
                editors[0].set_focus()
            focused=IUIA().iuia.GetFocusedElement()
            if focused.CurrentIsPassword or focused.CurrentControlType not in (50004,50030):
                raise ValueError('Focus an editable text field in the target application before dictating text.')
            # Paste once: rapid VK_PACKET input is unreliable in modern Notepad.
            # OLE preserves all clipboard formats, including images and file lists.
            from pywinauto.controls.uiawrapper import UIAWrapper
            from pywinauto.uia_element_info import UIAElementInfo
            editor=UIAWrapper(UIAElementInfo(focused))
            try:
                read=lambda: editor.iface_text.DocumentRange.GetText(-1)
                before=read()
            except Exception:
                try:
                    read=lambda: editor.iface_value.CurrentValue
                    before=read()
                except Exception:
                    raise ValueError('This editor does not expose readable text; no text was inserted.')
            from desktop.clipboard import temporary_text
            with temporary_text(target):
                if win32gui.GetForegroundWindow()!=handle:
                    raise RuntimeError('Focus changed; no text was inserted.')
                send_keys('^v',pause=.05)
                deadline=time.monotonic()+3
                while time.monotonic()<deadline:
                    after=read()
                    if after!=before and target.replace('\r\n','\n') in after.replace('\r\n','\n'): break
                    time.sleep(.05)
                else:
                    raise RuntimeError('Could not verify the pasted text. Check the editor before retrying.')
            return f'Typed the requested text into {item["title"]}.'
    raise ValueError('Unsupported Windows action.')
