from app.services import media_manager


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }
import os


class MediaHandler:
    print("MEDIA HANDLER FILE:", os.path.abspath(__file__))

    MEDIA_ACTIONS = {
        "volume_up",
        "volume_down",
        "set_volume",
        "mute",
        "unmute",
        "play",
        "pause",
        "play_pause",
        "next",
        "next_track",
        "previous",
        "previous_track",
    }

    def _manager_response(self, result):

        if result is None:
            return response(False, "No response from media manager.")

        return response(
            result.get("success", False),
            result.get("message", "Unknown error."),
            result
        )

    def handle(self, action, target, value, query=None):

        print(
            f"[{self.__class__.__name__}] "
            f"action={action} target={target} value={value}"
        )

        if action not in self.MEDIA_ACTIONS:
            return None

        try:

            # -------------------------
            # Volume Up
            # -------------------------

            if action == "volume_up":
                return self._manager_response(
                    media_manager.volume_up()
                )

            # -------------------------
            # Volume Down
            # -------------------------

            if action == "volume_down":
                return self._manager_response(
                    media_manager.volume_down()
                )

            # -------------------------
            # Set Volume
            # -------------------------

            if action == "set_volume":

                if value is None:
                    return response(False, "Specify a volume level.")

                try:
                    volume = int(value)
                except (TypeError, ValueError):
                    return response(False, "Volume must be a number.")

                volume = max(0, min(100, volume))

                return self._manager_response(
                    media_manager.set_volume(volume)
                )

            # -------------------------
            # Mute
            # -------------------------

            if action == "mute":
                return self._manager_response(
                    media_manager.mute()
                )

            # -------------------------
            # Unmute
            # -------------------------

            if action == "unmute":
                return self._manager_response(
                    media_manager.unmute()
                )

            # -------------------------
            # Play / Pause
            # -------------------------

            if action in ("play", "pause", "play_pause"):
                return self._manager_response(
                    media_manager.play_pause()
                )

            # -------------------------
            # Next Track
            # -------------------------

            if action in ("next", "next_track"):
                return self._manager_response(
                    media_manager.next_track()
                )

            # -------------------------
            # Previous Track
            # -------------------------

            if action in ("previous", "previous_track"):
                return self._manager_response(
                    media_manager.previous_track()
                )

            return None

        except Exception as e:

            print(e)

            return response(
                False,
                str(e)
            )
        