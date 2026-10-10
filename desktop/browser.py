"""Edge navigation through native accessibility; no browser debugging/profile access."""
import json
import re
import time
from difflib import SequenceMatcher
from urllib.parse import quote_plus, urlparse
from desktop import windows

SHORTCUTS = {'back':'%{LEFT}', 'forward':'%{RIGHT}', 'reload':'{F5}',
             'new tab':'^t', 'close tab':'^w', 'reopen tab':'^+t',
             'next tab':'^{TAB}', 'previous tab':'^+{TAB}',
             'downloads':'^j', 'history':'^h', 'favorites':'^+o',
             'zoom in':'^{+}', 'zoom out':'^-', 'reset zoom':'^0',
             'scroll down':'{PGDN}', 'scroll up':'{PGUP}',
             'top':'^{HOME}', 'bottom':'^{END}', 'escape':'{ESC}'}
ACTIONS = {'edge_shortcut', 'edge_navigate', 'edge_search', 'edge_find',
           'edge_inspect', 'edge_tabs', 'edge_select_tab', 'edge_close_tab', 'edge_close_tabs', 'edge_click', 'edge_fill'}


def parse(text, context=None):
    text = text.strip()
    explicit = bool(re.search(r'^(?:(?:in|on) )?(?:microsoft )?(?:edge|(?:the )?browser)\b| (?:in|on|using) (?:microsoft )?(?:edge|the browser)$', text, re.I))
    scoped = explicit or (context or {}).get('last_window', '').casefold() in ('microsoft edge', 'edge', 'msedge')
    clean = re.sub(r'^(?:in|on) (?:microsoft )?(?:edge|the browser)[, ]+', '', text, flags=re.I)
    clean = re.sub(r' (?:in|on|using) (?:microsoft )?(?:edge|the browser)$', '', clean, flags=re.I)
    clean = re.sub(r'^(?:microsoft )?(?:edge|browser)[, ]+', '', clean, flags=re.I)
    aliases = {
        'back': ['go back', 'go back a page', 'take me back', 'take me to the previous page', 'previous page', 'back'],
        'forward': ['go forward', 'next page', 'forward'],
        'reload': ['refresh', 'refresh the page', 'reload', 'reload this page', 'refresh this page', 'try loading this again', 'refresh this'],
        'new tab': ['open a new tab', 'new tab', 'add a tab', 'open another tab', 'give me a fresh tab'],
        'close tab': ['close this tab', 'close the tab', 'close current tab'],
        'reopen tab': ['restore the last tab', 'reopen the closed tab', 'bring back the last tab', 'undo close tab'],
        'next tab': ['next tab', 'switch to the next tab', 'go to the next tab'],
        'previous tab': ['previous tab', 'switch to the previous tab', 'go to the previous tab'],
        'downloads': ['show downloads', 'open downloads'], 'history':['show history', 'open history'],
        'favorites':['show favorites', 'open bookmarks', 'open favorites'],
        'zoom in':['zoom in', 'make the page bigger', 'this is too small', 'make this easier to read'], 'zoom out':['zoom out', 'make the page smaller', 'this is too big'],
        'reset zoom':['reset zoom', 'normal zoom'], 'scroll down':['scroll down', 'page down'],
        'scroll up':['scroll up', 'page up'], 'top':['go to the top', 'top of the page'],
        'bottom':['go to the bottom', 'bottom of the page']}
    if not scoped: return None
    for key, phrases in aliases.items():
        if clean.casefold() in phrases: return {'action':'edge_shortcut', 'target':key}
    if re.fullmatch(r'(?:list|show|read)(?: my| the| all)?(?: open)? tabs', clean, re.I):
        return {'action':'edge_tabs', 'target':''}
    if re.fullmatch(r'(?:inspect|read|describe|show)(?: me)?(?: this| the| current)? page', clean, re.I):
        return {'action':'edge_inspect', 'target':''}
    for action, pattern in [
        ('edge_select_tab', r'(?:switch to|select|open) (?:the )?(.+?) tab'),
        ('edge_navigate', r'(?:go to|navigate to|visit|open) (\S+\.\S+)'),
        ('edge_search', r'(?:search(?: the web)?(?: for)?|look up|google) (.+)'),
        ('edge_find', r'(?:find|look for) (.+?)(?: on (?:this|the) page)?'),
        ('edge_click', r'(?:click|activate|choose) (.+)')]:
        match = re.fullmatch(pattern, clean, re.I)
        if match: return {'action':action, 'target':match[1]}
    match = re.fullmatch(r'(?:fill|type) (.+) (?:into|in) (?:the )?(.+?)(?: field)?', clean, re.I)
    if match: return {'action':'edge_fill', 'target':match[2], 'value':match[1]}
    return None


