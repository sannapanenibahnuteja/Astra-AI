import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from desktop.speaker import SpeakerProfile
from desktop.voice import Voice
from desktop.runtime import Runtime


class SpeakerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.profile = SpeakerProfile(self.temp.name)
        self.addCleanup(self.profile.close)
        self.audio = np.ones(48000*3, dtype=np.float32)*.1

    def test_three_samples_encrypted_reload_and_delete(self):
        with patch.object(self.profile, 'embedding', return_value=np.array([1.,0.],dtype=np.float32)):
            self.assertFalse(self.profile.enroll('Bhanu',self.audio,48000)['enrolled'])
            self.assertFalse(self.profile.enroll('Bhanu',self.audio,48000)['enrolled'])
            self.assertTrue(self.profile.enroll('Bhanu',self.audio,48000)['enrolled'])
            self.assertNotIn(b'Bhanu',self.profile.path.read_bytes())
            restored = SpeakerProfile(self.temp.name)
            self.assertEqual(restored.status()['name'],'Bhanu')
            restored.clear()
            self.assertFalse(restored.path.exists())
            self.assertFalse(restored.status()['enrolled'])

    def test_unknown_and_short_speech_never_match(self):
        self.profile._profile = {'name':'Owner','vector':np.array([1.,0.])}
        with patch.object(self.profile, 'embedding', return_value=np.array([0.,1.])):
            self.assertEqual(self.profile.identify(self.audio,48000)['state'],'unknown')
        with patch.object(self.profile, 'embedding', side_effect=ValueError('Too short')):
            result=self.profile.identify(self.audio,48000)
            self.assertEqual(result['state'],'uncertain')
            self.assertEqual(result['name'],'')

    def test_matching_and_inconsistent_enrollment(self):
        with patch.object(self.profile, 'embedding', side_effect=[np.array([1.,0.]),np.array([0.,1.])]):
            self.profile.enroll('Owner',self.audio,48000)
            with self.assertRaises(ValueError): self.profile.enroll('Owner',self.audio,48000)
        self.assertEqual(self.profile.status()['samples'],1)
        self.profile._profile={'name':'Owner','vector':np.array([1.,0.])}
        with patch.object(self.profile, 'embedding', return_value=np.array([1.,0.])):
            self.assertEqual(self.profile.identify(self.audio,48000)['name'],'Owner')

    def test_optional_off_does_not_run_matching(self):
        voice = Voice(); voice.speaker=self.profile
        with patch.object(self.profile,'identify') as identify:
            result=voice._recognize_speaker({'text':'Hello'},self.audio,48000,None)
            self.assertNotIn('speaker',result)
            identify.assert_not_called()
        voice.speaker_enabled=True
        result=voice._recognize_speaker({'text':'Hello'},self.audio,48000,None)
        self.assertEqual(result['speaker']['state'],'not_enrolled')

    def test_default_off_and_settings_validation(self):
        runtime=Runtime(self.temp.name)
        self.assertFalse(runtime.bootstrap()['settings']['speaker_enabled'])
        with self.assertRaises(ValueError): runtime.save_settings({'speaker_enabled':'yes'})
        runtime.save_settings({'speaker_enabled':True})
        self.assertTrue(runtime._voice.speaker_enabled)
        runtime.save_settings({'speaker_enabled':False})
        self.assertFalse(runtime._voice.speaker_enabled)
        self.assertEqual(runtime._voice.last_speaker['state'],'disabled')

    def test_bad_profile_is_not_identified(self):
        self.profile.path.write_bytes(b'corrupt')
        restored=SpeakerProfile(self.temp.name)
        self.assertFalse(restored.status()['enrolled'])
        self.assertTrue(restored.status()['error'])
        self.assertEqual(restored.identify(self.audio,48000)['state'],'not_enrolled')

    def test_identity_context_only_for_current_captured_voice(self):
        import time
        runtime=Runtime(self.temp.name)
        runtime.save_settings({'speaker_enabled':True})
        speaker={'state':'matched','name':'Bhanu','similarity':.9}
        runtime._voice.last_speaker=speaker
        with patch.object(runtime._commands,'plan',return_value=None), patch('desktop.runtime.ChatConnection') as model:
            model.return_value.stream.return_value=iter([{'message':{'content':'Hello'},'done':True}])
            job=runtime.start_chat(runtime.new_conversation(),'Who am I?',True,speaker)
            for _ in range(100):
                if runtime.poll_chat(job)['done']: break
                time.sleep(.01)
            self.assertIn('Local voice profile match',model.call_args.args[1]['messages'][0]['content'])
            model.return_value.stream.return_value=iter([{'message':{'content':'Hello'},'done':True}])
            job=runtime.start_chat(runtime.new_conversation(),'Who am I?',True)
            for _ in range(100):
                if runtime.poll_chat(job)['done']: break
                time.sleep(.01)
            self.assertNotIn('Local voice profile match',model.call_args.args[1]['messages'][0]['content'])

    def test_short_silence_and_invalid_audio_rejected(self):
        for audio in (np.zeros(48000*3),np.ones(4800),np.array([np.nan]*48000*3)):
            with self.assertRaises(ValueError): self.profile.embedding(audio,48000)
