"""Interactive speaker-path diagnosis; raw audio never leaves memory."""
import json,sys,threading,tkinter as tk
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop.storage import Store
from desktop.speaker import SpeakerProfiles,prepare_audio
from desktop.microphone import input_device,gain_for
import sounddevice as sd
from pywebrtc_audio import AudioProcessor

root=tk.Tk();root.title('Bob - check my saved voice');root.geometry('650x350');root.configure(bg='#101115');root.attributes('-topmost',True)
status=tk.StringVar(value='Stop voice conversation in Bob first.\nClick Check my voice, then speak normally for ten seconds.\nTalk about your day; there are no exact words to read.')
closed=False

def complete(result,error):
    if closed:return
    button.config(state='normal')
    if error:status.set(error);return
    status.set('Check complete.\nRaw microphone: '+result['raw']['state']+' (similarity '+str(result['raw'].get('similarity','unavailable'))+')\nConversation audio: '+result['processed']['state']+' (similarity '+str(result['processed'].get('similarity','unavailable'))+')\nNo recording was saved. You can close this window.')

def capture():
    button.config(state='disabled');status.set('Speak now for ten seconds, at your normal volume and distance.')
    def work():
        result={};error=''
        bank=None
        try:
            store=Store();settings=store.settings();bank=SpeakerProfiles(store.root)
            bank.threshold=.75 if settings['speaker_match_mode']=='strict' else .65
            index,device,key=input_device(sd);rate=int(device['default_samplerate']);chunk=int(rate*.05)
            frames=[]
            with sd.InputStream(device=index,samplerate=rate,channels=1,dtype='float32',blocksize=chunk) as stream:
                for tick in range(200):
                    if closed:return
                    block,over=stream.read(chunk)
                    if over:raise RuntimeError('Audio capture fell behind. Please try the check again.')
                    frames.append(block[:,0].copy())
                    if not closed:root.after(0,lambda tick=tick:status.set(f'Speak naturally: {(tick+1)*.05:.1f} / 10 seconds'))
            original=np.concatenate(frames);gain=gain_for(settings.get('microphone_calibration',{}),key)
            raw=np.clip(original*gain,-.999,.999)
            ap=AudioProcessor(sample_rate=48000,echo_cancellation=True,noise_suppression=True,auto_gain_control=False)
            if rate!=48000:
                target=np.interp(np.arange(round(len(original)*48000/rate))*rate/48000,np.arange(len(original)),original).astype(np.float32)
            else:target=original
            blocks=[]
            for i in range(0,len(target)//480*480,480):blocks.append(ap.process(target[i:i+480],np.zeros(480,np.float32)))
            processed=np.clip(np.concatenate(blocks)*gain,-.999,.999)
            for name,audio,sample_rate in [('raw',raw,rate),('processed',processed,48000)]:
                match=bank.identify(audio,sample_rate,select=False)
                result[name]={k:v for k,v in match.items() if k in ('state','similarity','threshold','speech_seconds','message')}
                vector=bank.extractor.embedding(audio,sample_rate)
                result[name]['profile_scores']=[round(float(p._profile['vector']@vector),3) for p in bank.profiles.values()]
            result['audio_saved']=False
            Path('.cache/live-speaker-path-check.json').write_text(json.dumps(result,indent=2))
        except Exception as exc:error=str(exc)
        finally:
            if bank:bank.close()
        if not closed:root.after(0,lambda:complete(result,error))
    threading.Thread(target=work,daemon=True).start()

def close():
    global closed
    closed=True;root.destroy()

tk.Label(root,text='Check both voice-recognition paths',bg='#101115',fg='white',font=('Segoe UI',17)).pack(pady=24)
tk.Label(root,textvariable=status,bg='#101115',fg='#dce0ef',font=('Segoe UI',11),wraplength=600).pack(pady=10)
button=tk.Button(root,text='Check my voice',command=capture);button.pack(pady=12)
root.protocol('WM_DELETE_WINDOW',close);root.mainloop()
