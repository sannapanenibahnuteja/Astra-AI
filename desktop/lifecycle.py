"""Release desktop services even if one service fails during shutdown."""
import logging


def shutdown(runtime):
    runtime._automations.stop.set()
    runtime._commands.reminders.stop.set()
    for close in (runtime.cancel_chat, runtime.close_mobile, runtime._voice.close):
        try: close()
        except Exception: logging.exception('Bob service shutdown failed')
