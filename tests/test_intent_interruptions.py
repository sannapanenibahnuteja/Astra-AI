import threading
import queue
import unittest
from unittest.mock import Mock,patch
import numpy as np
from desktop.interruption import intended_interruption,reply_stop_control
from desktop.duplex_audio import DuplexAudio,CapturedTurn,RATE
from desktop.voice import Voice


class InterruptionIntentTests(unittest.TestCase):
    def test_clear_directed_requests_and_repairs(self):
        for text in ('Bob, stop','Hey Bob, open YouTube','Shorter','Actually, open calculator','Bob, what is that?','No, I meant Friday','Bob, stop listening and open YouTube','Actually, just give me the short version','Bob, can you please open calculator'):
            with self.subTest(text=text):self.assertTrue(intended_interruption(text,.95,False))

    def test_gibberish_fillers_boilerplate_and_background_narration(self):
        for text in ('um uh','blah blah','Bob','Bob um banana','Actually, flibber wibble','thanks for watching','Bob subscribe','the television is playing','open youtube','Bob, do not stop','Bob, keep talking'):
            with self.subTest(text=text):self.assertFalse(intended_interruption(text,.99,False))

    def test_clear_words_with_uncertain_asr_still_cannot_interrupt(self):
        self.assertFalse(intended_interruption('Bob stop',.79,False))
        self.assertFalse(intended_interruption('Bob stop',.99,True))

    def test_pure_reply_stop_cannot_become_an_app_command(self):
        self.assertTrue(reply_stop_control('Bob, stop'))
        self.assertTrue(reply_stop_control('Actually, please stop talking'))
        self.assertFalse(reply_stop_control('Bob, stop listening and open calculator'))
        self.assertFalse(reply_stop_control('Bob, type stop into notepad'))


