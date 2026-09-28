import unittest,tempfile
from unittest.mock import patch,MagicMock
from contextlib import nullcontext
from desktop import devices
from desktop.commands import Commands,parse
from desktop.storage import Store

class DeviceTests(unittest.TestCase):
 def test_spoken_variants_and_percentages(self):
  for phrase in ['set volume of 50%','set the volume to fifty percent','turn volume to 50']:
   self.assertEqual(('volume','50'),(parse(phrase)['action'],parse(phrase)['target']))
  self.assertEqual('100',parse('increase brightness to one hundred percent')['target'])
 def test_monitor_selection(self):
  for phrase,selected in [('set monitor two brightness to forty','2'),('lower external brightness','external'),('set laptop brightness to 40','internal')]:
   self.assertEqual(selected,parse(phrase)['display'])
 def test_queries_never_set_levels(self):
  self.assertEqual('brightness_status',parse('What is my current brightness?')['action'])
  self.assertEqual('audio_status',parse('Tell me the current volume')['action'])
  self.assertIsNone(devices.parse_device("don't change volume to 50"))
 def test_routine_compound_uses_fast_path(self):
  with tempfile.TemporaryDirectory() as root:
   c=Commands(Store(root));steps=c.plan('set brightness to forty and volume to fifty','unused')
   self.assertEqual(['brightness','volume'],[p['action'] for p in steps])
   self.assertFalse(any(p['confirm'] for p in steps))
 def test_out_of_range_is_not_silently_clamped(self):
  with self.assertRaises(ValueError):parse('set brightness to 200')
 def test_display_readback_mismatch_is_reported(self):
  import screen_brightness_control as sbc
  fake=MagicMock();fake.get_brightness.return_value=100
  info={'method':type('VCP',(),{})}
  with patch.object(sbc,'list_monitors_info',return_value=[info]),patch.object(sbc.Display,'from_dict',return_value=fake),patch('desktop.devices.com_thread',return_value=nullcontext()),patch('desktop.devices.time.sleep'):
   with self.assertRaisesRegex(RuntimeError,'still reports 100'):devices.brightness('brightness','40')
 def test_displays_keep_own_method_index_and_query_does_not_write(self):
  import screen_brightness_control as sbc
  infos=[{'method':type('WMI',(),{}),'index':0},{'method':type('VCP',(),{}),'index':0}]
  first=MagicMock();first.get_brightness.return_value=40
  second=MagicMock();second.get_brightness.return_value=80
  with patch.object(sbc,'list_monitors_info',return_value=infos),patch.object(sbc.Display,'from_dict',side_effect=[first,second]) as factory,patch('desktop.devices.com_thread',return_value=nullcontext()):
   result=devices.brightness('brightness_status')
   self.assertIn('Monitor 1 (laptop): 40%',result);self.assertIn('Monitor 2 (external): 80%',result)
   first.set_brightness.assert_not_called();second.set_brightness.assert_not_called()
   self.assertEqual([infos[0],infos[1]],[c.args[0] for c in factory.call_args_list])
 def test_positive_volume_unmutes_and_checks_actual_endpoint(self):
  from pycaw.pycaw import AudioUtilities
  d=MagicMock();d.FriendlyName='Test speakers';v=d.EndpointVolume
  v.GetMasterVolumeLevelScalar.side_effect=[.2,.5,.5];v.GetMute.side_effect=[True,False]
  with patch.object(AudioUtilities,'GetSpeakers',return_value=d):
   self.assertIn('50%',devices._audio('volume','50'))
   v.SetMute.assert_called_once_with(False,None)

if __name__=='__main__':unittest.main()
