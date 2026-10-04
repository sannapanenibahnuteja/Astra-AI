"""Opt-in loopback mobile gateway. Expose only through a private HTTPS VPN proxy."""
import hmac
import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


class Mobile:
    def __init__(self, runtime, public_url='', port=8787, token=None, identity=None):
        self.runtime = runtime
        self.token = token or secrets.token_urlsafe(32)
        self.identity = identity or runtime.new_conversation()
        self.job = None
        self.lock = threading.Lock()
        self.audio_busy = False
        parsed = urlparse(public_url)
        if public_url and (parsed.scheme != 'https' or not (parsed.hostname or '').endswith('.ts.net') or parsed.username or parsed.password or parsed.port or parsed.path not in ('','/') or parsed.query or parsed.fragment):
            raise ValueError('Use your private Tailscale HTTPS address, such as https://your-pc.your-tailnet.ts.net.')
        self.public_url = public_url.rstrip('/')
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_): pass  # Never log tokens or personal requests.

            def send(self, status, data, html=False):
                body = data.encode() if html else json.dumps(data).encode()
                self.send_response(status)
                self.send_header('Content-Type','text/html; charset=utf-8' if html else 'application/json')
                self.send_header('Content-Length',str(len(body)))
                self.send_header('Cache-Control','no-store')
                self.send_header('X-Content-Type-Options','nosniff')
                self.send_header('Referrer-Policy','no-referrer')
                self.send_header('X-Frame-Options','DENY')
                self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'nonce-"+owner.nonce+"'; style-src 'unsafe-inline'; connect-src 'self'; media-src blob: 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
                self.end_headers(); self.wfile.write(body)

            def allowed(self, auth=True):
                host = self.headers.get('Host','')
                hosts = {f'127.0.0.1:{owner.server.server_port}',f'localhost:{owner.server.server_port}'}
                if owner.public_url: hosts.add(urlparse(owner.public_url).netloc)
                if host not in hosts: self.send(403,{'error':'Unrecognized host.'}); return False
                origin = self.headers.get('Origin')
                if origin and origin not in {f'http://127.0.0.1:{owner.server.server_port}',f'http://localhost:{owner.server.server_port}',owner.public_url}:
                    self.send(403,{'error':'Unrecognized origin.'}); return False
                if self.headers.get('Sec-Fetch-Site') == 'cross-site': self.send(403,{'error':'Cross-site request denied.'}); return False
                if auth and not hmac.compare_digest(self.headers.get('Authorization',''), 'Bearer '+owner.token):
                    self.send(401,{'error':'Pair this phone from Bob Settings again.'}); return False
                return True

            def do_GET(self):
                if self.path == '/':
                    if self.allowed(False): self.send(200,HTML.replace('NONCE',owner.nonce),True)
                    return
                if not self.allowed(): return
                if self.path != '/api/state': self.send(404,{'error':'Not found.'}); return
                result = {'text':'','done':True,'error':''}
                if owner.job:
                    try: result=owner.runtime.poll_chat(owner.job)
                    except ValueError: result={'text':'This response is no longer available.','done':True,'error':''}
                self.send(200,{**result,'reminders':owner.runtime._commands.reminders.items()})

            def do_POST(self):
                if not self.allowed(): return
                if self.headers.get('Content-Type','').split(';')[0] != 'application/json': self.send(415,{'error':'Use JSON.'}); return
                try:
                    length=int(self.headers.get('Content-Length','0'))
                    maximum=2_900_000 if self.path=='/api/transcribe' else 20000
                    if not 0<length<=maximum: raise ValueError('Request too large or empty.')
                    self.connection.settimeout(5)
                    data=json.loads(self.rfile.read(length))
                    if not isinstance(data,dict): raise ValueError('Invalid request.')
                    if self.path=='/api/stop':
                        current=owner.runtime._job
                        if current and current['id']==owner.job: owner.runtime.cancel_chat()
                        if owner.audio_busy: owner.runtime._voice.stop()
                        self.send(200,{'stopped':True}); return
                    with owner.lock:
                        if not self.allowed(): return
                        if self.path=='/api/chat':
                            message=data.get('message','')
                            if not isinstance(message,str) or not 1<=len(message.strip())<=4000: raise ValueError('Use between 1 and 4,000 characters.')
                            owner.job=owner.runtime.start_chat(owner.identity,message,spoken=True)
                            self.send(200,{'started':True})
                        elif self.path=='/api/transcribe':
                            from desktop.private_voice import transcribe
                            owner.audio_busy=True
                            try: self.send(200,transcribe(owner.runtime._voice,data.get('audio','')))
                            finally: owner.audio_busy=False
                        elif self.path=='/api/audio':
                            from desktop.private_voice import render
                            owner.audio_busy=True
                            try: self.send(200,{'audio':render(owner.runtime._voice,data.get('text',''),owner.runtime._store.settings()['voice_rate'])})
                            finally: owner.audio_busy=False
                        elif self.path=='/api/reminder_ack':
                            identity=data.get('id','')
                            if not isinstance(identity,str): raise ValueError('Invalid reminder.')
                            with owner.runtime._store.connect() as db:
                                db.execute("UPDATE reminders SET status='delivered on phone' WHERE id=? AND status='ready on phone'",(identity,))
                            self.send(200,{'acknowledged':True})
                        elif self.path=='/api/stop':
                            current=owner.runtime._job
                            if current and current['id']==owner.job: owner.runtime.cancel_chat()
                            self.send(200,{'stopped':True})
                        else: self.send(404,{'error':'Not found.'})
                except Exception: self.send(409,{'error':'Bob is busy, or the voice/request could not be processed. Stop desktop voice mode, wait for the current response and try again.'})

        self.nonce=secrets.token_urlsafe(20)
        self.server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
        self.server.daemon_threads=True
        threading.Thread(target=self.server.serve_forever,daemon=True,name='bob-mobile').start()

    def pairing(self):
        base=self.public_url or f'http://127.0.0.1:{self.server.server_port}'
        return {'url':base+'/#'+self.token,'enabled':True,'remote_ready':bool(self.public_url)}

    def close(self):
        self.token=secrets.token_urlsafe(32)
        current=self.runtime._job
        if current and current['id']==self.job: self.runtime.cancel_chat()
        if self.audio_busy: self.runtime._voice.stop()
        self.server.shutdown(); self.server.server_close()


