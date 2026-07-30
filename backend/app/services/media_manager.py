import comtypes
from pycaw.pycaw import AudioUtilities


def _volume():
    comtypes.CoInitialize()

    device = AudioUtilities.GetSpeakers()

    return device.EndpointVolume

def get_volume():

    try:

        volume = _volume()

        level = int(volume.GetMasterVolumeLevelScalar() * 100)

        muted = bool(volume.GetMute())

        return {
            "success": True,
            "volume": level,
            "muted": muted,
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }


def set_volume(percent):
    comtypes.CoInitialize()
    try:
        percent = max(0, min(100, int(percent)))

        volume = _volume()

        print("Before:", volume.GetMasterVolumeLevelScalar())

        volume.SetMasterVolumeLevelScalar(percent / 100, None)

        print("After :", volume.GetMasterVolumeLevelScalar())

        return {
            "success": True,
            "message": f"Volume set to {percent} percent.",
            "volume": percent,
        }

    except Exception as e:
        print(e)
        return {
            "success": False,
            "message": str(e),
        }

    finally:
        comtypes.CoUninitialize()


def volume_up(step=5):

    info = get_volume()

    if not info["success"]:
        return info

    return set_volume(info["volume"] + step)


def volume_down(step=5):

    info = get_volume()

    if not info["success"]:
        return info

    return set_volume(info["volume"] - step)


def mute():

    try:

        volume = _volume()

        volume.SetMute(1, None)

        return {
            "success": True,
            "message": "Muted.",
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }


def unmute():

    try:

        volume = _volume()

        volume.SetMute(0, None)

        return {
            "success": True,
            "message": "Unmuted.",
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }


def toggle_mute():

    try:

        volume = _volume()

        muted = bool(volume.GetMute())

        volume.SetMute(not muted, None)

        return {
            "success": True,
            "muted": not muted,
            "message": "Muted." if not muted else "Unmuted.",
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }


def volume_max():

    return set_volume(100)


def volume_min():

    return set_volume(0)