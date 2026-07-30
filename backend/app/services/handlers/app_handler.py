from app.services import app_manager
from app.services.astra_brain import brain


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }
import os

class AppHandler:
    def handle(self, action, target, value, query=None):
        print("APP HANDLER FILE:", os.path.abspath(__file__))
        print("APP HANDLER ARGS:", action, target, value, query)

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

    # These targets belong to other handlers.
    RESERVED_TARGETS = {
        # Websites
        "google",
        "gmail",
        "youtube",
        "github",
        "chatgpt",
        "reddit",
        "linkedin",
        "facebook",
        "instagram",
        "twitter",
        "x",

        # Windows folders
        "desktop",
        "documents",
        "downloads",
        "pictures",
        "videos",
        "music",
        "recycle bin",

        # Windows tools
        "settings",
        "control panel",
        "task manager",
        "device manager",
        "disk management",
        "event viewer",
        "services",
        "registry editor",
        "explorer",
        "cmd",
        "powershell",
        "terminal",
    }

    def handle(self, action, target, value, query=None):
        print(
            f"[{self.__class__.__name__}] "
            f"action={action} target={target} value={value}"
        )

        if action not in self.APP_ACTIONS:
            return None

        # Only reuse previous app for follow-up commands.
        if not target:

            if action in ("close", "exit", "quit",
                          "focus", "switch", "activate",
                          "status", "running"):

                target = getattr(brain, "last_app", None)

                if not target:
                    return response(False, "Which application?")

            else:
                return response(False, "Which application?")

        target = target.lower().strip()

        # Let Browser/File/System handlers process these.
        if target in self.RESERVED_TARGETS:
            return None

        # ----------------------------
        # Open / Launch
        # ----------------------------

        if action in ("open", "launch", "start", "run"):

            try:
                if app_manager.focus_window(target):
                    brain.set_app(target)

                    return response(
                        True,
                        f"{target.title()} is already open."
                    )
            except Exception:
                pass

            try:
                if app_manager.launch_app(target):
                    brain.set_app(target)

                    return response(
                        True,
                        f"Opening {target.title()}."
                    )
            except Exception as e:
                print(e)

            return response(
                False,
                f"Couldn't open {target.title()}."
            )

        # ----------------------------
        # Close
        # ----------------------------

        if action in ("close", "exit", "quit"):

            try:
                if app_manager.close_app(target):
                    return response(
                        True,
                        f"Closed {target.title()}."
                    )
            except Exception as e:
                print(e)

            return response(
                False,
                f"{target.title()} is not running."
            )

        # ----------------------------
        # Focus
        # ----------------------------

        if action in ("focus", "switch", "activate"):

            try:
                if app_manager.focus_window(target):
                    brain.set_app(target)

                    return response(
                        True,
                        f"Switched to {target.title()}."
                    )
            except Exception as e:
                print(e)

            return response(
                False,
                f"Couldn't find {target.title()}."
            )

        # ----------------------------
        # Status
        # ----------------------------

        if action in ("status", "running"):

            try:
                running = app_manager.is_running(target)
            except Exception:
                running = False

            brain.set_app(target)

            return response(
                True,
                f"{target.title()} is {'running' if running else 'not running'}.",
                running,
            )

        return None