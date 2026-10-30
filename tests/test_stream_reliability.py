import asyncio
import threading
import unittest
from unittest.mock import patch
from desktop.transport import ChatConnection


class StalledClient:
    def __init__(self,**kwargs):pass
    async def __aenter__(self):return self
    async def __aexit__(self,*args):pass
    def stream(self,*args,**kwargs):return self
    @property
    def status_code(self):return 200
    async def aiter_lines(self):
        await asyncio.sleep(10)
        yield '{}'


class StreamReliabilityTests(unittest.TestCase):
    def test_total_deadline_is_reported_not_swallowed_as_clean_eof(self):
        connection=ChatConnection('http://fixture.invalid',{},threading.Event())
        connection.TOTAL_TIMEOUT=.02
        with patch('desktop.transport.httpx.AsyncClient',StalledClient):
            with self.assertRaisesRegex(TimeoutError,'time limit'):list(connection.stream())
        self.assertFalse(connection.cancelled.is_set())

    def test_cancellation_interrupts_stalled_stream_without_retry(self):
        cancel=threading.Event();connection=ChatConnection('http://fixture.invalid',{},cancel)
        timer=threading.Timer(.02,cancel.set);timer.start()
        try:
            with patch('desktop.transport.httpx.AsyncClient',StalledClient):
                self.assertEqual(list(connection.stream()),[])
        finally:timer.join()

    def test_inference_threads_leave_audio_capacity_and_are_bounded(self):
        from desktop.voice import Voice
        for cores,expected in ((1,1),(4,2),(16,4),(None,1)):
            voice=Voice()
            try:
                with patch('desktop.voice.os.cpu_count',return_value=cores),patch('faster_whisper.WhisperModel') as model:
                    voice._load_model()
                    self.assertEqual(model.call_args.kwargs['cpu_threads'],expected)
            finally:voice.close()
