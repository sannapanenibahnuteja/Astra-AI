import tempfile
import time
import unittest
from unittest.mock import patch
from desktop import window_tasks, tab_tasks, browser, conversation
from desktop.runtime import Runtime

class WindowGroupTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.runtime=Runtime(self.temp.name); self.identity=self.runtime.new_conversation()
        self.rows=[{'handle':1,'title':'YouTube - Edge','process':'msedge.exe'}, {'handle':2,'title':'Other page - Edge','process':'msedge.exe'}, {'handle':3,'title':'YouTube notes','process':'notepad.exe'}]
        self.tabs=[{'handle':1,'id':[1],'title':'YouTube'}, {'handle':2,'id':[2],'title':'Video - YouTube'}]

    def test_whole_windows_include_inactive_tabs_and_exclude_notes(self):
        with patch('desktop.windows.window_inventory',return_value=self.rows),patch('desktop.tab_tasks.inventory',return_value=self.tabs):
            steps=self.runtime._commands.plan('close all youtube windows',self.identity)
        self.assertEqual([s['_window_ref']['handle'] for s in steps],[1,2])
        self.assertIn('ALL their tabs',steps[0]['description'])
        self.assertTrue(steps[0]['confirm'])
        self.assertEqual(self.runtime._commands.plan('close all',self.identity),steps)

    def test_first_window_retains_other_for_followup(self):
        self.runtime._commands.window_choices[self.identity]=(time.monotonic(),self.rows[:2])
        self.runtime._store.context(self.identity,{'last_reference':'windows'})
        step=self.runtime._commands.plan('close the first one',self.identity)[0]
        with patch('desktop.windows.window_inventory',return_value=self.rows),patch('desktop.windows.execute',return_value='Closed window.'):
            self.runtime._commands.execute(step,self.identity)
        other=self.runtime._commands.plan('close the other one',self.identity)
        self.assertEqual(other[0]['_window_ref']['handle'],2)

    def test_tab_subset_retains_remaining_and_expired_reference_clarifies(self):
        context={'last_window':'Microsoft Edge','last_reference':'tabs','tab_reference':{'query':'youtube','time':time.time(),'tabs':self.tabs}}
        command=tab_tasks.prepare(tab_tasks.request('close the first one',context),context)
        with patch('desktop.tab_tasks.execute',return_value='Closed 1 selected Edge tab(s).'):
            browser.execute(command,context)
        self.assertEqual(tab_tasks.request('close the other one',context)['tabs'],self.tabs[1:])
        context['tab_reference']['time']=0
        self.assertEqual(tab_tasks.request('close it',context)['action'],'clarify')

    def test_success_claim_detection(self):
        self.assertTrue(conversation.success_claim('I opened YouTube.'))
        self.assertFalse(conversation.success_claim('I can open YouTube.'))

    def test_launch_verification_matches_process_and_does_not_log_request(self):
        from desktop.launch import wait_for_app
        wrong=[{'handle':4,'title':'Calculator guide - Edge','process':'msedge.exe'}]
        with patch('desktop.windows.window_inventory',return_value=wrong):
            self.assertIsNone(wait_for_app('calculator','calc.exe',timeout=0))
        with patch('desktop.commands.subprocess.Popen'),patch('desktop.launch.wait_for_app',return_value=None):
            result=self.runtime._commands.execute({'action':'open','target':'calculator'},self.identity)
        self.assertIn('could not verify',result)
        self.assertNotIn('Opened',result)
        self.assertFalse(self.runtime._store.context(self.identity).get('last_app'))

if __name__=='__main__': unittest.main()
