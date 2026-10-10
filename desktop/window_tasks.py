"""Explicit whole-window groups, kept separate from Edge tab groups."""
import re
import time
from desktop import windows


def plans(rows):
    if not rows: return {'action':'clarify','target':'No matching windows are visible. Which app or site should I close?'}
    if len(rows)>12: return {'action':'clarify','target':'More than twelve windows match. Name a smaller group first.'}
    result=[{**windows.validate('close_window',row['title']), '_window_ref':dict(row), 'confirm':index==0,
             'description':'close the entire window '+row['title']} for index,row in enumerate(rows)]
    result[0]['description']='close these '+str(len(rows))+' entire windows, including ALL their tabs: '+ '; '.join(row['title'] for row in rows)
    return result


def request(text,context,selection):
    match=re.fullmatch(r'close (?:all|both)(?: (?:of )?the)? (.+?) (?:windows|apps|applications)',text,re.I)
    if match:
        from desktop.tab_tasks import canonical_query
        query=canonical_query(match[1])
        if query in ('those','these','them'):
            reference=context.get('tab_reference',{})
            if context.get('last_reference')=='tabs' and time.time()-reference.get('time',0)<300:
                handles={row['handle'] for row in reference.get('tabs',[])}
                return plans([row for row in windows.window_inventory() if row['handle'] in handles])
            text='close all those'
        else:
            aliases={'edge':'msedge','microsoft edge':'msedge','chrome':'chrome','firefox':'firefox','notepad':'notepad'}
            items=windows.window_inventory()
            handles=set()
            if query in ('youtube','google','github'):
                from desktop import tab_tasks
                handles={row['handle'] for row in tab_tasks.inventory() if tab_tasks.matches(row['title'],query)}
            if query in ('youtube','google','github'):
                items=[row for row in items if row['process'].lower() in ('msedge.exe','chrome.exe','firefox.exe','brave.exe','opera.exe')]
            rows=[row for row in items if row['handle'] in handles or
                  re.search(r'\b'+re.escape(query)+r'\b',row['title'],re.I) or
                  row['process'].lower().removesuffix('.exe')==aliases.get(query,query)]
            return plans(rows)
    if text.lower() in ('close all windows','close all apps','close all applications'):
        return {'action':'clarify','target':'Which app or site should I close? For example, “close all YouTube windows”.'}
    if context.get('last_reference')!='windows': return None
    followup=re.fullmatch(r'close (?:all(?: (?:those|these|of them|of those))?|them|those|these|both|it|the other one|the (first|second|third)(?: one| window)?)',text,re.I)
    if not followup: return None
    if not selection or time.monotonic()-selection[0]>180:
        return {'action':'clarify','target':'That window selection expired. Name the app or site again.'}
    rows=selection[1]
    if text.lower() in ('close it','close the other one') and len(rows)!=1:
        return {'action':'clarify','target':'Which remaining window? Say “the first one” or “all those”.'}
    if followup[1]: rows=rows[{'first':0,'second':1,'third':2}[followup[1].lower()]:][:1]
    if text.lower()=='close both' and len(rows)!=2:
        return {'action':'clarify','target':'Which two windows do you mean? Name them or say “close all those”.'}
    return plans(rows)
