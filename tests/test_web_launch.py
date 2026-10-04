import unittest
from unittest.mock import Mock, patch
from desktop.intent import voice_request
from desktop import web_launch


class WebLaunchTests(unittest.TestCase):
    def setUp(self):
        inventory = patch.object(web_launch.windows, 'window_inventory', return_value=[])
        inventory.start()
        self.addCleanup(inventory.stop)

    def test_stop_listening_preserves_next_action(self):
        self.assertEqual({'text':'open youtube','stop_listening':True}, voice_request('Actually stop listening and open youtube'))
        self.assertEqual({'text':'','stop_listening':True}, voice_request('Actually, stop listening.'))
        for text in ('Do not stop listening and open youtube', 'Type stop listening and open youtube in Notepad'):
            self.assertFalse(voice_request(text)['stop_listening'])

    def test_close_youtube_targets_a_verified_tab_action(self):
        from desktop.commands import Commands
        from desktop.storage import Store
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            store = Store(folder)
            identity = store.new_conversation()
            plan = Commands(store).plan('Please close YouTube', identity)
            self.assertEqual('edge_close_tab',plan['action'])
            self.assertEqual('youtube',plan['target'])

    def test_browser_success_requires_visible_address(self):
        with patch.object(web_launch,'edge_path',return_value='edge.exe'), patch.object(web_launch,'visible_address',return_value=42), patch.object(web_launch.subprocess,'Popen') as launch:
            result, handle = web_launch.open_website('https://youtube.com')
            launch.assert_called_once_with(['edge.exe','--new-window','https://youtube.com'])
            self.assertEqual(42,handle)
            self.assertIn('address is visible',result)

    def test_launch_failure_does_not_report_opened(self):
        process = Mock(); process.poll.return_value = 1
        with patch.object(web_launch,'edge_path',return_value='edge.exe'), patch.object(web_launch,'visible_address',return_value=None), patch.object(web_launch.subprocess,'Popen',return_value=process):
            with self.assertRaises(RuntimeError): web_launch.open_website('https://youtube.com')

    def test_unverified_launch_is_not_reported_as_opened(self):
        with patch.object(web_launch,'edge_path',return_value='edge.exe'), patch.object(web_launch,'visible_address',return_value=None), patch.object(web_launch.subprocess,'Popen'), patch.object(web_launch.time,'monotonic',side_effect=[0,6]):
            result, handle = web_launch.open_website('https://youtube.com')
            self.assertIsNone(handle)
            self.assertTrue(result.startswith('Asked Edge'))


if __name__ == '__main__': unittest.main()
