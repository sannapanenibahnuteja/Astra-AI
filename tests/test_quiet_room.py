import tempfile
import unittest
from unittest.mock import Mock, patch
import numpy as np
from desktop.voice_evidence import interruption_speech
from desktop.duplex_audio import completed_speech_candidate, DuplexAudio, RATE
from desktop.audio_pipeline import validate_options
from desktop.runtime import Runtime


class QuietRoomTests(unittest.TestCase):
    def signal(self):
        return (.005*np.sin(2*np.pi*200*np.arange(RATE)/RATE)).astype(np.float32)

    def test_quiet_utterance_can_reach_final_checks_with_more_gaps(self):
        self.assertFalse(completed_speech_candidate(False,38,160))
        self.assertTrue(completed_speech_candidate(False,38,160,'quiet'))
        self.assertFalse(completed_speech_candidate(False,8,160,'quiet'))
        self.assertFalse(completed_speech_candidate(False,38,500,'quiet'))

    def test_shorter_neural_speech_span_is_accepted_only_in_quiet_mode(self):
        with patch('faster_whisper.vad.get_speech_timestamps', return_value=[{'start':1000,'end':7000}]) as vad:
            self.assertFalse(interruption_speech(self.signal()))
            self.assertTrue(interruption_speech(self.signal(),'quiet'))
            self.assertEqual(vad.call_args.args[1].threshold,.55)

    def test_quiet_mode_never_bypasses_failed_neural_inference(self):
        with patch('faster_whisper.vad.get_speech_timestamps', side_effect=RuntimeError('unavailable')):
            self.assertFalse(interruption_speech(self.signal(),'quiet'))

    def test_actual_neural_detector_still_rejects_seeded_noise_and_taps(self):
        rng=np.random.default_rng(151)
        noise=rng.normal(0,.01,RATE*2).astype(np.float32)
        taps=np.zeros(RATE*2,np.float32)
        for start in (10000,25000,47000):taps[start:start+100]=rng.normal(0,.3,100)
        self.assertFalse(interruption_speech(noise,'quiet'))
        self.assertFalse(interruption_speech(taps,'quiet'))
        self.assertFalse(interruption_speech(np.zeros(RATE),'quiet'))

    def test_more_sensitive_vad_keeps_authorization_and_no_ducking(self):
        from desktop.voice import Voice
        voice=Voice();voice.audio_options['audio_room_mode']='quiet'
        engine=DuplexAudio(Mock(),Mock(),voice.audio_options);self.addCleanup(engine.close)
        voice.configure_interruptions(engine)
        self.assertEqual(engine.authorize_interrupt,voice._authorize_interrupt)
        self.assertFalse(engine.options['audio_fast_barge_in'])

    def test_mode_validation_and_active_session_change_is_rejected(self):
        for mode in ('disabled',None,True,[]):
            with self.assertRaises(ValueError):validate_options({'audio_room_mode':mode})
        with tempfile.TemporaryDirectory() as root:
            runtime=Runtime(root)
            try:
                runtime._voice._hold=True
                with self.assertRaises(ValueError):runtime.save_settings({'audio_room_mode':'quiet'})
                self.assertEqual(runtime._store.settings()['audio_room_mode'],'balanced')
                runtime._store.save_settings({'audio_room_mode':'quiet'})
                with self.assertRaises(ValueError):runtime.save_settings({'audio_room_mode':'quiet'})
                runtime._voice._hold=False
                runtime.save_settings({'audio_room_mode':'quiet'})
                self.assertEqual(runtime._voice.audio_options['audio_room_mode'],'quiet')
                self.assertEqual(runtime._voice.speaker.threshold,.65)
            finally:runtime._voice.close()


if __name__=='__main__':unittest.main()