def validate(command):
    action = command.get('action'); target = command.get('target', ''); value = command.get('value', '')
    if action not in ACTIONS or any(not isinstance(v, str) or len(v)>4000 for v in (target, value, command.get('window',''))):
        raise ValueError('Invalid Edge command.')
    if action == 'edge_shortcut' and target not in SHORTCUTS: raise ValueError('Unknown Edge shortcut.')
    if action == 'edge_navigate':
        if re.match(r'^[a-z][a-z0-9+.-]*:', target, re.I) and not re.match(r'^https?://', target, re.I):
            raise ValueError('Only HTTP and HTTPS web addresses are supported.')
        if not re.match(r'^https?://', target, re.I): target = 'https://' + target
        url = urlparse(target)
        if url.scheme not in ('http','https') or not url.hostname or url.username or url.password or re.search(r'[\s\x00-\x1f]',target) or ':' in url.hostname:
            raise ValueError('Use a web address without credentials or executable schemes.')
        if '://' in url.path: raise ValueError('Invalid web address.')
    if action not in {'edge_tabs','edge_inspect'} and not target.strip(): raise ValueError('Specify the Edge target.')
    if action == 'edge_fill' and (not value or '\n' in value or '\r' in value): raise ValueError('Provide single-line text to fill.')
    return {'action':action, 'target':target, 'value':value, 'window':command.get('window',''),
            'confirm':action in {'edge_click','edge_close_tab','edge_close_tabs'} or (action == 'edge_shortcut' and target == 'close tab')}


def close_named_tab(label, preferred=None):
    matches = []
    with windows.com_thread():
        import win32gui
        from pywinauto import Desktop
        from pywinauto.keyboard import send_keys
        for item in windows.window_inventory():
            if item['process'].casefold() != 'msedge.exe': continue
            try:
                wrapper = Desktop(backend='uia').window(handle=item['handle']).wrapper_object()
                for tab in windows.accessible_descendants(wrapper, control_type='TabItem', depth=15):
                    name = re.split(r' - memory usage', tab.element_info.name, flags=re.I)[0]
                    if tab.is_visible() and re.search(r'\b'+re.escape(label)+r'\b',name,re.I):
                        matches.append((item, wrapper, tab, name))
            except Exception:
                continue
        # Prefer the window Bob just opened, but never guess between its tabs.
        selected = [m for m in matches if m[0]['handle'] == preferred]
        if selected: matches = selected
        if not matches: raise ValueError('No visible Edge tab matches '+label+'. Ask me to list tabs first.')
        if len(matches)!=1: raise ValueError('Several tabs match '+label+'. Use the exact tab title: '+ '; '.join(m[3] for m in matches[:5]))
        item, wrapper, tab, name = matches[0]
        if win32gui.IsIconic(item['handle']): wrapper.restore()
        wrapper.set_focus()
        if win32gui.GetForegroundWindow()!=item['handle']: raise RuntimeError('Edge did not receive focus. No tab was closed.')
        tab.select()
        if not tab.is_selected(): raise RuntimeError('The requested tab was not selected. No tab was closed.')
        send_keys('^w')
        for _ in range(15):
            if not win32gui.IsWindow(item['handle']): return 'Closed '+name+'.'
            names = [re.split(r' - memory usage',n.element_info.name,flags=re.I)[0] for n in windows.accessible_descendants(wrapper, control_type='TabItem',depth=15)]
            if name not in names: return 'Closed '+name+'.'
            time.sleep(.1)
        raise RuntimeError('The tab is still visible. I could not verify that it closed.')


def select_window(query='', preferred=None):
    items = [w for w in windows.window_inventory() if w['process'].casefold() == 'msedge.exe']
    if query and query.casefold() not in ('edge','microsoft edge','browser'):
        items = [w for w in items if query.casefold() == w['title'].casefold()]
    elif preferred:
        selected = [w for w in items if w['handle'] == preferred]
        if selected: return selected[0]
    if len(items) != 1:
        raise ValueError('Open Edge first.' if not items else 'Several Edge windows are open. Focus the one you want before waking Bob, or give its exact title.')
    return items[0]


def match_control(nodes, label, fuzzy=False):
    def name(node):
        text = node.element_info.name.casefold()
        if getattr(node.element_info, 'control_type', '') == 'TabItem':
            text = re.split(r' - memory usage', text)[0]
        return text
    exact = [n for n in nodes if name(n) == label.casefold()]
    if len(exact) == 1: return exact[0]
    if not exact and fuzzy:
        scores = sorted([(SequenceMatcher(None,label.casefold(),name(n)).ratio(),i,n) for i,n in enumerate(nodes)], reverse=True)
        if scores and scores[0][0]>=.86 and (len(scores)==1 or scores[0][0]-scores[1][0]>=.12): return scores[0][2]
    raise ValueError('That label is missing or ambiguous. Ask Bob to read the page or list tabs first, then use a displayed label.')


def literal(text):
    return ''.join({'{':'{{}', '}':'{}}', '+':'{+}', '^':'{^}', '%':'{%}', '~':'{~}', '(':'{(}', ')':'{)}'}.get(c,c) for c in text)


