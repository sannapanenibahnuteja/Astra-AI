"""Temporarily supply Unicode text without losing existing clipboard formats."""
from contextlib import contextmanager
import threading
import time


@contextmanager
def temporary_text(text):
    ready=threading.Event(); done=threading.Event(); errors=[]
    def worker():
        import ctypes
        import pythoncom
        import win32clipboard as clipboard
        initialized=False
        try:
            # OLE needs STA; the UI Automation caller may already use MTA.
            pythoncom.OleInitialize(); initialized=True
            previous=pythoncom.OleGetClipboard()
            clipboard.OpenClipboard()
            try:
                clipboard.EmptyClipboard()
                clipboard.SetClipboardText(text,clipboard.CF_UNICODETEXT)
            finally: clipboard.CloseClipboard()
            sequence=clipboard.GetClipboardSequenceNumber()
            ready.set()
            try:
                while not done.wait(.01): pythoncom.PumpWaitingMessages()
            finally:
                if clipboard.GetClipboardSequenceNumber()==sequence:
                    for attempt in range(20):
                        try:
                            pythoncom.OleSetClipboard(previous)
                            break
                        except Exception:
                            if attempt==19: raise
                            pythoncom.PumpWaitingMessages()
                            time.sleep(.05)
                    if previous is not None: pythoncom.OleFlushClipboard()
        except Exception as exc: errors.append(exc)
        finally:
            ready.set()
            if initialized: ctypes.windll.ole32.OleUninitialize()
    thread=threading.Thread(target=worker,daemon=True)
    thread.start(); ready.wait()
    try:
        if errors: raise RuntimeError('Clipboard is unavailable; no text was inserted.') from errors[0]
        yield
    finally:
        done.set(); thread.join()
    if errors: raise RuntimeError('Text was inserted, but the original clipboard could not be restored.') from errors[0]
