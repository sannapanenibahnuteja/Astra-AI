from app.services import window_manager


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }


class WindowHandler:

    def handle(self, action, target, value):

        # -------------------------
        # Close Active Window
        # -------------------------

        if action == "close_window":

            window_manager.close_window()

            return response(
                True,
                "Closed active window."
            )

        # -------------------------
        # Minimize
        # -------------------------

        if action == "minimize":

            window_manager.minimize()

            return response(
                True,
                "Window minimized."
            )

        # -------------------------
        # Maximize
        # -------------------------

        if action == "maximize":

            window_manager.maximize()

            return response(
                True,
                "Window maximized."
            )

        # -------------------------
        # Restore
        # -------------------------

        if action == "restore":

            window_manager.restore()

            return response(
                True,
                "Window restored."
            )

        # -------------------------
        # Full Screen
        # -------------------------

        if action == "fullscreen":

            window_manager.fullscreen()

            return response(
                True,
                "Fullscreen toggled."
            )

        # -------------------------
        # Switch Window
        # -------------------------

        if action == "switch_window":

            window_manager.switch_window()

            return response(
                True,
                "Switched window."
            )

        # -------------------------
        # Snap Left
        # -------------------------

        if action == "snap_left":

            window_manager.snap_left()

            return response(
                True,
                "Window snapped left."
            )

        # -------------------------
        # Snap Right
        # -------------------------

        if action == "snap_right":

            window_manager.snap_right()

            return response(
                True,
                "Window snapped right."
            )

        return None