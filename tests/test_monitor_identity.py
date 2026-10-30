import time
import unittest
from contextlib import nullcontext
from unittest.mock import Mock,patch
from desktop import devices


class MonitorIdentityTests(unittest.TestCase):
    def test_explicit_number_is_not_replaced_by_stale_model_context(self):
        command={'action':'brightness','target':'50','display':'2'}
        self.assertEqual(devices.bind_explicit_monitor(command,'Change only my first monitor brightness to 50.')['display'],'1')
        self.assertEqual(devices.bind_explicit_monitor(command,'Set screen one to fifty percent.')['display'],'1')
        for request in ('Leave monitor 1 alone and dim the external screen','Set monitor 1 to 40 and monitor 2 to 60','Explain monitor 1 but do not change it'):
            self.assertIs(devices.bind_explicit_monitor(command,request),command)
        self.assertEqual(command['display'],'2')

    def test_model_cannot_omit_display_and_accidentally_change_all_screens(self):
        import tempfile
        from desktop.commands import Commands
        from desktop.storage import Store
        from desktop.runtime import VOICE_PLAN
        self.assertIn('display',VOICE_PLAN['properties']['actions']['items']['required'])
        with tempfile.TemporaryDirectory() as root:
            commands=Commands(Store(root))
            with self.assertRaisesRegex(ValueError,'omitted'):
                commands.validate_model_action({'action':'brightness','target':'40'},'fixture')
            self.assertEqual(commands.validate_model_action({'action':'brightness','target':'40','display':'external'},'fixture')['display'],'external')

    def setUp(self):
        self.internal={'method':type('WMI',(),{}),'index':0,'uid':'11'}
        self.external={'method':type('VCP',(),{}),'index':0,'uid':'22'}
        self.layout=[{'number':1,'device':'screen1','rect':(0,100,100,200),'primary':True,'uids':['11']},
                     {'number':2,'device':'screen2','rect':(0,0,100,100),'primary':False,'uids':['22']}]
        self.rows=devices.map_display_controls([self.external,self.internal],self.layout)

    def test_reversed_brightness_order_cannot_swap_monitor_numbers(self):
        self.assertIs(devices.select_displays(self.rows,'1')[0]['info'],self.internal)
        self.assertIs(devices.select_displays(self.rows,'2')[0]['info'],self.external)
        self.assertIs(devices.select_displays(self.rows,'top')[0]['info'],self.external)
        self.assertIs(devices.select_displays(self.rows,'primary')[0]['info'],self.internal)

    def test_unknown_individual_monitor_does_not_fall_back_to_another(self):
        rows=devices.map_display_controls([self.internal],self.layout)
        with self.assertRaisesRegex(ValueError,'no verified brightness control'):devices.select_displays(rows,'2')
        with self.assertRaises(ValueError):devices.select_displays(rows,'3')
        self.assertEqual(len(devices.select_displays(rows,'all')),1)

    def test_followup_requires_recent_same_physical_identity(self):
        context={'last_brightness_display':{'uid':'22','device':'screen2','at':time.time()}}
        self.assertIs(devices.select_displays(self.rows,'previous',context)[0]['info'],self.external)
        self.assertIs(devices.select_displays(self.rows,'other',context)[0]['info'],self.internal)
        context['last_brightness_display']['uid']='disconnected'
        with self.assertRaises(ValueError):devices.select_displays(self.rows,'previous',context)
        context['last_brightness_display'].update(uid='22',at=time.time()-301)
        with self.assertRaises(ValueError):devices.select_displays(self.rows,'other',context)

    def test_ambiguous_spatial_choice_and_duplicate_identity_do_not_guess(self):
        with self.assertRaises(ValueError):devices.select_displays(self.rows,'left')
        duplicated=devices.map_display_controls([self.internal,dict(self.internal)],self.layout)
        with self.assertRaises(ValueError):devices.select_displays(duplicated,'1')

    def test_single_display_write_leaves_other_device_untouched_and_verifies(self):
        import screen_brightness_control as sbc
        device=Mock();device.get_brightness.side_effect=[50,40]
        context={}
        with patch.object(sbc,'list_monitors_info',return_value=[self.external,self.internal]),patch('desktop.devices.display_layout',return_value=self.layout),patch.object(sbc.Display,'from_dict',return_value=device) as factory,patch('desktop.devices.com_thread',return_value=nullcontext()),patch('desktop.devices.time.sleep'):
            result=devices.brightness('brightness','40','2',context)
        factory.assert_called_once_with(self.external)
        device.set_brightness.assert_called_once_with(40)
        self.assertIn('Monitor 2 (external): 40%',result)
        self.assertEqual(context['last_brightness_display']['uid'],'22')

    def test_failed_write_does_not_update_followup_context(self):
        import screen_brightness_control as sbc
        device=Mock();device.get_brightness.return_value=50
        context={}
        with patch.object(sbc,'list_monitors_info',return_value=[self.internal,self.external]),patch('desktop.devices.display_layout',return_value=self.layout),patch.object(sbc.Display,'from_dict',return_value=device),patch('desktop.devices.com_thread',return_value=nullcontext()),patch('desktop.devices.time.sleep'):
            with self.assertRaises(RuntimeError):devices.brightness('brightness','40','2',context)
        self.assertNotIn('last_brightness_display',context)

    def test_one_point_change_cannot_report_success_without_movement(self):
        import screen_brightness_control as sbc
        device=Mock();device.get_brightness.return_value=50
        with patch.object(sbc,'list_monitors_info',return_value=[self.internal,self.external]),patch('desktop.devices.display_layout',return_value=self.layout),patch.object(sbc.Display,'from_dict',return_value=device),patch('desktop.devices.com_thread',return_value=nullcontext()),patch('desktop.devices.time.sleep'):
            with self.assertRaisesRegex(RuntimeError,'still reports 50'):devices.brightness('brightness','51','2')

    def test_natural_selectors_validate_and_uppercase_number_words_work(self):
        for text,selected in [('dim the upper monitor a little','top'),('make that one dimmer','previous'),('raise brightness on the other screen','other')]:
            self.assertEqual(devices.parse_device(text)['display'],selected)
        self.assertEqual(devices.number_words('FORTY TWO'),'42')
        self.assertEqual(devices.validate({'action':'brightness','target':'40','display':'laptop'})['display'],'internal')
        self.assertEqual(devices.parse_device('lower the monitor brightness')['display'],'all')
