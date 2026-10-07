import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from unittest.mock import Mock
from types import SimpleNamespace
from desktop import tab_tasks
from desktop.commands import Commands
from desktop.storage import Store


class TabContextTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{'handle':1,'id':[1,2],'title':'YouTube'},
                     {'handle':2,'id':[3,4],'title':'Video - YouTube'},
                     {'handle':2,'id':[5,6],'title':'GitHub'}]

    def test_ambiguity_then_close_all_freezes_only_matching_tabs(self):
        context = {}
        with patch.object(tab_tasks,'inventory',return_value=self.rows):
            with self.assertRaisesRegex(ValueError,'Several tabs'):
                tab_tasks.prepare({'action':'edge_close_tab','target':'youtube'},context)
            for text in ['close all','close all those','close both','close them']:
                command=tab_tasks.prepare(tab_tasks.request(text,context),context)
                self.assertEqual(command['tabs'],self.rows[:2])
                self.assertIn('2 selected',command['description'])
            with patch.object(tab_tasks,'close_one',return_value=True) as close:
                self.assertIn('Closed 2',tab_tasks.execute(command))
                self.assertEqual([c.args[0] for c in close.call_args_list],self.rows[:2])

    def test_natural_direct_commands_and_conversation_isolation(self):
        with tempfile.TemporaryDirectory() as root:
            commands=Commands(Store(root))
            for text in ['close all YouTube','Hey Bob, please close all YouTube tabs.']:
                plan=commands.plan(text,'a')
                self.assertEqual((plan['action'],plan['target']),('edge_close_tabs','youtube'))
            context={'last_window':'Microsoft Edge','tab_reference':{'query':'youtube','tabs':self.rows[:2],'time':time.time()}}
            commands.store.context('a',context)
            self.assertEqual(commands.plan('close all','a')['tabs'],self.rows[:2])
            self.assertEqual(commands.plan('close all','b')['action'],'clarify')
            context['tab_reference']['time']-=301
            self.assertEqual(tab_tasks.request('close all',context)['action'],'clarify')
            self.assertIsNone(commands.plan('do not close all YouTube','a'))

    def test_ordinal_and_single_reference_are_scoped(self):
        context={'last_window':'Microsoft Edge','tab_reference':{'query':'youtube','tabs':self.rows[:2],'time':time.time()}}
        self.assertEqual(tab_tasks.request('close the second one',context)['tabs'],self.rows[1:2])
        self.assertEqual(tab_tasks.request('close it',context)['action'],'clarify')
        context['tab_reference']['tabs']=self.rows
        self.assertEqual(tab_tasks.request('close both',context)['action'],'clarify')
        context.pop('tab_reference')
        context['last_opened_browser']={'handle':99,'time':time.time()}
        with patch.object(tab_tasks,'inventory',return_value=self.rows):
            with self.assertRaisesRegex(ValueError,'No matching'):
                tab_tasks.prepare(tab_tasks.request('close it',context),context)

    def test_cancellation_and_partial_failures_are_honest(self):
        command={'action':'edge_close_tabs','target':'youtube','tabs':self.rows[:2]}
        cancel=threading.Event()
        def close(*args): cancel.set(); return True
        with patch.object(tab_tasks,'close_one',side_effect=close) as call:
            self.assertIn('Stopped. Closed 1',tab_tasks.execute(command,cancel))
            self.assertEqual(call.call_count,1)
        with patch.object(tab_tasks,'close_one',side_effect=[True,RuntimeError('focus failed')]):
            with self.assertRaisesRegex(RuntimeError,'Closed 1.*focus failed'):
                tab_tasks.execute(command)
        with patch.object(tab_tasks,'close_one',return_value=False):
            self.assertIn('Closed 0',tab_tasks.execute(command))

    def test_native_close_verifies_identity_with_duplicate_titles(self):
        first=Mock(element_info=SimpleNamespace(runtime_id=[1,2],name='YouTube'))
        second=Mock(element_info=SimpleNamespace(runtime_id=[5,6],name='YouTube'))
        first.is_selected.return_value=True
        wrapper=Mock()
        wrapper.descendants.side_effect=[[first,second],[second]]
        with patch('pywinauto.Desktop') as desktop, patch('win32gui.IsWindow',return_value=True), \
             patch('win32gui.IsIconic',return_value=False), patch('win32gui.GetForegroundWindow',return_value=1), \
             patch('pywinauto.keyboard.send_keys') as keys:
            desktop.return_value.window.return_value.wrapper_object.return_value=wrapper
            self.assertTrue(tab_tasks.close_one(self.rows[0],'youtube'))
            keys.assert_called_once_with('^w')
            first.select.assert_called_once()
            second.select.assert_not_called()

    def test_native_close_refuses_changed_site_or_failed_focus(self):
        tab=Mock(element_info=SimpleNamespace(runtime_id=[1,2],name='GitHub'))
        wrapper=Mock();wrapper.descendants.return_value=[tab]
        with patch('pywinauto.Desktop') as desktop, patch('win32gui.IsWindow',return_value=True), \
             patch('win32gui.IsIconic',return_value=False), patch('win32gui.GetForegroundWindow',return_value=99), \
             patch('pywinauto.keyboard.send_keys') as keys:
            desktop.return_value.window.return_value.wrapper_object.return_value=wrapper
            with self.assertRaisesRegex(ValueError,'changed site'):
                tab_tasks.close_one(self.rows[0],'youtube')
            tab.element_info.name='YouTube'
            with self.assertRaisesRegex(RuntimeError,'receive focus'):
                tab_tasks.close_one(self.rows[0],'youtube')
            keys.assert_not_called()
