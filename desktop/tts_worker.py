"""Reuse Windows speech synthesis between sentences; close after a short idle."""
import base64
import json
import queue
import threading
import time

SCRIPT = r"""$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[Text.UTF8Encoding]::new(); Add-Type -AssemblyName System.Speech;
$voice=[System.Speech.Synthesis.SpeechSynthesizer]::new()
$defaultVoice=$voice.Voice.Name
try {
 while ($null -ne ($line=[Console]::ReadLine())) {
  $buffer=[IO.MemoryStream]::new()
  try {
   $cfg=$line | ConvertFrom-Json
   $name=if ($cfg.voice) {[string]$cfg.voice} else {$defaultVoice}
   if ($voice.Voice.Name -ne $name) {$voice.SelectVoice($name)}
   $voice.Rate=[int]$cfg.rate
   $voice.SetOutputToWaveStream($buffer)
   $voice.Speak([string]$cfg.text)
   $voice.SetOutputToNull()
   [Console]::WriteLine((@{audio=[Convert]::ToBase64String($buffer.ToArray())} | ConvertTo-Json -Compress))
  } catch {
   [Console]::WriteLine('{"error":"Windows speech rendering failed. Check the selected voice."}')
  } finally {$buffer.Dispose(); [Console]::Out.Flush()}
 }
} finally {$voice.Dispose()}
"""


class WindowsSpeech:
    def __init__(self, spawn, idle_seconds=60):
        self.spawn=spawn; self.idle_seconds=idle_seconds
        self.lock=threading.RLock(); self.process=None; self.responses=None; self.timer=None; self.busy=False

    def _reader(self,process,responses):
        try:
            while True:
                line=process.stdout.readline(28_000_000)
                if not line: break
                try: responses.put(json.loads(line.lstrip('\ufeff')))
                except ValueError: responses.put({'error':'Invalid Windows speech response.'})
        finally:
            responses.put({'error':'Windows speech renderer stopped.'})
            try: process.wait(timeout=1)
            except Exception: pass
            for stream in (process.stdout,process.stderr,process.stdin):
                try: stream.close()
                except Exception: pass

    def _ensure(self):
        with self.lock:
            if self.timer: self.timer.cancel(); self.timer=None
            if self.process is None or self.process.poll() is not None:
                self.process=self.spawn(SCRIPT); self.responses=queue.Queue()
                threading.Thread(target=self._reader,args=(self.process,self.responses),daemon=True).start()
            return self.process,self.responses

    def _idle(self,process):
        with self.lock:
            if self.process is not process or self.busy: return
            if self.timer: self.timer.cancel()
            self.timer=threading.Timer(self.idle_seconds,lambda:self._expire(process))
            self.timer.daemon=True; self.timer.start()

    def _expire(self,process):
        with self.lock:
            if not self.busy: self.close(process)

    def warm(self):
        process,_=self._ensure(); self._idle(process)

    def interrupt(self):
        # Playback happens in the parent. An idle renderer has no speech to
        # stop and can remain ready for the user's replacement request.
        with self.lock:
            if self.busy: self.close()

    def close(self,expected=None):
        with self.lock:
            if expected is not None and self.process is not expected: return
            if self.timer: self.timer.cancel(); self.timer=None
            process=self.process; self.process=None; self.responses=None; self.busy=False
            if process and process.poll() is None:
                try: process.terminate()
                except OSError: pass

    def render(self,text,rate,voice,cancel,interrupted,timeout=90):
        if cancel.is_set() or interrupted.is_set(): return None
        process,responses=self._ensure()
        with self.lock:
            self.busy=True
            if self.timer: self.timer.cancel(); self.timer=None
        try:
            process.stdin.write(json.dumps({'text':text,'rate':rate,'voice':voice})+'\n')
            process.stdin.flush()
            deadline=time.monotonic()+timeout
            while time.monotonic()<deadline:
                if cancel.is_set() or interrupted.is_set(): self.close(process); return None
                try: result=responses.get(timeout=.025)
                except queue.Empty: continue
                if cancel.is_set() or interrupted.is_set(): self.close(process); return None
                if result.get('error'): raise RuntimeError(result['error'])
                data=base64.b64decode(result['audio'],validate=True)
                if not data.startswith(b'RIFF') or len(data)>20_000_000: raise RuntimeError('Invalid Windows speech audio.')
                with self.lock:
                    if self.process is process: self.busy=False
                    self._idle(process)
                return data
            raise RuntimeError('Windows speech rendering timed out.')
        except Exception:
            self.close(process)
            if cancel.is_set() or interrupted.is_set(): return None
            raise
