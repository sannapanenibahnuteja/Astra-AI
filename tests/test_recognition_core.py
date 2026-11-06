import io
import threading
import unittest
import wave
from types import SimpleNamespace
from unittest.mock import Mock
import numpy as np
from desktop.recognition import prepare,Recognizer


class RecognitionCoreTests(unittest.TestCase):
    def speech(self):return (.02*np.sin(np.arange(16000)*2*np.pi*180/16000)).astype(np.float32)
    def segment(self):return SimpleNamespace(text='open calculator',avg_logprob=-.2,no_speech_prob=.1,words=[SimpleNamespace(probability=.95)])
    def test_pcm_is_centered_contiguous_and_resampled_once(self):
        stream=io.BytesIO()
        with wave.open(stream,'wb') as wav:
            wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(16000)
            wav.writeframes(((self.speech()+.1)*32767).astype('<i2').tobytes())
        result=prepare(stream)
        self.assertEqual(len(result.samples),16000);self.assertTrue(result.samples.flags['C_CONTIGUOUS'])
        self.assertAlmostEqual(float(result.samples.mean()),0.,places=5)
        self.assertEqual(result.seconds,1.)
    def test_invalid_input_is_explicit_not_a_silent_ready_reset(self):
        for samples in (np.array([float('nan')]*16000),np.zeros(20),np.zeros((16000,2))):
            with self.assertRaises(ValueError):prepare(samples)
    def test_decoder_receives_same_buffer_for_evidence_gated_retry(self):
        model=Mock();model.transcribe.side_effect=[(iter([]),None),(iter([self.segment()]),None)]
        gate=Mock(side_effect=lambda samples:samples)
        result=Recognizer().decode(model,self.speech(),threading.Event(),gate,room_mode='quiet')
        self.assertEqual(result['text'],'open calculator')
        self.assertIs(model.transcribe.call_args_list[0].args[0],gate.call_args.args[0])
        self.assertIs(model.transcribe.call_args_list[1].args[0],gate.call_args.args[0])
        self.assertFalse(model.transcribe.call_args_list[1].kwargs['vad_filter'])
    def test_cancelled_audio_cannot_produce_a_command(self):
        cancel=threading.Event();cancel.set();model=Mock()
        result=Recognizer().decode(model,self.speech(),cancel,Mock())
        self.assertEqual(result['text'],'');model.transcribe.assert_not_called()
    def test_severe_clipping_requires_review_even_when_decoder_is_confident(self):
        model=Mock();model.transcribe.return_value=(iter([self.segment()]),None)
        samples=np.tile(np.array([1.,-1.],np.float32),8000)
        result=Recognizer().decode(model,samples,threading.Event(),Mock())
        self.assertTrue(result['needs_review'])
