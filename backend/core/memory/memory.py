"""
Astra Memory
Version: 1.0.0
"""

from pathlib import Path
import json


class Memory:

    def __init__(self):

        self.memory_file = (
            Path(__file__).parent / "data" / "memory.json"
        )

        if not self.memory_file.exists():

            self.memory_file.write_text("{}")

    def load(self):

        with open(self.memory_file, "r") as file:

            return json.load(file)

    def save(self, data):

        with open(self.memory_file, "w") as file:

            json.dump(data, file, indent=4)