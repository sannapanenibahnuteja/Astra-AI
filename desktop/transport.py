"""Cancellable local Ollama stream, including while a model is loading."""
import asyncio
import json
import queue
import threading
import httpx


class ChatConnection:
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
        chunks = queue.Queue()
        finished = object()

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
                                chunks.put(json.loads(line))
            except asyncio.CancelledError:
                pass
            except httpx.HTTPError:
                chunks.put(ConnectionError("Ollama isn't responding. Start Ollama and check your model in Settings."))
            except Exception as error:
                chunks.put(error)
            finally:
                with self._lock:
                    self._loop = self._task = None

        def run():
            try:
                asyncio.run(receive())
            finally:
                chunks.put(finished)

        worker = threading.Thread(target=run, daemon=True)
        worker.start()
        try:
            while True:
                item = chunks.get()
                if item is finished:
                    break
                if isinstance(item, Exception):
                    raise item
                yield item
        finally:
            # Finish/abort this request without changing the job's cancellation flag.
            with self._lock:
                loop, task = self._loop, self._task
            if loop and task:
                try:
                    loop.call_soon_threadsafe(task.cancel)
                except RuntimeError:
                    pass
            worker.join(timeout=2)
