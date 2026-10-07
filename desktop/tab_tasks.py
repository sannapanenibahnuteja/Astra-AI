"""Freeze a scoped Edge tab selection before approval; verify each closure."""
import re
import time
from desktop import windows


def inventory():
    rows=[]
    with windows.com_thread():
        from pywinauto import Desktop
        for item in windows.window_inventory():
            if item['process'].casefold() != 'msedge.exe': continue
            try:
                wrapper=Desktop(backend='uia').window(handle=item['handle']).wrapper_object()
                for tab in wrapper.descendants(control_type='TabItem',depth=15):
                    if tab.is_visible():
                        rows.append({'handle':item['handle'],'id':list(tab.element_info.runtime_id),
                                     'title':re.split(r' - memory usage',tab.element_info.name,flags=re.I)[0]})
            except Exception: continue
    return rows


def matches(title, query):
    return query == '*' or bool(re.search(r'\b'+re.escape(query)+r'\b',title,re.I))


def request(text, context):
    reference=context.get('tab_reference',{})
    recent=bool(reference and time.time()-reference.get('time',0)<300 and context.get('last_window')=='Microsoft Edge')
    if re.fullmatch(r'close (?:all(?: (?:those|these|of them|of those|tabs))?|both|them|those|these)(?: tabs)?',text,re.I):
        if not recent:
            if context.get('last_window') != 'Microsoft Edge' and text.lower() != 'close all': return None
            return {'action':'clarify','target':'Which tabs do you mean? Say “close all YouTube tabs” or name the site.'}
        if 'both' in text.lower() and len(reference['tabs']) != 2:
            return {'action':'clarify','target':'Which two tabs do you mean? Use their titles or say “close all those”.'}
        return {'action':'edge_close_tabs','target':reference['query'],'tabs':reference['tabs'],'confirm':True}
    match=re.fullmatch(r'close all (.+?)(?: tabs| pages)?',text,re.I)
    if match and match[1].lower() not in ('windows','apps','applications'):
        return {'action':'edge_close_tabs','target':match[1].lower(),'confirm':True}
    if recent and re.fullmatch(r'close (?:it|that|that tab|that one|the first one|the second one)',text,re.I):
        rows=reference['tabs']
        if 'first' in text.lower(): rows=rows[:1]
        elif 'second' in text.lower(): rows=rows[1:2]
        if len(rows)!=1: return {'action':'clarify','target':'Several tabs were listed. Say “close all those” or use an exact tab title.'}
        return {'action':'edge_close_tab','target':reference['query'],'tabs':rows,'confirm':True}
    opened = context.get('last_opened_browser', {})
    if context.get('last_window') == 'Microsoft Edge' and time.time()-opened.get('time',0) < 300 and re.fullmatch(r'close (?:it|that|that tab)',text,re.I):
        return {'action':'edge_close_tab','target':'*','scope_handle':opened['handle'],'confirm':True}
    return None


def prepare(command, context, preferred=None):
    rows=command.get('tabs')
    if rows is None:
        rows=[row for row in inventory() if matches(row['title'],command['target'])]
        if command.get('scope_handle'):
            rows=[row for row in rows if row['handle']==command['scope_handle']]
        if command['action']=='edge_close_tab':
            selected=[row for row in rows if row['handle']==preferred]
            if selected: rows=selected
    context.update(last_window='Microsoft Edge',tab_reference={'query':command['target'],'tabs':rows,'time':time.time()})
    if not rows: raise ValueError('No matching Edge tabs found. Ask me to list tabs or name a site.')
    if len(rows)>30: raise ValueError('More than thirty matching tabs; close a smaller group at a time.')
    if command['action']=='edge_close_tab' and len(rows)>1:
        raise ValueError('Several tabs match '+command['target']+': '+ '; '.join(row['title'] for row in rows[:5])+'. Say “close all those”, “close the first one”, or use an exact title.')
    descriptions='; '.join(row['title'][:120] for row in rows[:5])
    return {**command,'tabs':rows,'confirm':True,'description':f"close {len(rows)} selected Edge tab(s): {descriptions}"}


def close_one(row, query):
    with windows.com_thread():
        import win32gui
        from pywinauto import Desktop
        from pywinauto.keyboard import send_keys
        if not win32gui.IsWindow(row['handle']): return False
        wrapper=Desktop(backend='uia').window(handle=row['handle']).wrapper_object()
        def tabs(): return wrapper.descendants(control_type='TabItem',depth=15)
        selected=[tab for tab in tabs() if list(tab.element_info.runtime_id)==row['id']]
        if not selected: return False
        tab=selected[0]
        if not matches(tab.element_info.name,query): raise ValueError('A selected tab changed site/title. Nothing further was closed.')
        if win32gui.IsIconic(row['handle']): wrapper.restore()
        wrapper.set_focus()
        if win32gui.GetForegroundWindow()!=row['handle']: raise RuntimeError('Edge did not receive focus. No further tabs were closed.')
        tab.select()
        if not tab.is_selected(): raise RuntimeError('The requested tab was not selected. No further tabs were closed.')
        send_keys('^w')
        for _ in range(20):
            if not win32gui.IsWindow(row['handle']): return True
            if not any(list(t.element_info.runtime_id)==row['id'] for t in tabs()): return True
            time.sleep(.1)
        raise RuntimeError('A tab remained open. I could not verify its closure.')


def execute(command, cancel=None):
    closed=missing=0
    for row in command['tabs']:
        if cancel and cancel.is_set(): return f'Stopped. Closed {closed} selected tab(s); remaining tabs were not touched.'
        try:
            if close_one(row,command['target']): closed+=1
            else: missing+=1
        except Exception as error:
            raise RuntimeError(f'Closed {closed} selected tab(s) before stopping: {error}') from error
    return f'Closed {closed} selected Edge tab(s).' + (f' {missing} selected tab(s) were already missing.' if missing else '')
