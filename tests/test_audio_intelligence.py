"""Signal, concurrency, privacy and action-boundary regression tests."""
import tempfile
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
import numpy as np
from desktop.audio_pipeline import Beamformer, EnvironmentMonitor, PreviewFrame, SourceSelector, recognition_samples, validate_options, validate_extraction
from desktop.conversational import AttentionEngine, DialogueState, ActionLedger, PauseModel, QualityMetrics, response_plan, SpeechBudget, semantic_hint
from desktop.duplex_audio import DuplexAudio, TurnDetector, CapturedTurn, BLOCK, RATE
from desktop.streaming_asr import PreviewWorker
from desktop.voice import Voice
from desktop.runtime import Runtime


class AudioStageTests(unittest.TestCase):
    def test_array_alignment_across_frame_boundaries(self):
        beam=Beamformer([0,2])
        first=beam.process(np.array([[0,1],[0,0],[0,0]],np.float32))
        second=beam.process(np.zeros((3,2),np.float32))
        np.testing.assert_allclose(np.r_[first,second],[0,0,.5,0,0,0])
        with self.assertRaises(ValueError):beam.process(np.zeros((10,1)))

    def test_resampler_rejects_out_of_band_aliases(self):
        t=np.arange(RATE)/RATE
        low=recognition_samples(np.sin(2*np.pi*500*t))
        high=recognition_samples(np.sin(2*np.pi*16000*t))
        self.assertEqual(len(low),16000)
        self.assertLess(np.std(high),np.std(low)*.05)

    def test_noise_estimate_waits_for_quiet_not_assistant_output(self):
        monitor=EnvironmentMonitor()
        quiet=np.random.default_rng(3).normal(0,.001,BLOCK).astype(np.float32)
        for _ in range(30):monitor.observe(quiet,quiet,False,True)
        self.assertIsNone(monitor.current['snr_db'])
        for _ in range(30):monitor.observe(quiet,quiet,False,False)
        signal=.03*np.sin(2*np.pi*500*np.arange(BLOCK)/RATE)
        for _ in range(5):monitor.observe(signal,signal,True,False)
        self.assertGreater(monitor.current['snr_db'],15)
        self.assertEqual(monitor.current['environment'],'speech')

    def test_source_choice_needs_consent_hysteresis_and_turn_boundary(self):
        selector=SourceSelector()
        sources={'laptop':{'consented':True,'stable':True,'snr_db':8},'phone':{'consented':False,'stable':True,'snr_db':30}}
        self.assertEqual(selector.choose(sources),'laptop')
        sources['phone']['consented']=True
        for _ in range(5):self.assertEqual(selector.choose(sources,False),'laptop')
        self.assertEqual(selector.choose(sources),'laptop')
        self.assertEqual(selector.choose(sources),'laptop')
        self.assertEqual(selector.choose(sources),'phone')
        sources['phone']['consented']=False
        self.assertIsNone(selector.choose(sources,False))
        self.assertEqual(selector.choose(sources),'laptop')

    def test_invalid_settings_and_extraction_fail_closed(self):
        for value in ({'audio_array_delays':[0]},{'audio_noise_level':True},{'audio_fast_barge_in':'yes'},{'audio_array_delays':[0,999]}):
            with self.assertRaises(ValueError):validate_options(value)
        for audio in (np.zeros(2),np.array([float('nan')]*3),np.zeros((3,1))):
            with self.assertRaises(ValueError):validate_extraction(np.zeros(3),audio)

    def test_ducked_playback_is_the_exact_echo_reference(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.samples=np.full(BLOCK,.5,np.float32);engine.duck_until=time.monotonic()+1
        outgoing=np.empty((BLOCK,2),np.float32)
        engine._audio(np.zeros((BLOCK,1),np.float32),outgoing,BLOCK,SimpleNamespace(outputBufferDacTime=.02,inputBufferAdcTime=0),None)
        _,reference,_=engine.blocks.get_nowait()
        np.testing.assert_array_equal(reference,outgoing[:,0])
        self.assertAlmostEqual(float(reference[-1]),.09,places=5)
        self.assertGreater(reference[0],reference[-1])

    def test_semantics_allow_a_thinking_pause_but_remain_bounded(self):
        detector=TurnDetector();detector.adaptive=True;detector.quiet_frames=65
        voice=np.full(BLOCK,.02,np.float32);silence=np.zeros(BLOCK,np.float32)
        for _ in range(50):detector.feed(voice,.99)
        detector.semantic_pause_ms=semantic_hint('open the file and')['pause_ms']
        for _ in range(120):self.assertIsNone(detector.feed(silence,0)[1])
        final=None
        for _ in range(60):
            _,audio,_=detector.feed(silence,0)
            if audio is not None:final=audio
        self.assertIsNotNone(final);self.assertEqual(detector.semantic_pause_ms,0)

    def test_incomplete_hints_never_authorize_actions(self):
        hint=semantic_hint('send an email to')
        self.assertFalse(hint['complete']);self.assertFalse(hint['may_execute'])
        self.assertEqual(hint['domain'],'mail')


class PreviewTests(unittest.TestCase):
    def frame(self,serial):return PreviewFrame(serial,np.zeros(BLOCK),np.zeros(BLOCK),time.monotonic())

    def test_stale_decode_never_publishes_after_end(self):
        entered=threading.Event();release=threading.Event();finished=threading.Event();published=[]
        def decode(frame):entered.set();release.wait(2);finished.set();return 'open youtube'
        worker=PreviewWorker(decode,lambda *args:published.append(args));self.addCleanup(worker.close)
        worker.begin(4);worker.submit(self.frame(4));self.assertTrue(entered.wait(1))
        worker.end(4);release.set();self.assertTrue(finished.wait(1));worker.close()
        self.assertEqual(published,[])

    def test_latest_only_queue_is_bounded_and_new_turn_drops_old(self):
        gate=threading.Event();entered=threading.Event();done=threading.Event();seen=[];published=[]
        def decode(frame):seen.append(frame.serial);entered.set();gate.wait(2);return 'hello bob'
        def publish(*args):published.append(args);done.set()
        worker=PreviewWorker(decode,publish);self.addCleanup(worker.close)
        worker.begin(1);worker.submit(self.frame(1));self.assertTrue(entered.wait(1))
        for _ in range(50):worker.submit(self.frame(1))
        worker.begin(2);worker.submit(self.frame(2));gate.set();self.assertTrue(done.wait(1))
        self.assertEqual(seen,[1,2]);self.assertEqual(published[0][0].serial,2)

    def test_unknown_speaker_and_final_decode_prevent_preview_inference(self):
        voice=Voice();voice._hold=True;voice._model=Mock();voice.speaker_enabled=True
        voice._focus_accept=Mock(return_value=False)
        self.assertIsNone(voice._preview_decode(self.frame(1)))
        voice._model.transcribe.assert_not_called()
        voice._focus_accept.return_value=True;voice._final_decoding.set()
        self.assertIsNone(voice._preview_decode(self.frame(1)))
        voice._model.transcribe.assert_not_called()

    def test_preview_never_waits_for_model_lock(self):
        voice=Voice();voice._hold=True;voice._model=Mock();voice._model_lock.acquire()
        try:self.assertIsNone(voice._preview_decode(self.frame(1)))
        finally:voice._model_lock.release()
        voice._model.transcribe.assert_not_called()

    def test_focus_change_during_identity_inference_invalidates_result(self):
        voice=Voice();voice.speaker_enabled=True;voice.speaker_focus='owner';voice.speaker=Mock()
        def identify(*args,**kwargs):
            voice.speaker_focus='different'
            return {'state':'matched','profile_id':'owner'}
        voice.speaker.identify.side_effect=identify
        self.assertFalse(voice._focus_accept(np.zeros(RATE,np.float32)))
        self.assertEqual(len(voice._verified_samples),0)

    def test_extractor_cannot_bypass_identity_or_feed_invalid_samples(self):
        voice=Voice();voice.target_extractor=Mock();engine=Mock()
        audio=np.full(RATE,.01,np.float32);engine.receive.return_value=CapturedTurn(audio,audio)
        with patch.object(voice,'_ensure_duplex',return_value=engine),patch.object(voice,'_recognize_speaker',return_value={'ignored':True}),patch.object(voice,'transcribe') as asr:
            voice.listen();voice.target_extractor.extract.assert_not_called();asr.assert_not_called()
        voice.target_extractor.extract.return_value=np.zeros(1)
        with patch.object(voice,'_ensure_duplex',return_value=engine),patch.object(voice,'_recognize_speaker',return_value={'speaker':{'state':'matched','profile_id':'owner'}}),patch.object(voice,'transcribe') as asr:
            with self.assertRaises(ValueError):voice.listen()
            asr.assert_not_called()


class ConversationalPolicyTests(unittest.TestCase):
    def test_attention_requires_activation_and_separate_speaker_proof(self):
        engine=AttentionEngine();speaker={'state':'matched'}
        self.assertFalse(engine.evaluate('hey bob open youtube',1,speaker,True)['accept'])
        engine.activate()
        self.assertFalse(engine.evaluate('hey bob open youtube',1,{},True)['accept'])
        self.assertTrue(engine.evaluate('what is gravity',.9,speaker,True)['accept'])
        self.assertFalse(engine.evaluate('he said ask bob about that',1,speaker,True)['accept'])
        engine.disengage();self.assertEqual(engine.snapshot()['state'],'IDLE')

    def test_microturn_attention_and_profile_context_isolation(self):
        attention=AttentionEngine();attention.activate();attention.awaiting_answer=True
        self.assertTrue(attention.evaluate('the second one',.9,{'state':'matched'},True)['accept'])
        dialogue=DialogueState();dialogue.finish('owner','Find a file','1. report.txt\n2. notes.txt')
        self.assertIn('notes.txt',dialogue.resolve('owner','the second one'))
        self.assertEqual(dialogue.resolve('guest','the second one'),'the second one')
        self.assertEqual(dialogue.session('guest').active_goal,'')

    def test_interrupted_reply_can_be_shortened_without_repeating_action(self):
        dialogue=DialogueState();dialogue.session('a').interrupted_response='A long explanation.'
        self.assertIn('A long explanation.',dialogue.resolve('a','shorter'))
        self.assertNotIn('A long explanation.',dialogue.resolve('b','shorter'))

    def test_spoken_privacy_and_budget_leave_full_visual_reply_available(self):
        secret='Your account number is 1234. Your address is private.'
        budget=SpeechBudget(response_plan('public'))
        self.assertEqual(budget.take(secret),'The details are on screen.')
        self.assertEqual(budget.take(secret),'')
        self.assertEqual(SpeechBudget(response_plan('meeting')).take(secret),'')
        self.assertEqual(SpeechBudget(response_plan('fast')).take('First. Second.'),'First. Second.')

    def test_pause_learning_is_derived_bounded_and_respects_explicit_pause(self):
        model=PauseModel();model.observe('owner',[1000,1200])
        self.assertGreater(model.pause('owner',650),650)
        self.assertEqual(model.pause('owner',1800),1800)
        self.assertEqual(model.pause('other',650),650)
        self.assertEqual(set(model.profiles['owner']),{'count','mid_pause_ms'})

    def test_action_ledger_cannot_replay_success_failure_or_cancel(self):
        ledger=ActionLedger();execute=Mock(return_value='done')
        self.assertEqual(ledger.run('1','open',execute),'done')
        self.assertEqual(ledger.run('1','open',execute),'done');execute.assert_called_once()
        failure=Mock(side_effect=RuntimeError('not delivered'))
        with self.assertRaises(RuntimeError):ledger.run('2','send',failure)
        with self.assertRaises(ValueError):ledger.run('2','send',failure)
        failure.assert_called_once()
        ledger.propose('3','delete');ledger.cancel('3')
        with self.assertRaises(ValueError):ledger.run('3','delete',execute)

    def test_aggregate_metrics_do_not_claim_accuracy_or_store_text(self):
        metrics=QualityMetrics();metrics.utterance('a','private name');metrics.utterance('a','private name')
        metrics.timing('asr',100)
        self.assertEqual(metrics.snapshot()['counts']['user_repetitions'],1)
        self.assertNotIn('private name',str(metrics.last))
        self.assertIn('false_activation_rate',metrics.snapshot()['unmeasured'])


class RuntimeIntelligenceTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.runtime=Runtime(temp.name);self.addCleanup(self.runtime._voice.close)
        self.identity=self.runtime.new_conversation()

    def test_autonomy_proposal_then_confirm_and_frozen_action_id(self):
        self.runtime.save_settings({'autonomy_level':2})
        step={'action':'volume','target':'20','confirm':False}
        job={'conversation':self.identity,'cancel':threading.Event(),'text':'','steps':0}
        with patch.object(self.runtime._commands,'execute',return_value='Volume set to 20%.') as execute:
            self.runtime._execute_steps(job,[step]);execute.assert_not_called()
            pending=self.runtime._pending[self.identity]
            key=pending['operation_ids'][0]
            self.assertEqual(pending['steps'],[step])
            job['_approved_action_keys']=pending['operation_ids']
            self.runtime._execute_steps(job,pending['steps'],True)
            execute.assert_called_once()
        self.assertEqual(self.runtime._actions.records[key]['state'],'SUCCEEDED')

    def test_failed_native_launch_is_not_recorded_as_success(self):
        job={'conversation':self.identity,'cancel':threading.Event(),'text':'','steps':0}
        with patch.object(self.runtime._commands,'execute',return_value='Asked Windows to open it.'):
            with self.assertRaises(RuntimeError):self.runtime._execute_steps(job,[{'action':'open','target':'youtube'}])
        self.assertEqual(self.runtime._actions.snapshot()[-1]['state'],'FAILED')
        self.assertEqual(job['steps'],0)

    def test_silent_and_public_apply_even_without_streaming_tts(self):
        with patch.object(self.runtime._voice,'speak',return_value=True) as speak:
            self.runtime.save_settings({'conversation_mode':'silent'})
            self.assertTrue(self.runtime.speak('private text'));speak.assert_not_called()
            self.runtime.save_settings({'conversation_mode':'public'})
            self.runtime.speak('private text');self.assertEqual(speak.call_args.args[0],'The details are on screen.')

    def test_invalid_audio_and_autonomy_never_reach_storage(self):
        for settings in ({'autonomy_level':True},{'autonomy_level':5},{'audio_noise_level':9}):
            with self.assertRaises(ValueError):self.runtime.save_settings(settings)
        self.assertEqual(self.runtime._store.settings()['autonomy_level'],3)

    def test_diagnostics_are_capability_honest(self):
        status=self.runtime.conversation_status()
        self.assertFalse(status['capabilities']['overlapping_speaker_separation'])
        self.assertFalse(status['capabilities']['camera_attention'])
        self.assertEqual(status['actions'],[])

    def test_cancelled_plan_never_starts_native_actions(self):
        cancelled=threading.Event();cancelled.set()
        job={'conversation':self.identity,'cancel':cancelled,'text':'','steps':0}
        with patch.object(self.runtime._commands,'execute') as execute:
            self.runtime._execute_steps(job,[{'action':'open','target':'youtube'},{'action':'volume','target':'20'}])
            execute.assert_not_called()
        self.assertEqual([r['state'] for r in self.runtime._actions.snapshot()],['CANCELLED','CANCELLED'])

    def test_autonomy_suggestion_returns_without_replanning_or_empty_reply(self):
        self.runtime.save_settings({'autonomy_level':1,'voice_enabled':False})
        model=Mock();model.stream.return_value=iter([{'message':{'tool_calls':[{'function':{'name':'windows_action','arguments':{'action':'volume_down','target':'','final_step':True}}}]},'done':True}])
        with patch.object(self.runtime._commands,'plan',return_value=None),patch.object(self.runtime._commands,'execute') as execute,patch('desktop.runtime.ChatConnection',return_value=model) as request:
            job=self.runtime.start_chat(self.identity,'Please make things quieter')
            for _ in range(200):
                result=self.runtime.poll_chat(job)
                if result['done']:break
                time.sleep(.01)
            self.assertTrue(result['done']);self.assertEqual(result['error'],'')
            self.assertIn('Proposed:',result['text']);request.assert_called_once();execute.assert_not_called()