class OwnerProofTests(unittest.TestCase):
    def voice(self,who='owner'):
        voice=Voice();voice.speaker_enabled=True;voice.speaker_focus='*';voice.interruption_owner='owner'
        voice.speaker=Mock();voice.speaker.active='owner';voice.speaker.profiles={}
        voice.speaker.identify.return_value={'state':'matched','profile_id':who,'name':'Fixture'}
        voice._decode_interruption=Mock(return_value={'text':'Bob stop','confidence':.95,'needs_review':False})
        return voice

    def turn(self):
        audio=np.zeros(RATE,np.float32)
        return CapturedTurn(audio,audio,1,interruption_ready=True,requires_authorization=True)

    def test_other_enrolled_voice_cannot_interrupt_primary_user(self):
        voice=self.voice('other');turn=self.turn()
        self.assertFalse(voice._authorize_interrupt(turn))
        voice._decode_interruption.assert_not_called()
        self.assertEqual(voice.speaker.active,'owner')

    def test_unknown_voice_does_not_consume_asr(self):
        voice=self.voice();voice.speaker.identify.return_value={'state':'unknown'}
        self.assertFalse(voice._authorize_interrupt(self.turn()))
        voice._decode_interruption.assert_not_called()

    def test_disabled_voice_matching_fails_closed(self):
        voice=self.voice();voice.speaker_enabled=False
        self.assertFalse(voice._authorize_interrupt(self.turn()))
        voice.speaker.identify.assert_not_called();voice._decode_interruption.assert_not_called()

    def test_no_selected_or_current_owner_cannot_grant_interrupt_permission(self):
        voice=self.voice();voice.interruption_owner=None;voice.speaker.active=None
        self.assertFalse(voice._authorize_interrupt(self.turn()))
        voice.speaker.identify.assert_not_called();voice._decode_interruption.assert_not_called()

    def test_strict_worker_cannot_duck_or_cancel_on_acoustics_alone(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.blocks=queue.Queue(maxsize=180)
        engine.processor=Mock();engine.processor.process.side_effect=lambda near,far:near
        engine.vad=Mock();engine.vad.is_speech.return_value=True
        engine.interrupt_vad=Mock();engine.interrupt_vad.is_speech.return_value=True
        engine.response_active=lambda:True;engine.authorize_interrupt=Mock(return_value=False)
        engine.play_started=1.;engine.echo_until=float('inf');seen=0
        def status(**values):
            nonlocal seen
            if 'level' in values:
                seen+=1
                if seen==170:engine.closed.set()
        engine.on_status=status
        signal=(.02*np.sin(2*np.pi*200*np.arange(480)/RATE)).astype(np.float32)
        for index in range(170):engine.blocks.put((signal if index<50 else np.zeros(480,np.float32),np.zeros(480,np.float32),0))
        engine._work()
        self.assertEqual(engine.error,'');self.assertEqual(engine.ducks,0)
        engine.on_interrupt.assert_not_called();self.assertTrue(engine.utterances.empty())

    def test_own_voice_gibberish_is_not_authorization(self):
        voice=self.voice();voice._decode_interruption.return_value={'text':'banana flibber','confidence':.99,'needs_review':False}
        turn=self.turn();self.assertFalse(voice._authorize_interrupt(turn));self.assertIsNone(turn.recognition)

    def test_own_voice_clear_request_creates_reusable_proof(self):
        voice=self.voice();turn=self.turn()
        self.assertTrue(voice._authorize_interrupt(turn))
        self.assertEqual(turn.recognition['profile'],'owner')
        self.assertEqual(turn.recognition['result']['text'],'Bob stop')
        self.assertEqual(voice.speaker.active,'owner')

    def test_focus_change_during_decode_invalidates_proof(self):
        voice=self.voice();turn=self.turn()
        def decode(*args):
            voice.speaker_focus='other'
            return {'text':'Bob stop','confidence':.99,'needs_review':False}
        voice._decode_interruption.side_effect=decode
        self.assertFalse(voice._authorize_interrupt(turn));self.assertIsNone(turn.recognition)

    def test_partial_proof_does_not_replace_final_transcript(self):
        voice=self.voice();turn=self.turn()
        self.assertTrue(voice._authorize_interrupt(turn,True));self.assertIsNone(turn.recognition)

    def test_rejected_intent_keeps_playback_and_queue_unchanged(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.turn_serial=1;engine.authorize_interrupt=Mock(return_value=False)
        engine.verify_interrupt=Mock(return_value=True)
        engine._deliver_focused_turn(self.turn())
        engine.on_interrupt.assert_not_called();engine.verify_interrupt.assert_not_called()
        self.assertTrue(engine.utterances.empty())

    def test_reply_starting_during_existing_capture_cannot_bypass_intent(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.turn_serial=1;engine.response_active=lambda:True
        engine.authorize_interrupt=Mock(return_value=False);engine.verify_interrupt=Mock(return_value=True)
        turn=self.turn();turn.requires_authorization=False
        engine._deliver_focused_turn(turn)
        engine.authorize_interrupt.assert_called_once();engine.verify_interrupt.assert_not_called()
        engine.on_interrupt.assert_not_called();self.assertTrue(engine.utterances.empty())

    def test_idle_identity_match_does_not_create_unproved_reply_stop(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.turn_serial=1;engine.authorize_interrupt=Mock();engine.verify_interrupt=Mock(return_value=True)
        turn=self.turn();turn.requires_authorization=False
        engine._deliver_focused_turn(turn)
        engine.authorize_interrupt.assert_not_called();engine.on_interrupt.assert_not_called()
        self.assertIs(engine.receive(threading.Event()),turn)

    def test_accepted_intent_cancels_once_and_delivers_real_new_request(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.turn_serial=1;engine.authorize_interrupt=Mock(return_value=True)
        turn=self.turn();engine._verified_interrupt(turn,1);engine._deliver_focused_turn(turn)
        engine.on_interrupt.assert_called_once();self.assertIs(engine.receive(threading.Event()),turn)
        self.assertEqual(engine.last_interrupted_serial,engine.acknowledged_serial)

    def test_stale_intent_cannot_cancel_or_queue_on_newer_turn(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.turn_serial=2;engine.authorize_interrupt=Mock(return_value=True)
        engine._deliver_focused_turn(self.turn())
        engine.on_interrupt.assert_not_called();engine.authorize_interrupt.assert_not_called()
        self.assertTrue(engine.utterances.empty())

    def test_turn_change_during_inference_discards_late_proof(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close);engine.turn_serial=1
        def authorize(*args):engine.turn_serial=2;return True
        engine.authorize_interrupt=authorize
        engine._deliver_focused_turn(self.turn())
        engine.on_interrupt.assert_not_called();self.assertTrue(engine.utterances.empty())

    def test_decoder_busy_keeps_current_reply_playing(self):
        voice=Voice();voice._model=Mock();turn=self.turn()
        voice._model_lock.acquire()
        try:self.assertIsNone(voice._decode_interruption(turn,True))
        finally:voice._model_lock.release()
        voice._model.transcribe.assert_not_called()

    def test_valid_full_proof_avoids_duplicate_asr(self):
        voice=self.voice();turn=self.turn();self.assertTrue(voice._authorize_interrupt(turn))
        engine=Mock();engine.receive.return_value=turn
        speaker={'speaker':{'state':'matched','profile_id':'owner'}}
        with patch.object(voice,'_ensure_duplex',return_value=engine),patch.object(voice,'_recognize_speaker',return_value=speaker),patch.object(voice,'transcribe') as decode:
            result=voice.listen()
            self.assertEqual(result['text'],'');self.assertEqual(result['interruption_control'],'stop_reply');decode.assert_not_called()
