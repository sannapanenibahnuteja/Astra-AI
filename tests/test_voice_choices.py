import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from desktop import voice_choices, speech_output
from desktop.runtime import Runtime


class VoiceChoiceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.runtime=Runtime(self.temp.name)

    def test_settings_persist_and_apply_without_credentials(self):
        with patch('desktop.voice_choices.installed',return_value=[{'id':'Microsoft David'}]):
            self.runtime.save_settings({'voice_provider':'windows','windows_voice':'Microsoft David','neural_voice':'en-US-AvaMultilingualNeural'})
            with self.assertRaises(ValueError): self.runtime.save_settings({'windows_voice':'invented'})
        reopened=Runtime(self.temp.name)
        self.assertEqual(reopened._voice.voice_options['windows_voice'],'Microsoft David')
        for invalid in [{'voice_provider':'secret'},{'neural_voice':'not-a-voice'}]:
            with self.assertRaises(ValueError): self.runtime.save_settings(invalid)

    def test_neural_preview_requires_configuration_and_does_not_save(self):
        with patch.object(self.runtime._voice,'speak',return_value=True) as speak:
            with self.assertRaises(ValueError): self.runtime.preview_voice({'voice_provider':'azure'})
            speak.assert_not_called()
            self.runtime.preview_voice({'voice_provider':'windows'})
            self.assertEqual(speak.call_args.args[3]['voice_provider'],'windows')
            self.assertEqual(self.runtime._store.settings()['voice_provider'],'auto')

    def test_catalog_never_returns_secrets(self):
        (Path(self.temp.name)/'neural-voice.json').write_text(json.dumps({'enabled':True,'region':'eastus','key':'PRIVATEKEY'}))
        with patch('desktop.voice_choices.installed',return_value=[]): catalog=self.runtime.voice_options()
        self.assertTrue(catalog['azure_ready'])
        self.assertNotIn('PRIVATEKEY',str(catalog))

    def test_neural_selection_rate_and_text_escaping(self):
        root=Path(self.temp.name)
        (root/'neural-voice.json').write_text(json.dumps({'enabled':True,'region':'eastus','key':'private','voice':'en-US-EmmaMultilingualNeural'}))
        response=Mock(); response.read.return_value=b'RIFFaudio'
        response.__enter__=Mock(return_value=response); response.__exit__=Mock(return_value=False)
        with patch('desktop.speech_output.urlopen',return_value=response) as send:
            self.assertEqual(speech_output.neural_audio('A & B <hello>',root,'en-US-AvaMultilingualNeural',2),b'RIFFaudio')
        xml=send.call_args.args[0].data.decode()
        self.assertIn('en-US-AvaMultilingualNeural',xml)
        self.assertIn('rate="13%"',xml)
        self.assertIn('A &amp; B &lt;hello&gt;',xml)

if __name__=='__main__': unittest.main()
