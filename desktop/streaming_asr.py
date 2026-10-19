"""Bounded latest-only incremental recognition. Previews cannot dispatch actions."""
import threading


class PreviewWorker:
    def __init__(self,decode,publish):
        self.decode=decode;self.publish=publish;self.condition=threading.Condition()
        self.pending=None;self.closed=False;self.serial=0;self.previous=''
        self.thread=threading.Thread(target=self._run,daemon=True,name='bob-asr-preview');self.thread.start()

    def begin(self,serial):
        with self.condition:
            self.serial=serial;self.previous='';self.pending=None

    def submit(self,frame):
        with self.condition:
            if self.closed or frame.serial!=self.serial:return
            self.pending=frame;self.condition.notify()

    def end(self,serial):
        with self.condition:
            if self.serial==serial:self.serial+=1;self.pending=None;self.previous=''

    def _run(self):
        while True:
            with self.condition:
                self.condition.wait_for(lambda:self.closed or self.pending is not None)
                if self.closed:return
                frame=self.pending;self.pending=None
            try:text=self.decode(frame)
            except Exception:text=None
            if not text:continue
            with self.condition:
                if self.closed or frame.serial!=self.serial:continue
                before=self.previous.split();after=text.split();common=[]
                for a,b in zip(before,after):
                    if a.casefold()!=b.casefold():break
                    common.append(b)
                self.previous=text
                # Serialize publication against end()/begin(): stale captions
                # cannot surface after cancellation or a different speaker turn.
                self.publish(frame,text,' '.join(common))

    def close(self):
        with self.condition:self.closed=True;self.pending=None;self.condition.notify_all()
        self.thread.join(timeout=.2)
