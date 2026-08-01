from dataclasses import dataclass, field
from typing import Any
from datetime import datetime
from app.memory.memory_service import (
    save_memory,
    search_memory,
    delete_memory,
)


@dataclass
class ConversationTurn:
    timestamp: datetime
    speaker: str
    message: str


@dataclass
class AstraBrain:

    # Current conversation
    conversation_history: list[ConversationTurn] = field(default_factory=list)

    # Persistent memory (key → value)
    memories: dict[str, str] = field(default_factory=dict)

    # Current context
    last_intent: str | None = None
    last_subject: str | None = None
    last_action: str | None = None
    last_app: str | None = None
    last_file: str | None = None
    last_url: str | None = None
    last_person: str | None = None
    last_folder: str | None = None
    last_song: str | None = None
    last_search: str | None = None
    last_browser: str | None = None
    last_volume: int | None = None
    last_response: str | None = None

    # Pending actions
    awaiting_confirmation: bool = False
    pending_action: str | None = None
    pending_data: Any = None

    # Dynamic variables
    variables: dict = field(default_factory=dict)

    # Session state
    active_window: str | None = None
    active_folder: str | None = None

    # -------------------------
    # Conversation Memory
    # -------------------------

    def remember_user(self, message: str):

        self.conversation_history.append(

            ConversationTurn(
                datetime.now(),
                "user",
                message
            )

        )

        self.conversation_history = self.conversation_history[-25:]

    def remember_astra(self, message: str):

        self.conversation_history.append(

            ConversationTurn(
                datetime.now(),
                "astra",
                message
            )

        )

        self.conversation_history = self.conversation_history[-25:]

    # -------------------------
    # Persistent Memory
    # -------------------------

    def remember(self, key: str, value: str):

        key = key.lower()

         # RAM cache
        self.memories[key] = value

        # Persistent storage
        save_memory(key, value)

    def recall(self, key: str):

        key=key.lower()

        # Fast lookup from RAM
        if key in self.memories:
            return self.memories[key]


        # Database lookup
        results = search_memory(key)

        if results:
            value = results[0]["value"]

            # Cache it
            self.memories[key] = value
            return value
        return None

    def forget(self, key: str):

        key = key.lower()
        self.memories.pop(key, None)
        delete_memory(key)

    # -------------------------
    # Context
    # -------------------------

    def set_intent(self, intent: str):

        self.last_intent = intent

    def set_subject(self, subject: str):

        self.last_subject = subject

    def set_app(self, app: str):

        self.last_app = app

    def set_file(self, file: str):

        self.last_file = file

    # -------------------------

    def ask_confirmation(self, action: str, data=None):

        self.awaiting_confirmation = True
        self.pending_action = action
        self.pending_data = data

    def clear_confirmation(self):

        self.awaiting_confirmation = False
        self.pending_action = None
        self.pending_data = None

    def reset(self):

        self.__init__()


brain = AstraBrain()