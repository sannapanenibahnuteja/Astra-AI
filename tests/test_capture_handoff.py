import queue
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
import numpy as np
from desktop.duplex_audio import DuplexAudio, CapturedTurn
from desktop.voice import Voice


class CaptureHandoffTests(unittest.TestCase):
    def engine(self):
        engine=DuplexAudio.__new__(DuplexAudio)
        engine.closed=threading.Event();engine.error=''
        engine.detector=SimpleNamespace(started=True)
        engine.pending_verifications=0;engine.delivery_pending=False
        return engine

    def test_idle_deadline_restarts_after_speech_not_during_handoff(self):
        engine=self.engine();clock=[0.];calls=[0];turn=object()
        def get(timeout):
            calls[0]+=1
            if calls[0]==1:clock[0]=2.;raise queue.Empty
            if calls[0]==2:
                clock[0]=2.5;engine.detector.started=False;raise queue.Empty
            return turn
        engine.utterances=SimpleNamespace(get=get)
        with patch('desktop.duplex_audio.time.monotonic',side_effect=lambda:clock[0]):
            self.assertIs(engine.receive(threading.Event(),timeout=1),turn)

    def test_endpoint_publication_remains_pending_without_active_detector(self):
        engine=self.engine();engine.detector.started=False;engine.delivery_pending=True
        turn=object();calls=[0]
        def get(timeout):
            calls[0]+=1
            if calls[0]==1:raise queue.Empty
            return turn
        engine.utterances=SimpleNamespace(get=get)
        self.assertIs(engine.receive(threading.Event(),timeout=0),turn)

    def test_true_idle_still_returns_and_cancellation_does_not_hang(self):
        engine=self.engine();engine.detector.started=False;engine.utterances=queue.Queue()
        self.assertIsNone(engine.receive(threading.Event(),timeout=0))
        engine.delivery_pending=True;cancel=threading.Event();cancel.set()
        self.assertIsNone(engine.receive(cancel))

    def test_alternate_uses_matched_echo_cancelled_audio_only(self):
        speech=(.03*np.sin(np.arange(48000)*2*np.pi*180/48000)).astype(np.float32)
        turn=CapturedTurn(np.zeros(48000,np.float32),speech)
        result=Voice._alternate_capture_audio(turn,{'speaker':{'state':'matched'}})
        self.assertEqual(len(result),16000)
        self.assertIsNone(Voice._alternate_capture_audio(turn,{'speaker':{'state':'uncertain'}}))
        self.assertIsNone(Voice._alternate_capture_audio(CapturedTurn(speech,speech),{'speaker':{'state':'matched'}}))
        self.assertIsNone(Voice._alternate_capture_audio(CapturedTurn(speech,np.zeros(48000,np.float32)),{'speaker':{'state':'matched'}}))

    def test_alternate_decode_is_bounded_and_empty_result_is_explicit(self):
        voice=Voice();self.addCleanup(voice.close)
        voice._model=Mock();voice._load_model=Mock();voice._defer_release=Mock()
        voice._model.transcribe.return_value=(iter([]),None)
        with patch.object(voice,'_retry_audio') as retry:
            result=voice.transcribe(np.ones(16000,np.float32),allow_retry=False)
        retry.assert_not_called()
        self.assertEqual(voice._model.transcribe.call_count,1)
        self.assertEqual(result['capture_status'],'no_words')
        self.assertTrue(result['retryable']);self.assertEqual(result['text'],'')

    def test_listen_recovers_empty_clean_path_without_rechecking_identity(self):
        voice=Voice();self.addCleanup(voice.close)
        speech=(.03*np.sin(np.arange(48000)*2*np.pi*180/48000)).astype(np.float32)
        turn=CapturedTurn(np.zeros(48000,np.float32),speech)
        engine=Mock();engine.receive.return_value=turn
        matched={'speaker':{'state':'matched','profile_id':'fixture'}}
        decoded=[{'text':'','capture_status':'no_words','message':'retry','retryable':True},
                 {'text':'open calculator','confidence':.95,'needs_review':False}]
        with patch.object(voice,'_ensure_duplex',return_value=engine),patch.object(voice,'_recognize_speaker',return_value=matched) as identify,patch.object(voice,'transcribe',side_effect=decoded) as decode:
            result=voice.listen()
        self.assertEqual(result['text'],'open calculator')
        self.assertEqual(result['capture_status'],'recovered')
        self.assertNotIn('message',result);self.assertNotIn('retryable',result)
        identify.assert_called_once();self.assertEqual(decode.call_count,2)
        self.assertFalse(decode.call_args.kwargs['allow_retry'])
