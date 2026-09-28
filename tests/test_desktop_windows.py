import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from desktop.commands import Commands,parse
from desktop.storage import Store
from desktop import windows
from desktop.voice import model_path

class WindowsCommandTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.store=Store(self.temp.name);self.commands=Commands(self.store);self.identity=self.store.new_conversation()
 def tearDown(self):self.temp.cleanup()
 def test_update_is_not_cpu_status(self):
  for phrase in ['check for system updates','check for windows updates','open windows update']:
   self.assertEqual('windows_update',parse(phrase)['action'])
  with patch('desktop.commands.os.startfile') as launch:
   result=self.commands.execute(parse('check for system updates'),self.identity)
   launch.assert_called_once_with('ms-settings:windowsupdate');self.assertIn("haven't scanned",result)
 def test_compound_request_reaches_planner(self):
  self.assertEqual(['open','type_text'], [p['action'] for p in self.commands.plan('open notepad and type hello',self.identity)])
  self.assertEqual(['search','brightness_down'], [p['action'] for p in self.commands.plan('search for music and lower brightness',self.identity)])
 def test_window_follow_up_reuses_previous_target(self):
  self.store.context(self.identity,{'last_app':'notepad'})
  with patch('desktop.windows.execute',return_value='Maximized Notepad.') as execute:
   self.commands.execute(self.commands.plan('maximize it',self.identity),self.identity)
   execute.assert_called_once_with('maximize_window','it','notepad')
 def test_brightness_boundaries_and_shortcuts(self):
  self.assertEqual('brightness',self.commands.plan('set brightness to 40 percent',self.identity)['action'])
  for invalid in ['-1','101','forty']:
   with self.assertRaises(ValueError):windows.validate('brightness',invalid)
  with self.assertRaises(ValueError):windows.validate('press_key','win+r')
  self.assertFalse(windows.validate('type_text','hello','notepad')['confirm'])
  self.assertEqual('ctrl+s', windows.validate('press_key','control S')['target'])
  self.assertEqual('', windows.validate('brightness','40','Notepad')['window'])
  self.assertEqual('Notepad', self.commands.plan('type Good morning Bob into Notepad', self.identity)['window'])
  self.assertIsNone(self.commands.plan('type that', self.identity))
 def test_model_window_target_survives_validation(self):
  result=self.commands.validate_model_action({'action':'type_text','target':'Hello','window':'Notepad'},self.identity)
  self.assertEqual('Notepad',result['window'])
 def test_embedded_model_works_without_sidecar(self):
  with tempfile.TemporaryDirectory() as bundle,tempfile.TemporaryDirectory() as install:
   model=Path(bundle)/'models/whisper-small.en';model.mkdir(parents=True)
   for name in ('config.json','model.bin','tokenizer.json','vocabulary.txt'):(model/name).touch()
   with patch('sys.frozen',True,create=True),patch('sys._MEIPASS',bundle,create=True),patch('sys.executable',str(Path(install)/'Bob.exe')):
    self.assertEqual(model,model_path())
 def test_incomplete_model_fails_before_loading(self):
  with tempfile.TemporaryDirectory() as folder:
   with patch('sys.frozen',True,create=True),patch('sys._MEIPASS',folder,create=True),patch('sys.executable',str(Path(folder)/'Bob.exe')):
    with self.assertRaisesRegex(RuntimeError,'incomplete'):model_path()

if __name__=='__main__':unittest.main()
