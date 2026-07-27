"""
Skill Manager
"""

from core.skills.builtin.hello import HelloSkill
from core.skills.builtin.apps.open_app import OpenAppSkill


class SkillManager:

    def __init__(self):

        self.skills = {}

        self.register(HelloSkill())
        self.register(OpenAppSkill())

    def register(self, skill):

        self.skills[skill.name] = skill

    def execute(self, name, *args):

        skill = self.skills.get(name)

        if not skill:

            return {
                "error": "Skill not found"
            }

        return skill.execute(*args)

    def list(self):

        return list(self.skills.keys())