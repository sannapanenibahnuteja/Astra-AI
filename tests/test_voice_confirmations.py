"""Speech-onset callbacks must not cancel newly accepted confirmations."""
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock,patch
from desktop.runtime import Runtime
from desktop.reply_audio import ReplyAudio

class VoiceConfirmations(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.runtime=Runtime(self.temp.name);self.identity=self.runtime.new_conversation()
        self.runtime._voice._hold=True

    def send(self,text):
        job=self.runtime.start_chat(self.identity,text,True)
        for _ in range(500):
            result=self.runtime.poll_chat(job)
            if result['done']: return result
            time.sleep(.01)
        self.fail('Voice request did not finish')

    def test_yes_survives_speech_onset_before_generation(self):
        generate=self.runtime._generate
        def onset_then_generate(job,text):
            self.runtime._voice_interrupt()
            generate(job,text)
        with patch.object(self.runtime,'speak',return_value=True),patch.object(self.runtime,'_generate',side_effect=onset_then_generate),patch.object(self.runtime._commands,'execute',return_value='Closed Microsoft Edge.') as execute:
            waiting=self.send('Close Microsoft Edge')
            self.assertIn('Should I close',waiting['text'])
            self.assertIn(self.identity,self.runtime._pending)
            execute.assert_not_called()
            done=self.send('Yes')
            self.assertEqual(done['error'],'')
            self.assertIn('Closed Microsoft Edge.',done['text'])
            self.assertNotIn('Response stopped',done['text'])
            execute.assert_called_once()
            self.assertEqual(execute.call_args.args[0]['action'],'close_window')
            self.assertEqual(done['steps'],1)

    def test_onset_during_native_action_keeps_verified_result(self):
        def execute(step,identity):
            # A concurrently speaking previous step must not hide this result.
            self.runtime._job['audio'].speaking=True
            self.runtime._voice_interrupt()
            self.runtime._job['audio'].speaking=False
            return 'Closed Microsoft Edge.'
        with patch.object(self.runtime,'speak',return_value=True),patch.object(self.runtime._commands,'execute',side_effect=execute):
            self.send('Close Microsoft Edge')
            result=self.send('Yes')
            self.assertEqual(result['error'],'')
            self.assertNotIn('Response stopped',result['text'])
            self.assertEqual(result['steps'],1)
            self.assertEqual(len(self.runtime._store.recent_actions(self.identity)),1)

    def test_model_reply_remains_interruptible(self):
        job={'done':False,'spoken':True,'cancel':threading.Event(),'transport':Mock()}
        self.runtime._job=job
        self.runtime._voice_interrupt()
        self.assertTrue(job['cancel'].is_set())
        self.assertTrue(job['interrupted'])

    def test_idle_response_audio_does_not_cancel_new_turn(self):
        job={'done':False,'spoken':True,'cancel':threading.Event(),'transport':None,'audio':ReplyAudio(Mock(),threading.Event())}
        job['audio'].spoken=True
        self.runtime._job=job
        self.runtime._voice_interrupt()
        self.assertFalse(job['cancel'].is_set())

    def test_manual_stop_still_cancels_actions(self):
        self.runtime._job={'done':False,'spoken':True,'cancel':threading.Event(),'transport':None,'executing_action':True,'conversation':self.identity}
        with patch.object(self.runtime._voice,'stop'):
            self.runtime.cancel_chat()
        self.assertTrue(self.runtime._job['cancel'].is_set())

    def test_reply_audio_tracks_active_speech_and_clears_after_failure(self):
        audio=None
        def speak(text):
            self.assertTrue(audio.speaking)
            raise RuntimeError('fixture output failed')
        audio=ReplyAudio(speak,threading.Event());audio.add('Hello.',flush=True);audio.finish()
        self.assertFalse(audio.speaking)
        self.assertIn('fixture output failed',audio.error)
