from app.services.astra_brain import brain
from app.services.context_engine import (
    resolve_context,
    update_context
)
from app.services.intent_engine import get_intent
from app.services.command_service import execute_command


class AstraCore:

    def process(self, message: str):

        # -----------------------------
        # Remember what the user said
        # -----------------------------

        brain.remember_user(message)

        # -----------------------------
        # Resolve context
        # Example:
        # "Install them"
        # ->
        # "Install updates"
        # -----------------------------

        resolved = resolve_context(message)

        # -----------------------------
        # Update conversation context
        # -----------------------------

        update_context(resolved)

        # -----------------------------
        # Detect intent
        # -----------------------------

        intent = get_intent(resolved)

        if intent:

            brain.set_intent(intent)

        # -----------------------------
        # Execute command
        # -----------------------------

        response = execute_command(resolved)

        # -----------------------------
        # Remember Astra's reply
        # -----------------------------

        if isinstance(response, dict):

            if "message" in response:

                brain.remember_astra(
                    response["message"]
                )

        return response


astra = AstraCore()