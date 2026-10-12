"""Durable daily routines. Scheduled steps are deterministic and low risk only."""
import json
import re
import threading
import time
import uuid
from datetime import datetime

SAFE = {'open', 'url', 'folder', 'search', 'volume', 'mute', 'unmute', 'time',
        'status', 'brightness', 'brightness_status', 'audio_status', 'list_monitors',
        'media_play', 'media_pause', 'media_next', 'media_previous'}


def voice_plan(arguments):
    target=arguments.get('target','')
    if not isinstance(target,str) or len(target)>4000: raise ValueError('Keep the routine within twelve short steps.')
    try: value=json.loads(target)
    except (ValueError,TypeError): raise ValueError('Specify a routine name, steps and daily HH:mm time, or leave its time empty.') from None
    if not isinstance(value,dict) or set(value)-{'name','steps','schedule'}: raise ValueError('Invalid routine setup.')
    name,steps,schedule=value.get('name'),value.get('steps'),value.get('schedule','')
    if not isinstance(name,str) or not name.strip() or len(name)>80 or not isinstance(steps,list) or not 1<=len(steps)<=12 or any(not isinstance(s,str) or not s.strip() or len(s)>1000 for s in steps):
        raise ValueError('Give the routine a name and one to twelve explicit steps.')
    if not isinstance(schedule,str) or (schedule and not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d',schedule)):
        raise ValueError('Specify an unambiguous daily time in HH:mm.')
    value={'name':name.strip(),'steps':steps,'schedule':schedule,'enabled':True}
    return {'action':'automation_create','target':json.dumps(value),'routine':value,'confirm':True,
            'description':f"save routine {name.strip()} ({'daily at '+schedule if schedule else 'manual'}): "+'; then '.join(steps)}


class Automations:
    def __init__(self, runtime):
        self.runtime = runtime
        self.store = runtime._store
        self.stop = threading.Event()
        self.lock = threading.Lock()
        with self.store.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS routines (id TEXT PRIMARY KEY, value TEXT NOT NULL)')

    def rows(self):
        with self.store.connect() as db:
            return [json.loads(r[0]) for r in db.execute('SELECT value FROM routines ORDER BY rowid DESC')]

    def request(self, text):
        from desktop.intent import normalize
        match = re.fullmatch(r'(?:run|start|do) (?:my |the )?(?:routine|automation) (.+)', normalize(text), re.I)
        if not match: return None
        rows = [row for row in self.rows() if row['name'].casefold() == match[1].strip().casefold()]
        if not rows: raise ValueError('I could not find that routine. Open Automations and use its saved name.')
        if len(rows) != 1: raise ValueError('Two routines have that name. Rename one in Automations so I can choose safely.')
        return ' then '.join(rows[0]['steps'])

    def save(self, value):
        with self.lock: return self._save(value)

    def _save(self, value):
        if not isinstance(value, dict): raise ValueError('Invalid routine.')
        name, steps = value.get('name', ''), value.get('steps', [])
        schedule = value.get('schedule', '')
        if not isinstance(name, str) or not name.strip() or len(name) > 80:
            raise ValueError('Give the routine a name of up to 80 characters.')
        if not isinstance(steps, list) or not 1 <= len(steps) <= 12 or any(not isinstance(s, str) or not s.strip() or len(s) > 1000 for s in steps):
            raise ValueError('Add one to twelve steps, each up to 1,000 characters.')
        if not isinstance(schedule, str) or (schedule and not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', schedule)):
            raise ValueError('Choose a daily time, or leave the routine manual.')
        identity = value.get('id') or uuid.uuid4().hex
        old = next((r for r in self.rows() if r['id'] == identity), None)
        if value.get('id') and not old: raise ValueError('Routine no longer exists.')
        enabled = value.get('enabled', True)
        if type(enabled) is not bool: raise ValueError('Invalid enabled setting.')
        row = {'id': identity, 'name': name.strip(), 'steps': [s.strip() for s in steps],
               'schedule': schedule, 'enabled': enabled, 'last_day': (old or {}).get('last_day', ''),
               'result': (old or {}).get('result', 'Not run yet'), 'updated': time.time()}
        if schedule: self.plans(row, 'routine-' + identity)
        self.write(row)
        return self.rows()

    def write(self, row):
        with self.store.connect() as db:
            db.execute('INSERT OR REPLACE INTO routines VALUES (?,?)', (row['id'], json.dumps(row)))

    def delete(self, identity):
        with self.lock:
            with self.store.connect() as db: db.execute('DELETE FROM routines WHERE id=?', (identity,))
        return self.rows()

    def plans(self, row, identity):
        plans = []
        context = {}
        for text in row['steps']:
            plan = self.runtime._commands.plan(text, identity, _context=context)
            choices = plan if isinstance(plan, list) else [plan]
            for item in choices:
                if not item or item.get('confirm') or item.get('action') not in SAFE:
                    raise ValueError('Daily routines support explicit app/site opening, folders, search, sound, brightness and media transport only. Use Run now for other tasks with normal confirmation.')
                plans.append(item)
            if len(plans) > 12: raise ValueError('Use at most twelve actions in a daily routine.')
        return plans

    def tick(self, now=None):
        now = now or datetime.now()
        if not self.lock.acquire(blocking=False): return
        try:
            if self.runtime._job and not self.runtime._job['done']: return
            if self.runtime._voice.status().get('phase', 'idle') != 'idle': return
            for row in self.rows():
                if self.stop.is_set(): return
                day = now.strftime('%Y-%m-%d')
                if not row['enabled'] or row['schedule'] != now.strftime('%H:%M') or row['last_day'] == day: continue
                # Claim before execution: a restart cannot repeat partially completed work.
                row['last_day'] = day
                row['result'] = 'Running'
                self.write(row)
                results = []
                try:
                    with self.runtime._lock:
                        if self.runtime._job and not self.runtime._job['done']:
                            raise ValueError('Bob became busy. Run this routine manually.')
                        identity = 'routine-' + row['id']
                        plans = self.plans(row, identity)
                        for plan in plans:
                            if self.stop.is_set(): raise ValueError('Bob is closing; remaining steps cancelled.')
                            result = self.runtime._commands.execute(plan, identity)
                            results.append(result)
                            if result.startswith(('Asked ', "I couldn't", 'Could not')):
                                raise ValueError('Stopped because the previous action was not verified.')
                            self.store.record_action(identity, plan, result)
                    row['result'] = '\n'.join(results)
                except Exception as error:
                    row['result'] = '\n'.join(results + ['Stopped: ' + str(error)])
                row['updated'] = time.time()
                self.write(row)
        finally: self.lock.release()

    def start(self):
        def worker():
            while not self.stop.wait(10):
                try: self.tick()
                except Exception:
                    import logging
                    logging.exception('Routine scheduler failed')
        threading.Thread(target=worker, daemon=True, name='bob-routines').start()
