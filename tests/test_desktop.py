import tempfile
import time
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from desktop.commands import Commands, parse, safe_url
from desktop.runtime import Runtime
from desktop.storage import Store
from desktop.prompt import build_messages
from desktop.runtime import SYSTEM


class DesktopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.runtime = Runtime(self.temp.name)
        self.store = self.runtime._store
        self.identity = self.store.new_conversation()

    def tearDown(self):
        self.temp.cleanup()

    def wait(self, job):
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            result = self.runtime.poll_chat(job)
            if result["done"]:
                return result
            time.sleep(.01)
        self.fail("Response did not finish")

    def model(self, message, chunks):
        with patch("desktop.runtime.ChatConnection") as request:
            request.return_value.stream.return_value = iter(chunks)
            result = self.wait(self.runtime.start_chat(self.identity, message))
            payload = request.call_args[0][1]
        return result, payload

    def test_conversation_persists_and_is_isolated(self):
        self.store.append(self.identity, "user", "My plan is a garden.")
        other = self.store.new_conversation()
        reopened = Store(self.temp.name)
        self.assertEqual(reopened.messages(self.identity)[0]["content"], "My plan is a garden.")
        self.assertEqual(reopened.messages(other), [])

    def test_memory_upserts_and_forgets(self):
        self.store.remember("Name", "First")
        self.store.remember("name", "Second")
        self.assertEqual(self.store.memories(), [{"key": "name", "value": "Second"}])
        self.store.forget("name")
        self.assertEqual(self.store.memories(), [])

    def test_no_substring_or_negative_commands(self):
        for text in ("Explain open source", "Do not open calculator", "I started learning Python", "How do I open Chrome?", "The word launch is interesting"):
            self.assertIsNone(parse(text), text)

    def test_politeness_and_voice_normalization(self):
        self.assertEqual(parse("Hey Bob, could you please open calculator?"), {"action": "open", "target": "calculator"})
        self.assertEqual(parse("Please set the volume to 35 percent")["target"], "35")

    def test_fuzzy_match_requires_confirmation(self):
        result = self.runtime._commands.plan("open calculatr", self.identity)
        self.assertEqual(result["target"], "calculator")
        self.assertTrue(result["confirm"])
        with patch("desktop.commands.subprocess.Popen") as execute:
            result = self.wait(self.runtime.start_chat(self.identity, "open calculatr"))
            self.assertIn("Should I", result["text"])
            execute.assert_not_called()
            result = self.wait(self.runtime.start_chat(self.identity, "yes"))
            execute.assert_called_once()
            self.assertIn("Opened", result["text"])

    def test_context_does_not_cross_conversations(self):
        self.store.context(self.identity, {"last_app": "calculator"})
        self.assertEqual(self.runtime._commands.plan("open it again", self.identity)["target"], "calculator")
        other = self.store.new_conversation()
        self.assertEqual(self.runtime._commands.plan("open it again", other)["action"], "clarify")

    def test_stream_includes_history_and_memory(self):
        self.store.append(self.identity, "user", "I am planning a garden")
        self.store.append(self.identity, "assistant", "What size?")
        self.store.remember("city", "Bengaluru")
        result, payload = self.model("Ten square meters", [{"message": {"content": "A small "}}, {"message": {"content": "garden."}, "done": True}])
        self.assertEqual(result["text"], "A small garden.")
        self.assertIn("Bengaluru", payload["messages"][0]["content"])
        self.assertEqual(payload["messages"][-3]["content"], "I am planning a garden")
        self.assertEqual(payload["keep_alive"], "2m")
        self.assertFalse(payload["think"])
        self.assertEqual(self.store.messages(self.identity)[-1]["content"], "A small garden.")

    def test_routine_model_actions_execute_without_confirmation(self):
        calls = [{"function": {"name": "windows_action", "arguments": {"action": "open", "target": "calculator"}}},
                 {"function": {"name": "windows_action", "arguments": {"action": "volume", "target": "20"}}}]
        with patch.object(Commands, "execute", return_value="Done") as execute:
            result, _ = self.model("I would like a calculator with softer sound, please", [{"message": {"tool_calls": calls}, "done": True}])
            self.assertEqual(execute.call_count, 2)
            self.assertNotIn(self.identity, self.runtime._pending)
            self.assertIn("Done", result["text"])

    def test_unapproved_actions_and_out_of_range_volume_rejected(self):
        for command in ({"action": "shell", "target": "anything"}, {"action": "volume", "target": "200"}, {"action": "search", "target": ""}):
            with self.assertRaises(ValueError):
                self.runtime._commands.validate_model_action(command, self.identity)

    def test_pending_confirmation_cancelled_on_unrelated_message(self):
        self.wait(self.runtime.start_chat(self.identity, "lock my computer"))
        self.wait(self.runtime.start_chat(self.identity, "what time is it"))
        self.assertNotIn(self.identity, self.runtime._pending)

    def test_memory_command_keeps_numbers(self):
        self.wait(self.runtime.start_chat(self.identity, "remember that my bike is GT650"))
        self.assertEqual(self.store.memories(), [{"key": "bike", "value": "GT650"}])

    def test_project_bounds_and_exclusions(self):
        project = Path(self.temp.name) / "project"
        project.mkdir()
        (project / "README.md").write_text("project contents", encoding="utf-8")
        (project / ".env").write_text("private", encoding="utf-8")
        (Path(self.temp.name) / "outside.txt").write_text("outside", encoding="utf-8")
        self.runtime.save_settings({"project_path": str(project)})
        commands = self.runtime._commands
        self.assertIn("project contents", commands.project_action("project_read", "README.md"))
        self.assertIn("inside", commands.project_action("project_read", "../outside.txt"))
        self.assertIn("excluded", commands.project_action("project_read", ".env"))
        self.assertNotIn(".env", commands.project_action("project_list", ""))

    def test_settings_validation(self):
        for values in ({"ollama_url": "https://example.com"}, {"keep_alive": "forever"}, {"context_size": 9999}, {"model": ""}):
            with self.assertRaises(ValueError):
                self.runtime.save_settings(values)
        for url in ("javascript:alert(1)", "file:///windows", "https://name:secret@example.com"):
            with self.assertRaises(ValueError):
                safe_url(url)

    def test_ollama_connection_status_reports_installed_model(self):
        with patch('desktop.runtime.urlopen', return_value=io.BytesIO(b'{"models":[{"name":"qwen3:8b"}]}')):
            result = self.runtime.ollama_status()
        self.assertTrue(result['online'])
        self.assertTrue(result['ready'])
        self.assertEqual(result['models'], ['qwen3:8b'])

    def test_empty_response_and_connection_failure_are_reported(self):
        result, _ = self.model("Hello", [{"done": True}])
        self.assertTrue(result["error"])
        from urllib.error import URLError
        with patch("desktop.runtime.ChatConnection") as transport:
            transport.return_value.stream.side_effect = URLError("offline")
            result = self.wait(self.runtime.start_chat(self.identity, "Hello again"))
        self.assertIn("Ollama", result["error"])

    def test_deleted_conversation_removes_history(self):
        self.store.append(self.identity, "user", "hello")
        self.store.context(self.identity, {"last_app": "calculator"})
        self.runtime.delete_conversation(self.identity)
        self.assertEqual(self.store.messages(self.identity), [])
        self.assertEqual(self.store.context(self.identity), {})
        with self.assertRaises(ValueError):
            self.store.append(self.identity, "user", "hello")

    def test_prompt_budget_scales_and_keeps_current_request(self):
        settings = self.store.settings()
        settings.update(context_size=2048, personality='P' * 8000)
        history = [{'role': 'user', 'content': 'old ' * 5000},
                   {'role': 'assistant', 'content': 'answer ' * 5000},
                   {'role': 'user', 'content': 'Current question ' + '界' * 15000}]
        memories = [{'key': str(i), 'value': 'a' * 3000} for i in range(20)]
        result = build_messages(SYSTEM, settings, memories, ['application' * 100] * 100, history)
        self.assertLessEqual(sum(len(t['content'].encode()) for t in result), 3200)
        self.assertEqual(result[-1]['role'], 'user')
        self.assertTrue(result[-1]['content'].startswith('Current question'))
        self.assertIn('shortened', result[-1]['content'])

    def test_cancellation_interrupts_waiting_for_headers(self):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        arrived, release = threading.Event(), threading.Event()

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                arrived.set()
                release.wait(5)

            def log_message(self, *_):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            self.runtime.save_settings({'ollama_url': f'http://127.0.0.1:{server.server_port}'})
            job = self.runtime.start_chat(self.identity, 'Tell me a story')
            self.assertTrue(arrived.wait(2))
            started = time.monotonic()
            self.runtime.cancel_chat()
            result = self.wait(job)
            self.assertLess(time.monotonic() - started, 1)
            self.assertIn('[Response stopped.]', result['text'])
            self.assertEqual(result['error'], '')
            self.assertEqual(len(self.store.messages(self.identity)), 2)
            followup = self.wait(self.runtime.start_chat(self.identity, 'what time is it'))
            self.assertFalse(followup['error'])
        finally:
            release.set()
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
import io
