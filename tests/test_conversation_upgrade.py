import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import numpy as np
from desktop.runtime import Runtime
from desktop.reply_audio import ReplyAudio
from desktop.duplex_audio import TurnDetector, BLOCK
from desktop import conversation


class ConversationUpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.runtime=Runtime(self.temp.name); self.identity=self.runtime.new_conversation()

    def wait(self,job):
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            value=self.runtime.poll_chat(job)
            if value['done']: return value
            time.sleep(.01)
        self.fail('Conversation did not finish')

    def send(self,text,spoken=False):
        if spoken: self.runtime._voice._hold=True
        return self.wait(self.runtime.start_chat(self.identity,text,spoken))

    def test_modes_pauses_and_vocabulary_persist_with_validation(self):
        self.send('Switch to tutor mode')
        self.send('Give me more time to think')
        self.runtime.save_settings({'voice_vocabulary':'Bhanu, Hyderabad'})
        reopened=Runtime(self.temp.name)
        self.assertEqual(reopened._store.settings()['conversation_mode'],'tutor')
        self.assertEqual(reopened._voice.turn_pause_ms,1800)
        self.assertEqual(reopened._voice.vocabulary,'Bhanu, Hyderabad')
        for change in [{'conversation_mode':'made up'},{'turn_pause_ms':True},{'stream_voice':'yes'},{'voice_vocabulary':'x'*1001}]:
            with self.assertRaises(ValueError): self.runtime.save_settings(change)
        self.assertIsNone(conversation.preference('Do not switch to tutor mode'))

    def test_patient_endpoint_allows_a_thinking_pause(self):
        detector=TurnDetector();detector.quiet_frames=180
        for _ in range(40): detector.feed(np.full(BLOCK,.03,np.float32),.99)
        for _ in range(120): self.assertIsNone(detector.feed(np.zeros(BLOCK,np.float32),0)[1])
        for _ in range(40): detector.feed(np.full(BLOCK,.03,np.float32),.99)
        audio=None
        for _ in range(180):
            _,chunk,_=detector.feed(np.zeros(BLOCK,np.float32),0)
            if chunk is not None: audio=chunk
        self.assertIsNotNone(audio)
        self.assertFalse(detector.started)

    def test_numeric_correction_reapproves_instead_of_executing(self):
        self.runtime._pending[self.identity]={'steps':[{'action':'volume','target':'40','confirm':True}], 'agent':None}
        with patch.object(self.runtime._commands,'execute',return_value='Volume changed') as execute:
            result=self.send('No, I meant fifty percent')
            self.assertIn('volume 50',result['text']); execute.assert_not_called()
            pending=self.runtime._pending[self.identity]
            self.assertEqual(pending['steps'][0]['target'],'50')
            self.send('yes');execute.assert_called_once()

    def test_reminder_day_correction_preserves_content_time_and_channel(self):
        due=datetime.now()+timedelta(days=2)
        command={'action':'reminder_add','target':'Take a break','value':str(due.timestamp()),'destination':'local','confirm':True}
        self.runtime._pending[self.identity]={'steps':[command],'agent':None}
        result=self.send('No, I meant Friday')
        self.assertIn('Should I',result['text'])
        corrected=self.runtime._pending[self.identity]['steps'][0]
        self.assertEqual(datetime.fromtimestamp(float(corrected['value'])).weekday(),4)
        self.assertEqual(datetime.fromtimestamp(float(corrected['value'])).time(),due.time())
        self.assertEqual(corrected['target'],'Take a break')
        self.assertEqual(corrected['destination'],'local')
        self.assertEqual(self.runtime._commands.reminders.items(),[])

    def test_user_can_request_reminder_approval_then_correct_and_cancel(self):
        waiting=self.send('Remind me in two days to take a break, and check with me first')
        self.assertIn('Should I',waiting['text'])
        self.assertEqual(self.runtime._commands.reminders.items(),[])
        corrected=self.send('No, I meant Friday')
        self.assertIn('Should I',corrected['text'])
        self.send('cancel')
        self.assertEqual(self.runtime._commands.reminders.items(),[])

    def test_unknown_correction_retains_pending_selection(self):
        pending={'steps':[{'action':'volume','target':'40','confirm':True}],'agent':None}
        self.runtime._pending[self.identity]=pending
        result=self.send('Actually louder than that')
        self.assertIn('percentage',result['text'])
        self.assertEqual(self.runtime._pending[self.identity],pending)

    def test_streaming_speaks_before_model_finishes_and_not_twice(self):
        spoken=threading.Event(); calls=[]
        def speak(text): calls.append(text);spoken.set();return True
        def chunks():
            yield {'message':{'content':'First sentence. '}}
            self.assertTrue(spoken.wait(2),'First sentence waited for the complete answer')
            yield {'message':{'content':'Second sentence.'},'done':True}
        model=Mock();model.stream.side_effect=chunks
        with patch.object(self.runtime,'speak',side_effect=speak),patch('desktop.runtime.ChatConnection',return_value=model):
            result=self.send('Explain a computer',True)
        self.assertTrue(result['voice_managed'])
        self.assertEqual(calls,['First sentence.','Second sentence.'])

    def test_barge_in_stops_stream_and_preserves_confirmation(self):
        command={'action':'volume','target':'40','confirm':True}
        def speak(text): self.runtime._voice_interrupt();return False
        with patch.object(self.runtime._commands,'plan',return_value=command),patch.object(self.runtime,'speak',side_effect=speak):
            result=self.send('Set a volume',True)
        self.assertIn('[Response stopped.]',result['text'])
        self.assertIn(self.identity,self.runtime._pending)
        self.assertEqual(self.runtime._pending[self.identity]['steps'][0],command)

    def test_answer_edit_uses_history_and_cannot_repeat_actions(self):
        self.runtime._store.append(self.identity,'user','Explain a computer')
        self.runtime._store.append(self.identity,'assistant','A computer processes instructions.')
        model=Mock();model.stream.return_value=iter([{'message':{'content':'It follows instructions.'},'done':True}])
        with patch('desktop.runtime.ChatConnection',return_value=model) as request:
            result=self.send('Shorter')
        self.assertEqual(result['text'],'It follows instructions.')
        payload=request.call_args.args[1]
        self.assertEqual(payload['tools'],[])
        self.assertIn('A computer processes instructions.',str(payload['messages']))

    def test_model_cannot_claim_execution_without_tools(self):
        model=Mock(); model.stream.return_value=iter([{'message':{'content':'I closed all your windows.'},'done':True}])
        with patch('desktop.runtime.ChatConnection',return_value=model),patch.object(self.runtime._commands,'execute') as execute:
            result=self.send('Please tidy up my workspace')
        execute.assert_not_called()
        self.assertIn('Nothing was changed',result['text'])

    def test_unverified_launch_stops_dependent_action_and_replay(self):
        steps=[{'action':'open','target':'notepad'},{'action':'type_text','target':'hello','window':'notepad'}]
        with patch.object(self.runtime._commands,'plan',return_value=steps),patch.object(self.runtime._commands,'execute',return_value='Asked Windows to launch notepad, but I could not verify a visible app window.') as execute:
            result=self.send('open notepad and type hello')
        self.assertEqual(execute.call_count,1)
        self.assertIn('Stopped dependent steps',result['error'])
        self.assertEqual(self.runtime._store.recent_actions(self.identity),[])

    def test_expired_confirmation_never_executes(self):
        self.runtime._pending[self.identity]={'steps':[{'action':'lock','target':'','confirm':True}],'expires':time.monotonic()-1}
        model=Mock();model.stream.return_value=iter([{'message':{'content':'What should I confirm?'},'done':True}])
        with patch('desktop.runtime.ChatConnection',return_value=model),patch.object(self.runtime._commands,'execute') as execute:
            self.send('yes');execute.assert_not_called()

    def test_speech_failure_surfaces_and_cancel_discards_queued_sentences(self):
        cancel=threading.Event();calls=[]
        def speak(text): calls.append(text);cancel.set();return False
        audio=ReplyAudio(speak,cancel);audio.add('First. Second. Third. ',flush=True);audio.finish()
        self.assertEqual(calls,['First.'])
        error=ReplyAudio(Mock(side_effect=RuntimeError('output missing')),threading.Event())
        error.add('Hello.',flush=True);error.finish()
        self.assertIn('output missing',error.error)

    def test_recent_setter_correction_is_scoped_and_runs_without_reapproval(self):
        self.runtime._store.record_action(self.identity,{'action':'brightness','target':'40','display':'2'},'Brightness changed')
        with patch.object(self.runtime._commands,'execute',return_value='Brightness is 50%') as execute:
            result=self.send('No, I meant fifty percent')
        self.assertIn('50%',result['text'])
        command=execute.call_args.args[0]
        self.assertEqual((command['target'],command['display'],command['confirm']),('50','2',False))

    def test_self_correction_executes_only_the_replacement(self):
        with patch.object(self.runtime._commands,'execute',return_value='Opened calculator') as execute:
            self.send('open notepad, no actually open calculator')
        execute.assert_called_once()
        self.assertEqual(execute.call_args.args[0]['target'],'calculator')
        for text in ['Type open notepad, no actually open calculator in Notepad', 'Explain open notepad, no actually open calculator', 'open "no actually open calculator"']:
            self.assertEqual(conversation.repair_utterance(text),text)
