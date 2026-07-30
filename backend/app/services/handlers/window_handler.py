from app.services import window_manager


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }


class WindowHandler:

    WINDOW_ACTIONS = {
        "minimize",
        "maximize",
        "restore",
        "close",
        "move",
        "resize",
        "snap_left",
        "snap_right",
    }

    def handle(self, action, target, value, query=None):

        print(
            f"[{self.__class__.__name__}] "
            f"action={action} target={target} value={value}"
        )

        if action not in self.WINDOW_ACTIONS:
            return None

        # -------------------------
        # Minimize
        # -------------------------

        if action == "minimize":

            if window_manager.minimize_active_window():
                return response(True, "Window minimized.")

            return response(False, "Couldn't minimize the window.")

        # -------------------------
        # Maximize
        # -------------------------

        if action == "maximize":

            if window_manager.maximize_active_window():
                return response(True, "Window maximized.")

            return response(False, "Couldn't maximize the window.")

        # -------------------------
        # Restore
        # -------------------------

        if action == "restore":

            if window_manager.restore_active_window():
                return response(True, "Window restored.")

            return response(False, "Couldn't restore the window.")

        # -------------------------
        # Close
        # -------------------------

        if action == "close":

            if window_manager.close_active_window():
                return response(True, "Window closed.")

            return response(False, "Couldn't close the window.")

        # -------------------------
        # Move
        # value = "x,y"
        # -------------------------

        if action == "move":

            if not value:
                return response(False, "Specify X,Y coordinates.")

            try:
                x, y = map(int, value.split(","))

                if window_manager.move_active_window(x, y):
                    return response(True, "Window moved.")

            except Exception:
                pass

            return response(False, "Couldn't move the window.")

        # -------------------------
        # Resize
        # value = "width,height"
        # -------------------------

        if action == "resize":

            if not value:
                return response(False, "Specify width,height.")

            try:
                width, height = map(int, value.split(","))

                if window_manager.resize_active_window(width, height):
                    return response(True, "Window resized.")

            except Exception:
                pass

            return response(False, "Couldn't resize the window.")

        # -------------------------
        # Snap Left
        # -------------------------

        if action == "snap_left":

            if window_manager.snap_left():
                return response(True, "Window snapped left.")

            return response(False, "Couldn't snap window left.")

        # -------------------------
        # Snap Right
        # -------------------------

        if action == "snap_right":

            if window_manager.snap_right():
                return response(True, "Window snapped right.")

            return response(False, "Couldn't snap window right.")

        return None