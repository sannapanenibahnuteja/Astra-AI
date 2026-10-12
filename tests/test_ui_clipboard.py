import unittest
from unittest.mock import Mock, patch
from desktop.runtime import Runtime


class ClipboardTests(unittest.TestCase):
    def test_unicode_copy_closes_clipboard(self):
        runtime = Runtime.__new__(Runtime)
        clipboard = Mock()
        with patch.dict('sys.modules', {'win32clipboard': clipboard}):
            self.assertTrue(runtime.copy_text('Hello, నమస్కారం'))
        clipboard.SetClipboardData.assert_called_once_with(13, 'Hello, నమస్కారం')
        clipboard.CloseClipboard.assert_called_once()

    def test_failed_write_releases_clipboard_and_reports_error(self):
        clipboard = Mock()
        clipboard.SetClipboardData.side_effect = RuntimeError('Clipboard busy')
        with patch.dict('sys.modules', {'win32clipboard': clipboard}):
            with self.assertRaisesRegex(RuntimeError, 'Clipboard busy'):
                Runtime.__new__(Runtime).copy_text('Fixture')
        clipboard.CloseClipboard.assert_called_once()

    def test_invalid_input_does_not_open_clipboard(self):
        clipboard = Mock()
        with patch.dict('sys.modules', {'win32clipboard': clipboard}):
            with self.assertRaises(ValueError):
                Runtime.__new__(Runtime).copy_text({'not': 'text'})
        clipboard.OpenClipboard.assert_not_called()
