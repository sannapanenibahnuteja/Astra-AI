import unittest
import itertools
import threading
from unittest.mock import Mock,patch
import numpy as np
from desktop.voice import Voice,transcript_result
from desktop.duplex_audio import DuplexAudio,CapturedTurn,RATE

class CompletedInterruptions(unittest.TestCase):
 def voice(self):
  voice=Voice();voice.speaker_enabled=True;voice.speaker_focus='owner';voice.speaker=Mock();voice.speaker.profiles={}
  voice.speaker.identify.return_value={'state':'matched','profile_id':'owner'}
  voice._decode_interruption=Mock(return_value={'text':'Hey Bob please stop talking','confidence':.98,'word_confidence_min':.95,'needs_review':False})
  return voice
 def turn(self):
  audio=np.zeros(RATE,np.float32)
  return CapturedTurn(audio,audio,1,interruption_ready=True,requires_authorization=True)
 def test_no_settings_combination_removes_authorization_or_enables_ducking(self):
  for wake,verified,duck in itertools.product((False,True),repeat=3):
   voice=self.voice();voice.audio_options.update(audio_wake_phrase_only=wake,audio_verified_interruptions=verified,audio_fast_barge_in=duck)
   engine=Mock();engine.options={'audio_fast_barge_in':duck};voice.configure_interruptions(engine)
   self.assertEqual(engine.authorize_interrupt,voice._authorize_interrupt);self.assertFalse(engine.options['audio_fast_barge_in'])
 def test_disabled_interruptions_never_decode_even_if_wake_mode_is_on(self):
  voice=self.voice();voice.audio_options['audio_verified_interruptions']=False
  self.assertFalse(voice._authorize_interrupt(self.turn()));voice._decode_interruption.assert_not_called()
 def test_partial_hallucinated_control_cannot_cancel_or_decode(self):
  voice=self.voice();self.assertFalse(voice._authorize_interrupt(self.turn(),partial=True))
  voice.speaker.identify.assert_not_called();voice._decode_interruption.assert_not_called()
 def test_worker_cannot_accept_a_positive_partial_callback(self):
  engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close);engine.turn_serial=1
  engine.authorize_interrupt=Mock(return_value=True);engine.verify_interrupt=Mock(return_value=True)
  engine._verified_interrupt(self.turn(),1)
  engine.authorize_interrupt.assert_not_called();engine.on_interrupt.assert_not_called()
  self.assertEqual(engine.last_interrupted_serial,-1)
 def test_direct_onset_path_cannot_bypass_completed_authorization(self):
  engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close);engine.turn_serial=1;engine.authorize_interrupt=Mock()
  engine._interrupt_verified(1);engine.on_interrupt.assert_not_called();self.assertEqual(engine.last_interrupted_serial,-1)
 def test_weak_acoustic_candidate_cannot_queue_even_with_positive_model(self):
  engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close);engine.turn_serial=1;engine.authorize_interrupt=Mock(return_value=True)
  turn=self.turn();turn.interruption_ready=False;engine._deliver_focused_turn(turn)
  engine.authorize_interrupt.assert_not_called();engine.on_interrupt.assert_not_called();self.assertTrue(engine.utterances.empty())
 def test_uncertain_wake_word_cannot_be_hidden_by_confident_other_words(self):
  voice=self.voice();voice._decode_interruption.return_value.update(word_confidence_min=.35)
  self.assertFalse(voice._authorize_interrupt(self.turn()))
 def test_explicit_phrase_still_required_when_idle_wake_mode_is_off(self):
  voice=self.voice();voice.audio_options['audio_wake_phrase_only']=False
  for text in ('Actually open calculator','Shorter','open calculator'):
   voice._decode_interruption.return_value['text']=text
   self.assertFalse(voice._authorize_interrupt(self.turn()),text)
 def test_final_verified_request_cancels_once_and_remains_available(self):
  voice=self.voice();engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close);engine.turn_serial=1
  engine.authorize_interrupt=voice._authorize_interrupt;turn=self.turn();engine._deliver_focused_turn(turn)
  engine.on_interrupt.assert_called_once();self.assertIs(engine.receive(threading.Event()),turn)
  self.assertEqual(turn.recognition['profile'],'owner')
 def test_preview_does_not_compete_with_reply_audio_or_final_decoder(self):
  voice=self.voice();voice.response_active=True;voice._model=Mock()
  self.assertIsNone(voice._preview_decode(Mock()));voice._model.transcribe.assert_not_called()

if __name__=='__main__':unittest.main()
