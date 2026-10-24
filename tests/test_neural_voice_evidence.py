import unittest
import threading
import tempfile
from unittest.mock import Mock, patch
import numpy as np
from desktop.voice_evidence import interruption_speech, learnable_turn
from desktop.voice import Voice
from desktop.duplex_audio import CapturedTurn, RATE
from desktop.duplex_audio import completed_speech_candidate
from desktop.interruption import intended_interruption


class NeuralSpeechTests(unittest.TestCase):
    def signal(self):
        t = np.arange(RATE, dtype=np.float32) / RATE
        return .03 * np.sin(2 * np.pi * 200 * t)

    def test_invalid_silent_tiny_and_short_audio_are_rejected(self):
        for audio in ([], [np.nan] * RATE, [np.inf] * RATE,
                      np.zeros(RATE), np.ones(1000) * .1,
                      self.signal() * .00001, np.ones(RATE * 22) * .1):
            self.assertFalse(interruption_speech(audio))

    def test_neural_not_speech_rejects_even_loud_voiced_acoustics(self):
        with patch('faster_whisper.vad.get_speech_timestamps', return_value=[]):
            self.assertFalse(interruption_speech(self.signal()))

    def test_neural_failure_retains_reply(self):
        with patch('faster_whisper.vad.get_speech_timestamps', side_effect=RuntimeError('model failed')):
            self.assertFalse(interruption_speech(self.signal()))

    def test_short_cough_like_span_rejected_and_speech_span_accepted(self):
        with patch('faster_whisper.vad.get_speech_timestamps', return_value=[{'start':0, 'end':4000}]):
            self.assertFalse(interruption_speech(self.signal()))
        with patch('faster_whisper.vad.get_speech_timestamps', return_value=[{'start':1000, 'end':10000}]):
            self.assertTrue(interruption_speech(self.signal()))

    def test_high_confidence_hallucination_cannot_bypass_neural_rejection(self):
        voice = Voice(); voice.speaker_enabled = True; voice.speaker_focus = 'owner'
        voice.speaker = Mock(); voice.speaker.profiles = {}
        voice.speaker.identify.return_value = {'state':'matched', 'profile_id':'owner'}
        voice._decode_interruption = Mock(return_value={'text':'Hey Bob stop talking', 'confidence':.99, 'needs_review':False})
        turn = CapturedTurn(self.signal(), self.signal(), 1, interruption_ready=True, requires_authorization=True)
        with patch('desktop.voice_evidence.interruption_speech', return_value=False):
            self.assertFalse(voice._authorize_interrupt(turn))
        voice.speaker.identify.assert_not_called()
        voice._decode_interruption.assert_not_called()
        self.assertFalse(voice._interrupt_proofs)

    def test_wake_alone_does_not_stop_reply_but_complete_request_can(self):
        for text in ('Hey Bob', 'Okay Bob', 'Hey Bob thanks for watching'):
            self.assertFalse(intended_interruption(text,.99,False,require_trigger=True))
        self.assertTrue(intended_interruption('Hey Bob please stop talking',.99,False,require_trigger=True))

    def test_actual_neural_model_rejects_seeded_non_speech(self):
        rng = np.random.default_rng(92)
        # Real local ONNX inference, not mocked VAD labels or a speech decoder.
        t = np.arange(RATE * 2) / RATE
        signals = [rng.normal(0,.015,len(t)).astype(np.float32),
                   (.02*np.sin(2*np.pi*60*t)).astype(np.float32)]
        taps = np.zeros(len(t), np.float32)
        for start in (5000,17000,31000,55000):
            taps[start:start+120] = rng.normal(0,.2,120)
        signals.append(taps)
        for signal in signals:
            self.assertFalse(interruption_speech(signal))

    def test_completed_quiet_speech_can_reach_neural_check_without_dense_short_window(self):
        self.assertTrue(completed_speech_candidate(False,80,240))
        self.assertFalse(completed_speech_candidate(False,8,150))
        self.assertFalse(completed_speech_candidate(False,40,150))
        self.assertFalse(completed_speech_candidate(False,50,500))
        self.assertTrue(completed_speech_candidate(True,80,240))


