import tempfile
import time
import unittest
from unittest.mock import patch
from desktop.personality import adjustment, style, traits, validate, options
from desktop.runtime import Runtime
from desktop.storage import Store


class PersonalityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.runtime=Runtime(self.temp.name)
        self.identity=self.runtime.new_conversation()

    def send(self,text):
        job=self.runtime.start_chat(self.identity,text)
        for _ in range(200):
            result=self.runtime.poll_chat(job)
            if result['done']: return result
            time.sleep(.01)
        self.fail('Personality request did not finish')

    def test_validation_and_persistence(self):
        self.runtime.save_settings({'personality_preset':'funny','personality_traits':{'humor':90,'honesty':0}})
        saved=Store(self.temp.name).settings()
        self.assertEqual(traits(saved)['humor'],90)
        self.assertEqual(traits(saved)['honesty'],0)
        for value in ([],{'shell':50},{'humor':True},{'honesty':-1},{'discretion':101},{'seriousness':.5}):
            with self.assertRaises(ValueError): validate(value)

    def test_all_styles_keep_truth_and_permission_rules(self):
        for profile in options():
            prompt=style({'personality_preset':profile['key'],'personality_traits':{'honesty':0}})
            self.assertIn('Always be truthful',prompt)
            self.assertIn('do not change action permissions',prompt)
            self.assertIn('never mock',prompt)

    def test_explicit_adjustments_not_examples_or_negation(self):
        self.assertEqual(adjustment('Be funnier!')['personality_preset'],'funny')
        self.assertEqual(adjustment('Set your humour to 80 percent')['personality_traits'],{'humor':80})
        self.assertEqual(adjustment('Hey Bob, could you please set your humor to eighty percent?')['personality_traits'],{'humor':80})
        for text in ('Do not be serious','Explain the phrase be funny','I said "be funny"','Can you explain discretion?'):
            self.assertIsNone(adjustment(text))
        with self.assertRaises(ValueError): adjustment('Set humor to 200')

    def test_conversational_adjustment_no_model_or_windows_actions(self):
        with patch('desktop.runtime.ChatConnection') as model, patch.object(self.runtime._commands,'execute') as execute:
            self.send('Be more honest')
            self.assertEqual(self.runtime.bootstrap()['settings']['personality_preset'],'candid')
            self.send('Set your humor to 80')
            self.send('Set discretion to 95')
            self.assertEqual(self.runtime.bootstrap()['settings']['personality_traits'],{'humor':80,'discretion':95})
            self.send('Stop joking')
            self.assertEqual(self.runtime.bootstrap()['settings']['personality_traits']['humor'],0)
            self.send('Be serious')
            self.assertEqual(self.runtime.bootstrap()['settings']['personality_traits'],{})
            model.assert_not_called(); execute.assert_not_called()

    def test_traits_reach_conversation_prompt(self):
        self.runtime.save_settings({'personality_preset':'discreet','personality_traits':{'humor':85,'honesty':100}})
        with patch('desktop.runtime.ChatConnection') as model:
            model.return_value.stream.return_value=iter([{'message':{'content':'Let’s make a plan.'},'done':True}])
            result=self.send('Help me plan my afternoon')
            prompt=model.call_args.args[1]['messages'][0]['content']
            self.assertIn('be playful and funny',prompt)
            self.assertIn('be frank and direct',prompt)
            self.assertIn('do not volunteer private facts',prompt)
            self.assertEqual(result['error'],'')
