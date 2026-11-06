"""Profile-scoped intent shortcuts learned only after verified action success.

Stored plans are revalidated and executed again. Replies/results are never cached.
Similarity is conservative token canonicalization, not a claimed neural classifier.
"""
import json
import re
import time
from desktop.devices import number_words

ALLOWED={'open','time','status','audio_status','volume','volume_up','volume_down','mute','unmute',
         'brightness','brightness_up','brightness_down','brightness_status','list_windows','list_monitors',
         'media_pause','media_play','media_next','media_previous','media_status'}
STOP={'please','could','can','would','you','i','my','the','a','an','for','me','just','little','bit','some','of','to','at','percent','points','percentage'}
WORDS={'sound':'volume','audio':'volume','louder':'up','quieter':'down','lower':'down',
       'reduce':'down','decrease':'down','raise':'up','increase':'up','brighter':'up','dimmer':'down',
       'dim':'down','brighten':'up','monitor':'screen','display':'screen','launch':'open',
       'start':'open','bring':'open','get':'open','ease':'turn','put':'set'}


def key(text):
    text=str(text).strip().lower().replace('’',"'")
    if (len(text)>240 or re.search(r"\b(?:not|never|don't|dont|without|except|actually|instead|then|and|or|if|that|this|it|those|them|same|other|again|last|said|meant)\b",text)
            or any(c in text for c in ('@','/','\\',':','"'))):return ''
    text=re.sub(r'^(?:(?:hey|okay|ok)\s+)?bob\b[, ]*','',text)
    tokens=re.findall(r'[a-z]+|\d+',number_words(text))
    values=[WORDS.get(t,t) for t in tokens if t not in STOP]
    if len(values)>14 or not values:return ''
    return ' '.join(sorted(set(values)))


def safe_plan(plan):
    if not isinstance(plan,dict) or plan.get('action') not in ALLOWED or plan.get('confirm'):return None
    if plan.get('window') or plan.get('tabs') or plan.get('display') in {'previous','other'}:return None
    result={k:plan[k] for k in ('action','target','display') if k in plan}
    if not result['action'].startswith('brightness'):result.pop('display',None)
    else:result.setdefault('display','all')
    result.setdefault('target','')
    if result['action'] in {'volume_up','volume_down','brightness_up','brightness_down'} and not result['target']:result['target']='10'
    if any(not isinstance(v,str) or len(v)>120 for v in result.values()):return None
    if result.get('action')=='open' and not re.fullmatch(r'[\w .+-]{1,100}',result.get('target','')):return None
    return result


class CommandLearning:
    def __init__(self,store):self.store=store
    def _schema(self,db):
        db.execute('CREATE TABLE IF NOT EXISTS voice_shortcuts(scope TEXT, phrase TEXT, fingerprint TEXT, plan TEXT, uses INTEGER DEFAULT 0, updated REAL, PRIMARY KEY(scope,phrase))')
    def learn(self,scope,text,plan):
        fingerprint=key(text);plan=safe_plan(plan)
        if not fingerprint or plan is None:return False
        families={'volume':r'\b(volume|sound|audio|loud|quieter|mute)\b',
                  'brightness':r'\b(brightness|bright|brighter|dimmer|screen|monitor|display)\b',
                  'media':r'\b(music|video|playback|track|song|media)\b'}
        family=next((name for name in families if plan['action'].startswith(name)),None)
        if family and not re.search(families[family],text,re.I):return False
        # A named application must still be explicit in the learned utterance.
        if plan['action']=='open' and not set(re.findall(r'\w+',plan['target'].lower())).issubset(set(re.findall(r'\w+',text.lower()))):return False
        with self.store.connect() as db:
            self._schema(db)
            db.execute('INSERT OR REPLACE INTO voice_shortcuts VALUES(?,?,?,?,COALESCE((SELECT uses FROM voice_shortcuts WHERE scope=? AND phrase=?),0),?)',
                       (scope,text.strip(),fingerprint,json.dumps(plan,sort_keys=True),scope,text.strip(),time.time()))
            db.execute('DELETE FROM voice_shortcuts WHERE scope=? AND rowid NOT IN (SELECT rowid FROM voice_shortcuts WHERE scope=? ORDER BY updated DESC LIMIT 100)',(scope,scope))
        return True
    def lookup(self,scope,text):
        fingerprint=key(text)
        if not fingerprint:return None
        with self.store.connect() as db:
            self._schema(db)
            rows=db.execute('SELECT phrase,plan FROM voice_shortcuts WHERE scope=? AND fingerprint=?',(scope,fingerprint)).fetchall()
            plans={row['plan'] for row in rows}
            if len(plans)!=1:return None # Conflicting learned interpretations must use the LLM.
            plan=safe_plan(json.loads(next(iter(plans))))
            if plan is None:return None
            db.execute('UPDATE voice_shortcuts SET uses=uses+1 WHERE scope=? AND fingerprint=?',(scope,fingerprint))
            return plan
    def rows(self,scope):
        with self.store.connect() as db:
            self._schema(db)
            return [dict(r) for r in db.execute('SELECT phrase,uses FROM voice_shortcuts WHERE scope=? ORDER BY updated DESC LIMIT 100',(scope,))]
    def clear(self,scope):
        with self.store.connect() as db:self._schema(db);db.execute('DELETE FROM voice_shortcuts WHERE scope=?',(scope,))
