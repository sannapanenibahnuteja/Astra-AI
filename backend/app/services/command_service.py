import traceback

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

        print("=" * 60)
        print(">>> COMMAND SERVICE EXECUTE <<<")
        print("=" * 60)

        try:

            parsed = parse_command(text)

            print("PARSED:", parsed)

            if not parsed:
                return response(False, "I couldn't understand that command.")

            action = parsed.action
            target = parsed.target
            value = parsed.value
            query = parsed.query

            print(f"ACTION : {action}")
            print(f"TARGET : {target}")
            print(f"VALUE  : {value}")
            print(f"QUERY  : {query}")

            if hasattr(brain, "remember_user"):
                brain.remember_user(text)

            # Unknown command -> AI fallback
            if action is None:
                result = AIHandler().handle(None, None, text)

            else:
                result = self.dispatch(action, target, value, query)

            if (
                result
                and result.get("success")
                and hasattr(brain, "remember_astra")
            ):
                brain.remember_astra(result["message"])

            return result or response(False, "Command not supported.")

        except Exception:
            traceback.print_exc()
            return response(False, "Internal error.")

    def dispatch(self, action, target, value, query):

        print(
            f">>> DISPATCH: action={action}, target={target}, value={value}, query={query}"
        )

        last_failure = None

        for handler in self.handlers:

            try:
                print(f"Calling {handler.__class__.__name__} with query={query}")
                result = handler.handle(action, target, value, query)

                if result is None:
                    continue

                print(
                    f"{handler.__class__.__name__}: "
                    f"{result}"
                )

                # SUCCESS -> stop immediately
                if result.get("success"):
                    return result

                # remember failure and allow later handlers
                last_failure = result

            except Exception:

                traceback.print_exc()

        # if somebody handled but failed, return the last failure
        if last_failure:
            return last_failure

        return response(False, "Command not supported.")


command_service = CommandService()


def execute_command(text):
    return command_service.execute(text)