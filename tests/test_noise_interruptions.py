import threading
import queue
import unittest
from unittest.mock import Mock, patch
import numpy as np
from desktop.duplex_audio import DuplexAudio, CapturedTurn, InterruptionGate, BLOCK
from desktop.voice import Voice


class NoiseInterruptionTests(unittest.TestCase):
    def run_frames(self,level,playing=True):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.blocks=queue.Queue(maxsize=200)
        engine.processor=Mock();engine.processor.process.side_effect=lambda near,far:near
        # Worst-case VAD false positive: the energy/duration gate must still
        # protect playback independently of these labels and VAD hangover.
        engine.vad=Mock();engine.vad.is_speech.return_value=True
        engine.interrupt_vad=Mock();engine.interrupt_vad.is_speech.return_value=True
        engine.play_started=1.;engine.echo_until=float('inf') if playing else 0
        frames=160;seen=0
        def status(**values):
            nonlocal seen
            if 'level' in values:
                seen+=1
                if seen==frames:engine.closed.set()
        engine.on_status=status
        signal=(level*np.sin(2*np.pi*200*np.arange(BLOCK)/48000)).astype(np.float32)
        for index in range(frames):
            engine.blocks.put((signal if index<40 else np.zeros(BLOCK,np.float32),np.zeros(BLOCK,np.float32),0))
        engine._work()
        self.assertEqual(engine.error,'')
        return engine

    def test_worker_does_not_duck_or_cancel_for_quiet_false_vad(self):
        engine=self.run_frames(.0005)
        self.assertEqual(engine.ducks,0)
        self.assertEqual(engine.completed_turns,0)
        engine.on_interrupt.assert_not_called()

    def test_quiet_capture_while_idle_keeps_its_existing_sensitivity(self):
        engine=self.run_frames(.0005,playing=False)
        self.assertEqual(engine.completed_turns,1)

    def test_worker_preserves_one_interrupt_for_sustained_speech(self):
        engine=self.run_frames(.02)
        engine.on_interrupt.assert_called_once()

    def test_tiny_sound_never_authorizes_interrupt_even_with_stuck_vad(self):
        gate=InterruptionGate()
        for _ in range(300):self.assertFalse(gate.feed(.0003,True,noise=0))

    def test_loud_short_click_followed_by_vad_hangover_is_rejected(self):
        gate=InterruptionGate()
        for _ in range(5):self.assertFalse(gate.feed(.03,True))
        for _ in range(100):self.assertFalse(gate.feed(.0001,True))

    def test_repeated_isolated_keyboard_sounds_do_not_accumulate(self):
        gate=InterruptionGate()
        for _ in range(20):
            for _ in range(4):self.assertFalse(gate.feed(.02,True))
            for _ in range(12):self.assertFalse(gate.feed(.0001,True))

    def test_sustained_soft_speech_with_consonant_gaps_can_interrupt(self):
        gate=InterruptionGate();ready=None
        for index in range(40):
            speech=index%5!=0
            if gate.feed(.002 if speech else .0001,speech):ready=index;break
        self.assertIsNotNone(ready)
        self.assertLessEqual((ready+1)*10,300)

    def test_aec_settling_and_room_floor_do_not_authorize_interrupt(self):
        gate=InterruptionGate()
        for _ in range(50):self.assertFalse(gate.feed(.05,True,settling=True))
        for _ in range(50):self.assertFalse(gate.feed(.002,True,noise=.001))

    def test_unqualified_final_match_does_not_cancel_speech(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.verify_interrupt=Mock(return_value=True);engine.turn_serial=1
        samples=np.zeros(BLOCK,np.float32)
        engine._deliver_focused_turn(CapturedTurn(samples,samples,1,interruption_ready=False))
        engine.on_interrupt.assert_not_called()

    def test_noise_candidate_between_sentences_does_not_stop_tts(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.detector.started=True # Sensitive onset is not permission to stop.
        voice=Voice();voice.config_root=None
        worker=Mock();worker.render.return_value=b'fixture'
        with patch.object(voice,'_ensure_duplex',return_value=engine),patch.object(voice,'_speech_worker',return_value=worker),patch.object(engine,'play') as play:
            self.assertTrue(voice.speak('Continue the next sentence.',0))
            play.assert_called_once()

    def test_consumed_interruption_does_not_silence_answer_to_new_request(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.turn_serial=4;engine._interrupt_verified(4)
        audio=np.zeros(BLOCK,np.float32)
        engine._queue_turn(CapturedTurn(audio,audio,4,interruption_ready=True))
        engine.receive(threading.Event())
        voice=Voice();worker=Mock();worker.render.return_value=b'fixture'
        with patch.object(voice,'_ensure_duplex',return_value=engine),patch.object(voice,'_speech_worker',return_value=worker),patch.object(engine,'play') as play:
            self.assertTrue(voice.speak('Here is the new answer.',0))
            play.assert_called_once()

    def test_unconsumed_real_interruption_prevents_next_sentence(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.turn_serial=2;engine._interrupt_verified(2)
        voice=Voice()
        with patch.object(voice,'_ensure_duplex',return_value=engine),patch.object(voice,'_speech_worker') as worker:
            self.assertFalse(voice.speak('Old reply should stop.',0))
            worker.assert_not_called()

    def test_discard_acknowledges_cancelled_turn(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.turn_serial=2;engine._interrupt_verified(2);engine.discard()
        self.assertEqual(engine.acknowledged_serial,2)
