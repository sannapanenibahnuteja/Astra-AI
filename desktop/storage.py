"""Durable, per-user data. Never write inside the installed application."""
import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path


class Store:
    def __init__(self, root=None):
        self.root = Path(root or os.environ.get("BOB_DATA_DIR") or
                         Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Bob").resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "bob.db"
        # Preserve existing users' conversations during the product rename.
        if not root and not os.environ.get("BOB_DATA_DIR") and not self.path.exists():
            self._import_previous_install()
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, updated TEXT DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY, conversation TEXT NOT NULL, role TEXT NOT NULL,
                    content TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS memories (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS context (
                    conversation TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS action_history (
                    id INTEGER PRIMARY KEY,
                    conversation TEXT NOT NULL,
                    command TEXT NOT NULL,
                    result TEXT NOT NULL,
                    created TEXT DEFAULT CURRENT_TIMESTAMP);
            """)

    def _import_previous_install(self):
        import shutil
        legacy = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Astra"
        database = legacy / "astra.db"
        if not database.exists():
            return
        source = sqlite3.connect(database)
        destination = sqlite3.connect(self.path)
        try:
            source.backup(destination)
            destination.execute("UPDATE settings SET key='bob_url' WHERE key='astra_url'")
            destination.commit()
        finally:
            source.close()
            destination.close()
        if (legacy / "notes").is_dir():
            shutil.copytree(legacy / "notes", self.root / "notes", dirs_exist_ok=True)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def settings(self):
        result = {"ollama_url": "http://127.0.0.1:11434", "model": "qwen3:8b",
                  "personality": "", "personality_preset": "balanced", "bob_url": "", "voice_enabled": True,
                  "voice_rate": 0, "voice_language": "en-US", "project_path": "",
                  "wake_enabled": True, "greeting_enabled": True,
                  "auto_listen": True,
                  "keep_alive": "2m", "context_size": 4096}
        with self.connect() as db:
            result.update({r["key"]: json.loads(r["value"]) for r in db.execute("SELECT * FROM settings")})
        return result

    def save_settings(self, values):
        with self.connect() as db:
            db.executemany("INSERT OR REPLACE INTO settings VALUES (?, ?)",
                           [(k, json.dumps(v)) for k, v in values.items()])
        return self.settings()

    def new_conversation(self):
        identity = uuid.uuid4().hex
        with self.connect() as db:
            db.execute("INSERT INTO conversations(id,title) VALUES (?, 'New conversation')", (identity,))
        return identity

    def conversations(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute("SELECT * FROM conversations ORDER BY updated DESC, rowid DESC")]

    def messages(self, identity, limit=200):
        with self.connect() as db:
            return [dict(r) for r in db.execute(
                "SELECT role,content FROM (SELECT id,role,content FROM messages WHERE conversation=? "
                "ORDER BY id DESC LIMIT ?) ORDER BY id", (identity, limit))]

    def append(self, identity, role, content):
        with self.connect() as db:
            if not db.execute("SELECT 1 FROM conversations WHERE id=?", (identity,)).fetchone():
                raise ValueError("Conversation no longer exists.")
            db.execute("INSERT INTO messages(conversation,role,content) VALUES (?,?,?)", (identity, role, content))
            db.execute("UPDATE conversations SET updated=CURRENT_TIMESTAMP WHERE id=?", (identity,))
            if role == "user":
                db.execute("UPDATE conversations SET title=? WHERE id=? AND title='New conversation'",
                           (content[:55], identity))

    def delete_conversation(self, identity):
        with self.connect() as db:
            for table in ("messages", "context", "action_history"):
                db.execute(f"DELETE FROM {table} WHERE conversation=?", (identity,))
            db.execute("DELETE FROM conversations WHERE id=?", (identity,))

    def memories(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute("SELECT * FROM memories ORDER BY key")]

    def remember(self, key, value):
        key, value = key.strip().lower(), value.strip()
        if not key or not value or len(key) > 120 or len(value) > 4000:
            raise ValueError("Use a memory name up to 120 characters and a value up to 4,000 characters.")
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO memories VALUES (?,?)", (key, value))

    def forget(self, key):
        with self.connect() as db:
            db.execute("DELETE FROM memories WHERE key=?", (key,))

    def context(self, identity, value=None):
        with self.connect() as db:
            if value is not None:
                db.execute("INSERT OR REPLACE INTO context VALUES (?,?)", (identity, json.dumps(value)))
            row = db.execute("SELECT value FROM context WHERE conversation=?", (identity,)).fetchone()
            return json.loads(row[0]) if row else {}

    def record_action(self, identity, command, result):
        payload = {k: v for k, v in command.items() if k != "_window_ref"}
        with self.connect() as db:
            db.execute("INSERT INTO action_history(conversation,command,result) VALUES (?,?,?)",
                       (identity, json.dumps(payload), str(result)[:4000]))
            db.execute("DELETE FROM action_history WHERE id NOT IN ("
                       "SELECT id FROM action_history WHERE conversation=? ORDER BY id DESC LIMIT 50"
                       ") AND conversation=?", (identity, identity))

    def recent_actions(self, identity, limit=10):
        with self.connect() as db:
            rows = db.execute("SELECT command,result,created FROM action_history WHERE conversation=? "
                              "ORDER BY id DESC LIMIT ?", (identity, limit))
            return [{**dict(r), "command": json.loads(r["command"])} for r in rows]
