import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from desktop.commands import Commands
from desktop.storage import Store
from desktop import calling, windows, pairing
from desktop.reminders import Reminders, parse
from desktop.voice import transcript_result
from desktop.personality import PRESETS, instruction


class UpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.store=Store(self.temp.name);self.commands=Commands(self.store)
    def tearDown(self): self.temp.cleanup()
    def test_literal_notepad_overrides_edge_context(self):
        self.commands.browser_handle=123
        self.store.context('test',{'last_window':'Microsoft Edge'})
        for request,expected in [('Type "Hello, world!" into Notepad','Hello, world!'),
                                 ('write Open Edge and set volume to 20%. into Notepad','Open Edge and set volume to 20%.'),
                                 ('in Notepad, A+B = {Bob}.','A+B = {Bob}.')]:
            result=self.commands.plan(request,'test')
            self.assertEqual((result['action'],result['window'],result['target']),('type_text','Notepad',expected))
    def test_move_and_compound_context(self):
        plan=self.commands.plan('move Notepad to monitor two','test')
        self.assertEqual((plan['action'],plan['target'],plan['window']),('move_window','2','Notepad'))
        plan=self.commands.plan('open Notepad and type Hello into Notepad','test')
        self.assertEqual([x['action'] for x in plan],['open','type_text'])
    def test_monitor_geometry_with_negative_coordinates(self):
        x,y,w,h=windows.destination_rect((0,0,2000,1200),(-1920,0,0,1040))
        self.assertEqual((x,y,w,h),(-1920,0,1920,1040))
        with self.assertRaises(ValueError): windows.validate('move_window','0','Notepad')
    def test_one_uncertain_word_is_not_hidden_by_average(self):
        seg=SimpleNamespace(text='delete file',avg_logprob=-.1,no_speech_prob=.1,words=[SimpleNamespace(probability=.99) for _ in range(10)]+[SimpleNamespace(probability=.1)])
        self.assertTrue(transcript_result([seg])['needs_review'])
    def test_personality_presets_are_distinct(self):
        self.assertEqual(len(PRESETS),6)
        self.assertEqual(len({instruction(k) for k in PRESETS}),6)
    def test_carrier_configuration_and_confirmation(self):
        command=parse('call me in ten minutes to take a break')
        self.assertEqual(command['destination'],'call')
        with self.assertRaises(ValueError): self.commands.reminders.validate(command)
        cfg={'enabled':True,'account_sid':'AC'+'a'*32,'auth_token':'fixture','from_number':'+12025550101','to_number':'+12025550102'}
        (self.store.root/'phone-calls.json').write_text(json.dumps(cfg))
        self.assertTrue(self.commands.reminders.validate(command)['confirm'])
        response=Mock();response.__enter__=Mock(return_value=response);response.__exit__=Mock(return_value=False);response.read.return_value=json.dumps({'sid':'CA'+'b'*32}).encode()
        with patch('desktop.calling.urlopen',return_value=response) as request:
            calling.submit(self.store.root,'<unsafe> & reminder')
            from urllib.parse import parse_qs
            data=parse_qs(request.call_args.args[0].data.decode())
            self.assertEqual(data['To'],[cfg['to_number']])
            self.assertIn('&lt;unsafe&gt; &amp;',data['Twiml'][0])

    def test_twilio_errors_keep_actionable_detail_without_numbers(self):
        error=HTTPError('https://api.twilio.com',400,'Bad Request',{},None)
        error.read=Mock(return_value=json.dumps({'code':21211,'message':'The To number +12025550102 is not valid.'}).encode())
        message=calling.provider_error(error)
        self.assertIn('Twilio error 21211',message)
        self.assertNotIn('+12025550102',message)
        self.assertIn('+...redacted',message)
    def test_calls_are_single_attempt_and_not_blocked_by_local_voice(self):
        with self.store.connect() as db: db.execute('INSERT INTO reminders VALUES(?,?,?,?,?,?)',('r1','test',time.time()-1,'call','pending',''))
        with patch('desktop.calling.submit',side_effect=RuntimeError('uncertain')) as call:
            self.commands.reminders.tick(Mock(),local_ready=False)
            self.commands.reminders.tick(Mock(),local_ready=False)
            call.assert_called_once()
        self.assertEqual(self.commands.reminders.items()[0]['status'],'failed')
    def test_pairing_is_encrypted_and_revocable(self):
        value={'url':'https://pc.test.ts.net','token':'fixture-private-token','identity':'x'}
        pairing.save(self.store.root,value)
        self.assertNotIn(b'fixture-private-token',(self.store.root/'mobile-pairing.dat').read_bytes())
        self.assertEqual(pairing.load(self.store.root),value)
        pairing.clear(self.store.root);self.assertIsNone(pairing.load(self.store.root))

    def test_ambiguous_close_followup_keeps_exact_windows(self):
        matches=[{'handle':1,'title':'YouTube A','process':'msedge.exe'}, {'handle':2,'title':'YouTube B','process':'msedge.exe'}]
        with patch('desktop.windows.execute',side_effect=windows.AmbiguousWindows(matches)):
            with self.assertRaises(windows.AmbiguousWindows):
                self.commands.execute({'action':'close_window','target':'youtube'},'test')
        plans=self.commands.plan('close all those','test')
        self.assertEqual([p['_window_ref'] for p in plans],matches)
        self.assertEqual([p['confirm'] for p in plans],[True,False])
        self.assertEqual(self.commands.plan('close the second one','test')[0]['target'],'YouTube B')
        self.assertEqual(self.commands.plan('close all those','different')['action'],'clarify')
        with patch('desktop.windows.window_inventory',return_value=[]),patch('desktop.windows.execute') as execute:
            with self.assertRaises(ValueError): self.commands.execute(plans[0],'test')
            execute.assert_not_called()
        self.commands.window_choices['test']=(time.monotonic()-181,matches)
        self.assertEqual(self.commands.plan('close all those','test')['action'],'clarify')


if __name__=='__main__': unittest.main()
