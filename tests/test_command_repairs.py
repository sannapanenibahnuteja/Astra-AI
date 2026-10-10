"""Regressions for the repeated requests shown in the user's screenshot."""
import tempfile
import time
import unittest
from unittest.mock import Mock, patch
from desktop.runtime import Runtime
from desktop.intent import normalize, dictation
from desktop import tab_tasks

class CommandRepairs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.runtime = Runtime(self.temp.name)
        self.identity = self.runtime.new_conversation()

    def send(self, message):
        job = self.runtime.start_chat(self.identity, message)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            result = self.runtime.poll_chat(job)
            if result['done']: return result
            time.sleep(.01)
        self.fail('Request did not finish')

    def test_repetition_prefixes_execute_without_model(self):
        with patch('desktop.runtime.ChatConnection',side_effect=AssertionError('Routine commands must bypass model')), patch.object(self.runtime._commands,'execute',return_value='Verified window list') as execute:
            for text in ['As I said, list windows', 'I said list windows.', 'No, I said show open windows', 'Hey Bob, as I said, please list windows']:
                result = self.send(text)
                self.assertEqual(result['error'],'')
                self.assertEqual(execute.call_args.args[0]['action'],'list_windows')

    def test_split_site_name_closes_selected_tabs_across_windows(self):
        rows = [{'handle':1,'id':[1,2],'title':'YouTube'}, {'handle':2,'id':[3,4],'title':'Video - YouTube'}, {'handle':2,'id':[5,6],'title':'GitHub'}]
        with patch('desktop.runtime.ChatConnection',side_effect=AssertionError('Must bypass model')), patch.object(tab_tasks,'inventory',return_value=rows):
            waiting = self.send('I said close all you tube.')
            self.assertEqual(waiting['error'],'')
            self.assertIn('2 selected Edge tab(s)',waiting['text'])
        with patch.object(tab_tasks,'inventory',side_effect=AssertionError('Approval must not rescan')), patch.object(tab_tasks,'close_one',return_value=True) as close:
            done = self.send('yes')
            self.assertEqual(done['error'],'')
            self.assertIn('Closed 2',done['text'])
            self.assertEqual([c.args[0] for c in close.call_args_list],rows[:2])

    def test_whole_window_aliases_and_hidden_site_tabs(self):
        windows = [{'handle':1,'title':'Other page - Microsoft Edge','process':'msedge.exe'}, {'handle':2,'title':'Work - Microsoft Edge','process':'msedge.exe'}]
        with patch('desktop.windows.window_inventory',return_value=windows), patch.object(tab_tasks,'inventory',return_value=[{'handle':1,'id':[2],'title':'YouTube'}]):
            plan = self.runtime._commands.plan('I said close all you tube windows',self.identity)
            self.assertEqual([p['_window_ref']['handle'] for p in plan],[1])
            self.assertTrue(plan[0]['confirm'])
            self.assertIn('ALL their tabs',plan[0]['description'])

    def test_repairs_preserve_literals_and_negation(self):
        self.assertEqual(dictation('I said type "You tube, I said close all!" into Notepad')['target'],'You tube, I said close all!')
        for text in ['I said do not close YouTube', 'I said closing YouTube is annoying', 'As I said, explain how to close windows']:
            self.assertEqual(normalize(text),text)
            self.assertIsNone(self.runtime._commands.plan(text,self.identity))
        self.assertFalse(tab_tasks.matches('YouTube tutorials','you tube tutorial'))

    def connection(self, message):
        connection=Mock();connection.stream.return_value=iter([{'message':message,'done':True}]);return connection

    def test_empty_reply_retries_once_and_returns_answer(self):
        with patch.object(self.runtime._commands,'plan',return_value=None), patch('desktop.runtime.ChatConnection',side_effect=[self.connection({'content':''}),self.connection({'content':'Hello there.'})]) as model:
            result=self.send('Hello Bob')
            self.assertEqual(result['error'],'')
            self.assertEqual(result['text'],'Hello there.')
            self.assertEqual(model.call_count,2)
            self.assertEqual(model.call_args.args[1]['messages'][-1]['content'],'Hello Bob')

    def test_repeated_empty_reply_reports_failure_without_actions(self):
        with patch.object(self.runtime._commands,'plan',return_value=None), patch.object(self.runtime._commands,'execute') as execute, patch('desktop.runtime.ChatConnection',side_effect=[self.connection({'content':' '}),self.connection({'content':''})]) as model:
            result=self.send('Hello Bob')
            self.assertIn('empty reply twice',result['error'])
            self.assertEqual(model.call_count,2)
            execute.assert_not_called()

    def test_retry_cannot_claim_unexecuted_success(self):
        with patch.object(self.runtime._commands,'plan',return_value=None), patch.object(self.runtime._commands,'execute') as execute, patch('desktop.runtime.ChatConnection',side_effect=[self.connection({'content':''}),self.connection({'content':'Opened YouTube.'})]):
            result=self.send('Could you get YouTube ready for me')
            self.assertIn('without executing',result['text'])
            execute.assert_not_called()

    def test_dynamic_uia_depth_race_reenumerates_without_depth(self):
        from desktop.windows import accessible_descendants
        wrapper=Mock();wrapper.descendants.side_effect=[AttributeError("'NoneType' object has no attribute 'has_depth'"),['tab']]
        self.assertEqual(accessible_descendants(wrapper,control_type='TabItem',depth=15),['tab'])
        self.assertEqual(wrapper.descendants.call_args.kwargs,{'control_type':'TabItem'})
        wrapper.descendants.side_effect=AttributeError('unrelated failure')
        with self.assertRaisesRegex(AttributeError,'unrelated'):
            accessible_descendants(wrapper,depth=15)

    def test_single_and_explicit_edge_alias_requests(self):
        for request,action in [('close you tube','edge_close_tab'),('as I said, close all you tube tabs in Edge','edge_close_tabs'),('close all YouTube pages using Microsoft Edge','edge_close_tabs')]:
            with self.subTest(request=request):
                plan=self.runtime._commands.plan(request,self.identity)
                self.assertEqual((plan['action'],plan['target']),(action,'youtube'))

    def test_retry_keeps_target_context_and_saved_preferences(self):
        self.runtime._store.context(self.identity,{'last_window':'Notepad','last_app':'notepad'})
        self.runtime._store.remember('favourite colour','blue')
        with patch.object(self.runtime._commands,'plan',return_value=None),patch('desktop.runtime.ChatConnection',side_effect=[self.connection({'content':''}),self.connection({'content':'Tell me the text to write.'})]) as model:
            self.send('Could you help with that window?')
            prompt=model.call_args.args[1]['messages'][0]['content']
            self.assertIn('Notepad',prompt)
            self.assertIn('favourite colour',prompt)
            self.assertIn('blue',prompt)
            self.assertNotIn('Use move_window target=monitor number',prompt)

    def test_cancelled_empty_request_does_not_retry(self):
        connection=Mock()
        def stream():
            self.runtime._job['cancel'].set()
            yield {'message':{'content':''},'done':True}
        connection.stream.side_effect=stream
        with patch.object(self.runtime._commands,'plan',return_value=None),patch('desktop.runtime.ChatConnection',return_value=connection) as model:
            result=self.send('Hello Bob')
            self.assertIn('Response stopped',result['text'])
            self.assertEqual(model.call_count,1)
