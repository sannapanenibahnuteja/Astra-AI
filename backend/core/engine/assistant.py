"""
Astra AI Assistant
Core Engine
Version: 1.0.0
"""

from datetime import datetime

from .state import AssistantState


class AstraAssistant:

    def __init__(self):

        self.name = "Astra"

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