"""
Hello Skill
"""

from core.skills.base.skill import Skill


class HelloSkill(Skill):

    def __init__(self):

        super().__init__()

        self.name = "hello"

        self.description = "Simple greeting"

    def execute(self):

        return {

            "response": "Hello! I am Astra."

        }