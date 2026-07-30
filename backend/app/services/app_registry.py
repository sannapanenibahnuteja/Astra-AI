import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(exist_ok=True)

REGISTRY_FILE = DATA_DIR / "apps.json"


class AppRegistry:

    def __init__(self):
        self.apps = {}
        self.load()

    def load(self):
        if REGISTRY_FILE.exists():
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                self.apps = json.load(f)
        else:
            self.apps = {}

    def save(self):
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.apps, f, indent=4)

    def register(self, key, app_data):
        self.apps[key.lower()] = app_data
        self.save()

    def get(self, key):
        return self.apps.get(key.lower())

    def exists(self, key):
        return key.lower() in self.apps

    def remove(self, key):
        if key.lower() in self.apps:
            del self.apps[key.lower()]
            self.save()

    def all(self):
        return self.apps


registry = AppRegistry()