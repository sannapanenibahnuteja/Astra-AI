import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
import numpy as np
from desktop.runtime import Runtime
from desktop.duplex_audio import DuplexAudio,CapturedTurn,RATE,InterruptionGate,TurnDetector,BLOCK
from desktop.microphone import interruption_floor

class GenerationProofTests(unittest.TestCase):
 def setUp(self):
  gate=patch('desktop.voice_evidence.interruption_speech',return_value=True);gate.start();self.addCleanup(gate.stop)
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
  self.runtime=Runtime(temp.name);self.addCleanup(self.runtime._voice.close)
  self.voice=self.runtime._voice
  self.voice.speaker_enabled=True;self.voice.speaker_focus='owner';self.voice.speaker=Mock();self.voice.speaker.profiles={}
  self.voice.speaker.identify.return_value={'state':'matched','profile_id':'owner'}
  self.result={'text':'Hey Bob please stop talking','confidence':.98,'word_confidence_min':.95,'needs_review':False}
  self.voice._decode_interruption=Mock(return_value=self.result)
  self.job={'id':'response-a','done':False,'spoken':True,'cancel':threading.Event(),'transport':Mock(),'text':''}
  self.runtime._job=self.job;self.voice.begin_response('response-a')
  self.engine=DuplexAudio(lambda:self.voice._barge_in(self.engine),Mock());self.engine.turn_serial=1
  self.engine.authorize_interrupt=self.voice._authorize_interrupt;self.engine.response_active=lambda:True
  self.voice._duplex=self.engine
 def turn(self):
  audio=np.zeros(RATE,np.float32)
  return CapturedTurn(audio,audio,1,interruption_ready=True,requires_authorization=True)
 def test_noise_callback_cannot_cancel_before_or_during_generation(self):
  for transport in (None,Mock()):
   self.job['transport']=transport
   self.assertFalse(self.runtime._voice_interrupt());self.assertFalse(self.job['cancel'].is_set())
 def test_direct_barge_callback_without_capture_proof_is_ignored(self):
  self.assertFalse(self.voice._barge_in(self.engine));self.assertFalse(self.voice._speech_interrupted.is_set())
  self.assertFalse(self.job['cancel'].is_set())
 def test_completed_real_proof_cancels_generation_and_preserves_request(self):
  turn=self.turn();self.engine._deliver_focused_turn(turn)
  self.assertTrue(self.job['cancel'].is_set());self.assertTrue(self.job['interrupted'])
  self.assertTrue(self.voice._speech_interrupted.is_set());self.assertIs(self.engine.receive(threading.Event()),turn)
 def test_same_proof_cannot_cancel_twice(self):
  tokens=[]
  self.voice.on_interrupt=lambda token:tokens.append(token) or self.runtime._voice_interrupt(token)
  self.engine._deliver_focused_turn(self.turn());self.assertEqual(len(tokens),1)
  self.job['cancel'].clear();self.assertFalse(self.runtime._voice_interrupt(tokens[0]));self.assertFalse(self.job['cancel'].is_set())
 def test_old_response_proof_cannot_cancel_new_response(self):
  self.assertTrue(self.voice._authorize_interrupt(self.turn()))
  self.voice.begin_response('response-b');self.job['id']='response-b';self.engine.last_interrupted_serial=1
  self.assertFalse(self.voice._barge_in(self.engine));self.assertFalse(self.job['cancel'].is_set())
 def test_response_change_during_decode_invalidates_permit(self):
  def decode(*args):self.voice.begin_response('response-b');return self.result
  self.voice._decode_interruption.side_effect=decode
  self.assertFalse(self.voice._authorize_interrupt(self.turn()));self.assertFalse(self.voice._interrupt_proofs)
 def test_finishing_old_response_does_not_clear_new_context(self):
  self.voice.begin_response('response-b');self.voice.finish_response('response-a')
  self.assertEqual(self.voice._interrupt_context,'response-b')
 def test_rejected_callback_does_not_cancel_playback_or_queue(self):
  self.engine.on_interrupt=lambda:False;self.engine.authorize_interrupt=Mock(return_value=True);self.engine.cancel_playback=Mock()
  self.engine._deliver_focused_turn(self.turn())
  self.engine.cancel_playback.assert_not_called();self.assertTrue(self.engine.utterances.empty())
  self.assertEqual(self.engine.last_interrupted_serial,-1)
 def test_manual_stop_invalidates_queued_proof(self):
  self.assertTrue(self.voice._authorize_interrupt(self.turn()))
  self.voice.stop();self.assertFalse(self.voice._interrupt_proofs)
  self.assertFalse(self.voice._barge_in(self.engine))
 def test_failed_commit_callback_retains_playback_and_drops_candidate(self):
  self.engine.on_interrupt=Mock(side_effect=RuntimeError('fixture callback failure'))
  self.engine.authorize_interrupt=Mock(return_value=True);self.engine.cancel_playback=Mock()
  with self.assertLogs(level='ERROR'):self.engine._deliver_focused_turn(self.turn())
  self.engine.cancel_playback.assert_not_called();self.assertTrue(self.engine.utterances.empty())
 def test_nonopaque_public_values_cannot_forge_a_permit(self):
  for permit in (None,True,'verified',{'verified':True},1):
   self.assertFalse(self.runtime._voice_interrupt(permit));self.assertFalse(self.job['cancel'].is_set())

class CalibratedFloorTests(unittest.TestCase):
 def profile(self):return {'device':'WASAPI:fixture','name':'Fixture','noise_rms':.00003,'speech_rms':.0045,'gain':7.7}
 def test_floor_uses_device_specific_post_gain_voice_level(self):
  self.assertAlmostEqual(interruption_floor(self.profile(),'WASAPI:fixture'),.0045*7.7*.08)
 def test_different_device_or_invalid_profile_uses_safe_default(self):
  self.assertEqual(interruption_floor(self.profile(),'different'),.0008)
  self.assertEqual(interruption_floor({},'WASAPI:fixture'),.0008)
 def test_calibrated_interrupt_floor_does_not_reduce_capture_sensitivity(self):
  gate=InterruptionGate(interruption_floor(self.profile(),'WASAPI:fixture'));detector=TurnDetector()
  signal=np.full(BLOCK,.001,np.float32)
  for _ in range(50):
   self.assertFalse(gate.feed(.001,True,noise=0));detector.feed(signal,.99)
  self.assertTrue(detector.started)

if __name__=='__main__':unittest.main()
