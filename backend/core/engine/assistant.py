"""
Bob AI Assistant
Core Engine
Version: 1.0.0
"""

from datetime import datetime

from .state import AssistantState


class BobAssistant:

    def __init__(self):

        self.name = "Bob"

        self.version = "1.0.0"

        self.state = AssistantState.IDLE

        self.created = datetime.now()

    def get_info(self):

        return {
            "name": self.name,
            "version": self.version,
            "state": self.state,
            "created": self.created.strftime("%d-%m-%Y %H:%M:%S")
        }

    def set_state(self, state):

        self.state = state