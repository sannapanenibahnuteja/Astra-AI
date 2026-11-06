"""Local neural retrieval over current profile's saved facts; never raw recordings."""
import hashlib
import json
import math
import threading
import urllib.request
from urllib.parse import urlparse

MODEL='nomic-embed-text:latest'


def embedding(text,url,timeout=.8):
    parsed=urlparse(url)
    if parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost','::1') or parsed.username or parsed.password:
        raise ValueError('Semantic memory requires local Ollama.')
    request=urllib.request.Request(url.rstrip('/')+'/api/embed',data=json.dumps({'model':MODEL,'input':text[:3000],'keep_alive':'2m'}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=timeout) as response:body=json.loads(response.read(300000))
    vector=body['embeddings'][0]
    if not isinstance(vector,list) or not 32<=len(vector)<=4096 or any(type(v) not in (int,float) or not math.isfinite(v) for v in vector):raise ValueError('Invalid memory embedding')
    norm=math.sqrt(sum(v*v for v in vector))
    if norm<1e-9:raise ValueError('Empty memory embedding')
    return [v/norm for v in vector]


class SemanticMemory:
    def __init__(self,store):self.store=store;self.index_lock=threading.Lock();self.generation=0
    def _schema(self,db):
        db.execute('CREATE TABLE IF NOT EXISTS memory_vectors(scope TEXT,key TEXT,digest TEXT,model TEXT,vector TEXT,PRIMARY KEY(scope,key))')
    def rank(self,scope,query,facts,url):
        if not facts:return facts
        # The call budget is bounded; stale facts are never resurrected from vectors.
        try:
            q=embedding('search_query: '+query,url)
            with self.store.connect() as db:
                self._schema(db)
                stored={r['key']:dict(r) for r in db.execute('SELECT * FROM memory_vectors WHERE scope=?',(scope,))}
            ranked=[];missing=[]
            for fact in facts[:100]:
                text=fact['key']+': '+fact['value'];digest=hashlib.sha256(text.encode()).hexdigest()
                record=stored.get(fact['key'])
                if not record or record['digest']!=digest or record['model']!=MODEL:
                    missing.append((fact,text,digest));continue
                vector=json.loads(record['vector'])
                if len(vector)==len(q):ranked.append((sum(a*b for a,b in zip(q,vector)),fact))
            if missing and self.index_lock.acquire(blocking=False):
                threading.Thread(target=self._index,args=(scope,missing[:8],url,self.generation),daemon=True,name='bob-memory-index').start()
            scores={fact['key']:score for score,fact in ranked if score>.2}
            return [{**fact,'_semantic_score':scores.get(fact['key'],0.)} for fact in facts]
        except Exception:return facts # Offline/degraded memory keeps existing lexical retrieval.
    def _index(self,scope,missing,url,generation):
        try:
            for fact,text,digest in missing:
                vector=embedding('search_document: '+text,url,timeout=2)
                with self.store.connect() as db:
                    if generation!=self.generation:continue
                    # A deletion/edit while embedding must not reinsert a stale fact.
                    if scope=='workspace':current=db.execute('SELECT value FROM memories WHERE key=?',(fact['key'],)).fetchone()
                    else:current=db.execute('SELECT value FROM voice_memories WHERE profile=? AND key=?',(scope,fact['key'])).fetchone()
                    if not current or hashlib.sha256((fact['key']+': '+current['value']).encode()).hexdigest()!=digest:continue
                    self._schema(db)
                    db.execute('INSERT OR REPLACE INTO memory_vectors VALUES(?,?,?,?,?)',(scope,fact['key'],digest,MODEL,json.dumps(vector)))
        except Exception:pass
        finally:self.index_lock.release()
    def clear(self,scope):
        self.generation+=1
        with self.store.connect() as db:self._schema(db);db.execute('DELETE FROM memory_vectors WHERE scope=?',(scope,))
