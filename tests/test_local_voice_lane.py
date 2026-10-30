import tempfile
import time
import unittest
from unittest.mock import Mock,patch
from desktop.runtime import Runtime


class LocalVoiceLaneTests(unittest.TestCase):
    def test_spoken_common_command_never_needs_model_and_runs_once(self):
        with tempfile.TemporaryDirectory() as root:
            runtime=Runtime(root)
            try:
                identity=runtime.new_conversation()
                runtime._commands.capture_explorer=Mock()
                runtime._store.save_settings({'voice_enabled':False})
                with patch.object(runtime._commands,'execute',return_value='Volume increased.') as execute,patch('desktop.runtime.ChatConnection',side_effect=AssertionError('No model for exact local command')):
                    job=runtime.start_chat(identity,'please turn up the volume',spoken=True)
                    deadline=time.monotonic()+5
                    while time.monotonic()<deadline:
                        result=runtime.poll_chat(job)
                        if result['done']:break
                        time.sleep(.01)
                    self.assertTrue(result['done']);self.assertFalse(result['error'])
                    execute.assert_called_once()
                    self.assertEqual(execute.call_args.args[0]['action'],'volume_up')
            finally:runtime._voice.close()

    def test_negative_compound_and_out_of_range_commands_cannot_use_fast_lane(self):
        with tempfile.TemporaryDirectory() as root:
            runtime=Runtime(root)
            try:
                for text in ('do not mute','volume up and delete that file','set volume to 200','I wonder whether volume up is a command'):
                    with patch.object(runtime._commands,'plan') as plan:
                        self.assertIsNone(runtime._commands.fast_local(text,'fixture'))
                        plan.assert_not_called()
            finally:runtime._voice.close()
