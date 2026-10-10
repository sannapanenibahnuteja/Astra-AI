import tempfile
import unittest
from unittest.mock import Mock, patch
from desktop.commands import Commands
from desktop.storage import Store
from desktop import web_launch


class WebsiteTargetTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.store=Store(self.temp.name); self.commands=Commands(self.store)
        self.identity=self.store.new_conversation()

    def test_spoken_names_and_web_app_suffixes(self):
        for text in ('open you tube','open the YouTube app','please open YouTube website','open website for YouTube','open YouTube in the browser'):
            self.assertEqual(self.commands.plan(text,self.identity),{'action':'url','target':'https://www.youtube.com'},text)

    def test_missing_services_use_real_web_versions(self):
        for name,url in [('spotify','https://open.spotify.com'),('whatsapp','https://web.whatsapp.com'),('gmail','https://mail.google.com'),('discord','https://discord.com/app')]:
            self.commands.apps.pop(name,None)
            self.assertEqual(self.commands.plan('open '+name,self.identity),{'action':'url','target':url})

    def test_installed_app_preferred_and_explicit_website_overrides(self):
        self.commands.apps['spotify']=('exe','Spotify.exe')
        self.assertEqual(self.commands.plan('open spotify',self.identity)['action'],'open')
        self.assertEqual(self.commands.plan('open spotify website',self.identity)['action'],'url')

    def test_domain_without_scheme_and_model_requests(self):
        self.assertEqual(self.commands.plan('open youtube.com',self.identity),{'action':'url','target':'https://youtube.com'})
        self.commands.apps.pop('netflix',None)
        self.assertEqual(self.commands.validate_model_action({'action':'open','target':'Netflix'},self.identity)['target'],'https://www.netflix.com')

    def test_unknown_names_and_local_paths_never_become_guessed_domains(self):
        for target in ('Invented Brand ZZ','C:\\private\\report.xyz'):
            plan=self.commands.plan('open '+target,self.identity)
            self.assertNotIn(plan['action'],('url','search'))
        self.assertIsNone(self.commands.plan('do not open spotify',self.identity))

    def test_verified_web_launch_preserves_open_again_context(self):
        with patch('desktop.web_launch.open_website',return_value=('Opened youtube.com; its address is visible.',42)) as launch:
            self.commands.execute(self.commands.plan('open YouTube app',self.identity),self.identity)
        launch.assert_called_once_with('https://www.youtube.com')
        self.assertEqual(self.commands.plan('open it again',self.identity),{'action':'url','target':'https://www.youtube.com'})

    def test_edge_launch_error_falls_back_to_windows_default(self):
        with patch.object(web_launch,'edge_path',return_value='missing-edge.exe'),patch.object(web_launch.windows,'window_inventory',return_value=[]),patch.object(web_launch.subprocess,'Popen',side_effect=FileNotFoundError),patch.object(web_launch.os,'startfile') as fallback:
            result,handle=web_launch.open_website('https://www.youtube.com')
        fallback.assert_called_once_with('https://www.youtube.com')
        self.assertIsNone(handle); self.assertTrue(result.startswith('Asked Windows'))

    def test_accessibility_failure_does_not_undo_launch(self):
        with patch.object(web_launch,'edge_path',return_value='edge.exe'),patch.object(web_launch.windows,'window_inventory',side_effect=RuntimeError('access denied')),patch.object(web_launch.subprocess,'Popen') as launch,patch.object(web_launch,'visible_address',side_effect=RuntimeError('access denied')):
            result,handle=web_launch.open_website('https://www.youtube.com')
        launch.assert_called_once(); self.assertIsNone(handle); self.assertTrue(result.startswith('Asked Edge'))


if __name__=='__main__': unittest.main()
