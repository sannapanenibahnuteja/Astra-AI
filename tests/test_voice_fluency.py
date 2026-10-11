import unittest
from unittest.mock import Mock, patch
import numpy as np
from desktop.duplex_audio import BLOCK, TurnDetector, natural_pause_ms
from desktop.voice import Voice


class VoiceFluencyTests(unittest.TestCase):
    def test_natural_pacing_preserves_explicit_modes(self):
        self.assertEqual([450, 650, 950], [natural_pause_ms(650, t) for t in (.3, 1, 3)])
        for base in (450, 1200, 1800):
            for duration in (.3, 1, 3): self.assertEqual(base, natural_pause_ms(base, duration))

    def detector(self, frames):
        detector = TurnDetector()
        detector.quiet_frames = 65
        detector.adaptive = True
        for _ in range(frames): detector.feed(np.full(BLOCK, .03, np.float32), .99)
        return detector

    def test_short_medium_and_long_turn_endpoints(self):
        for frames, pause in ((30, 45), (100, 65), (300, 95)):
            with self.subTest(frames=frames):
                detector = self.detector(frames)
                for _ in range(pause - 1):
                    self.assertIsNone(detector.feed(np.zeros(BLOCK, np.float32), 0)[1])
                self.assertIsNotNone(detector.feed(np.zeros(BLOCK, np.float32), 0)[1])

    def test_breath_does_not_split_long_thought(self):
        detector = self.detector(300)
        for _ in range(80): self.assertIsNone(detector.feed(np.zeros(BLOCK, np.float32), 0)[1])
        for _ in range(50): self.assertIsNone(detector.feed(np.full(BLOCK, .03, np.float32), .99)[1])
        for _ in range(94): self.assertIsNone(detector.feed(np.zeros(BLOCK, np.float32), 0)[1])
        audio = detector.feed(np.zeros(BLOCK, np.float32), 0)[1]
        self.assertEqual(350 * BLOCK, np.count_nonzero(audio))

    @patch('desktop.voice.threading.Timer')
    def test_preload_reuses_model_and_stale_release_cannot_unload(self, timer):
        voice = Voice()
        voice._hold = True
        model = Mock()
        model.transcribe.return_value = ([], None)
        def load():
            if voice._model is None: voice._model = model
        voice._load_model = Mock(side_effect=load)
        voice.prepare_transcription()
        voice._warming.join(2)
        self.assertIs(voice._model, model)
        serial = voice._release_serial
        voice.transcribe(None)
        voice._unload(serial)
        self.assertIs(voice._model, model)
        self.assertEqual(180, timer.call_args.args[0])
        voice.session(False)
        self.assertEqual(60, timer.call_args.args[0])
        voice.close()
        self.assertIsNone(voice._model)
        self.assertFalse(voice.prepare_transcription())

    @patch('desktop.voice.threading.Timer')
    def test_preload_failure_retries_and_does_not_change_capture_phase(self, timer):
        voice = Voice()
        voice._hold = True
        voice._update(phase='listening')
        voice._load_model = Mock(side_effect=RuntimeError('missing model'))
        with self.assertLogs(level='ERROR'): voice._warm_transcription()
        self.assertEqual('listening', voice.status()['phase'])
        model = Mock()
        model.transcribe.return_value = ([], None)
        voice._load_model.side_effect = lambda: setattr(voice, '_model', model)
        voice.transcribe(None)
        model.transcribe.assert_called_once()
        voice.close()
