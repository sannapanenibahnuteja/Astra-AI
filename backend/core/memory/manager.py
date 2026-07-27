"""
Astra Memory Manager
Version: 1.0.0
"""

from .memory import Memory


class MemoryManager:

    def __init__(self):

        self.memory = Memory()

    def remember(self, key, value):

        data = self.memory.load()

        data[key] = value

        self.memory.save(data)

    def recall(self, key):

        data = self.memory.load()

        return data.get(key, None)

    def all(self):

        return self.memory.load()