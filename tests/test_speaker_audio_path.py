import unittest
from unittest.mock import Mock,patch
import numpy as np
from desktop.duplex_audio import DuplexAudio,CapturedTurn,BLOCK
from desktop.voice import Voice

class SpeakerAudioPathTests(unittest.TestCase):
    def test_final_verifier_receives_speaker_channel_and_preserves_transcription_channel(self):
        engine=DuplexAudio(Mock(),Mock())
        self.addCleanup(engine.close)
        engine.verify_interrupt=Mock(return_value=True)
        clean=np.full(BLOCK,.001,np.float32);speaker=np.full(BLOCK,.009,np.float32)
        turn=CapturedTurn(clean,speaker)
        engine._deliver_focused_turn(turn)
        self.assertIs(engine.verify_interrupt.call_args.args[0],speaker)
        self.assertIs(engine.utterances.get_nowait(),turn)

    def test_listen_identifies_speaker_channel_and_decodes_clean_channel(self):
        voice=Voice();engine=Mock()
        speaker=np.full(48000*3,.009,np.float32);clean=np.full(48000*3,.001,np.float32)
        engine.receive.return_value=CapturedTurn(clean,speaker)
        with patch.object(voice,'_ensure_duplex',return_value=engine),patch.object(voice,'_recognize_speaker',return_value={}) as identity,patch.object(voice,'transcribe',return_value={'text':'hello','confidence':.9}) as transcript:
            result=voice.listen()
        self.assertIs(identity.call_args.args[1],speaker)
        self.assertEqual(result['text'],'hello');transcript.assert_called_once()

    def test_speaker_and_transcription_frames_stay_aligned_with_same_echo_reference(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.verify_interrupt=Mock(return_value=True)
        engine.processor=Mock();engine.processor.process.side_effect=lambda near,far:near*.1
        engine.speaker_processor=Mock();engine.speaker_processor.process.side_effect=lambda near,far:near*.9
        engine.vad=Mock();engine.vad.is_speech.return_value=True
        engine.detector=Mock();engine.detector.started=False;engine.detector.voiced=0;engine.detector.frames=[]
        engine.detector.noise=.0001
        count=0;clean_frames=[]
        def feed(clean,*args):
            nonlocal count
            clean_frames.append(clean.copy());count+=1
            if count==1:
                engine.detector.started=True;engine.detector.frames=list(clean_frames)
                return True,None,.001
            if count==3:
                engine.detector.started=False;engine.detector.frames=[]
                return False,np.concatenate(clean_frames),.001
            engine.detector.frames=list(clean_frames)
            return False,None,.001
        engine.detector.feed.side_effect=feed
        turns=[]
        def deliver(turn):turns.append(turn);engine.closed.set()
        engine._submit_focused_turn=deliver
        for level in [.01,.02,.03]:engine.blocks.put((np.full(BLOCK,level,np.float32),np.full(BLOCK,.003,np.float32),77))
        with patch('desktop.duplex_audio.acoustic_speech',return_value=True):engine._work()
        self.assertEqual(len(turns),1)
        self.assertEqual(len(turns[0].audio),len(turns[0].speaker))
        np.testing.assert_allclose(turns[0].speaker,turns[0].audio*9,rtol=1e-6)
        self.assertEqual(engine.processor.stream_delay_ms,77)
        self.assertEqual(engine.speaker_processor.stream_delay_ms,77)
        for primary,secondary in zip(engine.processor.process.call_args_list,engine.speaker_processor.process.call_args_list):
            self.assertIs(primary.args[1],secondary.args[1])

    def test_full_match_interrupts_after_early_partial_miss_without_double_interrupt(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.turn_serial=2;engine.cancel_playback=Mock()
        engine.verify_interrupt=Mock(return_value=False)
        audio=np.zeros(48000,np.float32)
        engine._verified_interrupt(audio,2)
        engine.on_interrupt.assert_not_called()
        engine.verify_interrupt.return_value=True
        engine._deliver_focused_turn(CapturedTurn(audio,audio,2))
        engine.on_interrupt.assert_called_once();engine.cancel_playback.assert_called_once()
        engine._verified_interrupt(audio,2)
        engine.on_interrupt.assert_called_once()

    def test_late_full_match_cannot_interrupt_newer_turn(self):
        engine=DuplexAudio(Mock(),Mock());self.addCleanup(engine.close)
        engine.turn_serial=3;engine.cancel_playback=Mock();engine.verify_interrupt=Mock(return_value=True)
        audio=np.zeros(48000,np.float32)
        engine._deliver_focused_turn(CapturedTurn(audio,audio,2))
        engine.on_interrupt.assert_not_called();engine.cancel_playback.assert_not_called()
