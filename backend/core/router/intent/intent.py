"""
Intent Detection
"""


class IntentDetector:

    def detect(self, command: str):

        command = command.lower().strip()

        if command in ["hello", "hi", "hey"]:
            return ("hello", [])

        if command.startswith("open "):

            app = command.replace("open ", "", 1)

            return ("open_app", [app])

        return (None, [])