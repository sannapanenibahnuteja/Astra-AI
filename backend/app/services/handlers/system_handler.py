from app.services import system_manager


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }


class SystemHandler:

    FOLDER_TARGETS = {
        "desktop",
        "downloads",
        "documents",
        "pictures",
        "music",
        "videos",
    }

    SYSTEM_TARGETS = {
        "settings",
        "control panel",
        "task manager",
        "explorer",
        "file explorer",
        "recycle bin",
    }

    def handle(self, action, target, value):

        if not action:
            return None

        # -------------------------
        # Open folders
        # -------------------------

        if action == "open":

            if target in self.FOLDER_TARGETS:

                if system_manager.open_folder(target):
                    return response(True, f"Opening {target.title()}.")

                return response(False, f"Couldn't open {target.title()}.")

            if target in self.SYSTEM_TARGETS:

                if system_manager.open_system(target):
                    return response(True, f"Opening {target.title()}.")

                return response(False, f"Couldn't open {target.title()}.")

        # -------------------------
        # Shutdown
        # -------------------------

        if action == "shutdown":

            system_manager.shutdown()

            return response(
                True,
                "Shutting down computer."
            )

        # -------------------------
        # Restart
        # -------------------------

        if action == "restart":

            system_manager.restart()

            return response(
                True,
                "Restarting computer."
            )

        # -------------------------
        # Sleep
        # -------------------------

        if action == "sleep":

            system_manager.sleep()

            return response(
                True,
                "Putting computer to sleep."
            )

        # -------------------------
        # Hibernate
        # -------------------------

        if action == "hibernate":

            system_manager.hibernate()

            return response(
                True,
                "Hibernating computer."
            )

        # -------------------------
        # Lock
        # -------------------------

        if action == "lock":

            system_manager.lock()

            return response(
                True,
                "Locking computer."
            )

        return None