import threading
import queue
import unittest
from unittest.mock import Mock
import numpy as np
from desktop.voice import Voice
from desktop.duplex_audio import DuplexAudio


class FocusedVoiceTests(unittest.TestCase):
    def voice(self,match):
        voice=Voice(); voice.speaker_enabled=True; voice.speaker_focus='owner'
        voice.speaker=Mock(); voice.speaker.identify.return_value=match
        voice.speaker.active='owner'
        return voice

    def test_competing_speaker_does_not_issue_command_or_switch_profile(self):
        voice=self.voice({'state':'matched','profile_id':'other','name':'Other'})
        result=voice._recognize_speaker({'text':'delete files','confidence':.99},np.zeros(48000),48000,None)
        self.assertEqual(result['text'],''); self.assertTrue(result['ignored'])
        self.assertEqual(voice.speaker.active,'owner')
        voice.speaker.identify.assert_called_once_with(unittest.mock.ANY,48000,select=False)

    def test_owner_accepted_unknown_rejected(self):
        voice=self.voice({'state':'matched','profile_id':'owner','name':'Owner'})
        self.assertEqual(voice._recognize_speaker({'text':'open calculator'},np.zeros(48000),48000,None)['text'],'open calculator')
        voice.speaker.identify.return_value={'state':'uncertain'}
        self.assertFalse(voice._focus_accept(np.zeros(48000)))
        self.assertTrue(voice._recognize_speaker({'text':'open calculator'},np.zeros(48000),48000,None)['ignored'])

    def test_interruption_requires_verified_owner_and_current_turn(self):
        engine=DuplexAudio.__new__(DuplexAudio)
        engine.closed=threading.Event(); engine.turn_serial=2; engine.interruptions=0
        engine.cancel_playback=Mock(); engine.on_interrupt=Mock()
        engine.verify_interrupt=Mock(return_value=False)
        engine._verified_interrupt(np.zeros(48000),2)
        engine.cancel_playback.assert_not_called()
        engine.verify_interrupt.return_value=True
        engine._verified_interrupt(np.zeros(48000),1)
        engine.cancel_playback.assert_not_called()
        engine._verified_interrupt(np.zeros(48000),2)
        engine.cancel_playback.assert_called_once(); engine.on_interrupt.assert_called_once()

    def test_verifier_failure_never_interrupts(self):
        engine=DuplexAudio.__new__(DuplexAudio)
        engine.closed=threading.Event(); engine.turn_serial=1; engine.interruptions=0
        engine.cancel_playback=Mock(); engine.on_interrupt=Mock(); engine.verify_interrupt=Mock(side_effect=RuntimeError('Unavailable'))
        engine._verified_interrupt(np.zeros(48000),1)
        engine.on_interrupt.assert_not_called()

    def test_all_saved_voices_mode_accepts_enrolled_match_and_rejects_unknown(self):
        voice=self.voice({'state':'matched','profile_id':'other','name':'Other'})
        voice.speaker_focus='*'
        self.assertTrue(voice._focus_accept(np.zeros(48000)))
        self.assertEqual(voice._recognize_speaker({'text':'hello'},np.zeros(48000),48000,None)['text'],'hello')
        self.assertEqual(voice.speaker.active,'other')
        voice.speaker.identify.return_value={'state':'unknown'}
        self.assertFalse(voice._focus_accept(np.zeros(48000)))
        self.assertTrue(voice._recognize_speaker({'text':'open youtube'},np.zeros(48000),48000,None)['ignored'])

    def test_unmatched_audio_does_not_reach_whisper(self):
        voice=self.voice({'state':'unknown'})
        engine=Mock(); engine.receive.return_value=np.zeros(48000*3,np.float32)
        from unittest.mock import patch
        with patch.object(voice,'_ensure_duplex',return_value=engine),patch.object(voice,'transcribe') as whisper:
            self.assertTrue(voice.listen()['ignored'])
            whisper.assert_not_called()
            voice.speaker=None
            self.assertTrue(voice.listen()['ignored'])
            whisper.assert_not_called()

    def test_playback_meter_measures_output_not_microphone(self):
        readings=[]
        engine=DuplexAudio(Mock(),lambda **values: (readings.append(values),engine.closed.set()))
        engine.processor=Mock(); engine.processor.process.return_value=np.zeros(480,np.float32)
        engine.blocks.put((np.zeros(480,np.float32),np.full(480,.05,np.float32),0))
        engine._work()
        self.assertAlmostEqual(readings[0]['output_level'],.5,places=4)
        self.assertEqual(readings[0]['level'],0)

    def test_background_voices_cannot_fill_pending_command_queue(self):
        engine=DuplexAudio.__new__(DuplexAudio)
        engine.closed=threading.Event(); engine.utterances=queue.Queue(maxsize=2)
        engine.completed_turns=0; engine.on_status=Mock(); engine.verify_interrupt=Mock(return_value=False)
        for _ in range(5): engine._deliver_focused_turn(np.zeros(48000))
        self.assertTrue(engine.utterances.empty())
        engine.verify_interrupt.return_value=True
        engine._deliver_focused_turn(np.zeros(48000))
        self.assertEqual(engine.utterances.qsize(),1)
        self.assertEqual(engine.completed_turns,1)
