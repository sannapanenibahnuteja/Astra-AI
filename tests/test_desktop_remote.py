import http.client
import json
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from desktop.storage import Store
from desktop.reminders import Reminders, parse
from desktop.mobile import Mobile
from desktop.speech_output import spoken_text, neural_audio


class ReminderTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.store=Store(self.temp.name); self.r=Reminders(self.store)
    def tearDown(self): self.temp.cleanup()
    def test_parse_and_persistence(self):
        command=parse('remind me in ten minutes to take a break')
        self.assertEqual(command['target'],'take a break')
        context={}; self.r.execute(command,context)
        self.assertEqual(Reminders(self.store).items()[0]['id'],context['last_reminder'])
    def test_bad_time_and_private_phone(self):
        for value in ('nan','inf','-1','yesterday'):
            with self.assertRaises(ValueError): self.r.validate({'action':'reminder_add','target':'test','value':value})
        self.assertEqual(self.r.validate(parse('remind me on my phone in ten minutes to take a break'))['destination'],'phone')
    def test_delivery_once_and_cancel(self):
        context={}; self.r.execute(parse('remind me in two minutes to stretch'),context)
        with self.store.connect() as db: db.execute('UPDATE reminders SET due=?',(time.time()-1,))
        deliver=Mock(); self.r.tick(deliver); self.r.tick(deliver)
        self.assertEqual(deliver.call_count,1)
        self.assertEqual(self.r.items()[0]['status'],'delivered')
        self.r.execute(parse('remind me in two minutes to drink water'),context)
        self.r.execute({'action':'reminder_cancel','target':'it'},context)
        self.assertTrue(any(r['status']=='cancelled' for r in self.r.items()))
    def test_phone_reminder_waits_for_private_page(self):
        with self.store.connect() as db:
            db.execute('INSERT INTO reminders VALUES(?,?,?,?,?,?)',('test','stretch',time.time()-400,'phone','pending',''))
        deliver=Mock();self.r.tick(deliver);self.r.tick(deliver);deliver.assert_not_called()
        self.assertEqual(self.r.items()[0]['status'],'ready on phone')


class MobileTests(unittest.TestCase):
    def setUp(self):
        self.runtime=Mock();self.runtime.new_conversation.return_value='mobile';self.runtime._commands.reminders.items.return_value=[]
        self.runtime._job=None
        self.runtime.start_chat.return_value='job';self.runtime.poll_chat.return_value={'text':'Done','done':True,'error':''}
        self.mobile=Mobile(self.runtime,port=0)
    def tearDown(self): self.mobile.close()
    def request(self, path, data=None, headers=None):
        connection=http.client.HTTPConnection('127.0.0.1',self.mobile.server.server_port,timeout=3)
        connection.request('POST' if data is not None else 'GET',path,json.dumps(data) if data is not None else None,headers or {})
        response=connection.getresponse();result=response.status,response.read();connection.close();return result
    def test_auth_required(self):
        self.assertEqual(self.request('/api/state')[0],401)
        self.assertEqual(self.request('/api/state',headers={'Authorization':'Bearer '+self.mobile.token})[0],200)
    def test_origin_and_host_rejected(self):
        auth={'Authorization':'Bearer '+self.mobile.token,'Content-Type':'application/json'}
        self.assertEqual(self.request('/api/chat',{'message':'open calculator'},{**auth,'Origin':'https://evil.test'})[0],403)
        self.assertEqual(self.request('/api/state',headers={**auth,'Host':'evil.test'})[0],403)
        self.runtime.start_chat.assert_not_called()
    def test_chat_bound_to_mobile_identity(self):
        auth={'Authorization':'Bearer '+self.mobile.token,'Content-Type':'application/json'}
        self.assertEqual(self.request('/api/chat',{'message':'open calculator'},auth)[0],200)
        self.runtime.start_chat.assert_called_once_with('mobile','open calculator',spoken=True)
        self.assertEqual(self.request('/api/chat',{'message':'x'*4001},auth)[0],409)
    def test_private_gateway_only(self):
        self.assertEqual(self.mobile.server.server_address[0],'127.0.0.1')
        with self.assertRaises(ValueError): Mobile(self.runtime,'http://example.com',port=0)
        with self.assertRaises(ValueError): Mobile(self.runtime,'https://pc.ts.net.evil.test',port=0)
    def test_page_cannot_expose_token(self):
        status,body=self.request('/')
        self.assertEqual(status,200);self.assertNotIn(self.mobile.token.encode(),body)


class SpeechTests(unittest.TestCase):
    def test_markdown_is_not_spoken_literally(self):
        self.assertEqual(spoken_text('**Hello** [Bob](https://example.com)'), 'Hello Bob')
        self.assertNotIn('print',spoken_text('```python\nprint(1)\n```'))
    def test_cloud_is_opt_in(self):
        with tempfile.TemporaryDirectory() as root:
            from pathlib import Path
            with patch('desktop.speech_output.urlopen') as network:
                self.assertIsNone(neural_audio('Hello',Path(root)));network.assert_not_called()
