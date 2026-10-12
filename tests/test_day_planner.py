import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
from desktop.storage import Store
from desktop.day_planner import DayPlanner, day_date, local_estimates, maps_link


class DayPlannerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.days=DayPlanner(Store(self.root)); self.day=day_date('tomorrow')
        self.now=datetime.fromisoformat(self.day+'T00:00:00+05:30')

    def tearDown(self): self.temp.cleanup()

    def plan(self, **extra):
        return self.days.save({'day':self.day,'origin':'Start address, City','start':'08:00','buffer':15,
          'stops':[{'title':'Meeting','address':'Office address, City','at':'09:00','minutes':60,'travel':30}],**extra})

    def test_manual_backward_schedule_with_buffer(self):
        self.plan(); result=self.days.calculate(self.day,False)
        leg=result['legs'][0]
        self.assertIn('08:15',leg['leave']); self.assertIn('08:45',leg['arrive'])
        self.assertIn('09:00',leg['begin']); self.assertEqual(result['conflicts'],0)

    def test_late_conflict_does_not_reschedule_appointment(self):
        self.plan(start='08:50'); result=self.days.calculate(self.day,False)
        self.assertEqual(result['legs'][0]['late_minutes'],35)
        self.assertEqual(self.days.get(self.day)['stops'][0]['at'],'09:00')

    def test_flexible_stops_and_multiple_legs(self):
        self.plan(stops=[{'title':'Errand','address':'Shop','at':'','minutes':20,'travel':10},
                         {'title':'Meeting','address':'Office','at':'10:00','minutes':30,'travel':15}])
        result=self.days.calculate(self.day,False)
        self.assertEqual(result['legs'][1]['origin'],'Shop')
        self.assertEqual(result['total_travel'],25)

    def test_local_batch_runs_once_and_labels_guesses(self):
        self.plan()
        with patch('desktop.day_planner.local_estimates',return_value=[20]) as provider:
            result=self.days.calculate(self.day,True,now=self.now)
            self.assertEqual(provider.call_count,1)
            self.assertIn('08:25',result['legs'][0]['leave'])
        self.assertEqual(result['mode'],'local')
        self.assertIn('not measured',result['note'])
        self.assertIsNone(DayPlanner(self.days.store).live)

    def test_failure_clears_previous_estimate(self):
        self.plan(); self.days.calculate(self.day,False)
        with patch('desktop.day_planner.local_estimates',side_effect=ValueError('Unavailable')):
            with self.assertRaisesRegex(ValueError,'Unavailable'): self.days.calculate(self.day,True)
        self.assertIsNone(self.days.live)

    def test_status_has_no_credentials_or_billing(self):
        status=self.days.status()
        self.assertFalse(status['billing']); self.assertFalse(status['live_traffic'])
        self.assertNotIn('api_key',status); self.assertFalse((self.root/'routes.json').exists())

    def model_response(self, content):
        response=Mock(status_code=200,content=b'fixture')
        response.json.return_value={'message':{'content':content}}
        client=Mock(); client.__enter__=Mock(return_value=client); client.__exit__=Mock(return_value=False)
        client.post.return_value=response
        return client

    def test_loopback_request_is_one_batch_with_no_proxy(self):
        plan=self.plan(); client=self.model_response('{"minutes":[30]}')
        with patch('desktop.day_planner.httpx.Client',return_value=client) as factory:
            self.assertEqual(local_estimates(self.days.store.settings(),plan),[30])
        self.assertFalse(factory.call_args.kwargs['trust_env'])
        url=client.post.call_args.args[0]
        self.assertEqual(url,'http://127.0.0.1:11434/api/chat')
        payload=client.post.call_args.kwargs['json']
        self.assertFalse(payload['think']); self.assertEqual(payload['options']['num_predict'],256)
        self.assertIn('no maps',payload['messages'][0]['content'])

    def test_remote_endpoints_rejected_before_sending_addresses(self):
        plan=self.plan()
        for url in ['https://example.com','http://127.0.0.1.evil.test:11434','http://user@localhost:11434','http://localhost:11434/path','http://localhost:11434?proxy=x']:
            with patch('desktop.day_planner.httpx.Client') as network:
                with self.assertRaises(ValueError): local_estimates({'ollama_url':url,'model':'fixture'},plan)
                network.assert_not_called()

    def test_invalid_missing_unknown_estimates_are_refused(self):
        plan=self.plan()
        for value in ['{}','{"minutes":[]}','{"minutes":[null]}','{"minutes":[true]}','{"minutes":[-1]}','{"minutes":[721]}','{"minutes":[12.5]}','{"minutes":["30"]}','{"minutes":[30,40]}','not json']:
            with patch('desktop.day_planner.httpx.Client',return_value=self.model_response(value)):
                with self.assertRaises(ValueError): local_estimates(self.days.store.settings(),plan)

    def test_unavailable_model_does_not_use_manual_fallback(self):
        import httpx
        plan=self.plan(); client=self.model_response('{"minutes":[30]}')
        client.post.side_effect=httpx.ConnectError('private details')
        with patch('desktop.day_planner.httpx.Client',return_value=client):
            with self.assertRaises(ValueError) as captured: local_estimates(self.days.store.settings(),plan)
        self.assertNotIn('private details',str(captured.exception))

    def test_validation_rejects_bad_times_offsets_and_stop_limit(self):
        for extra in [{'start':'8 am'},{'offset':'+14:30'},{'buffer':-1},{'origin':''},{'stops':[{'title':'x'}]*9}]:
            with self.assertRaises(ValueError): self.plan(**extra)
        with self.assertRaises(ValueError): self.days.validate({'action':'day_add','destination':'Office','target':'Meeting','value':'evening'})

    def test_natural_follow_up_uses_last_day(self):
        for phrase in ['Plan my day','When should I leave?','Check traffic for my day']:
            command=self.days.request(phrase,{'last_day':self.day})
            self.assertEqual(command['day'],self.day); self.assertEqual(command['action'],'day_refresh')
        self.assertEqual(self.days.request('show my day tomorrow',{})['action'],'day_show')
        self.assertIsNone(self.days.request('What are the benefits of day planning?',{}))

    def test_voice_add_and_show_are_durable(self):
        start=self.days.validate({'action':'day_start','day':self.day,'origin':'Start','start':'08:00'})
        self.days.execute(start)
        add=self.days.validate({'action':'day_add','day':self.day,'target':'Dentist','destination':'Clinic','value':'10:00','minutes':30})
        self.assertIn('Added Dentist',self.days.execute(add))
        self.assertIn('Dentist',self.days.execute(self.days.validate({'action':'day_show','day':self.day})))
        self.days.delete(self.day); self.assertEqual(self.days.rows(),[])

    def test_route_link_encodes_user_text(self):
        link=maps_link('A & B','City / Shop')
        self.assertIn('origin=A+%26+B',link); self.assertIn('travelmode=driving',link)

    def test_plan_crossing_midnight_is_flagged(self):
        self.plan(start='23:45',stops=[{'title':'Late','address':'Office','minutes':60,'travel':30}])
        self.assertTrue(self.days.calculate(self.day,False)['crosses_day'])

    def test_manual_mode_never_calls_model(self):
        self.plan()
        with patch('desktop.day_planner.local_estimates') as model:
            result=self.days.calculate(self.day,False)
            model.assert_not_called()
        self.assertEqual(result['mode'],'manual')
        self.assertIn('manual',self.days.brief())

    def test_follow_up_reuses_day_selected_in_builder(self):
        self.plan()
        self.assertEqual(self.days.request('When should I leave?',{})['day'],self.day)

    def test_voice_actions_do_not_invent_missing_times_or_duration(self):
        with self.assertRaises(ValueError): self.days.validate({'action':'day_start','origin':'Start'})
        with self.assertRaises(ValueError): self.days.validate({'action':'day_add','target':'Meeting','destination':'Office','value':'09:00'})

    def test_natural_route_command_uses_stop_number(self):
        command=self.days.request('Open the driving route to stop two for tomorrow',{})
        self.assertEqual(command['action'],'day_route'); self.assertEqual(command['target'],'2')
        with self.assertRaises(ValueError): self.days.request('open route to stop 99',{})


if __name__ == '__main__': unittest.main()
