import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from desktop.voice import Voice, transcript_result
from desktop.storage import Store


def segment(text='open calculator', confidence=.9, logprob=-.2, no_speech=.1):
    return SimpleNamespace(text=text, avg_logprob=logprob, no_speech_prob=no_speech,
                           words=[SimpleNamespace(probability=confidence)])

class VoiceTests(unittest.TestCase):
    def test_noise_is_not_a_command(self):
        self.assertEqual('', transcript_result([segment(no_speech=.95)])['text'])
        self.assertEqual('', transcript_result([])['text'])

    def test_uncertain_text_requires_review(self):
        result = transcript_result([segment(confidence=.5)])
        self.assertTrue(result['needs_review'])
        self.assertEqual('open calculator', result['text'])
        json.dumps(result)

    def test_clear_speech_and_poor_likelihood(self):
        self.assertFalse(transcript_result([segment()])['needs_review'])
        self.assertTrue(transcript_result([segment(logprob=-.9)])['needs_review'])

    def test_session_pauses_wake_and_close_disables_it(self):
        voice=Voice()
        voice.configure(True)
        voice.session(True)
        self.assertEqual('paused', voice.status()['wake'])
        voice.session(False)
        voice.close()
        self.assertEqual('off', voice.status()['wake'])
        self.assertTrue(voice._cancel.is_set())

    def test_rename_preserves_history_and_notes(self):
        with tempfile.TemporaryDirectory() as folder:
            legacy=Path(folder)/'Astra'
            source=Store(legacy)
            identity=source.new_conversation()
            source.append(identity,'user','My project is Moon Garden')
            source.remember('preferred name','Bhanu')
            (legacy/'notes').mkdir()
            (legacy/'notes'/'one.txt').write_text('Keep me')
            source.path.rename(legacy/'astra.db')
            with patch.dict(os.environ, {'LOCALAPPDATA':folder, 'BOB_DATA_DIR':''}):
                destination=Store()
                self.assertEqual('My project is Moon Garden',destination.messages(identity)[0]['content'])
                self.assertEqual('Bhanu',destination.memories()[0]['value'])
                self.assertEqual('Keep me',(destination.root/'notes'/'one.txt').read_text())
                destination.remember('preferred name','Bob user')
                self.assertEqual('Bob user',Store().memories()[0]['value'])

if __name__ == '__main__': unittest.main()
