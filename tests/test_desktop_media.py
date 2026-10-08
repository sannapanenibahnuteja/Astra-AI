import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from desktop import media
from desktop.commands import Commands
from desktop.storage import Store


class MediaTests(unittest.TestCase):
    def test_transport_and_named_player(self):
        for text, action in [('pause the video','media_pause'),('resume','media_play'),('next song','media_next'),('what is playing','media_status')]:
            self.assertEqual(media.validate(media.parse(text))['action'],action)
        command=media.validate(media.parse('pause in Spotify'))
        self.assertEqual(command['window'],'Spotify')
        self.assertFalse(command['confirm'])

    def test_seek_spoken_units_and_timestamps(self):
        for text,action,value in [('rewind thirty seconds','media_back',30),('fast forward two minutes','media_forward',120),('seek to 1:30','media_seek',90),('go to 1:02:03','media_seek',3723)]:
            command=media.validate(media.parse(text))
            self.assertEqual(command['action'],action)
            self.assertEqual(float(command['value']),value)
        with self.assertRaises(ValueError):media.parse('seek to 1:99')

    def test_negations_and_spoken_stop_mode_do_not_change_playback(self):
        for text in ('do not pause the video','how do I play music','stop listening','never play this','explain rewind'):
            self.assertIsNone(media.parse(text))

    def test_rate_shuffle_repeat_bounds(self):
        for text,action in [('shuffle on','media_shuffle'),('repeat one','media_repeat'),('set speed to 1.5x','media_rate')]:
            self.assertEqual(media.validate(media.parse(text))['action'],action)
        for value in ('NaN','inf','-2','500'):
            with self.assertRaises(ValueError):media.validate({'action':'media_rate','value':value})
        with self.assertRaises(ValueError):media.validate({'action':'media_repeat','value':'anything'})

    def test_context_and_verified_response(self):
        result={'app':'MSEdge','title':'Sample','artist':'Test','state':'Paused','position':20}
        context={}
        with patch('desktop.media.native',return_value=result):
            self.assertEqual(media.execute({'action':'media_pause'},context),'Paused: Sample.')
        self.assertEqual(context['last_media_app'],'MSEdge')
        with patch('desktop.media.native',side_effect=RuntimeError('Rejected')):
            with self.assertRaisesRegex(RuntimeError,'Rejected'):media.execute({'action':'media_play'},context)

    def test_local_music_and_no_scripts(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); track=root/'My song.mp3';track.write_bytes(b'fixture')
            with patch('desktop.media.files.known_folder',return_value=root),patch('desktop.media.os.startfile') as start:
                context={};result=media.local_media('My song',context)
                start.assert_called_once_with(str(track))
                self.assertIn('Asked your default media player',result)
                self.assertIn('unverified',result)
                self.assertNotIn('Playing',result)
                self.assertEqual(context['last_media_file'],str(track))
            script=root/'test.cmd';script.write_text('echo example')
            with patch('desktop.media.os.startfile') as start:
                with self.assertRaises(ValueError):media.local_media(str(script),{})
                start.assert_not_called()

    def test_multiple_tracks_require_exact_target(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name in ('song one.mp3','song two.mp3'):(root/name).write_bytes(b'fixture')
            with patch('desktop.media.files.known_folder',return_value=root),patch('desktop.media.os.startfile') as start:
                with self.assertRaisesRegex(ValueError,'Several'):media.local_media('song',{})
                start.assert_not_called()

    def test_generic_music_falls_back_only_when_no_session_exists(self):
        with patch('desktop.media.native',return_value=[]),patch('desktop.media.local_media',return_value='Opened a track') as local:
            self.assertEqual(media.execute(media.parse('play music'),{}),'Opened a track')
            local.assert_called_once_with('*',{})
        with patch('desktop.media.native',side_effect=RuntimeError('ambiguous')),patch('desktop.media.local_media') as local:
            with self.assertRaises(RuntimeError):media.execute(media.parse('play music'),{})
            local.assert_not_called()

    def test_media_and_volume_compound_is_direct(self):
        with tempfile.TemporaryDirectory() as folder:
            store=Store(folder);identity=store.new_conversation();commands=Commands(store)
            plans=commands.plan('pause the video and set volume to twenty percent',identity)
            self.assertEqual([p['action'] for p in plans],['media_pause','volume'])
            plans=commands.plan("I'd like you to pause the current video and go back thirty seconds.",identity)
            self.assertEqual([p['action'] for p in plans],['media_pause','media_back'])
            self.assertEqual(float(plans[1]['value']),30)

    def test_search_never_claims_autoplay(self):
        with patch('desktop.media.webbrowser.open',return_value=True) as browser:
            result=media.execute({'action':'media_search','target':'jazz & piano','window':'youtube'}, {})
            self.assertIn('does not autoplay',result)
            self.assertIn('jazz+%26+piano',browser.call_args.args[0])

    def test_missing_foreground_window_does_not_break_chat(self):
        with tempfile.TemporaryDirectory() as folder:
            commands=Commands(Store(folder));commands.explorer_handle=123
            with patch('win32gui.GetForegroundWindow',return_value=0),patch('win32process.GetWindowThreadProcessId',return_value=(0,-1)):
                commands.capture_explorer()
            self.assertIsNone(commands.explorer_handle)


if __name__=='__main__':unittest.main()
