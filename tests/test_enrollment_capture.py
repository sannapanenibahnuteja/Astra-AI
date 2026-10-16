import unittest
from unittest.mock import Mock, patch
import numpy as np
from desktop.voice import Voice


class EnrollmentCaptureTests(unittest.TestCase):
    def capture(self, mode):
        voice = Voice()
        voice._pause_wake = Mock()
        voice._ensure_duplex = Mock(side_effect=AssertionError('Enrollment must bypass conversation detector'))
        voice._recognize_speaker = Mock(return_value={'enrollment': {'samples': 1}})
        reads = []
        class Stream:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, count):
                if count != 800: return np.zeros((count, 1), dtype=np.float32), False
                index = len(reads)
                reads.append(index)
                # Six seconds of silence between two speech passages.
                value = .04 if index < 100 or index >= 220 else 0
                if index == 340:
                    if mode == 'finish': voice.finish_enrollment()
                    if mode == 'cancel': voice.stop()
                return np.full((count, 1), value, dtype=np.float32), False
        with patch('sounddevice.query_devices', return_value={'default_samplerate':16000}), patch('sounddevice.InputStream', return_value=Stream()), patch('winsound.Beep'):
            result = voice.listen(enrollment='Test')
        return voice, reads, result

    def test_long_mid_sentence_pause_keeps_recording_until_finish(self):
        voice, reads, result = self.capture('finish')
        self.assertEqual(len(reads), 341)
        self.assertEqual(result['enrollment']['samples'], 1)
        audio = voice._recognize_speaker.call_args.args[1]
        self.assertGreater(len(audio), 16*16000)
        self.assertFalse(voice.status()['enrolling'])

    def test_cancel_discards_current_take(self):
        voice, reads, result = self.capture('cancel')
        self.assertEqual(len(reads), 341)
        voice._recognize_speaker.assert_not_called()
        self.assertEqual(result['text'], '')

    def test_recording_is_bounded_even_without_finish(self):
        voice, reads, result = self.capture('timeout')
        self.assertLessEqual(len(reads), 1201)
        self.assertGreaterEqual(len(reads), 1200)
        self.assertEqual(result['enrollment']['samples'], 1)

    def test_finish_is_inert_outside_enrollment(self):
        voice = Voice()
        self.assertFalse(voice.finish_enrollment())
        self.assertFalse(voice._finish_enrollment.is_set())
