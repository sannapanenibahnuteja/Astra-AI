import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from desktop.speaker import SpeakerProfile, SpeakerProfiles
from desktop.storage import Store
from desktop.voice import Voice
from desktop.runtime import Runtime


class VoiceProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.bank=SpeakerProfiles(self.temp.name); self.addCleanup(self.bank.close)
        self.audio=(.1*np.sin(np.arange(48000*4)*2*np.pi*180/48000)).astype(np.float32)

    def enroll(self,name,vector):
        with patch.object(self.bank.extractor,'embedding',return_value=np.array(vector,dtype=np.float32)):
            for _ in range(3): result=self.bank.enroll(name,self.audio,48000)
        return next(p['id'] for p in result['profiles'] if p['name']==name)

    def test_multiple_people_reload_and_personality(self):
        a=self.enroll('Alice',[1,0]); b=self.enroll('Ben',[0,1])
        self.bank.personalize(a,'funny'); self.bank.personalize(b,'serious')
        restored=SpeakerProfiles(self.temp.name); self.addCleanup(restored.close)
        self.assertEqual(restored.preferences(a)['personality_preset'],'funny')
        self.assertEqual(restored.preferences(b)['personality_preset'],'serious')
        with patch.object(restored.extractor,'embedding',return_value=np.array([1.,0.])):
            first=restored.identify(self.audio,48000); second=restored.identify(self.audio,48000)
        self.assertEqual(first['profile_id'],a); self.assertTrue(first['profile_changed']); self.assertFalse(second['profile_changed'])
        with patch.object(restored.extractor,'embedding',return_value=np.array([0.,1.])):
            self.assertEqual(restored.identify(self.audio,48000)['profile_id'],b)

    def test_ties_and_noise_do_not_switch(self):
        a=self.enroll('Alice',[1,0]); self.enroll('Ben',[1,0]); self.bank.active=a
        with patch.object(self.bank.extractor,'embedding',return_value=np.array([1.,0.])):
            result=self.bank.identify(self.audio,48000)
        self.assertEqual(result['state'],'uncertain'); self.assertEqual(self.bank.active,a)
        self.assertEqual(self.bank.identify(np.zeros(48000*4),48000)['state'],'uncertain')

    def test_delete_one_preserves_others_and_legacy_import(self):
        legacy=SpeakerProfile(self.temp.name); self.addCleanup(legacy.close)
        with patch.object(legacy,'embedding',return_value=np.array([1.,0.])):
            for _ in range(3): legacy.enroll('Previous owner',self.audio,48000)
        restored=SpeakerProfiles(self.temp.name); self.addCleanup(restored.close)
        self.assertIn('legacy',restored.profiles)
        a=self.enroll('Alice',[0,1]); b=self.enroll('Ben',[1,0])
        self.bank.clear(a); self.assertIn(b,self.bank.profiles); self.assertNotIn(a,self.bank.profiles)

    def test_personal_conversations_and_memories_are_scoped(self):
        store=Store(self.temp.name); a=store.voice_conversation('a'); b=store.voice_conversation('b')
        self.assertNotEqual(a,b); self.assertEqual(store.voice_conversation('a'),a)
        store.remember('drink','tea','a'); store.remember('drink','coffee','b'); store.remember('drink','water')
        self.assertEqual(store.memories('a')[0]['value'],'tea'); self.assertEqual(store.memories('b')[0]['value'],'coffee')
        store.forget('drink','a'); self.assertEqual(store.memories('a'),[]); self.assertEqual(store.memories()[0]['value'],'water')
        store.delete_conversation(a); self.assertNotEqual(store.voice_conversation('a'),a)

    def test_enrollment_allows_pauses_and_skips_transcription(self):
        voice=Voice(); voice.speaker=self.bank
        engine=Mock(); engine.detector=SimpleNamespace(quiet_frames=65)
        def receive(cancel):
            self.assertEqual(engine.detector.quiet_frames,180); return self.audio
        engine.receive.side_effect=receive
        with patch.object(voice,'_ensure_duplex',return_value=engine), patch.object(voice,'transcribe') as transcript, patch.object(self.bank.extractor,'embedding',return_value=np.array([1.,0.])):
            result=voice.listen(enrollment='Alice')
        transcript.assert_not_called(); self.assertEqual(result['enrollment']['samples'],1); self.assertEqual(engine.detector.quiet_frames,65)

    def test_pause_is_restored_on_capture_error(self):
        voice=Voice(); engine=Mock(); engine.detector=SimpleNamespace(quiet_frames=45); engine.receive.side_effect=RuntimeError('device disconnected')
        with patch.object(voice,'_ensure_duplex',return_value=engine):
            with self.assertRaises(RuntimeError): voice.listen(enrollment='Alice')
        self.assertEqual(engine.detector.quiet_frames,45)

    def test_fallback_announces_ready_only_after_input_setup(self):
        voice=Voice(); voice.speaker=self.bank
        stream=MagicMock(); stream.__enter__.return_value=stream
        def entered():
            self.assertEqual(voice.status()['phase'],'preparing'); return stream
        stream.__enter__.side_effect=entered
        calls=0
        def read(count):
            nonlocal calls
            calls+=1
            if calls<=2 or calls>82: return np.zeros((count,1),np.float32),False
            self.assertEqual(voice.status()['phase'],'listening')
            return self.audio[:count].reshape(-1,1),False
        stream.read.side_effect=read
        with patch.object(voice,'_ensure_duplex',return_value=None), patch('sounddevice.query_devices',return_value={'default_samplerate':48000}), patch('sounddevice.InputStream',return_value=stream), patch('winsound.Beep'), patch.object(self.bank.extractor,'embedding',return_value=np.array([1.,0.])):
            result=voice.listen(enrollment='Alice')
        self.assertEqual(result['enrollment']['samples'],1)

    def test_balanced_calibration_preserves_strict_cutoff(self):
        profile=SpeakerProfile(self.temp.name); self.addCleanup(profile.close)
        vectors=[np.array([1.,0.]),np.array([.6,.8]),np.array([.8,.6])]
        with patch.object(profile,'embedding',side_effect=vectors):
            for _ in range(3): profile.enroll('Alice',self.audio,48000)
        self.assertAlmostEqual(profile._profile['balanced_threshold'],.55)
        vector=np.array([.57,np.sqrt(1-.57**2)])
        # Consensus remains required, and Strict remains at .75.
        profile.threshold=.75
        with patch.object(profile,'embedding',return_value=vector): self.assertEqual(profile.identify(self.audio,48000)['threshold'],.75)

    def test_untrusted_voice_result_cannot_select_profile(self):
        runtime=Runtime(self.temp.name); self.addCleanup(runtime._voice.close)
        current=runtime.new_conversation(); runtime.save_settings({'speaker_enabled':True})
        result={'state':'matched','profile_id':'fake','name':'Alice'}
        self.assertEqual(runtime.voice_conversation(current,result),current)

    def test_native_reply_greets_only_on_speaker_change(self):
        runtime=Runtime(self.temp.name); self.addCleanup(runtime._voice.close)
        runtime.save_settings({'speaker_enabled':True}); runtime._voice.speaker=self.bank
        profile=self.enroll('Alice',[1,0])
        speaker={'state':'matched','name':'Alice','profile_id':profile,'profile_changed':True}
        runtime._voice.last_speaker=speaker
        identity=runtime.voice_conversation(None,speaker)
        with patch.object(runtime._commands,'capture_explorer'):
            job=runtime.start_chat(identity,'What time is it?',True,speaker)
            for _ in range(200):
                response=runtime.poll_chat(job)
                if response['done']: break
                time.sleep(.01)
        self.assertTrue(response['done']); self.assertTrue(response['text'].startswith('Hi, Alice.'))

    def test_unknown_requests_reach_local_llm_without_native_guess(self):
        runtime=Runtime(self.temp.name); self.addCleanup(runtime._voice.close)
        with patch.object(runtime._commands,'capture_explorer'), patch('desktop.runtime.ChatConnection') as model, patch.object(runtime._commands,'execute') as execute:
            model.return_value.stream.return_value=iter([{'message':{'content':'Which calculator app do you mean?'},'done':True}])
            job=runtime.start_chat(runtime.new_conversation(),'Could you get the calculator ready so I can work out these costs?')
            for _ in range(200):
                if runtime.poll_chat(job)['done']: break
                time.sleep(.01)
            self.assertTrue(model.called); execute.assert_not_called()

    def test_deleted_voice_memories_remain_reviewable(self):
        runtime=Runtime(self.temp.name); self.addCleanup(runtime._voice.close)
        runtime._voice.speaker=self.bank; runtime.save_settings({'speaker_enabled':True})
        identity=self.enroll('Alice',[1,0])
        speaker={'state':'matched','name':'Alice','profile_id':identity}
        runtime._voice.last_speaker=speaker
        runtime.voice_conversation(None,speaker)
        runtime.save_memory('drink','tea',identity)
        runtime.forget_speaker(identity)
        self.assertIn({'id':identity,'name':'Alice'},runtime.memory_spaces()['spaces'])
        self.assertEqual(runtime.profile_memories(identity)[0]['value'],'tea')
        runtime.delete_memory('drink',identity)
        self.assertEqual(runtime.profile_memories(identity),[])


if __name__=='__main__': unittest.main()
