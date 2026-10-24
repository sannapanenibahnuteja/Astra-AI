import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from desktop.speech_models import path_for, options
from desktop.runtime import Runtime
from desktop.voice_model_diagnostics import errors


class SpeechModelTests(unittest.TestCase):
    def test_unknown_and_path_traversal_are_not_models(self):
        for identity in ('../private', '/tmp/model', 'large-v9', None, []):
            with self.assertRaises(ValueError):
                path_for(identity)

    def test_option_catalog_has_no_paths_and_runtime_never_downloads(self):
        rows = options()
        self.assertEqual({r['id'] for r in rows}, {'small.en', 'distil-large-v3'})
        self.assertTrue(all(set(row)=={'id','label','installed'} for row in rows))

    def test_settings_validate_before_saving_and_block_active_switch(self):
        with tempfile.TemporaryDirectory() as root:
            runtime = Runtime(root)
            try:
                with self.assertRaises(ValueError):
                    runtime.save_settings({'transcription_model':'../../private'})
                self.assertEqual(runtime._store.settings()['transcription_model'], 'small.en')
                runtime._voice._hold = True
                with self.assertRaisesRegex(ValueError, 'End the voice conversation'):
                    runtime.save_settings({'transcription_model':'distil-large-v3'})
                runtime._voice._hold = False
                old = object(); runtime._voice._model = old
                with patch('desktop.speech_models.path_for', return_value=Path(root)):
                    saved = runtime.save_settings({'transcription_model':'distil-large-v3'})
                self.assertEqual(saved['transcription_model'], 'distil-large-v3')
                self.assertIsNone(runtime._voice._model)
                self.assertEqual(runtime._voice.transcription_model, 'distil-large-v3')
            finally:
                runtime._voice.close()

    def test_missing_model_does_not_save_broken_selection(self):
        with tempfile.TemporaryDirectory() as root:
            runtime = Runtime(root)
            try:
                with patch('desktop.speech_models.path_for', side_effect=RuntimeError('incomplete')):
                    with self.assertRaises(RuntimeError):
                        runtime.save_settings({'transcription_model':'distil-large-v3'})
                self.assertEqual(runtime._store.settings()['transcription_model'], 'small.en')
            finally:
                runtime._voice.close()

    def test_word_error_measurement(self):
        self.assertEqual(errors('Hey Bob, stop.', 'hey bob stop'), (0,3))
        self.assertEqual(errors('open the calculator', 'open calculator'), (1,3))


if __name__ == '__main__':
    unittest.main()
