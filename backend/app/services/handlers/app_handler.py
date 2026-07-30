from app.services import app_manager
from app.services.astra_brain import brain


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }


class AppHandler:

    APP_ACTIONS = {
        "open",
        "launch",
        "start",
        "run",
        "close",
        "exit",
        "quit",
        "focus",
        "switch",
        "activate",
        "status",
        "running",
    }

    # These are NOT desktop applications.
    RESERVED_TARGETS = {
        "gmail",
        "google",
        "youtube",
        "github",
        "chatgpt",
        "reddit",
        "linkedin",
        "facebook",
        "instagram",
        "twitter",
        "x",

        "explorer",
        "desktop",
        "downloads",
        "documents",
        "pictures",
        "music",
        "videos",
        "settings",
        "control panel",
        "task manager",
        "recycle bin",
    }

    def handle(self, action, target, value):

        if action not in self.APP_ACTIONS:
            return None

        if not target:

            if getattr(brain, "last_app", None):
                target = brain.last_app
            else:
                return response(False, "Which application?")

        target = target.lower()

        # Browser/system commands belong elsewhere.
        if target in self.RESERVED_TARGETS:
            return None

        if action in ("open", "launch", "start", "run"):

            if app_manager.focus_window(target):

                brain.set_app(target)

                return response(
                    True,
                    f"{target.title()} is already open."
                )

            if app_manager.launch_app(target):

                brain.set_app(target)

                return response(
                    True,
                    f"Opening {target.title()}."
                )

            return response(
                False,
                f"Couldn't open {target.title()}."
            )

        if action in ("close", "exit", "quit"):

            if app_manager.close_app(target):

                return response(
                    True,
                    f"Closed {target.title()}."
                )

            return response(
                False,
                f"{target.title()} is not running."
            )

        if action in ("focus", "switch", "activate"):

            if app_manager.focus_window(target):

                brain.set_app(target)

                return response(
                    True,
                    f"Switched to {target.title()}."
                )

            return response(
                False,
                f"Couldn't find {target.title()}."
            )

        if action in ("status", "running"):

            running = app_manager.is_running(target)

            brain.set_app(target)

            return response(
                True,
                f"{target.title()} is {'running' if running else 'not running'}.",
                running,
            )

        return None