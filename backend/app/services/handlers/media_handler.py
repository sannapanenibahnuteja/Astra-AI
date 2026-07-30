from app.services import media_manager


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }


class MediaHandler:

    def handle(self, action, target, value):

        # -------------------------
        # Volume Up
        # -------------------------

        if action == "volume_up":

            media_manager.volume_up()

            return response(
                True,
                "Increasing volume."
            )

        # -------------------------
        # Volume Down
        # -------------------------

        if action == "volume_down":

            media_manager.volume_down()

            return response(
                True,
                "Decreasing volume."
            )

        # -------------------------
        # Set Volume
        # -------------------------

        if action == "set_volume":

            if value is None:
                return response(False, "Specify a volume level.")

            try:
                volume = int(value)
            except ValueError:
                return response(False, "Volume must be a number.")

            volume = max(0, min(100, volume))

            media_manager.set_volume(volume)

            return response(
                True,
                f"Volume set to {volume}%."
            )

        # -------------------------
        # Mute
        # -------------------------

        if action == "mute":

            media_manager.mute()

            return response(
                True,
                "Muted."
            )

        # -------------------------
        # Unmute
        # -------------------------

        if action == "unmute":

            media_manager.unmute()

            return response(
                True,
                "Unmuted."
            )

        # -------------------------
        # Play / Pause
        # -------------------------

        if action == "play_pause":

            media_manager.play_pause()

            return response(
                True,
                "Play/Pause toggled."
            )

        # -------------------------
        # Next Track
        # -------------------------

        if action == "next_track":

            media_manager.next_track()

            return response(
                True,
                "Skipping to next track."
            )

        # -------------------------
        # Previous Track
        # -------------------------

        if action == "previous_track":

            media_manager.previous_track()

            return response(
                True,
                "Playing previous track."
            )

        return None