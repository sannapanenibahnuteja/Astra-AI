"""Every advertised tool must have a validated test fixture; no OS execution."""
import tempfile
import time
import unittest
from desktop.runtime import TOOLS
from desktop.commands import Commands
from desktop.storage import Store
from desktop import browser, settings_control, web_targets

BASE = {'search','remember','recall','note','volume','mute','unmute','volume_up','volume_down','time','status','lock','project_search','project_read','project_list','open_project','windows_update','brightness','brightness_up','brightness_down','brightness_status','audio_status','click_control','close_window','focus_window','inspect_window','list_monitors','list_windows','maximize_window','minimize_window','move_window','press_key','restore_window','type_text','open'}
FILES = {'explorer_selection','file_copy','file_find','file_list','file_mkdir','file_move','file_open','file_properties','file_recycle','file_rename'}
SETTINGS = {'radio_set','radio_status','settings_inspect','settings_open','settings_set','settings_status','wifi_connect','wifi_disconnect','wifi_profiles','wifi_status'}
EDGE = {'edge_click','edge_close_tab','edge_close_tabs','edge_fill','edge_find','edge_inspect','edge_navigate','edge_search','edge_select_tab','edge_shortcut','edge_tabs'}
MEDIA = {'media_back','media_forward','media_next','media_open','media_pause','media_play','media_previous','media_rate','media_repeat','media_search','media_seek','media_sessions','media_shuffle','media_status','media_stop'}
REMINDERS = {'reminder_add','reminder_cancel','reminder_list'}

class CapabilityContracts(unittest.TestCase):
    def test_every_advertised_action_is_validated(self):
        advertised=set(TOOLS[0]['function']['parameters']['properties']['action']['enum'])
        self.assertEqual(advertised,BASE|FILES|SETTINGS|EDGE|MEDIA|REMINDERS,'A new advertised capability needs a fixture')
        with tempfile.TemporaryDirectory() as root:
            commands=Commands(Store(root))
            for action in sorted(advertised):
                with self.subTest(action=action):
                    command={'action':action,'target':'fixture','window':'Bob Automation Verification'}
                    if action in FILES: command['destination']=root
                    if action in ('volume','brightness','brightness_up','brightness_down','volume_up','volume_down'): command['target']='40'
                    if action=='move_window': command['target']='2'
                    if action=='press_key': command['target']='ctrl+s'
                    if action=='open': command['target']='calculator'
                    if action in ('radio_status','radio_set'): command.update(target='bluetooth',value='on')
                    if action=='settings_open': command['target']='sound'
                    if action=='settings_set': command.update(target='Airplane mode',value='off',page='airplane mode')
                    if action=='edge_shortcut': command['target']='reload'
                    if action=='edge_navigate': command['target']='https://example.com'
                    if action=='edge_fill': command['value']='Hello + Bob'
                    if action in MEDIA: command['value']='1' if action=='media_rate' else 'on' if action=='media_shuffle' else 'all' if action=='media_repeat' else '30'
                    if action=='reminder_add': command.update(value=str(time.time()+3600),destination='local')
                    plan=commands.validate_model_action(command,'fixture')
                    self.assertEqual(plan['action'],action)
                    self.assertIsInstance(plan['confirm'],bool)

    def test_every_browser_shortcut_and_settings_page(self):
        for shortcut in browser.SHORTCUTS:
            with self.subTest(shortcut=shortcut): self.assertEqual(browser.validate({'action':'edge_shortcut','target':shortcut})['target'],shortcut)
        for page in settings_control.PAGES:
            with self.subTest(page=page): self.assertEqual(settings_control.validate({'action':'settings_open','target':page})['target'],page)

    def test_every_known_website_and_voice_alias(self):
        for key,url in web_targets.SERVICES.items():
            with self.subTest(service=key): self.assertEqual(web_targets.resolve(key)[1],url)
        for alias,key in web_targets.ALIASES.items():
            with self.subTest(alias=alias): self.assertEqual(web_targets.resolve(alias)[0],key)
