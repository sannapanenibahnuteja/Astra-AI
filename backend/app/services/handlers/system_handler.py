from app.services import system_manager


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }
import os

class SystemHandler:
    print("SYSTEM HANDLER LOADED FROM:")
    print(os.path.abspath(__file__))

    FOLDER_TARGETS = {
        "desktop",
        "downloads",
        "documents",
        "pictures",
        "music",
        "videos",
        "recycle bin",
    }

    SYSTEM_TARGETS = {
        "settings",
        "control panel",
        "task manager",
        "explorer",
        "file explorer",
        "device manager",
        "disk management",
        "services",
        "event viewer",
        "registry editor",
        "cmd",
        "powershell",
        "terminal",
    }

    SYSTEM_ACTIONS = {
    "open",
    "shutdown",
    "restart",
    "sleep",
    "hibernate",
    "lock",

    "set_brightness",
    "brightness_up",
    "brightness_down",
}

    def handle(self, action, target, value, query=None):

        print(
            f"[{self.__class__.__name__}] "
            f"action={action} target={target} value={value}"
        )

        if action not in self.SYSTEM_ACTIONS:
            return None

        # -------------------------
        # Open Folder
        # -------------------------

        if action == "open":

            if not target:
                return None

            target = target.lower().strip()

            if target in self.FOLDER_TARGETS:

                try:
                    if system_manager.open_folder(target):
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

            if target in self.SYSTEM_TARGETS:

                try:
                    if system_manager.open_system(target):
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

            return None

        # -------------------------
        # Shutdown
        # -------------------------

        if action == "shutdown":

            try:
                system_manager.shutdown()

                return response(
                    True,
                    "Shutting down computer."
                )

            except Exception as e:
                print(e)

                return response(
                    False,
                    "Shutdown failed."
                )

        # -------------------------
        # Restart
        # -------------------------

        if action == "restart":

            try:
                system_manager.restart()

                return response(
                    True,
                    "Restarting computer."
                )

            except Exception as e:
                print(e)

                return response(
                    False,
                    "Restart failed."
                )

        # -------------------------
        # Sleep
        # -------------------------

        if action == "sleep":

            try:
                system_manager.sleep()

                return response(
                    True,
                    "Putting computer to sleep."
                )

            except Exception as e:
                print(e)

                return response(
                    False,
                    "Sleep failed."
                )

        # -------------------------
        # Hibernate
        # -------------------------

        if action == "hibernate":

            try:
                system_manager.hibernate()

                return response(
                    True,
                    "Hibernating computer."
                )

            except Exception as e:
                print(e)

                return response(
                    False,
                    "Hibernate failed."
                )

        # -------------------------
        # Lock
        # -------------------------

        if action == "lock":

            try:
                system_manager.lock()

                return response(
                    True,
                    "Locking computer."
                )

            except Exception as e:
                print(e)

                return response(
                    False,
                    "Lock failed."
                )

        # -------------------------
        # Set Brightness
        # -------------------------

        if action == "set_brightness":

            if value is None:
                return response(False, "Specify a brightness level.")

            try:
                level = int(value)
            except (ValueError, TypeError):
                return response(False, "Brightness must be a number.")

            result = system_manager.set_brightness(level)

            return response(
                result["success"],
                result["message"],
                result,
            )

        # -------------------------
        # Brightness Up
        # -------------------------

        if action == "brightness_up":

            result = system_manager.brightness_up()

            return response(
                result["success"],
                result["message"],
                result,
            )

        # -------------------------
        # Brightness Down
        # -------------------------

        if action == "brightness_down":

            result = system_manager.brightness_down()

            return response(
                result["success"],
                result["message"],
                result,
            )

        return None