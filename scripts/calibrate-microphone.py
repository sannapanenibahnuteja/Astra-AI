"""Interactive local microphone calibration; recordings remain in memory only."""
import json
import sys
import threading
import tkinter as tk
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop.voice import Voice
from desktop.storage import Store

voice=Voice()
root=tk.Tk();root.title('Bob - calibrate laptop microphone');root.geometry('620x420');root.configure(bg='#101115')
root.attributes('-topmost',True)
status=tk.StringVar(value='Stop voice conversation in Bob first.\nKeep your laptop microphone at your normal speaking distance.')
detail=tk.StringVar(value=voice.microphone_status()['name'])
running=False
closed=False

def finish(result,error):
    global running
    running=False
    quiet.config(state='normal');cancel.config(state='normal')
    if error:
        status.set(error);return
    if result.get('cancelled'):
        status.set('Cancelled. Your previous calibration is kept.');return
    if result.get('noise_ready'):
        speak.config(state='normal')
        status.set('Room noise measured.\nClick Record my normal voice, then speak for ten seconds.')
    if result.get('profile'):
        store=Store()
        saved={'microphone_calibration':result['profile']}
        if natural.get(): saved['turn_pause_ms']=650
        store.save_settings(saved)
        Path('.cache/microphone-calibration-result.json').write_text(json.dumps({'applied':True,'gain':result['profile']['gain'],'natural_pauses':natural.get(),'audio_saved':False}))
        status.set('Calibration saved for your laptop microphone.\nClose old Bob and open the updated EXE when it is ready.\nThen record your three voice samples again.')
        detail.set('Input gain: '+str(result['profile']['gain'])+'x - no recording saved')
        speak.config(state='disabled')

def measure(stage):
    global running
    running=True
    quiet.config(state='disabled');speak.config(state='disabled')
    status.set('Stay quiet for three seconds.' if stage=='noise' else 'Speak now for ten seconds. Tell Bob about your day.')
    def work():
        result={};error=''
        try: result=voice.calibrate_microphone(stage)
        except Exception as exc:error=str(exc)
        if not closed: root.after(0,lambda:finish(result,error))
    threading.Thread(target=work,daemon=True).start()

def close():
    global closed
    closed=True;voice.stop();root.destroy()

def poll():
    if closed:return
    if running:
        value=voice.status()
        detail.set(f"{value.get('input_device','Microphone')} | {value.get('calibration_seconds',0):.1f}s | level {value.get('level',0)*100:.0f}%")
    root.after(100,poll)

tk.Label(root,text='Let Bob hear your normal voice',font=('Segoe UI',18),bg='#101115',fg='white').pack(pady=(22,12))
tk.Label(root,textvariable=status,font=('Segoe UI',11),wraplength=565,bg='#101115',fg='#dce0ef').pack(pady=8)
tk.Label(root,textvariable=detail,font=('Segoe UI',10),bg='#101115',fg='#a8b2d4').pack(pady=8)
quiet=tk.Button(root,text='1. Measure room noise (stay quiet)',command=lambda:measure('noise'));quiet.pack(pady=6)
speak=tk.Button(root,text='2. Record my normal voice',state='disabled',command=lambda:measure('speech'));speak.pack(pady=6)
natural=tk.BooleanVar(value=True)
tk.Checkbutton(root,text='Use natural pauses while I speak (recommended)',variable=natural,bg='#101115',fg='#dce0ef',selectcolor='#242737',activebackground='#101115',activeforeground='white').pack(pady=5)
cancel=tk.Button(root,text='Cancel current measurement',command=voice.stop);cancel.pack(pady=5)
root.protocol('WM_DELETE_WINDOW',close);root.after(100,poll);root.mainloop();voice.close()