class TrustedLearningTests(unittest.TestCase):
    def result(self):
        return {'text':'open calculator', 'confidence':.95, 'needs_review':False,
                'speaker':{'state':'matched', 'profile_id':'owner'}}

    def test_accepted_matched_user_can_learn(self):
        self.assertTrue(learnable_turn(self.result()))

    def test_no_learning_from_noise_uncertain_other_or_rejected_turns(self):
        for patch_values in ({'ignored':True}, {'text':''}, {'needs_review':True},
                             {'confidence':.7}, {'speaker':{'state':'uncertain'}},
                             {'speaker':{'state':'matched'}}):
            self.assertFalse(learnable_turn({**self.result(), **patch_values}))


class FocusedProfileTests(unittest.TestCase):
    def profiles(self):
        from desktop.speaker import SpeakerProfiles
        profiles = SpeakerProfiles.__new__(SpeakerProfiles)
        profiles.lock = threading.RLock(); profiles.threshold = .75
        profiles.active = 'other'
        profiles.extractor = Mock(); profiles.extractor.embedding.return_value = np.array([1.,0.])
        first = Mock(); second = Mock()
        first.identify.return_value = {'state':'matched','similarity':.90,'name':'First'}
        second.identify.return_value = {'state':'matched','similarity':.89,'name':'Second'}
        profiles.profiles = {'owner':first,'other':second}
        return profiles

    def test_duplicate_templates_do_not_block_explicit_target_but_auto_stays_ambiguous(self):
        profiles = self.profiles()
        with patch('desktop.speaker.prepare_audio', return_value=(np.ones(48000),3.)):
            self.assertEqual(profiles.identify(np.ones(48000),48000)['state'], 'uncertain')
            result = profiles.identify_target('owner',np.ones(48000),48000)
        self.assertEqual(result['state'],'matched')
        self.assertEqual(result['profile_id'],'owner')
        self.assertEqual(profiles.active,'other')
        self.assertEqual(profiles.profiles['owner'].threshold,.75)

    def test_target_rejection_cannot_substitute_another_user(self):
        profiles = self.profiles()
        profiles.profiles['owner'].identify.return_value = {'state':'unknown'}
        with patch('desktop.speaker.prepare_audio', return_value=(np.ones(48000),3.)):
            result = profiles.identify_target('owner',np.ones(48000),48000)
        self.assertEqual(result['state'],'unknown')
        profiles.profiles['other'].identify.assert_not_called()

    def test_missing_target_does_not_load_model_or_select_another(self):
        profiles = self.profiles()
        self.assertEqual(profiles.identify_target('missing',[],48000)['state'],'not_enrolled')
        profiles.extractor.embedding.assert_not_called()


class RuntimeLearningBoundaryTests(unittest.TestCase):
    def setUp(self):
        from desktop.runtime import Runtime
        self.root=tempfile.TemporaryDirectory();self.addCleanup(self.root.cleanup)
        self.runtime=Runtime(self.root.name);self.addCleanup(self.runtime._voice.close)
        self.runtime._voice.speaker_enabled=True

    def listen(self,text,**values):
        turn={'text':text,'confidence':.95,'needs_review':False,
              'speaker':{'state':'matched','profile_id':'owner'},'_speaking_pauses':[1000.]}
        self.runtime._voice.listen=Mock(return_value={**turn,**values})
        return self.runtime.listen()

    def test_unaddressed_matched_voice_does_not_learn_before_trigger_filter(self):
        result=self.listen('open calculator')
        self.assertTrue(result['ignored'])
        self.assertFalse(self.runtime._voice.pause_model.profiles)
        self.assertNotIn('_speaking_pauses',result)

    def test_confident_activated_matched_turn_learns_bounded_statistics(self):
        result=self.listen('Hey Bob open calculator')
        self.assertEqual(result['text'],'open calculator')
        self.assertEqual(self.runtime._voice.pause_model.profiles['owner']['count'],1)
        self.assertNotIn('_speaking_pauses',result)

    def test_learning_off_prevents_update(self):
        self.runtime._voice.audio_options['audio_pause_learning']=False
        self.listen('Hey Bob open calculator')
        self.assertFalse(self.runtime._voice.pause_model.profiles)

    def test_uncertain_transcript_does_not_learn(self):
        self.listen('Hey Bob open calculator',needs_review=True)
        self.assertFalse(self.runtime._voice.pause_model.profiles)


if __name__ == '__main__':
    unittest.main()
