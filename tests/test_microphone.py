import unittest
from unittest.mock import patch, Mock
import numpy as np
from desktop.microphone import calibration, gain_for, input_device, validate
from desktop.voice import Voice

class MicrophoneTests(unittest.TestCase):
    def tone(self, gain=.001):
        return (np.sin(np.arange(16000*5)*2*np.pi*180/16000)*gain).astype(np.float32)

    def test_quiet_microphone_gets_bounded_gain_for_exact_device(self):
        profile=calibration('device-a','Built in',.00001,self.tone(),16000)
        self.assertEqual(profile['gain'],16)
        self.assertEqual(gain_for(profile,'device-a'),16)
        self.assertEqual(gain_for(profile,'device-b'),1)
        validate(profile)

    def test_hiss_silence_clipping_and_short_speech_do_not_calibrate(self):
        rng=np.random.default_rng(4)
        for audio in [np.zeros(16000*5),rng.normal(0,.005,16000*5),np.ones(16000*5),self.tone()[:16000]]:
            with self.assertRaises(ValueError):calibration('a','Mic',.001,audio,16000)

    def test_bad_profiles_cannot_amplify_input(self):
        for value in [None,{'gain':1000},{'device':'a','name':'Mic','noise_rms':0,'speech_rms':.1,'gain':float('nan')}]:
            self.assertEqual(gain_for(value,'a'),1)
            with self.assertRaises(ValueError):validate(value)

    def test_same_wasapi_input_as_conversation(self):
        sd=Mock();sd.query_hostapis.return_value=[{'name':'Windows WASAPI','default_input_device':4}]
        sd.query_devices.return_value={'name':'Built in','default_samplerate':48000}
        index,device,key=input_device(sd)
        self.assertEqual(index,4);self.assertEqual(key,'Windows WASAPI:Built in')
        sd.query_devices.assert_called_once_with(4)

    def test_manual_enrollment_keeps_voice_below_old_threshold(self):
        voice=Voice();voice._pause_wake=Mock();voice._recognize_speaker=Mock(return_value={'enrollment':{'samples':1}})
        count=0
        class Stream:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):
                nonlocal count
                if n!=800:return np.zeros((n,1),np.float32),False
                count+=1
                if count==200:voice.finish_enrollment()
                # Below the old .003 gate, but clear voice with five seconds of speech.
                return self_audio[:n].reshape(-1,1),False
        self_audio=self.tone(.0009)
        with patch('desktop.microphone.input_device',return_value=(4,{'name':'Built in','default_samplerate':16000},'device-a')),patch('sounddevice.InputStream',return_value=Stream()),patch('winsound.Beep'):
            result=voice.listen(enrollment='Test')
        self.assertEqual(result['enrollment']['samples'],1)
        self.assertEqual(count,200)
        self.assertGreater(len(voice._recognize_speaker.call_args.args[1]),16000*9)

    def test_empty_enrollment_reaches_quality_checks_instead_of_dropping_capture(self):
        voice=Voice();voice._pause_wake=Mock();voice._recognize_speaker=Mock(side_effect=ValueError('Not enough clear speech'))
        count=0
        class Stream:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):
                nonlocal count
                if n==800:
                    count+=1
                    if count==100:voice.finish_enrollment()
                return np.zeros((n,1),np.float32),False
        with patch('desktop.microphone.input_device',return_value=(4,{'name':'Mic','default_samplerate':16000},'a')),patch('sounddevice.InputStream',return_value=Stream()),patch('winsound.Beep'):
            with self.assertRaisesRegex(ValueError,'Not enough clear speech'):voice.listen(enrollment='Test')
        self.assertFalse(voice._operation.locked())

    def test_guided_calibration_measures_noise_then_voice_without_changing_input(self):
        voice=Voice();voice._pause_wake=Mock()
        class Stream:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):
                samples=np.zeros(n,np.float32) if voice.status()['microphone_stage']=='noise' else self_audio[:n]
                return samples.reshape(-1,1),False
        self_audio=self.tone()
        with patch('desktop.microphone.input_device',return_value=(4,{'name':'Built in','default_samplerate':16000},'device-a')),patch('sounddevice.InputStream',return_value=Stream()):
            self.assertTrue(voice.calibrate_microphone('noise')['noise_ready'])
            result=voice.calibrate_microphone('speech')
        self.assertEqual(result['profile']['device'],'device-a')
        self.assertEqual(result['profile']['gain'],16)
        self.assertFalse(voice._operation.locked())

    def test_cancelled_calibration_preserves_previous_profile(self):
        voice=Voice();voice._pause_wake=Mock();voice.microphone_calibration={'previous':'untouched'}
        class Stream:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):
                voice.stop()
                return np.zeros((n,1),np.float32),False
        with patch('desktop.microphone.input_device',return_value=(4,{'name':'Mic','default_samplerate':16000},'a')),patch('sounddevice.InputStream',return_value=Stream()):
            self.assertTrue(voice.calibrate_microphone('noise')['cancelled'])
        self.assertEqual(voice.microphone_calibration,{'previous':'untouched'})
        self.assertFalse(voice._operation.locked())
