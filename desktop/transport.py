"""Cancellable local Ollama stream, including while a model is loading."""
import asyncio
import json
import queue
import threading
import httpx


class ChatConnection:
    TOTAL_TIMEOUT = 180
    def __init__(self, url, payload, cancelled):
        self.url = url
        self.payload = payload
        self.cancelled = cancelled
        self._lock = threading.Lock()
        self._loop = None
        self._task = None

    def abort(self):
        self.cancelled.set()
        with self._lock:
            loop, task = self._loop, self._task
        if loop and task:
            try:
                loop.call_soon_threadsafe(task.cancel)
            except RuntimeError:
                pass

    def stream(self):
        chunks = queue.Queue(maxsize=64)
        finished = threading.Event()
        consumer_done = threading.Event()

        async def publish(item):
            while not consumer_done.is_set() and not self.cancelled.is_set():
                try:chunks.put_nowait(item);return
                except queue.Full:await asyncio.sleep(.005)

        async def receive():
            with self._lock:
                self._loop = asyncio.get_running_loop()
                self._task = asyncio.current_task()
            try:
                if self.cancelled.is_set():
                    return
                async with httpx.AsyncClient(timeout=httpx.Timeout(90, connect=3), trust_env=False) as client:
                    async with client.stream('POST', self.url, json=self.payload) as response:
                        if response.status_code != 200:
                            if response.status_code == 404:
                                raise ValueError('Choose an installed Ollama model in Settings.')
                            raise ValueError(f'Ollama returned HTTP {response.status_code}.')
                        async for line in response.aiter_lines():
                            if self.cancelled.is_set():
                                break
                            if line.strip():
                                await publish(json.loads(line))
            except asyncio.CancelledError:
                raise
            except httpx.HTTPError:
                await publish(ConnectionError("Ollama isn't responding. Start Ollama and check your model in Settings."))
            except Exception as error:
                await publish(error)
            finally:
                with self._lock:
                    self._loop = self._task = None

        async def bounded_receive():
            try:await asyncio.wait_for(receive(),timeout=self.TOTAL_TIMEOUT)
            except asyncio.CancelledError:pass
            except asyncio.TimeoutError:
                await publish(TimeoutError('Model response exceeded its time limit. No action will be retried automatically.'))

        def run():
            try:
                asyncio.run(bounded_receive())
            finally:
                finished.set()

        worker = threading.Thread(target=run, daemon=True)
        worker.start()
        try:
            while True:
                if self.cancelled.is_set():break
                try:item = chunks.get(timeout=.05)
                except queue.Empty:
                    if finished.is_set():break
                    continue
                if isinstance(item, Exception):
                    raise item
                yield item
        finally:
            consumer_done.set()
            # Finish/abort this request without changing the job's cancellation flag.
            with self._lock:
                loop, task = self._loop, self._task
            if loop and task:
                try:
                    loop.call_soon_threadsafe(task.cancel)
                except RuntimeError:
                    pass
            worker.join(timeout=2)