def execute(command, context, preferred=None, cancel=None):
    bound=command.get('tabs')
    command = validate(command)
    action, target = command['action'], command['target']
    if action in ('edge_close_tab','edge_close_tabs'):
        from desktop import tab_tasks
        if bound is None: command=tab_tasks.prepare(command,context,preferred)
        else: command['tabs']=bound
        result=tab_tasks.execute(command,cancel)
        reference=context.get('tab_reference',{})
        closed={(row['handle'],tuple(row['id'])) for row in command['tabs']}
        remaining=[row for row in reference.get('tabs',[]) if (row['handle'],tuple(row['id'])) not in closed]
        if remaining and not (cancel and cancel.is_set()): reference['tabs']=remaining
        else:
            context.pop('tab_reference',None)
            context.pop('last_reference',None)
        context.pop('last_opened_browser',None)
        return result
    item = select_window(command['window'], preferred or context.get('edge_handle'))
    with windows.com_thread():
        import win32gui
        from pywinauto import Desktop
        from pywinauto.keyboard import send_keys
        wrapper = Desktop(backend='uia').window(handle=item['handle']).wrapper_object()
        nodes = None
        def controls():
            nonlocal nodes
            if nodes is None:
                nodes = [n for n in windows.accessible_descendants(wrapper, depth=20)[:1500] if n.is_visible() and not getattr(n.element_info,'is_password',False)]
            return nodes
        if action in {'edge_inspect','edge_tabs'}:
            rows = [{'name':n.element_info.name[:250], 'type':n.element_info.control_type} for n in controls()
                    if n.element_info.name and (action != 'edge_tabs' or n.element_info.control_type == 'TabItem')][:100]
            if action == 'edge_tabs':
                from desktop import tab_tasks
                selected = [row for row in tab_tasks.inventory() if row['handle'] == item['handle']]
                context.update(last_window='Microsoft Edge', last_reference='tabs', tab_reference={'query':'*','tabs':selected,'time':time.time()})
            result = json.dumps({'window':item['title'],'controls':rows,'limited':True}, ensure_ascii=False)
        else:
            if win32gui.IsIconic(item['handle']): wrapper.restore()
            wrapper.set_focus()
            for _ in range(5):
                if win32gui.GetForegroundWindow() == item['handle']: break
                time.sleep(.1)
            if win32gui.GetForegroundWindow() != item['handle']: raise RuntimeError('Edge did not receive focus; no input was sent.')
            if action in {'edge_click','edge_select_tab','edge_fill'}:
                kinds = {'edge_select_tab':{'TabItem'}, 'edge_fill':{'Edit'}, 'edge_click':{'Button','Hyperlink','MenuItem','CheckBox','RadioButton'}}[action]
                node = match_control([n for n in controls() if n.is_enabled() and n.element_info.control_type in kinds], target, fuzzy=action=='edge_select_tab')
                if action == 'edge_fill':
                    node.iface_value.SetValue(command['value'])
                    for _ in range(10):
                        if node.iface_value.CurrentValue == command['value']: break
                        time.sleep(.1)
                    if node.iface_value.CurrentValue != command['value']: raise RuntimeError('Edge did not retain the requested field text.')
                    result = 'Filled '+node.element_info.name+'. The form has not been submitted.'
                elif action == 'edge_select_tab':
                    node.select()
                    for _ in range(10):
                        if node.is_selected(): break
                        time.sleep(.1)
                    if not node.is_selected(): raise RuntimeError('Edge did not select the tab.')
                    result = 'Switched to '+node.element_info.name+'.'
                else:
                    if node.element_info.control_type == 'CheckBox':
                        node.iface_toggle.Toggle()
                    elif node.element_info.control_type == 'RadioButton':
                        node.select()
                    else:
                        node.iface_invoke.Invoke()
                    result = 'Activated '+node.element_info.name+'. Read the page to check the result.'
            elif action == 'edge_shortcut':
                send_keys(SHORTCUTS[target], pause=.015)
                wording = {'new tab':'open a fresh tab', 'back':'take you back', 'forward':'take you forward',
                           'reload':'refresh the page', 'next tab':'switch to the next tab',
                           'previous tab':'switch to the previous tab', 'reopen tab':'bring back the closed tab'}
                result = "I've asked Edge to " + wording.get(target,target) + '.'
            elif action in {'edge_navigate','edge_search'}:
                address = target if action == 'edge_navigate' else 'https://www.bing.com/search?q='+quote_plus(target)
                send_keys('^l', pause=.015)
                from pywinauto.uia_defines import IUIA
                focused = IUIA().iuia.GetFocusedElement()
                if focused.CurrentControlType != 50004 or focused.CurrentIsPassword:
                    raise RuntimeError('The Edge address bar is not ready. No address was typed.')
                send_keys(literal(address), with_spaces=True, pause=.001, vk_packet=True)
                send_keys('{ENTER}')
                result = 'Requested '+('navigation to '+target if action=='edge_navigate' else 'an Edge search for '+target)+'.'
            else:
                send_keys('^f', pause=.015)
                send_keys(literal(target), with_spaces=True, pause=.001, vk_packet=True)
                result = 'Opened Find in Edge for '+target+'.'
        context['last_window'] = 'Microsoft Edge'
        context['edge_handle'] = item['handle']
        return result
