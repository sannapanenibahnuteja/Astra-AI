"""Bounded sentence queue: generation continues while verified speech plays."""
import queue
import re
import threading


class ReplyAudio:
    def __init__(self, speak, cancelled):
        self.speak, self.cancelled = speak, cancelled
        self.items=queue.Queue(maxsize=12)
        self.buffer=''
        self.worker=None
        self.error=''
        self.spoken=False
        self.speech_stopped=False

    def add(self, text, flush=False):
        if self.cancelled.is_set() or self.speech_stopped: return
        self.buffer+=text
        # Wait for sentence boundaries, and never voice fenced code blocks.
        while '```' not in self.buffer:
            match=re.search(r'[.!?](?:\s|$)|\n',self.buffer)
            if not match: break
            end=match.end()
            sentence=self.buffer[:end].strip(); self.buffer=self.buffer[end:]
            if sentence: self._put(sentence)
        if flush and self.buffer.strip():
            value=re.sub(r'```[\s\S]*?(?:```|$)',' Code is shown on screen. ',self.buffer)
            self.buffer=''; self._put(value)

    def _put(self, text):
        if self.worker is None:
            self.worker=threading.Thread(target=self._run,daemon=True)
            try: self.worker.start()
            except RuntimeError as error:
                self.error=str(error); self.speech_stopped=True; self.worker=None; return
        while not self.cancelled.is_set() and not self.speech_stopped:
            try: self.items.put(text,timeout=.05); return
            except queue.Full: pass

    def _run(self):
        while True:
            try: text=self.items.get(timeout=.05)
            except queue.Empty:
                if self.cancelled.is_set(): return
                continue
            if text is None: return
            if self.cancelled.is_set() or self.speech_stopped: continue
            try:
                self.spoken=True
                if self.speak(text) is False: self.speech_stopped=True
            except Exception as error:
                self.error=str(error); self.speech_stopped=True

    def finish(self):
        if self.worker is None: return
        while self.worker.is_alive():
            try: self.items.put(None,timeout=.05); break
            except queue.Full:
                if self.cancelled.is_set(): break
        self.worker.join()
