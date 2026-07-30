from app.services.astra_brain import brain


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }


class AIHandler:

    AI_ACTIONS = {
        None,           # Fallback for unknown commands
        "chat",
        "ask",
        "explain",
        "summarize",
        "remember",
        "recall",
    }

    def handle(self, action, target, value, query=None):

        print(
            f"[{self.__class__.__name__}] "
            f"action={action} target={target} value={value}"
        )

        if action not in self.AI_ACTIONS:
            return None

        # -------------------------
        # Conversation / Fallback
        # -------------------------

        if action is None or action in (
            "chat",
            "ask",
            "explain",
            "summarize",
        ):

            text = value or target

            if not text:
                return response(
                    True,
                    "I'm listening."
                )

            return response(
                True,
                text
            )

        # -------------------------
        # Remember
        # -------------------------

        if action == "remember":

            if not target:
                return response(
                    False,
                    "Missing memory key."
                )

            if value is None:
                return response(
                    False,
                    "Missing memory value."
                )

            try:

                if hasattr(brain, "remember"):

                    brain.remember(target, value)

                    return response(
                        True,
                        f"I'll remember '{target}'."
                    )

            except Exception as e:
                print(e)

            return response(
                False,
                "Memory system unavailable."
            )

        # -------------------------
        # Recall
        # -------------------------

        if action == "recall":

            if not target:
                return response(
                    False,
                    "Missing memory key."
                )

            try:

                if hasattr(brain, "recall"):

                    memory = brain.recall(target)

                    if memory is not None:

                        return response(
                            True,
                            f"I remembered '{target}'.",
                            memory
                        )

                    return response(
                        False,
                        "Nothing remembered."
                    )

            except Exception as e:
                print(e)

            return response(
                False,
                "Memory system unavailable."
            )

        return None