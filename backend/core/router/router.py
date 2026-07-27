"""
Command Router
"""

from core.router.intent.intent import IntentDetector
from core.skills import SkillManager


class CommandRouter:

    def __init__(self):

        self.intent = IntentDetector()
        self.skills = SkillManager()

    def execute(self, command: str):

        skill, args = self.intent.detect(command)

        if skill is None:

            return {
                "success": False,
                "response": "Sorry, I don't understand that command yet."
            }

        result = self.skills.execute(skill, *args)

        return {
            "success": True,
            "intent": skill,
            "result": result
        }