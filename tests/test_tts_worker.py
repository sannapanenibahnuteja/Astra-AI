import base64
import json
import queue
import threading
import time
import unittest
from unittest.mock import Mock
from desktop.tts_worker import WindowsSpeech
from desktop.reply_audio import ReplyAudio
from desktop.voice import Voice

class Output:
    def __init__(self): self.lines=queue.Queue()
    def readline(self,*args): return self.lines.get(timeout=2)
    def close(self): pass

class Process:
    def __init__(self,respond=True):
        self.stdout=Output(); self.stderr=Mock(); self.requests=[]; self.ended=False; self.respond=respond
        self.stdin=Mock(); self.stdin.write.side_effect=self.write
    def write(self,line):
        self.requests.append(json.loads(line))
        if self.respond: self.stdout.lines.put(json.dumps({'audio':base64.b64encode(b'RIFFtest audio').decode()})+'\n')
    def poll(self): return 0 if self.ended else None
    def terminate(self): self.ended=True; self.stdout.lines.put('')
    def wait(self,timeout=None): return 0

class SpeechWorkerTests(unittest.TestCase):
    def test_reuses_process_and_applies_rate_and_voice_each_time(self):
        process=Process(); spawn=Mock(return_value=process)
        worker=WindowsSpeech(spawn); self.addCleanup(worker.close)
        cancel=threading.Event(); interrupted=threading.Event()
        worker.warm()
        self.assertEqual(worker.render('First.',0,'Hazel',cancel,interrupted),b'RIFFtest audio')
        worker.render('Second.',2,'Zira',cancel,interrupted)
        spawn.assert_called_once()
        self.assertEqual(process.requests[-1],{'text':'Second.','rate':2,'voice':'Zira'})

    def test_interrupt_kills_pending_renderer_without_waiting_for_audio(self):
        process=Process(respond=False); worker=WindowsSpeech(Mock(return_value=process)); self.addCleanup(worker.close)
        cancel=threading.Event(); interrupted=threading.Event()
        timer=threading.Timer(.04,interrupted.set); timer.start()
        start=time.monotonic()
        self.assertIsNone(worker.render('Long text.',0,'',cancel,interrupted))
        self.assertLess(time.monotonic()-start,.5)
        self.assertTrue(process.ended); timer.join()

    def test_idle_renderer_releases_process(self):
        process=Process(); worker=WindowsSpeech(Mock(return_value=process),idle_seconds=.04)
        self.addCleanup(worker.close)
        worker.render('Hi.',0,'',threading.Event(),threading.Event())
        deadline=time.monotonic()+1
        while not process.ended and time.monotonic()<deadline: time.sleep(.01)
        self.assertTrue(process.ended)

    def test_cancelled_request_never_starts_renderer(self):
        spawn=Mock(); worker=WindowsSpeech(spawn); cancel=threading.Event(); cancel.set()
        self.assertIsNone(worker.render('Hi.',0,'',cancel,threading.Event()))
        spawn.assert_not_called()

    def test_stream_does_not_split_partial_decimal_or_title(self):
        calls=[]; audio=ReplyAudio(lambda text:calls.append(text),threading.Event())
        audio.add('It is 3.'); self.assertIsNone(audio.worker)
        audio.add('14 meters. Meet Dr. Smith. '); audio.finish()
        self.assertEqual(calls,['It is 3.14 meters.','Meet Dr. Smith.'])

    def test_phone_reply_clears_old_desktop_interruption(self):
        from desktop.private_voice import render
        voice=Voice(); voice._speech_interrupted.set()
        voice._tts=Mock();voice._tts.render.return_value=b'RIFFtest audio'
        self.assertEqual(base64.b64decode(render(voice,'Hello')),b'RIFFtest audio')
        self.assertFalse(voice._speech_interrupted.is_set())

    def test_idle_expiry_does_not_kill_active_rendering(self):
        process=Process();worker=WindowsSpeech(Mock(return_value=process));self.addCleanup(worker.close)
        worker._ensure();worker.busy=True;worker._expire(process)
        self.assertFalse(process.ended)

    def test_playback_interrupt_retains_idle_renderer_for_next_reply(self):
        process=Process();worker=WindowsSpeech(Mock(return_value=process));self.addCleanup(worker.close)
        worker._ensure();worker.interrupt();self.assertFalse(process.ended)
        worker.busy=True;worker.interrupt();self.assertTrue(process.ended)

    def test_rewarming_replaces_previous_idle_timer(self):
        process=Process();worker=WindowsSpeech(Mock(return_value=process));self.addCleanup(worker.close)
        worker.warm(); old=worker.timer; worker.warm()
        self.assertTrue(old.finished.is_set())
        self.assertIsNot(old,worker.timer)

if __name__=='__main__': unittest.main()
