from ctypes import POINTER, cast

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


def _volume():
    devices = AudioUtilities.GetSpeakers()

    interface = devices.Activate(
        IAudioEndpointVolume._iid_,
        CLSCTX_ALL,
        None,
    )

    return cast(interface, POINTER(IAudioEndpointVolume))


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

    try:

        percent = max(0, min(100, int(percent)))

        volume = _volume()

        volume.SetMasterVolumeLevelScalar(percent / 100, None)

        return {
            "success": True,
            "message": f"Volume set to {percent} percent.",
            "volume": percent,
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }


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