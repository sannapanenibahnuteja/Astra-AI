"""Serve a silent browser fixture, or verify only its named Windows media session.
Run --serve, open http://127.0.0.1:8793, click Play, then run --verify.
"""
import argparse,json,re,sys,wave
from pathlib import Path
from http.server import BaseHTTPRequestHandler,HTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop import media
parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');parser.add_argument('--serve',action='store_true');args=parser.parse_args()
root=Path(__file__).resolve().parents[1]/'.cache/media-fixture';root.mkdir(parents=True,exist_ok=True)
if args.verify:
    rows=media.native({'action':'media_sessions'}, {})
    assert len([r for r in rows if r['title']=='Bob Playback Verification'])==1, 'Open and play the silent fixture first.'
    results=[]
    for action,value in [('media_pause',''),('media_seek','30'),('media_play','')]:
        result=media.native({'action':action,'value':value,'window':'Bob Playback Verification'}, {})
        results.append({'action':action,'result':result})
    assert results[0]['result']['state']=='Paused'
    assert abs(results[1]['result']['position']-30)<3
    assert results[2]['result']['state']=='Playing'
    (root/'result.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(json.dumps(results,indent=2))
else:
    with wave.open(str(root/'silent.wav'),'wb') as audio:
        audio.setnchannels(1);audio.setsampwidth(2);audio.setframerate(8000);audio.writeframes(bytes(8000*120*2))
    page='''<!doctype html><title>Bob Playback Verification</title><h1>Silent Bob playback fixture</h1><button onclick="a.play()">Play silent fixture</button><audio id="a" controls src="silent.wav"></audio><script>
const a=document.getElementById('a');navigator.mediaSession.metadata=new MediaMetadata({title:'Bob Playback Verification',artist:'Automated test'});
function state(){navigator.mediaSession.playbackState=a.paused?'paused':'playing';if(Number.isFinite(a.duration))navigator.mediaSession.setPositionState({duration:a.duration,position:a.currentTime,playbackRate:a.playbackRate});}
a.onplay=state;a.onpause=state;a.ontimeupdate=state;
navigator.mediaSession.setActionHandler('play',()=>a.play());navigator.mediaSession.setActionHandler('pause',()=>a.pause());navigator.mediaSession.setActionHandler('seekto',x=>{a.currentTime=x.seekTime;state()});
</script>'''.encode()
    data=(root/'silent.wav').read_bytes()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path=='/':
                self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Length',str(len(page)));self.end_headers();self.wfile.write(page);return
            if self.path!='/silent.wav':self.send_error(404);return
            match=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers.get('Range',''))
            start=int(match[1]) if match else 0;end=min(int(match[2]) if match and match[2] else len(data)-1,len(data)-1)
            if start>end:self.send_error(416);return
            self.send_response(206 if match else 200);self.send_header('Content-Type','audio/wav');self.send_header('Accept-Ranges','bytes')
            if match:self.send_header('Content-Range',f'bytes {start}-{end}/{len(data)}')
            self.send_header('Content-Length',str(end-start+1));self.end_headers();self.wfile.write(data[start:end+1])
    print('Open http://127.0.0.1:8793 and click Play silent fixture.',flush=True)
    HTTPServer(('127.0.0.1',8793),Handler).serve_forever()
