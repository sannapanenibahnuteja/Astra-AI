import traceback

from app.services.astra_brain import brain
from app.services.ai_service import ask_astra
from app.memory.memory_service import save_memory


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }


class AIHandler:

    AI_ACTIONS = {
        None,
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

        # -----------------------------------
        # Chat / Ollama
        # -----------------------------------

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

            try:

                reply = ask_astra(text)

                return response(
                    True,
                    reply
                )

            except Exception as e:

                print("OLLAMA ERROR:", e)

                return response(
                    False,
                    "Unable to contact Ollama."
                )

        # -----------------------------------
        # Remember
        # -----------------------------------

        if action == "remember":

            if not target:
                return response(False, "Missing memory key.")

            if value is None:
                return response(False, "Missing memory value.")

            try:

                brain.remember(target, value)

                return response(
                    True,
                    f"I'll remember '{target}'."
                )

            except Exception as e:

                traceback.print_exc()

                return response(
                    False,
                    "Memory system unavailable."
                )

        # -----------------------------------
        # Recall
        # -----------------------------------

        if action == "recall":

            if not target:
                return response(False, "Missing memory key.")

            try:

                memory = brain.recall(target)

                if memory is not None:

                    return response(
                        True,
                        str(memory),
                        memory,
                    )

                return response(
                    False,
                    "Nothing remembered."
                )

            except Exception as e:

                traceback.print_exc()

                return response(
                    False,
                    "Memory system unavailable."
                )

        return None