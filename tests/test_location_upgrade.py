import tempfile
import time
import unittest
from unittest.mock import patch
from desktop import location
from desktop.storage import Store
from desktop.day_planner import DayPlanner
from desktop.runtime import Runtime


class LocationUpgrade(unittest.TestCase):
    def test_disabled_never_accesses_windows(self):
        with patch('desktop.location.subprocess.run') as native:
            with self.assertRaisesRegex(ValueError, 'Enable Current location'):
                location.current({'location_enabled':False})
            native.assert_not_called()

    def test_invalid_and_stale_fixes_are_rejected(self):
        fix=dict(latitude=12,longitude=77,accuracy=100,timestamp=1000)
        self.assertEqual(location.validate(fix,1000)['latitude'],12)
        for values in ({'latitude':91},{'longitude':float('nan')},{'accuracy':60000},{'timestamp':800},{'latitude':True}):
            with self.assertRaises(ValueError): location.validate({**fix,**values},1000)

    def test_each_calculation_refreshes_without_persisting_coordinates(self):
        with tempfile.TemporaryDirectory() as root:
            store=Store(root); store.save_settings({'location_enabled':True})
            planner=DayPlanner(store)
            plan=planner.save({'day':'tomorrow','origin':'my current location','start':'08:00','buffer':10,
                'stops':[{'title':'Museum','address':'Museum, Bengaluru','at':'10:00','minutes':30,'travel':20}]})
            fixes=[dict(latitude=12,longitude=77,accuracy=100,timestamp=time.time()),dict(latitude=13,longitude=78,accuracy=100,timestamp=time.time())]
            with patch('desktop.day_planner.location.current',side_effect=fixes) as native:
                first=planner.calculate(plan['day'],False); second=planner.calculate(plan['day'],False)
            self.assertEqual(native.call_count,2)
            self.assertNotEqual(first['legs'][0]['origin'],second['legs'][0]['origin'])
            self.assertEqual(planner.get(plan['day'])['origin'],location.CURRENT)


class VoiceApprovalUpgrade(unittest.TestCase):
    def test_routine_spoken_action_executes_once_without_prompt(self):
        with tempfile.TemporaryDirectory() as root:
            runtime=Runtime(root); identity=runtime.new_conversation()
            job={'conversation':identity,'spoken':True,'text':'','cancel':__import__('threading').Event()}
            with patch.object(runtime._commands,'execute',return_value='Opened Notepad.') as execute:
                runtime._execute_steps(job,[{'action':'open','target':'notepad','confirm':True}])
            execute.assert_called_once()
            self.assertNotIn(identity,runtime._pending)

    def test_sensitive_action_still_requires_one_approval(self):
        with tempfile.TemporaryDirectory() as root:
            runtime=Runtime(root); identity=runtime.new_conversation()
            job={'conversation':identity,'spoken':True,'text':'','cancel':__import__('threading').Event()}
            with patch.object(runtime._commands,'execute',return_value='Locked.') as execute:
                runtime._execute_steps(job,[{'action':'lock','target':'','confirm':True}])
                execute.assert_not_called()
                runtime._execute_steps(job,runtime._pending.pop(identity)['steps'],approved_first=True)
                execute.assert_called_once()
