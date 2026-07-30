from app.services.command_parser import parse_command

from app.services.handlers.app_handler import AppHandler
from app.services.handlers.browser_handler import BrowserHandler
from app.services.handlers.system_handler import SystemHandler
from app.services.handlers.media_handler import MediaHandler
from app.services.handlers.file_handler import FileHandler
from app.services.handlers.window_handler import WindowHandler
from app.services.handlers.ai_handler import AIHandler

from app.services.astra_brain import brain


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }


class CommandService:

    def __init__(self):
        self.handlers = [
            AppHandler(),
            SystemHandler(),
            BrowserHandler(),
            FileHandler(),
            MediaHandler(),
            WindowHandler(),
            AIHandler(),
        ]

    def execute(self, text):
        print(">>> COMMAND SERVICE EXECUTE CALLED <<<")
        try:
            parsed = parse_command(text)
            print("PARSED:", parsed)

            if not parsed:
                return response(False, "I couldn't understand that command.")

            action = parsed.action
            target = parsed.target
            value = parsed.value

            if hasattr(brain, "remember_user"):
                brain.remember_user(text)

            print(f"[COMMAND] action={action} target={target} value={value}")

            result = self.dispatch(action, target, value)
            print(result)

            if result and result.get("success") and hasattr(brain, "remember_astra"):
                brain.remember_astra(result["message"])

            return result or response(False, "Command not supported.")

        except Exception as e:
            return response(False, str(e))

    def dispatch(self, action, target, value):
        print(f">>> DISPATCH: action={action}, target={target}, value={value}")

        for handler in self.handlers:
            result = handler.handle(action, target, value)
            if result is not None:
                return result

        return response(False, "Command not supported.")


command_service = CommandService()


def execute_command(text):
    return command_service.execute(text)