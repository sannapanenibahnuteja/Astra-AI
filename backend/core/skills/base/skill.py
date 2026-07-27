"""
Astra Skill Base
"""

from abc import ABC, abstractmethod


class Skill(ABC):

    def __init__(self):

        self.name = "Unnamed Skill"

        self.description = ""

    @abstractmethod
    def execute(self, *args, **kwargs):

        pass