"""Result-driven workflows, without manipulating the user's desktop."""
import tempfile
import time
import unittest
from unittest.mock import Mock, patch
from desktop.runtime import Runtime


def turn(action=None, target='', content='Done with your task.'):
    message = {'content':content} if action is None else {'tool_calls':[
        {'function':{'name':'windows_action', 'arguments':{'action':action, 'target':target}}}]}
    connection = Mock()
    connection.stream.return_value = iter([{'message':message, 'done':True}])
    return connection


class AgentWorkflows(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.runtime = Runtime(self.temp.name)
        self.runtime._commands.apps['notepad'] = ('exe', 'notepad.exe')
        self.identity = self.runtime.new_conversation()
        self.addCleanup(self.temp.cleanup)

    def send(self, text):
        job = self.runtime.start_chat(self.identity, text)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            result = self.runtime.poll_chat(job)
            if result['done']: return result
            time.sleep(.01)
        self.fail('Workflow did not finish')

    def plan(self, text, identity):
        return {'action':'open','target':'notepad'} if text == 'open notepad' else None

    def test_continues_after_noninspection_and_receives_results(self):
        with patch.object(self.runtime._commands, 'plan', side_effect=self.plan), \
             patch.object(self.runtime._commands, 'execute', side_effect=['Opened Notepad.', 'Typed Hello.']) as execute, \
             patch('desktop.runtime.ChatConnection', side_effect=[turn('open','notepad'), turn('type_text','Hello'), turn()]) as model:
            result = self.send('Please prepare a hello note for me')
            self.assertEqual(execute.call_count, 2)
            feedback = model.call_args_list[1].args[1]['messages']
            self.assertIn('Opened Notepad.', str(feedback))
            self.assertIn('prepare a hello note', str(feedback))
            self.assertEqual(result['steps'], 2)
            self.assertEqual(result['error'], '')

    def test_confirmation_resumes_original_goal_without_repeating(self):
        with patch.object(self.runtime._commands, 'plan', side_effect=self.plan), \
             patch.object(self.runtime._commands, 'execute', return_value='Success') as execute, \
             patch('desktop.runtime.ChatConnection', side_effect=[turn('lock'), turn('time'), turn()]) as model:
            waiting = self.send('Please secure my workspace and then tell me the time')
            self.assertEqual(waiting['progress'], 'Waiting for confirmation')
            execute.assert_not_called()
            result = self.send('yes')
            self.assertEqual([call.args[0]['action'] for call in execute.call_args_list], ['lock','time'])
            self.assertIn('secure my workspace', str(model.call_args_list[1].args[1]['messages']))
            self.assertNotIn(self.identity, self.runtime._pending)
            self.assertEqual(result['error'], '')

    def test_failure_stops_later_actions(self):
        with patch.object(self.runtime._commands, 'plan', side_effect=self.plan), \
             patch.object(self.runtime._commands, 'execute', side_effect=RuntimeError('Window disappeared')) as execute, \
             patch('desktop.runtime.ChatConnection', side_effect=[turn('open','notepad'), turn('type_text','Hello')]) as model:
            result = self.send('Prepare my note')
            self.assertEqual(execute.call_count, 1)
            self.assertEqual(model.call_count, 1)
            self.assertIn('Window disappeared', result['error'])

    def test_repeated_action_is_not_executed_again(self):
        with patch.object(self.runtime._commands, 'plan', side_effect=self.plan), \
             patch.object(self.runtime._commands, 'execute', return_value='Opened') as execute, \
             patch('desktop.runtime.ChatConnection', side_effect=[turn('open','notepad'), turn('open','notepad')]):
            result = self.send('Prepare my note')
            self.assertEqual(execute.call_count, 1)
            self.assertIn('repeated', result['error'])

    def test_cancellation_prevents_followup_planning(self):
        def cancel(*args):
            self.runtime._job['cancel'].set()
            return 'Opened'
        with patch.object(self.runtime._commands, 'plan', side_effect=self.plan), \
             patch.object(self.runtime._commands, 'execute', side_effect=cancel), \
             patch('desktop.runtime.ChatConnection', side_effect=[turn('open','notepad'), turn('time')]) as model:
            result = self.send('Prepare my note')
            self.assertEqual(model.call_count, 1)
            self.assertIn('[Response stopped.]', result['text'])

    def test_multiple_approvals_keep_completed_results(self):
        batch = turn('time')
        batch.stream.return_value = iter([{'message':{'tool_calls':[
            {'function':{'name':'windows_action','arguments':{'action':'time','target':''}}},
            {'function':{'name':'windows_action','arguments':{'action':'lock','target':''}}},
            {'function':{'name':'windows_action','arguments':{'action':'wifi_disconnect','target':''}}}]}, 'done':True}])
        with patch.object(self.runtime._commands, 'plan', side_effect=self.plan), \
             patch.object(self.runtime._commands, 'execute', side_effect=['Time checked','Locked','Disconnected']) as execute, \
             patch('desktop.runtime.ChatConnection', side_effect=[batch, turn()]) as model:
            self.send('Please check the time, lock my PC and disconnect Wi-Fi')
            self.assertEqual(execute.call_count, 1)
            self.send('yes')
            self.assertEqual(execute.call_count, 2)
            result = self.send('yes')
            self.assertEqual(execute.call_count, 3)
            self.assertEqual(result['steps'], 3)
            self.assertEqual(result['error'], '')
            self.assertIn('Time checked', str(model.call_args_list[-1].args[1]['messages']))

    def test_planning_round_limit_stops_without_repeating(self):
        with patch.object(self.runtime._commands, 'plan', side_effect=self.plan), \
             patch.object(self.runtime._commands, 'execute', return_value='Done') as execute, \
             patch('desktop.runtime.ChatConnection', side_effect=[turn('note',str(i)) for i in range(9)]) as model:
            result = self.send('Make my notes')
            self.assertEqual(execute.call_count, 8)
            self.assertEqual(model.call_count, 8)
            self.assertIn('eight-round', result['error'])
