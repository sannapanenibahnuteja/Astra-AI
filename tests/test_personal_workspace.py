import json
import tempfile
import threading
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from desktop.storage import Store
from desktop.runtime import Runtime
from desktop.automations import Automations
from desktop import screen


class PersonalWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(self.temp.name)
        self.runtime = Runtime.__new__(Runtime)
        self.runtime._store = self.store
        self.runtime._voice = SimpleNamespace(status=lambda: {'phase':'idle'})
        self.runtime._commands = SimpleNamespace(plan=Mock(return_value={'action':'volume','target':'20','confirm':False}), execute=Mock(return_value='Volume is 20%.'))
        self.runtime._job = None
        self.runtime._lock = threading.Lock()
        self.routines = Automations(self.runtime)

    def tearDown(self): self.temp.cleanup()

    def routine(self, **extra):
        return self.routines.save({'name':'Focus', 'steps':['set volume to 20 percent'], 'schedule':'09:00', **extra})[0]

    def test_daily_runs_once_even_after_restart(self):
        self.routine()
        now = datetime(2026, 10, 12, 9, 0)
        self.routines.tick(now)
        Automations(self.runtime).tick(now)
        self.runtime._commands.execute.assert_called_once()
        self.assertEqual(self.routines.rows()[0]['result'], 'Volume is 20%.')

    def test_busy_does_not_consume_due_routine(self):
        self.routine(); self.runtime._job = {'done':False}
        self.routines.tick(datetime(2026,10,12,9,0))
        self.assertEqual(self.routines.rows()[0]['last_day'], '')
        self.runtime._commands.execute.assert_not_called()

    def test_paused_and_missed_routines_do_not_run(self):
        self.routine(enabled=False)
        self.routines.tick(datetime(2026,10,12,9,0))
        self.routines.tick(datetime(2026,10,12,10,0))
        self.runtime._commands.execute.assert_not_called()

    def test_all_steps_validated_before_side_effects(self):
        row=self.routine()
        self.runtime._commands.plan.return_value={'action':'close_window','target':'app','confirm':True}
        self.routines.tick(datetime(2026,10,12,9,0))
        self.runtime._commands.execute.assert_not_called()
        self.assertIn('Stopped:',self.routines.rows()[0]['result'])
        self.assertEqual(row['last_day'],'')

    def test_rejects_unsafe_or_unknown_daily_steps(self):
        for value in (None, {'action':'type_text','confirm':False}, {'action':'open','confirm':True}):
            self.runtime._commands.plan.return_value=value
            with self.assertRaises(ValueError): self.routine()
        self.assertEqual(self.routines.rows(), [])

    def test_manual_can_store_natural_instructions(self):
        self.runtime._commands.plan.return_value=None
        row=self.routine(schedule='',steps=['Help me plan my day'])
        self.assertEqual(row['steps'],['Help me plan my day'])
        self.routines.delete(row['id']); self.assertEqual(self.routines.rows(),[])

    def test_partial_failure_stops_following_steps(self):
        self.routine(steps=['step one','step two','step three'])
        self.runtime._commands.execute.side_effect=['Volume is 20%.',RuntimeError('Blocked')]
        self.routines.tick(datetime(2026,10,12,9,0))
        self.assertEqual(self.runtime._commands.execute.call_count,2)
        self.assertIn('Stopped: Blocked',self.routines.rows()[0]['result'])

    def test_invalid_builder_inputs(self):
        for extra in ({'schedule':'25:00'},{'steps':[]},{'name':''},{'enabled':'yes'},{'steps':['x']*13}):
            with self.assertRaises(ValueError): self.routine(**extra)

    def test_voice_routine_lookup_and_ambiguity(self):
        self.routine(schedule='')
        self.assertEqual(self.routines.request('Run my routine Focus'), 'set volume to 20 percent')
        self.assertIsNone(self.routines.request('Tell me about focus'))
        with self.assertRaises(ValueError): self.routines.request('run routine Missing')
        self.routine(schedule='')
        with self.assertRaises(ValueError): self.routines.request('run routine Focus')

    def test_setup_is_optional_and_scoped(self):
        self.runtime._memory_profile=lambda:'person-1'
        self.runtime.bootstrap=lambda:{'memories':self.store.memories('person-1')}
        data=self.runtime.personal_setup({'preferred name':' Alex ', 'communication style':''})
        self.assertEqual(data['memories'],[{'key':'preferred name','value':'Alex'}])
        self.assertEqual(self.store.memories(),[])
        self.assertTrue(self.store.settings()['onboarding_done'])

    def test_setup_validates_everything_before_saving(self):
        with self.assertRaises(ValueError): self.runtime.personal_setup({'preferred name':'Alex','unknown':'x'})
        self.assertEqual(self.store.memories(),[])

    def test_screen_rejects_changed_window(self):
        with patch('desktop.windows.window_inventory',return_value=[]), patch('desktop.windows.execute') as execute:
            with self.assertRaises(ValueError): screen.observe({'handle':1,'title':'Old','process':'app'})
            execute.assert_not_called()

    def test_screen_reads_only_selected_accessibility_window(self):
        ref={'handle':1,'title':'Fixture','process':'app'}
        with patch('desktop.windows.window_inventory',return_value=[ref]), patch('desktop.windows.execute',return_value=json.dumps({'window':'Fixture','controls':[{'name':'Save','type':'Button'}]})) as execute:
            data=screen.observe(ref)
            execute.assert_called_once_with('inspect_window','','Fixture',reference=ref)
            self.assertIn('password',data['note'])

    def test_screen_click_requires_fresh_observation_and_confirmation(self):
        ref={'handle':1,'title':'Fixture','process':'app'}
        import time
        context={'screen_observation':{'at':time.time(),'reference':ref,'data':{'controls':[{'name':'Save','type':'Button'}]}}}
        plan=screen.plan('click Save in this window',context,ref)
        self.assertTrue(plan['confirm']); self.assertEqual(plan['_window_ref'],ref)
        context['screen_observation']['at']=0
        self.assertEqual(screen.plan('click Save in this window',context,ref)['action'],'clarify')

    def test_ambiguous_controls_ask_small_question(self):
        import time
        ref={'handle':1,'title':'Fixture'}
        context={'screen_observation':{'at':time.time(),'reference':ref,'data':{'controls':[{'name':'Save'},{'name':'Save'}]}}}
        self.assertEqual(screen.plan('click Save in this window',context,ref)['action'],'clarify')

    def test_shutdown_continues_after_a_service_failure(self):
        from desktop.lifecycle import shutdown
        self.runtime._automations = self.routines
        self.runtime._commands.reminders = SimpleNamespace(stop=threading.Event())
        self.runtime.cancel_chat = Mock(side_effect=RuntimeError('Fixture failure'))
        self.runtime.close_mobile = Mock()
        self.runtime._voice.close = Mock()
        with self.assertLogs(level='ERROR'): shutdown(self.runtime)
        self.assertTrue(self.routines.stop.is_set())
        self.assertTrue(self.runtime._commands.reminders.stop.is_set())
        self.runtime.close_mobile.assert_called_once()
        self.runtime._voice.close.assert_called_once()


if __name__ == '__main__': unittest.main()