HTML = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bob · Mobile</title>
<style>*{box-sizing:border-box}body{margin:0;background:#090c14;color:#e6ebff;font:16px system-ui}main{max-width:680px;margin:auto;padding:28px 20px}header{display:flex;justify-content:space-between;align-items:center}h1{letter-spacing:7px;font-weight:400}small{color:#91a5bb}article,section{padding:20px;border:1px solid #283242;border-radius:18px;background:#111825;margin:20px 0}#reply{white-space:pre-wrap;line-height:1.7;min-height:150px}textarea{width:100%;min-height:110px;resize:vertical;background:#0c121e;border:1px solid #344055;border-radius:12px;color:inherit;padding:16px;font:inherit}button{background:#badbe7;color:#102330;border:0;padding:12px 18px;border-radius:12px;margin:8px 8px 0 0;font:inherit;cursor:pointer}button:disabled{opacity:.4}#status{color:#92d8c4}li{margin-bottom:12px}label{display:block;margin:12px 0}</style>
<main><header><h1>BOB</h1><small>YOUR PC · WITH YOU</small></header><p id="status">Connecting…</p><article id="reply" aria-live="polite">What would you like to do?</article>
<form id="form"><label for="message">Talk to Bob</label><textarea id="message" maxlength="4000" placeholder="Remind me in ten minutes to take a break…"></textarea><button id="send">Send</button><button type="button" id="mic">Start private voice conversation</button><button type="button" id="stop">Stop</button></form>
<label><input type="checkbox" id="rememberPhone"> Remember this phone</label><audio id="replyAudio" controls style="width:100%;margin-top:16px"></audio><label><input type="checkbox" id="read" checked> Read replies aloud on this phone</label><section><h2>Reminders</h2><ul id="reminders"></ul></section><button id="logout">Unpair this tab</button><p><small>Your PC must be awake with Bob running. Use your private Tailscale connection outside home. Keep this page open for voice and phone reminders. Speech recognition and reply audio run on your PC.</small></p></main>
<script nonce="NONCE">
let token=location.hash.slice(1)||sessionStorage.getItem('bob-token')||localStorage.getItem('bob-token')||'';history.replaceState(null,'',location.pathname);if(token)sessionStorage.setItem('bob-token',token);
const $=id=>document.getElementById(id);let running=false,timer,voiceMode=false,recording=false,transcribing=false,recorder,player,playing=false,stream,context,finishPlayback,sequence=0,audioUrl;
const seen=new Set();$('rememberPhone').checked=!!localStorage.getItem('bob-token');$('rememberPhone').onchange=()=>{if($('rememberPhone').checked)localStorage.setItem('bob-token',token);else localStorage.removeItem('bob-token');};
async function api(path,data){const response=await fetch(path,{method:data?'POST':'GET',headers:{Authorization:'Bearer '+token,...(data?{'Content-Type':'application/json'}:{})},body:data?JSON.stringify(data):undefined});const value=await response.json();if(!response.ok)throw Error(value.error);return value;}
async function speak(text){if(!$('read').checked||!text)return;playing=true;const generation=sequence;let url;try{const r=await api('/api/audio',{text:text.slice(0,5000)});if(generation!==sequence)return;const bytes=Uint8Array.from(atob(r.audio),c=>c.charCodeAt(0));if(audioUrl)URL.revokeObjectURL(audioUrl);url=URL.createObjectURL(new Blob([bytes],{type:'audio/wav'}));audioUrl=url;player=$('replyAudio');player.src=url;await new Promise((resolve,reject)=>{finishPlayback=resolve;player.onended=resolve;player.onerror=()=>reject(Error('Audio playback failed.'));player.play().catch(()=>{voiceMode=false;$('status').textContent='Tap Play in the audio player to hear Bob, then restart voice when ready.';resolve();});});}finally{playing=false;}}
async function send(message){await api('/api/chat',{message});running=true;$('send').disabled=true;$('message').value='';}
async function poll(){try{const s=await api('/api/state');if(!recording&&!playing)$('status').textContent=s.done?'Connected · Ready':'Bob is working…';if(s.text)$('reply').textContent=s.text;if(running&&s.done){running=false;await speak(s.text);if(voiceMode)record();}const list=$('reminders');list.replaceChildren();for(const r of s.reminders){const li=document.createElement('li');li.textContent=r.text+' · '+new Date(r.due*1000).toLocaleString()+' · '+r.status;list.appendChild(li);if(r.status==='ready on phone'&&!seen.has(r.id)&&!running&&!recording&&!playing){seen.add(r.id);$('reply').textContent='Reminder: '+r.text;if($('read').checked){await speak('A quick reminder: '+r.text);await api('/api/reminder_ack',{id:r.id});}}}$('send').disabled=!s.done||recording||transcribing;}catch(e){$('status').textContent=e.message;running=false;voiceMode=false;}if(token)timer=setTimeout(poll,running?500:4000);}
function endCapture(){stream?.getTracks().forEach(t=>t.stop());if(context){context.close();context=null;}recording=false;}
async function record(){if(recording||transcribing||running||playing||!voiceMode)return;try{stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true}});context=new (window.AudioContext||window.webkitAudioContext)();const source=context.createMediaStreamSource(stream),analyser=context.createAnalyser();source.connect(analyser);analyser.fftSize=1024;const wave=new Float32Array(1024);let heard=false,last=performance.now(),start=last,chunks=[];recorder=new MediaRecorder(stream);recording=true;recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};recorder.onstop=async()=>{clearInterval(meter);endCapture();if(!voiceMode)return;if(!heard){voiceMode=false;$('status').textContent='No speech detected. Tap the voice button to try again.';return;}try{transcribing=true;$('status').textContent='Transcribing privately on your PC…';const blob=new Blob(chunks,{type:recorder.mimeType});const encoded=await new Promise(resolve=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.readAsDataURL(blob);});const result=await api('/api/transcribe',{audio:encoded});if(!voiceMode)return;$('message').value=result.text||'';if(!result.text||result.needs_review){voiceMode=false;$('status').textContent='Please check the words and tap Send.';return;}if(/^(stop listening|stop voice|go to sleep)$/i.test(result.text.replace(/[.!?]/g,''))){voiceMode=false;$('status').textContent='Voice conversation ended.';return;}await send(result.text);}catch(e){voiceMode=false;$('status').textContent=e.message;}finally{transcribing=false;}};recorder.start();$('status').textContent='Listening · speak naturally';const meter=setInterval(()=>{analyser.getFloatTimeDomainData(wave);const rms=Math.sqrt(wave.reduce((sum,x)=>sum+x*x,0)/wave.length);const now=performance.now();if(now-start>300&&rms>.018){heard=true;last=now;}if(now-start>20000||(heard&&now-last>1200)||(!heard&&now-start>8000)){if(recorder.state==='recording')recorder.stop();}},100);}catch(e){endCapture();voiceMode=false;$('status').textContent='Microphone unavailable. Use HTTPS and allow microphone access, or type your message.';}}
$('form').onsubmit=async e=>{e.preventDefault();try{await send($('message').value);clearTimeout(timer);poll();}catch(e){$('status').textContent=e.message;}};
$('mic').onclick=()=>{voiceMode=true;record();};
$('stop').onclick=async()=>{voiceMode=false;sequence++;if(recorder?.state==='recording')recorder.stop();endCapture();if(player)player.pause();if(finishPlayback)finishPlayback();playing=false;try{await api('/api/stop',{});}catch(e){$('status').textContent=e.message;}};
$('logout').onclick=()=>{$('stop').click();token='';sessionStorage.removeItem('bob-token');localStorage.removeItem('bob-token');clearTimeout(timer);$('reply').textContent='Unpaired. Disable mobile access in desktop Settings to revoke all links.';$('status').textContent='Unpaired';};poll();
</script></html>'''
