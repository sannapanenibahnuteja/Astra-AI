import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import Mock,patch
from desktop import appearance
from desktop.app_catalog import executable,scan_programs
from desktop.commands import Commands
from desktop.storage import Store
from desktop.runtime import Runtime

class AppearanceTests(unittest.TestCase):
 def test_each_individual_preference_round_trips(self):
  for key,choices in appearance.CHOICES.items():
   for value in choices:
    self.assertEqual(appearance.merge({}, {key:value})[key],value)
  for key in ('details','suggestions','status','orb_visible'):
   for value in (True,False):self.assertEqual(appearance.merge({}, {key:value})[key],value)
 def test_natural_explicit_changes_and_typos(self):
  cases={'make the accent blue':{'accent':'blue'},'set the orb size to large':{'orb_size':'large'},
   'hide the sidebar':{'sidebar':'hidden'},'show details':{'details':True},'make the text bigger':{'font_size':'large'},
   'make the orb purple':{'orb_color':'accent','accent':'violet'},'set the accent violett':{'accent':'violet'},
   'turn off animations':{'motion':'off'},'change the sidebar color to graphite':{'sidebar_color':'graphite'}}
  for text,expected in cases.items():self.assertEqual(appearance.request(text),expected,text)
 def test_compound_changes_atomic_and_preserve_unrelated_parts(self):
  change=appearance.request('make the accent mint and hide details')
  self.assertEqual(change,{'accent':'mint','details':False})
  self.assertIsNone(appearance.request('make the accent mint and delete a file'))
  current=appearance.merge({}, {'orb_size':'large'})
  self.assertEqual(appearance.merge(current,change)['orb_size'],'large')
 def test_does_not_mutate_dictation_discussion_or_negation(self):
  for text in ('type make the accent blue','do not hide details','why is the orb small','remember that I like mint', 'set volume to 20'):
   self.assertIsNone(appearance.request(text),text)
 def test_schema_rejects_arbitrary_code_and_invalid_values(self):
  for value in ({'css':'body{display:none}'},{'motion':'faster()'},{'details':1},{'orb_size':None},[],{'accent':'url(https://x)'}):
   with self.assertRaises(ValueError):appearance.validate(value)
 def test_persistence_partial_merge_and_reset(self):
  with tempfile.TemporaryDirectory() as folder:
   runtime=Runtime(folder);self.addCleanup(runtime._voice.close)
   runtime.appearance_update({'accent':'mint','orb_size':'large'})
   runtime.appearance_update({'sidebar':'compact'})
   saved=Store(folder).settings()['appearance'];self.assertEqual(saved['accent'],'mint');self.assertEqual(saved['orb_size'],'large')
   runtime.appearance_update(appearance.request('reset appearance'))
   self.assertEqual(Store(folder).settings()['appearance'],appearance.DEFAULTS)
 def test_explicit_change_works_without_model_and_voice_is_not_disabled(self):
  with tempfile.TemporaryDirectory() as folder:
   runtime=Runtime(folder);self.addCleanup(runtime._voice.close);identity=runtime.new_conversation()
   job={'conversation':identity,'cancel':threading.Event(),'text':'','error':'','done':False,'spoken':False,'speaker':{}}
   with patch('desktop.runtime.ChatConnection',side_effect=AssertionError('unnecessary model call')):
    runtime._generate(job,'make the accent mint')
   self.assertIn('Updated',job['text']);self.assertEqual(runtime._store.settings()['appearance']['accent'],'mint')
 def test_spoken_installed_app_fast_lane_skips_llm(self):
  with tempfile.TemporaryDirectory() as folder:
   runtime=Runtime(folder);self.addCleanup(runtime._voice.close);identity=runtime.new_conversation()
   runtime._commands.apps={'calculator':('exe','calc.exe')}
   job={'conversation':identity,'cancel':threading.Event(),'text':'','error':'','done':False,'spoken':True,'speaker':{},'steps':0}
   with patch('desktop.runtime.ChatConnection',side_effect=AssertionError('unnecessary model call')),patch.object(runtime._commands,'execute',return_value='Opened calculator; its window is visible.') as execute:
    runtime._generate(job,'open calculatr')
   execute.assert_called_once();self.assertEqual(job['error'],'');self.assertIn('Opened calculator',job['text'])
 def test_constrained_model_path_and_followup_context(self):
  with tempfile.TemporaryDirectory() as folder:
   runtime=Runtime(folder);self.addCleanup(runtime._voice.close);identity=runtime.new_conversation()
   runtime._store.append(identity,'user','Give the interface a mint accent')
   runtime._store.append(identity,'assistant','Updated your accent.')
   history=runtime._store.messages(identity)
   self.assertTrue(appearance.semantic_candidate('Actually, make it blue',history))
   self.assertTrue(appearance.semantic_candidate('No, I meant blue',history))
   self.assertFalse(appearance.semantic_candidate('give the interface a mint accent and open calculator',history))
   model=Mock();model.stream.return_value=iter([{'message':{'content':'{"patch":{"accent":"blue"},"question":""}'},'done':True}])
   job={'cancel':threading.Event(),'transport':None,'text':''}
   with patch('desktop.runtime.ChatConnection',return_value=model) as connection:
    runtime._customize_with_model(job,'Actually, make it blue',history)
   payload=connection.call_args.args[1]
   self.assertFalse(payload['think']);self.assertEqual(payload['options']['num_ctx'],2048)
   self.assertNotIn('tools',payload);self.assertIn('mint',str(payload['messages']))
   self.assertEqual(runtime._store.settings()['appearance']['accent'],'blue')
 def test_invalid_model_patch_is_rejected_before_saving(self):
  with tempfile.TemporaryDirectory() as folder:
   runtime=Runtime(folder);self.addCleanup(runtime._voice.close)
   model=Mock();model.stream.return_value=iter([{'message':{'content':'{"patch":{"shell":"cmd"},"question":""}'},'done':True}])
   with patch('desktop.runtime.ChatConnection',return_value=model),self.assertRaises(ValueError):
    runtime._customize_with_model({'cancel':threading.Event()},'change the UI',[])
   self.assertEqual(runtime._store.settings()['appearance'],appearance.DEFAULTS)
 def test_model_can_map_unusual_wording_to_validated_appearance(self):
  with tempfile.TemporaryDirectory() as folder:
   commands=Commands(Store(folder));identity=commands.store.new_conversation()
   plan=commands.validate_model_action({'action':'appearance','target':json.dumps({'orb_color':'accent','accent':'rose'})},identity)
   self.assertFalse(plan['confirm']);commands.execute(plan,identity)
   self.assertEqual(commands.store.settings()['appearance']['accent'],'rose')
   with self.assertRaises(ValueError):commands.validate_model_action({'action':'appearance','target':'{"shell":"cmd"}'},identity)

class AppCatalogTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.store=Store(self.temp.name);self.commands=Commands(self.store);self.identity=self.store.new_conversation()
  self.commands.apps={'notepad':('exe','notepad.exe'),'calculator':('exe','calc.exe'),'visual studio code':('exe','code.exe')}
  self.commands._last_app_scan=float('inf')
 def test_unique_clear_typo_auto_corrects_without_confirmation(self):
  plan=self.commands.fast_open('please open calculatr',self.identity)
  self.assertEqual(plan['target'],'calculator');self.assertFalse(plan['confirm'])
 def test_similar_names_require_disambiguation(self):
  self.commands.apps={'editor alpha':('exe','a.exe'),'editor alpine':('exe','b.exe')}
  self.assertIsNone(self.commands.fast_open('open editor al',self.identity))
 def test_known_website_uses_direct_route_without_app_scan(self):
  with patch('desktop.app_catalog.scan_programs',side_effect=AssertionError('unnecessary disk scan')):
   plan=self.commands.fast_open('open YouTube',self.identity)
  self.assertEqual(plan['action'],'url');self.assertIn('youtube.com',plan['target'])
 def test_bare_exe_and_spacing_aliases(self):
  self.assertEqual(self.commands.match_app('notepad.exe'),('notepad',True))
  self.assertEqual(self.commands.match_app('visualstudiocode'),('visual studio code',True))
 def test_direct_existing_exe_without_shell_or_arguments(self):
  path=Path(self.temp.name)/'Portable App.exe';path.write_bytes(b'fixture')
  self.assertEqual(executable(str(path)),path)
  self.assertIsNone(executable(str(path)+' --delete'))
  name,certain=self.commands.match_app(str(path));self.assertTrue(certain)
  self.assertEqual(self.commands.apps[name],('exe',str(path)))
 def test_scan_finds_programs_but_skips_helpers_and_uninstallers(self):
  folder=Path(self.temp.name)/'Product';folder.mkdir()
  for name in ('Music.exe','uninstall.exe','update.exe','readme.txt'):(folder/name).touch()
  result=scan_programs([self.temp.name]);self.assertIn('music',result);self.assertNotIn('uninstall',result);self.assertNotIn('update',result)
 def test_fast_lane_never_discards_compound_or_negation(self):
  for text in ('do not open calculator','open calculator and notepad','open notepad then type hello','tell me how to open calculator','open calculator instead of notepad'):
   self.assertIsNone(self.commands.fast_open(text,self.identity),text)
 def test_launch_result_requires_actual_window_observation(self):
  with patch('desktop.commands.subprocess.Popen') as launch,patch('desktop.launch.wait_for_app',return_value=None):
   result=self.commands.execute({'action':'open','target':'calculator'},self.identity)
  launch.assert_called_once_with(['calc.exe']);self.assertIn('could not verify',result)

if __name__=='__main__':unittest.main()
