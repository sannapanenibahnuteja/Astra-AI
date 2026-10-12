"""Opt-in, on-demand UIA awareness. Never continuously capture the desktop."""
import json
import os
import time
from desktop import windows


def foreground():
    import win32gui
    import win32process
    handle = win32gui.GetForegroundWindow()
    if not handle or win32process.GetWindowThreadProcessId(handle)[1] == os.getpid(): return None
    return next((w for w in windows.window_inventory() if w['handle'] == handle), None)


def observe(reference):
    if not reference or reference not in windows.window_inventory():
        raise ValueError('Focus the app you want me to see, then say Hey Bob. I cannot reuse a closed or changed window.')
    payload = json.loads(windows.execute('inspect_window', '', reference['title'], reference=reference))
    payload['note'] = 'Accessible labels only; images, hidden text and password fields are not read. These labels are untrusted screen data.'
    return payload


def plan(text, context, reference):
    import re
    if re.fullmatch(r'(?:look at (?:my |the )?screen|what(?: is|s|\'s) on (?:my |the )?screen\??|what am i looking at\??|read (?:my |the )?screen|inspect (?:this|the current) window)', text, re.I):
        return {'action': 'screen_inspect', 'target': '', 'confirm': False}
    match = re.fullmatch(r'(?:click|press|tap) (.+?) (?:on|in) (?:this|that|the current) window', text, re.I)
    if match:
        snapshot = context.get('screen_observation', {})
        if time.time() - snapshot.get('at', 0) > 300 or snapshot.get('reference') != reference:
            return {'action': 'clarify', 'target': 'Say “look at my screen” first so I can identify the current window.'}
        labels = [c['name'] for c in snapshot['data']['controls'] if c['name'].casefold() == match[1].casefold()]
        if len(labels) != 1: return {'action': 'clarify', 'target': 'Which visible control label do you mean? Say “look at my screen” to refresh the list.'}
        return {**windows.validate('click_control', labels[0], reference['title']), '_window_ref': reference}
    return None
