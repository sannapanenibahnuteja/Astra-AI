"""Durable one-shot reminders with explicit local or private phone delivery."""
import re
import threading
import time
import uuid
from datetime import datetime, timedelta
from desktop.devices import number_words

ACTIONS = {'reminder_add', 'reminder_list', 'reminder_cancel'}


def parse(text):
    approval=re.fullmatch(r'(.+?)(?:;|,|\band)\s*(?:ask me before scheduling(?: it)?|check with me first)',text,re.I)
    if approval:
        command=parse(approval[1].strip())
        if command and command['action']=='reminder_add':
            command['confirm']=True
            return command
    if re.fullmatch(r'(?:list|show|what are)(?: me)?(?: my)? reminders', text, re.I):
        return {'action':'reminder_list','target':''}
    match = re.fullmatch(r'(?:cancel|delete) reminder (.+)', text, re.I)
    if match: return {'action':'reminder_cancel','target':match[1]}
    match = re.fullmatch(r'(remind me(?: on my phone)?|call me)(?: on my phone)? in (.+?) (seconds?|minutes?|hours?|days?) (?:to|about) (.+)', text, re.I)
    if match:
        amount = number_words(match[2].lower())
        if not amount.isdigit(): raise ValueError('Tell me a number of seconds, minutes, hours or days.')
        seconds = int(amount) * {'second':1,'minute':60,'hour':3600,'day':86400}[match[3].lower().rstrip('s')]
        channel='call' if match[1].lower()=='call me' else 'phone' if 'phone' in match[1].lower() else 'local'
        return {'action':'reminder_add','target':match[4],'value':str(time.time()+seconds), 'destination':channel}
    return None


class Reminders:
    def __init__(self, store):
        self.store = store
        self.stop = threading.Event()
        with store.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS reminders (id TEXT PRIMARY KEY, text TEXT NOT NULL, due REAL NOT NULL, channel TEXT NOT NULL, status TEXT NOT NULL, detail TEXT NOT NULL DEFAULT "")')

    def validate(self, command):
        action = command.get('action'); target = command.get('target','')
        if action not in ACTIONS or not isinstance(target,str) or len(target)>1000: raise ValueError('Invalid reminder.')
        result = {'action':action,'target':target,'confirm':False}
        if action == 'reminder_add':
            raw = str(command.get('value',''))
            try:
                due = float(raw) if re.fullmatch(r'\d+(?:\.\d+)?',raw) else datetime.fromisoformat(raw).timestamp()
            except (ValueError, OverflowError): raise ValueError('Tell me when to remind you, including AM or PM for a clock time.')
            if not time.time()+1 <= due <= time.time()+366*86400: raise ValueError('Choose a reminder time in the next year, at least two seconds from now.')
            channel = command.get('destination','local')
            if channel not in ('local','phone','call') or not target.strip(): raise ValueError('A reminder needs text and a local, phone-page or call destination.')
            if channel=='call':
                from desktop.calling import config
                config(self.store.root)
            result.update(value=str(due), destination=channel, confirm=channel=='call' or command.get('confirm') is True)
        return result

    def items(self):
        with self.store.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM reminders ORDER BY due DESC LIMIT 100')]

    def execute(self, command, context):
        command = self.validate(command)
        action = command['action']
        if action == 'reminder_list':
            rows = self.items()
            return '\n'.join(f"{r['id']}: {r['text']} — {datetime.fromtimestamp(r['due']).strftime('%d %b %I:%M %p')} ({r['channel']}, {r['status']})" for r in rows) or "You don't have any reminders yet."
        if action == 'reminder_cancel':
            identity = context.get('last_reminder') if command['target'].lower() in ('it','that','that reminder') else command['target']
            with self.store.connect() as db:
                changed = db.execute("UPDATE reminders SET status='cancelled' WHERE id=? AND status='pending'",(identity,)).rowcount
            if not changed: raise ValueError('That pending reminder was not found. Ask me to list your reminders.')
            return 'That reminder is cancelled.'
        identity = uuid.uuid4().hex[:8]
        with self.store.connect() as db:
            db.execute('INSERT INTO reminders(id,text,due,channel,status) VALUES(?,?,?,?,?)',(identity,command['target'],float(command['value']),command['destination'],'pending'))
        context['last_reminder'] = identity
        when = datetime.fromtimestamp(float(command['value'])).strftime('%d %b at %I:%M:%S %p')
        delivery={'local':'remind you here','phone':'alert you on the private phone page','call':'call your configured phone number'}
        return f"I'll {delivery[command['destination']]} on {when}: {command['target']}. Reminder {identity}."

    def tick(self, deliver, local_ready=True):
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            item = db.execute("SELECT * FROM reminders WHERE status='pending' AND due<=? AND (channel!='local' OR ?) ORDER BY due LIMIT 1",(time.time(),local_ready)).fetchone()
            if not item: return
            db.execute("UPDATE reminders SET status='delivering' WHERE id=?",(item['id'],))
        status, detail = 'delivered', ''
        try:
            if item['channel']=='call':
                if time.time()-item['due']>300: raise RuntimeError('Call time missed while Bob was unavailable. Reschedule it; no late call was placed.')
                from desktop.calling import submit
                detail=submit(self.store.root,item['text']);status='call submitted'
            elif item['channel']=='phone':
                status='ready on phone'
                detail='Open the private phone page to hear this reminder.'
            else: deliver(dict(item))
        except Exception as exc: status,detail='failed',str(exc)[:300]
        with self.store.connect() as db:
            db.execute('UPDATE reminders SET status=?,detail=? WHERE id=?',(status,detail,item['id']))

    def start(self, deliver, ready=lambda:True):
        def run():
            while not self.stop.wait(2):
                try:
                    self.tick(deliver,ready())
                except Exception: pass  # Keep future reminders alive after transient DB errors.
        threading.Thread(target=run,daemon=True,name='bob-reminders').start()
