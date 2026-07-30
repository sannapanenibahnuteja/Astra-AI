from app.services.astra_brain import brain


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }


class AIHandler:

    AI_ACTIONS = {
        "chat",
        "ask",
        "explain",
        "summarize",
        "remember",
        "recall",
    }

    def handle(self, action, target, value):

        if action not in self.AI_ACTIONS:
            return None

        # -------------------------
        # Chat
        # -------------------------

        if action == "chat":

            return response(
                True,
                value,
            )

        # -------------------------
        # Ask
        # -------------------------

        if action == "ask":

            return response(
                True,
                value,
            )

        # -------------------------
        # Explain
        # -------------------------

        if action == "explain":

            return response(
                True,
                value,
            )

        # -------------------------
        # Summarize
        # -------------------------

        if action == "summarize":

            return response(
                True,
                value,
            )

        # -------------------------
        # Remember
        # -------------------------

        if action == "remember":

            if not target or value is None:
                return response(False, "Missing memory key or value.")

            if hasattr(brain, "remember"):
                brain.remember(target, value)
                return response(True, "Memory stored.")

            return response(False, "Memory system unavailable.")

        # -------------------------
        # Recall
        # -------------------------

        if action == "recall":

            if not target:
                return response(False, "Missing memory key.")

            if hasattr(brain, "recall"):
                memory = brain.recall(target)
                return response(True, "Memory recalled.", memory)

            return response(False, "Memory system unavailable.")

        return None