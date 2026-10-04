import io
import threading
import unittest
import wave
from unittest.mock import Mock, patch

import numpy as np

from desktop.duplex_audio import BLOCK, RATE, DuplexAudio, TurnDetector, wav_samples
from desktop.voice import Voice


class DuplexTests(unittest.TestCase):
    def test_silence_and_short_noise_never_interrupt(self):
        detector = TurnDetector()
        for _ in range(100):
            self.assertFalse(detector.feed(np.zeros(BLOCK, np.float32), .99)[0])
        for _ in range(10):
            self.assertFalse(detector.feed(np.full(BLOCK, .03, np.float32), .99)[0])
        for _ in range(100):
            interrupt, audio, _ = detector.feed(np.zeros(BLOCK, np.float32), 0)
            self.assertFalse(interrupt)
            self.assertIsNone(audio)

    def test_sustained_voice_interrupts_once_and_preserves_start(self):
        detector = TurnDetector()
        zero = np.zeros(BLOCK, np.float32)
        signal = np.full(BLOCK, .03, np.float32)
        for _ in range(30):
            detector.feed(zero, 0)
        interrupts = []
        for _ in range(40):
            interrupts.append(detector.feed(signal, .99, speaking=True)[0])
        self.assertEqual(1, sum(interrupts))
        result = None
        for _ in range(80):
            _, audio, _ = detector.feed(zero, 0)
            if audio is not None: result = audio
        self.assertIsNotNone(result)
        self.assertEqual(40 * BLOCK, np.count_nonzero(result))

    def test_background_residual_does_not_hold_command_open(self):
        detector = TurnDetector()
        signal = np.full(BLOCK, .08, np.float32)
        noise = np.full(BLOCK, .005, np.float32)
        for _ in range(40): detector.feed(signal, .99)
        utterance = None
        for _ in range(65):
            _, utterance, _ = detector.feed(noise, .99)
        self.assertIsNotNone(utterance)
        self.assertFalse(detector.started)

    def test_pending_audio_status_includes_incomplete_interruption(self):
        voice = Voice()
        engine = Mock()
        engine.utterances.empty.return_value = True
        engine.detector.started = True
        voice._duplex = engine
        self.assertTrue(voice.status()['pending_audio'])
        engine.detector.started = False
        self.assertFalse(voice.status()['pending_audio'])
        engine.utterances.empty.return_value = False
        self.assertTrue(voice.status()['pending_audio'])

    def test_conversational_interruption_keeps_dictation_literal(self):
        from desktop.intent import normalize
        self.assertEqual('open calculator', normalize('Actually, open calculator.'))
        self.assertEqual('Type actually open calculator', normalize('Type actually open calculator'))

    def test_playback_settling_is_not_a_command(self):
        detector = TurnDetector()
        for _ in range(35):
            interrupt, audio, _ = detector.feed(np.full(BLOCK, .1, np.float32), .99,
                                                speaking=True, settling=True)
            self.assertFalse(interrupt)
            self.assertIsNone(audio)

    def test_wav_resampling_and_stereo_downmix(self):
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(24000)
            w.writeframes(np.full((240, 2), 16384, '<i2').tobytes())
        result = wav_samples(buf.getvalue())
        self.assertEqual(BLOCK, len(result))
        np.testing.assert_allclose(result, .5)

    def test_explicit_stop_discards_pending_commands(self):
        voice = Voice()
        engine = Mock()
        voice._duplex = engine
        voice.stop()
        self.assertTrue(voice._cancel.is_set())
        engine.cancel_playback.assert_called_once()
        engine.discard.assert_called_once()

    def test_barge_in_keeps_capture_and_invokes_cancellation(self):
        voice = Voice()
        voice._duplex = Mock()
        voice.on_interrupt = Mock()
        voice._barge_in()
        self.assertTrue(voice._speech_interrupted.is_set())
        self.assertFalse(voice._cancel.is_set())
        voice._duplex.discard.assert_not_called()
        voice.on_interrupt.assert_called_once()

    def test_session_closes_microphone(self):
        voice = Voice()
        engine = Mock()
        voice._duplex = engine
        voice.session(False)
        engine.close.assert_called_once()
        self.assertIsNone(voice._duplex)
        self.assertEqual('off', voice.status()['aec'])

    def test_failed_device_uses_safe_turn_by_turn_fallback(self):
        voice = Voice()
        voice.session(True)
        with patch.object(DuplexAudio, 'start', side_effect=RuntimeError('no microphone')):
            self.assertIsNone(voice._ensure_duplex())
        self.assertEqual('unavailable', voice.status()['aec'])
        self.assertIn('turn-by-turn', voice.status()['error'])

    def test_actual_webrtc_suppresses_delayed_echo(self):
        from pywebrtc_audio import AudioProcessor
        ap = AudioProcessor(sample_rate=RATE, echo_cancellation=True, noise_suppression=True,
                            stream_delay_ms=60)
        rng = np.random.default_rng(42)
        far = rng.normal(0, .08, RATE * 5).astype(np.float32)
        near = np.concatenate([np.zeros(2880, np.float32), far[:-2880] * .6])
        clean = np.concatenate([ap.process(near[i:i+BLOCK], far[i:i+BLOCK])
                                for i in range(0, len(far), BLOCK)])
        before = np.mean(near[-RATE:] ** 2)
        after = np.mean(clean[-RATE:] ** 2)
        self.assertLess(after, before / 10, 'AEC must reduce simulated delayed echo by at least 10 dB')


if __name__ == '__main__':
    unittest.main()
