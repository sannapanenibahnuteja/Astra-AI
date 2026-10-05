import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, Mock

from desktop import files, network, settings_control as settings
from desktop.commands import Commands
from desktop.runtime import describe
from desktop.runtime import Runtime
from desktop.storage import Store


class SystemTests(unittest.TestCase):
    def setUp(self):
        cache = Path(__file__).resolve().parents[1] / '.cache'
        cache.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=cache)
        self.root = Path(self.temp.name)
        self.store = Store(self.root / 'data')
        self.commands = Commands(self.store)
        self.identity = self.store.new_conversation()

    def tearDown(self): self.temp.cleanup()

    def test_radio_phrasings_negation_and_confirmation(self):
        for text in ('turn Bluetooth on', 'enable bluetooth', 'switch on bluetooth'):
            p = self.commands.plan(text, self.identity)
            self.assertEqual((p['action'],p['target'],p['value'],p['confirm']),('radio_set','bluetooth','on',False))
        self.assertTrue(self.commands.plan('disable Wi-Fi',self.identity)['confirm'])
        self.assertTrue(self.commands.plan('turn aeroplane mode on',self.identity)['confirm'])
        for text in ('do not turn bluetooth off','explain how to disconnect wifi'):
            self.assertIsNone(settings.parse(text, {}))

    def test_setting_followups_and_conversation_isolation(self):
        with patch('desktop.network.radio', return_value='Bluetooth is on.'):
            self.commands.execute(self.commands.plan('enable Bluetooth',self.identity),self.identity)
        p = self.commands.plan('turn it back off',self.identity)
        self.assertEqual((p['target'],p['value']),('bluetooth','off'))
        other = self.store.new_conversation()
        self.assertEqual(self.commands.plan('turn it back off',other)['action'],'clarify')
        plan = self.commands.plan('enable bluetooth and turn it off',other)
        self.assertEqual([p['target'] for p in plan],['bluetooth','bluetooth'])

    def test_compound_does_not_split_setting_names_or_quoted_paths(self):
        self.assertEqual(self.commands.plan('open date and time settings',self.identity)['target'],'date and time')
        plan = self.commands.plan('open bluetooth settings and set volume to 40 percent',self.identity)
        self.assertEqual([p['action'] for p in plan],['settings_open','volume'])
        (self.root/'copy and move.txt').write_text('hello')
        destination = self.root/'destination'; destination.mkdir()
        p = self.commands.plan(f'copy "{self.root / "copy and move.txt"}" to "{destination}"',self.identity)
        self.assertEqual(p['action'],'file_copy')

    def test_wifi_no_unknown_profiles_or_shell_interpolation(self):
        row = {'adapter':'test','state':4,'profile':'','profiles':['Home & Work'], 'query_error':0}
        connected = dict(row, state=1, profile='Home & Work')
        with patch('desktop.network.snapshot', side_effect=[[row],[connected]]), patch('desktop.network.subprocess.run', return_value=SimpleNamespace(returncode=0)) as run:
            context = {}
            self.assertIn('Connected',network.wifi('wifi_connect','Home & Work',context))
            self.assertEqual(run.call_args.args[0][-1], 'name=Home & Work')
            self.assertNotIn('shell',run.call_args.kwargs)
            self.assertEqual(context['last_wifi'],'Home & Work')
        with patch('desktop.network.snapshot', return_value=[row]), patch('desktop.network.subprocess.run') as run:
            with self.assertRaises(ValueError): network.wifi('wifi_connect','Unknown')
            run.assert_not_called()

    def test_radio_helper_uses_structured_input_and_reports_failure(self):
        import json
        with patch('desktop.network.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout=b'"Bluetooth is on."')) as run:
            self.assertEqual(network.radio('bluetooth','on'),'Bluetooth is on.')
            self.assertEqual(json.loads(run.call_args.kwargs['input']),{'kind':'bluetooth','state':'on'})
            self.assertNotIn('shell',run.call_args.kwargs)
        with patch('desktop.network.subprocess.run',return_value=SimpleNamespace(returncode=1,stderr=b'Windows denied access')):
            with self.assertRaisesRegex(RuntimeError,'denied'): network.radio('wifi','off')
        with self.assertRaises(ValueError): network.radio('wifi','anything else')

    def test_wifi_denial_and_failed_readback_never_claim_success(self):
        row = {'adapter':'test','state':1,'profile':'','profiles':['Home'], 'query_error':5}
        with patch('desktop.network.snapshot',return_value=[row]), patch('desktop.network.subprocess.run') as run:
            self.assertIn('withheld',network.wifi('wifi_status'))
            with self.assertRaises(RuntimeError): network.wifi('wifi_connect','Home')
            run.assert_not_called()
        row.update(query_error=0,profile='Home')
        with patch('desktop.network.snapshot',return_value=[row]), patch('desktop.network.subprocess.run',return_value=SimpleNamespace(returncode=0)), patch('desktop.network.time.sleep'):
            with self.assertRaisesRegex(RuntimeError,'not confirmed'): network.wifi('wifi_disconnect')

    def test_settings_reads_toggle_and_reports_disabled(self):
        toggle = SimpleNamespace(CurrentToggleState=0)
        toggle.Toggle = lambda: setattr(toggle,'CurrentToggleState',1)
        node = SimpleNamespace(element_info=SimpleNamespace(name='Airplane mode',control_type='Button'),
                               iface_toggle=toggle, is_enabled=lambda:True)
        with patch('desktop.settings_control._controls',return_value=[node]), patch('desktop.settings_control.os.startfile'):
            self.assertIn('off',settings.set_control('airplane mode',None))
            self.assertEqual(toggle.CurrentToggleState,0)
            self.assertIn('on',settings.set_control('airplane mode','on'))
            node.is_enabled = lambda:False
            with self.assertRaisesRegex(RuntimeError,'disabled'): settings.set_control('airplane mode','off')

    def test_confirmation_includes_value_and_destination(self):
        p = settings.validate({'action':'settings_set','target':'airplane mode','value':'on'})
        self.assertTrue(p['confirm'])
        self.assertIn('on',describe(p))
        p = settings.validate({'action':'settings_set','target':'battery saver','page':'battery saver','value':'on'})
        self.assertFalse(p['confirm'])
        with self.assertRaises(ValueError): settings.validate({'action':'settings_open','target':'ms-settings:anything'})

    def test_file_flow_find_copy_rename_move_and_context(self):
        source = self.root/'report.txt'; source.write_text('report data')
        destination = self.root/'copies'; destination.mkdir()
        context = {}
        result = files.execute(files.prepare({'action':'file_find','target':'report','destination':str(self.root)},context),context)
        self.assertIn(str(source),result)
        command = files.prepare({'action':'file_copy','target':'those files','destination':str(destination)},context)
        self.assertFalse(command['confirm'])
        files.execute(command,context)
        copy = destination/source.name
        self.assertEqual(copy.read_text(),'report data')
        command = files.prepare({'action':'file_rename','target':'it','destination':'finished.txt'},context)
        self.assertTrue(command['confirm'])
        self.assertIn('finished.txt',describe(command))
        files.execute(command,context)
        command = files.prepare({'action':'file_move','target':'it','destination':str(self.root)},context)
        files.execute(command,context)
        self.assertEqual((self.root/'finished.txt').read_text(),'report data')
        self.assertTrue(source.exists())

    def test_file_approval_freezes_selection_and_rejects_changed_source(self):
        a,b = self.root/'a.txt', self.root/'b.txt'
        a.write_text('a'); b.write_text('b')
        context = {'last_files':[str(a)]}
        command = files.prepare({'action':'file_rename','target':'it','destination':'renamed.txt'},context)
        context['last_files']=[str(b)]
        files.execute(command,context)
        self.assertTrue(b.exists())
        self.assertFalse(a.exists())
        command = files.prepare({'action':'file_recycle','target':str(b)},context)
        b.write_text('changed content')
        with self.assertRaisesRegex(ValueError,'source changed'): files.execute(command,context)

    def test_no_overwrites_and_ambiguous_references(self):
        a,b = self.root/'a.txt', self.root/'b.txt'
        a.write_text('a'); b.write_text('b')
        with self.assertRaisesRegex(ValueError,'already exists'):
            files.prepare({'action':'file_rename','target':str(a),'destination':'b.txt'}, {})
        with self.assertRaisesRegex(ValueError,'items are remembered'):
            files.sources('it',{'last_files':[str(a),str(b)]})
        with self.assertRaisesRegex(ValueError,'No remembered'):
            files.sources('those files',{})
        with self.assertRaises(ValueError): files.path_for(r'C:\file.txt:secret',{})

    def test_recycle_uses_recycle_bin_and_checks_result(self):
        file = self.root/'discard.txt'; file.write_text('fixture')
        command = files.prepare({'action':'file_recycle','target':str(file)}, {})
        with patch('send2trash.send2trash') as recycle:
            with self.assertRaisesRegex(RuntimeError,'did not confirm'): files.execute(command,{})
            recycle.assert_called_once_with(str(file))
        self.assertTrue(file.exists())

    def test_folder_list_clears_stale_selection_and_mkdir(self):
        context = {'last_files':['stale']}
        files.execute(files.prepare({'action':'file_list','target':str(self.root)},context),context)
        self.assertEqual(context['last_files'],[])
        files.execute(files.prepare({'action':'file_mkdir','target':'Test folder','destination':'here'},context),context)
        self.assertTrue((self.root/'Test folder').is_dir())
        with self.assertRaises(ValueError):
            files.execute(files.prepare({'action':'file_mkdir','target':'../outside','destination':'here'},context),context)

    def test_dependent_file_steps_resolve_after_find_and_freeze_confirmation(self):
        import threading
        source = self.root/'report.txt'; source.write_text('test')
        destination = self.root/'destination'; destination.mkdir()
        runtime = Runtime(self.root/'runtime')
        identity = runtime.new_conversation()
        plans = runtime._commands.plan(f'find report in "{self.root}" and move those files to "{destination}"',identity)
        job = {'conversation':identity,'cancel':threading.Event(),'text':''}
        runtime._execute_steps(job,plans)
        self.assertTrue(source.exists())
        self.assertIn(str(destination/'report.txt'),job['text'])
        pending = runtime._pending.pop(identity)
        runtime._execute_steps(job,pending['steps'],approved_first=True)
        self.assertFalse(source.exists())
        self.assertTrue((destination/'report.txt').exists())

    def test_explorer_selection_keeps_pre_wake_window(self):
        selected = self.root/'selected.txt'; selected.write_text('test')
        self.commands.explorer_handle = 12345
        with patch('desktop.files.explorer_selection',return_value=(str(self.root),[str(selected)])) as read:
            step = self.commands.plan('use selected files',self.identity)
            self.commands.execute(step,self.identity)
            read.assert_called_once_with(12345)
        context = self.store.context(self.identity)
        self.assertEqual(context['last_files'],[str(selected)])
        self.assertNotIn('explorer_handle',context)

    def test_model_gets_inspection_results_before_followup_action(self):
        import time
        runtime = Runtime(self.root/'runtime')
        identity = runtime.new_conversation()
        def call(action, target='', **extras):
            return {'message':{'tool_calls':[{'function':{'name':'windows_action','arguments':{'action':action,'target':target,**extras}}}]},'done':True}
        rounds = [iter([call('settings_inspect')]),iter([call('settings_set','Night light',value='on',page='display')])]
        with patch('desktop.runtime.ChatConnection') as transport, patch.object(runtime._commands,'execute',return_value='Night light [Button]: off') as execute:
            transport.return_value.stream.side_effect = rounds
            jid=runtime.start_chat(identity,'Please make the screen warmer using its settings')
            end=time.monotonic()+3
            while not runtime.poll_chat(jid)['done'] and time.monotonic()<end: time.sleep(.01)
            result=runtime.poll_chat(jid)
            self.assertFalse(result['error'])
            execute.assert_called_once()
            self.assertIn('Night light to on',result['text'])
            messages=transport.call_args.args[1]['messages']
            self.assertTrue(any(m['role']=='tool' and 'Night light' in m['content'] for m in messages))


if __name__ == '__main__': unittest.main()
