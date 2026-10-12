import json
import tempfile
import time
import unittest
from datetime import datetime
from unittest.mock import patch, Mock
from desktop.runtime import Runtime


class VoiceAutomationsTests(unittest.TestCase):
    def test_semantic_setup_confirms_once_and_does_not_claim_early_success(self):
        with tempfile.TemporaryDirectory() as root:
            runtime=Runtime(root); runtime._store.save_settings({'voice_enabled':False})
            identity=runtime.new_conversation()
            routine={'name':'Morning','steps':['open youtube','set volume to 35'],'schedule':'08:00'}
            payload={'intent':'action','actions':[{'action':'automation_create','target':json.dumps(routine),'final_step':True}],'reply':'I have saved it!'}
            model=Mock(); model.stream.return_value=iter([{'message':{'content':json.dumps(payload)},'done':True}])
            def send(text):
                key=runtime.start_chat(identity,text,True)
                deadline=time.monotonic()+5
                while time.monotonic()<deadline:
                    result=runtime.poll_chat(key)
                    if result['done']: return result
                    time.sleep(.01)
                self.fail('Voice routine did not finish')
            with patch.object(runtime._commands,'capture_explorer'),patch('desktop.runtime.ChatConnection',return_value=model) as generate:
                waiting=send('Set up a daily routine called Morning at 8 AM: open YouTube and set volume to 35 percent.')
                self.assertEqual(waiting['progress'],'Waiting for confirmation')
                self.assertNotIn('I have saved',waiting['text'])
                self.assertEqual(runtime._automations.rows(),[])
                done=send('yes')
                self.assertEqual(len(runtime._automations.rows()),1)
                self.assertIn('Saved routine Morning',done['text'])
                self.assertEqual(generate.call_count,1)

    def test_voice_plan_saves_without_executing_then_scheduler_runs_once(self):
        with tempfile.TemporaryDirectory() as root:
            runtime=Runtime(root); identity=runtime.new_conversation()
            action={'action':'automation_create','target':json.dumps({'name':'Morning','steps':['open youtube','set volume to 35'],'schedule':'08:00'})}
            plan=runtime._commands.validate_model_action(action,identity)
            self.assertTrue(plan['confirm'])
            with patch.object(runtime._commands,'execute',wraps=runtime._commands.execute) as execute:
                result=runtime._commands.execute(plan,identity)
                self.assertIn('daily at 08:00',result); self.assertEqual(execute.call_count,1)
            with patch.object(runtime._commands,'execute',side_effect=['Opened YouTube.','Volume set to 35.']) as execute:
                runtime._automations.tick(datetime(2026,10,14,8,0))
                runtime._automations.tick(datetime(2026,10,14,8,0))
                self.assertEqual(execute.call_count,2)
            self.assertIn('Volume set',runtime._automations.rows()[0]['result'])

    def test_consequential_scheduled_steps_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            runtime=Runtime(root)
            action={'action':'automation_create','target':json.dumps({'name':'Unsafe','steps':['lock computer'],'schedule':'08:00'})}
            with self.assertRaises(ValueError): runtime._commands.validate_model_action(action,runtime.new_conversation())
            self.assertEqual(runtime._automations.rows(),[])
