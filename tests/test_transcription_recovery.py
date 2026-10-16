import queue
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
import numpy as np
from desktop.voice import Voice
from desktop.duplex_audio import DuplexAudio


def segment(text='open calculator', confidence=.9, no_speech=.1):
    return SimpleNamespace(text=text, avg_logprob=-.2, no_speech_prob=no_speech,
                           words=[SimpleNamespace(probability=confidence)])


class TranscriptionRecoveryTests(unittest.TestCase):
    def voice(self):
        voice=Voice()
        voice._model=Mock()
        voice._load_model=Mock()
        voice._defer_release=Mock()
        return voice

    def test_empty_vad_result_retried_once_for_speech(self):
        voice=self.voice()
        voice._model.transcribe.side_effect=[(iter([]),None),(iter([segment()]),None)]
        audio=np.sin(np.arange(16000)*2*np.pi*180/16000).astype(np.float32)*.03
        result=voice.transcribe(audio)
        self.assertEqual(result['text'],'open calculator')
        self.assertEqual(voice._model.transcribe.call_count,2)
        self.assertFalse(voice._model.transcribe.call_args.kwargs['vad_filter'])

    def test_silence_and_hiss_are_not_retried(self):
        for audio in [np.zeros(16000,np.float32), np.random.default_rng(1).normal(0,.02,16000).astype(np.float32)]:
            voice=self.voice(); voice._model.transcribe.return_value=(iter([]),None)
            self.assertEqual(voice.transcribe(audio)['text'],'')
            self.assertEqual(voice._model.transcribe.call_count,1)

    def test_retry_preserves_confidence_review_and_no_speech_filter(self):
        for response,expected in [(segment(confidence=.4),'open calculator'),(segment(no_speech=.98),'')]:
            voice=self.voice()
            voice._model.transcribe.side_effect=[(iter([]),None),(iter([response]),None)]
            with patch.object(voice,'_retry_audio',return_value=np.ones(16000,np.float32)):
                result=voice.transcribe(np.zeros(16000,np.float32))
            self.assertEqual(result['text'],expected)
            if expected: self.assertTrue(result['needs_review'])

    def test_no_extra_decode_for_success_or_cancellation(self):
        voice=self.voice(); voice._model.transcribe.return_value=(iter([segment()]),None)
        with patch.object(voice,'_retry_audio') as retry:
            voice.transcribe(np.zeros(16000,np.float32)); retry.assert_not_called()
        voice._cancel.set(); voice._model.transcribe.return_value=(iter([]),None)
        with patch.object(voice,'_retry_audio') as retry:
            voice.transcribe(np.zeros(16000,np.float32)); retry.assert_not_called()

    def test_completed_turn_reuses_exact_verified_audio_only(self):
        voice=Voice(); voice.speaker_enabled=True; voice.speaker_focus='*'; voice.speaker=Mock()
        voice.speaker.identify.return_value={'state':'matched','profile_id':'owner','name':'Test'}
        first=np.zeros(48000,np.float32); second=np.zeros(48000,np.float32)
        self.assertTrue(voice._focus_accept(first)); self.assertTrue(voice._focus_accept(second))
        self.assertEqual(voice._recognize_speaker({},second,48000,None)['speaker']['state'],'matched')
        self.assertEqual(voice.speaker.identify.call_count,2)
        voice.speaker.identify.return_value={'state':'unknown'}
        self.assertTrue(voice._recognize_speaker({},second.copy(),48000,None)['ignored'])
        voice.speaker_focus='different-owner'
        self.assertTrue(voice._recognize_speaker({},first,48000,None)['ignored'])

    def test_receive_waits_for_pending_match_instead_of_losing_turn(self):
        engine=DuplexAudio.__new__(DuplexAudio)
        engine.closed=threading.Event();engine.error='';engine.detector=SimpleNamespace(started=False)
        engine.utterances=queue.Queue();engine.pending_verifications=1
        audio=np.zeros(48000,np.float32)
        timer=threading.Timer(.12,lambda: engine.utterances.put(audio));timer.start()
        try: self.assertIs(engine.receive(threading.Event(),timeout=.01),audio)
        finally: timer.join()

    def test_failed_match_surfaces_reason_without_queueing(self):
        engine=DuplexAudio.__new__(DuplexAudio); engine.verify_interrupt=Mock(return_value=False)
        engine.on_status=Mock();engine._queue_turn=Mock()
        engine._deliver_focused_turn(np.zeros(48000,np.float32))
        engine._queue_turn.assert_not_called()
        self.assertIn('saved-voice filter',engine.on_status.call_args.kwargs['voice_notice'])

    def test_match_work_is_bounded_and_pending_is_cleared_on_failure(self):
        engine=DuplexAudio.__new__(DuplexAudio); engine.pending_verifications=2
        engine._verification_lock=threading.Lock();engine.on_status=Mock()
        with patch('desktop.duplex_audio.threading.Thread') as thread:
            engine._submit_focused_turn(np.zeros(48000,np.float32));thread.assert_not_called()
        engine._deliver_focused_turn=Mock(side_effect=RuntimeError('model failure'))
        with self.assertRaises(RuntimeError): engine._verify_turn(np.zeros(48000,np.float32))
        self.assertEqual(engine.pending_verifications,1)
