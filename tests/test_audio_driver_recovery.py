import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
import numpy as np
from desktop.duplex_audio import DuplexAudio, BLOCK


class AudioDriverRecoveryTests(unittest.TestCase):
    def engine(self):
        engine=DuplexAudio(Mock(),Mock())
        self.addCleanup(engine.close)
        return engine

    def test_start_retries_same_wasapi_pair_in_shared_mode(self):
        engine=self.engine();engine.worker=Mock()
        sd=Mock()
        sd.query_hostapis.return_value=[{'name':'Windows WASAPI','default_input_device':2,'default_output_device':3}]
        sd.query_devices.side_effect=[{'name':'Mic','max_input_channels':1},{'name':'Speaker','max_output_channels':2}]
        failed=Mock();failed.start.side_effect=RuntimeError('driver unavailable')
        good=Mock();sd.Stream.side_effect=[failed,good]
        with patch.dict('sys.modules',{'sounddevice':sd}):engine.start()
        self.assertIs(engine.stream,good)
        self.assertEqual([c.kwargs['latency'] for c in sd.Stream.call_args_list],['low','high'])
        self.assertTrue(all(c.kwargs['device']==(2,3) for c in sd.Stream.call_args_list))
        self.assertTrue(all(c.kwargs=={'exclusive':False,'auto_convert':True} for c in sd.WasapiSettings.call_args_list))
        failed.close.assert_called_once();engine.worker.start.assert_called_once()

    def test_failed_candidates_do_not_start_worker_or_change_devices(self):
        engine=self.engine();engine.worker=Mock();engine.worker.is_alive.return_value=False
        sd=Mock()
        sd.query_hostapis.return_value=[{'name':'Windows WASAPI','default_input_device':2,'default_output_device':3}]
        sd.query_devices.side_effect=[{'name':'Mic','max_input_channels':1},{'name':'Speaker','max_output_channels':2}]
        sd.Stream.side_effect=RuntimeError('PRIVATE DRIVER DETAIL')
        with patch.dict('sys.modules',{'sounddevice':sd}):
            with self.assertRaisesRegex(RuntimeError,'No alternate microphone was selected') as error:engine.start()
        self.assertNotIn('PRIVATE DRIVER DETAIL',str(error.exception))
        engine.worker.start.assert_not_called()

    def callback(self,engine,status):
        incoming=np.zeros((BLOCK,1),np.float32)
        outgoing=np.empty((BLOCK,2),np.float32)
        engine._audio(incoming,outgoing,BLOCK,SimpleNamespace(outputBufferDacTime=1.,inputBufferAdcTime=1.),status)
        return outgoing

    def test_one_recoverable_dropout_does_not_cancel_or_drop_reference(self):
        engine=self.engine();engine.samples=np.full(BLOCK,.1,np.float32)
        outgoing=self.callback(engine,True)
        self.assertEqual(engine.error,'');self.assertEqual(engine.stream_glitches,1)
        engine.on_interrupt.assert_not_called()
        _,reference,_,captured_at=engine.blocks.get_nowait()
        self.assertGreater(captured_at,0)
        np.testing.assert_array_equal(reference,outgoing[:,0])

    def test_repeated_driver_failure_remains_a_visible_audio_error(self):
        engine=self.engine()
        with patch('desktop.duplex_audio.time.monotonic',return_value=10.):
            for _ in range(20):self.callback(engine,True)
        self.assertIn('Repeated audio driver dropouts',engine.error)
        engine.on_interrupt.assert_not_called()


if __name__=='__main__':unittest.main()
