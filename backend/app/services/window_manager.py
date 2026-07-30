import psutil
import pygetwindow as gw


def get_active_window():
    """
    Returns the currently active window.
    """

    try:

        win = gw.getActiveWindow()

        if win:

            return {
                "title": win.title,
                "window": win,
                "left": win.left,
                "top": win.top,
                "width": win.width,
                "height": win.height,
            }

    except Exception:
        pass

    return None


def close_active_window():

    active = get_active_window()

    if not active:
        return False

    try:
        active["window"].close()
        return True
    except Exception:
        return False


def minimize_active_window():

    active = get_active_window()

    if not active:
        return False

    try:
        active["window"].minimize()
        return True
    except Exception:
        return False


def maximize_active_window():

    active = get_active_window()

    if not active:
        return False

    try:
        active["window"].maximize()
        return True
    except Exception:
        return False


def restore_active_window():

    active = get_active_window()

    if not active:
        return False

    try:
        active["window"].restore()
        return True
    except Exception:
        return False


def move_active_window(x, y):

    active = get_active_window()

    if not active:
        return False

    try:
        active["window"].moveTo(x, y)
        return True
    except Exception:
        return False


def resize_active_window(width, height):

    active = get_active_window()

    if not active:
        return False

    try:
        active["window"].resizeTo(width, height)
        return True
    except Exception:
        return False


def snap_left():

    active = get_active_window()

    if not active:
        return False

    try:

        screen = gw.getAllScreens()[0]

        active["window"].moveTo(0, 0)
        active["window"].resizeTo(screen.width // 2, screen.height)

        return True

    except Exception:
        return False


def snap_right():

    active = get_active_window()

    if not active:
        return False

    try:

        screen = gw.getAllScreens()[0]

        active["window"].moveTo(screen.width // 2, 0)
        active["window"].resizeTo(screen.width // 2, screen.height)

        return True

    except Exception:
        return False


def list_running_apps():

    apps = []

    for proc in psutil.process_iter(["pid", "name"]):

        try:

            name = proc.info["name"]

            if name:
                apps.append(name)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return sorted(set(apps))