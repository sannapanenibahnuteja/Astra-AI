"""Run with python -m desktop.main or launch packaged Bob.exe."""
import argparse
import json
import logging
import sys
import threading
from pathlib import Path

from desktop.runtime import Runtime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--data-dir")
    parser.add_argument("--ui-test", action="store_true")
    parser.add_argument("--voice-test-dir", help="Transcribe WAV fixtures without microphone capture or actions")
    parser.add_argument('--windows-test', action='store_true', help='Exercise only the dedicated Bob Automation Verification fixture')
    parser.add_argument('--device-test', action='store_true', help='Read monitor brightness and active output volume without changing them')
    parser.add_argument('--system-test', action='store_true', help='Read Bluetooth/Wi-Fi state and validate bundled network modules without changing connectivity')
    parser.add_argument('--media-test', action='store_true', help='Read Windows media sessions without changing playback')
    args = parser.parse_args()
    runtime = Runtime(args.data_dir)
    if args.media_test:
        from desktop.media import native
        result = native({'action':'media_sessions'}, {})
        (runtime._store.root / 'media-test.json').write_text(json.dumps(result), encoding='utf-8')
        return
    if args.system_test:
        from desktop import network
        result = {'version':runtime.bootstrap()['version'], 'bluetooth':network.radio('bluetooth'),
                  'wifi':network.radio('wifi'), 'connection':network.wifi('wifi_status')}
        (runtime._store.root / 'system-test.json').write_text(json.dumps(result), encoding='utf-8')
        return
    if args.device_test:
        from desktop.devices import execute
        result = {action: execute({'action':action,'target':''}) for action in ('brightness_status','audio_status')}
        (runtime._store.root / 'device-test.json').write_text(json.dumps(result), encoding='utf-8')
        return
    if args.windows_test:
        from desktop.windows import execute
        title = 'Bob Automation Verification'
        result = [execute('focus_window', title), execute('type_text', 'Hello + {Bob}', title),
                  execute('click_control', 'Record', title), execute('maximize_window', title),
                  execute('restore_window', title)]
        (runtime._store.root / 'windows-test.json').write_text(json.dumps(result), encoding='utf-8')
        return
    if args.ui_test:
        # Exercise the complete frontend wake/listen/reply loop without recording
        # the user's microphone or producing sound during the automated UI test.
        utterances = iter(("What time is it?", "stop listening"))
        runtime._voice.listen = lambda *args: {"text": next(utterances, ""), "confidence": .99, "needs_review": False}
        runtime._voice.speak = lambda *args: True
    if args.voice_test_dir:
        result = {p.name: runtime._voice.transcribe(str(p)) for p in Path(args.voice_test_dir).glob('*.wav')}
        (runtime._store.root / 'voice-test.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        return
    project_root = Path(sys.executable).parent.parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
    if not runtime._store.settings()["project_path"] and (project_root / "backend").is_dir() and (project_root / "frontend").is_dir():
        runtime._store.save_settings({"project_path": str(project_root)})
    if args.smoke_test:
        result = {"ok": True, "version": runtime.bootstrap()["version"], "ollama": runtime.ollama_status()}
        output = runtime._store.root / "smoke-test.json"
        output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        if sys.stdout:
            print(json.dumps(result))
        return
    import webview
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    index = root / "frontend/dist/index.html"
    logging.basicConfig(filename=runtime._store.root / "bob.log", level=logging.INFO)
    if not index.exists():
        raise RuntimeError("Frontend not built. Run npm run build in frontend first.")
    window = webview.create_window("Bob · Personal AI", str(index), js_api=runtime,
                                  width=1380, height=900, min_size=(900, 650), background_color="#080c14")
    window.events.closed += runtime.cancel_chat
    quitting = threading.Event()
    from PIL import Image, ImageDraw, ImageFont
    import pystray
    icon_image = Image.new("RGBA", (64, 64), "#0c1721")
    draw = ImageDraw.Draw(icon_image)
    draw.ellipse((4, 4, 60, 60), outline="#5cbbab", width=2)
    draw.text((17, 9), "B", font=ImageFont.load_default(size=42), fill="#c2b8ff")

    def sleep_renderer(sleeping):
        # WebView2's sleeping-tab API reduces hidden renderer CPU and memory.
        # Invoke on the WinForms UI thread; never synchronously wait on its task.
        from System import Action
        def update():
            renderer = window.native.webview
            if sleeping:
                renderer.Visible = False
                renderer.CoreWebView2.TrySuspendAsync()
            else:
                renderer.CoreWebView2.Resume()
                renderer.Visible = True
        try:
            window.native.Invoke(Action(update))
        except Exception:
            logging.exception("WebView suspension unavailable")

    def show(*_):
        sleep_renderer(False)
        window.show()
        window.restore()
        window.evaluate_js("document.documentElement.classList.remove('background-mode')")

    def quit_app(*_):
        quitting.set()
        runtime._voice.close()
        runtime.cancel_chat()
        tray.stop()
        window.destroy()

    tray = pystray.Icon("Bob", icon_image, "Bob · Personal AI", pystray.Menu(
        pystray.MenuItem("Open Bob", show, default=True), pystray.MenuItem("Quit Bob", quit_app)))

    def hide_on_close():
        if quitting.is_set() or args.ui_test:
            return True
        window.evaluate_js("window.dispatchEvent(new Event('bob-hide')); document.documentElement.classList.add('background-mode')")
        runtime._voice.stop()
        runtime._voice.session(False)
        window.hide()
        sleep_renderer(True)
        return False

    window.events.closing += hide_on_close
    window.events.minimized += lambda: window.evaluate_js("document.documentElement.classList.add('background-mode')")
    window.events.restored += lambda: window.evaluate_js("document.documentElement.classList.remove('background-mode')")
    if not args.ui_test:
        tray.run_detached()
        def wake():
            runtime._commands.capture_explorer()
            show()
            window.evaluate_js("window.dispatchEvent(new Event('bob-wake'))")

        def voice_start():
            import time
            for _ in range(100):
                if window.evaluate_js("!!window.bobVoiceReady"):
                    break
                time.sleep(.1)
            try:
                settings = runtime._store.settings()
                if settings["greeting_enabled"] and settings["voice_enabled"]:
                    runtime.speak("Bob online. I'm ready to listen." if settings['auto_listen'] else "Bob online. Say Hey Bob when you need me.")
            except Exception as exc:
                runtime._voice._update(error=str(exc)[:400])
                logging.exception("Startup greeting failed")
            runtime._voice.start(wake, runtime._store.settings()["wake_enabled"])
            if runtime._store.settings()['auto_listen']:
                runtime._voice.session(True)
                wake()
        window.events.loaded += lambda: threading.Thread(target=voice_start, daemon=True).start()
    else:
        def ui_test():
            import time
            try:
                for _ in range(100):
                    if window.evaluate_js("!!window.pywebview?.api && !!document.querySelector('.welcome') && !document.querySelector('.connection-pill').textContent.includes('PREVIEW')"):
                        break
                    time.sleep(.1)
                result = window.evaluate_js("JSON.stringify({title:document.title, brand:document.querySelector('.brand').textContent, voiceReady:!!window.bobVoiceReady, welcome:!!document.querySelector('.welcome'), navigation:document.querySelectorAll('.nav-item').length, width:innerWidth, overflow:document.documentElement.scrollWidth>innerWidth, status:document.querySelector('.connection-pill').textContent})")
                (runtime._store.root / "ui-test.json").write_text(result, encoding="utf-8")
                assert json.loads(result)['title'].startswith('Bob'), 'Wrong application assets were served'
                assert json.loads(result)['voiceReady'], 'Wake event handler was not registered'
                window.evaluate_js("window.dispatchEvent(new Event('bob-wake'))")
                completed = False
                for _ in range(80):
                    completed = window.evaluate_js("document.querySelector('.message.user')?.textContent.includes('What time is it?') && document.querySelector('.message.assistant')?.textContent.includes(\"It's\") && document.querySelector('.voice-status')?.textContent.includes('ready')")
                    if completed:
                        break
                    time.sleep(.1)
                data = json.loads(result)
                data['voice_round_trip'] = bool(completed)
                (runtime._store.root / "ui-test.json").write_text(json.dumps(data), encoding='utf-8')
                assert completed, 'Wake-to-conversation round trip did not complete'
                import psutil
                process = psutil.Process()
                window.evaluate_js("document.documentElement.classList.add('background-mode')")
                window.hide()
                sleep_renderer(True)
                time.sleep(8)  # Exclude renderer startup from the idle sample.
                processes = [process] + process.children(recursive=True)
                for item in processes:
                    item.cpu_percent()
                time.sleep(3)
                working_set = sum(item.memory_info().rss for item in processes if item.is_running())
                cpu = sum(item.cpu_percent() for item in processes if item.is_running())
                (runtime._store.root / "idle-metrics.json").write_text(json.dumps({
                    "processes": len(processes), "summed_working_set_mb": round(working_set / 1048576, 1),
                    "cpu_percent_one_core": round(cpu, 1), "sample_seconds": 3,
                    "note": "Bob and child processes only. Shared pages may be counted more than once. Ollama excluded."
                }, indent=2), encoding="utf-8")
            finally:
                quitting.set()
                window.destroy()
        window.events.loaded += lambda: threading.Thread(target=ui_test, daemon=True).start()
    # Persistent WebView defaults to port 42001, which can serve another running
    # build's assets. Select a fresh loopback port while keeping SQLite durable.
    webview.settings['DEFAULT_HTTP_PORT'] = 0
    webview.start(gui="edgechromium", private_mode=False, storage_path=str(runtime._store.root / "webview"))
    runtime._voice.close()


if __name__ == "__main__":
    main()
