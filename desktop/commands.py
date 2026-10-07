"""Anchored command grammar with conservative fuzzy application matching.

Model output is never executed. A conversational sentence containing an action
word is not sufficient to trigger a Windows action.
"""
import ctypes
import os
import re
import subprocess
import webbrowser
import time
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import quote_plus, urlparse
from desktop import windows
from desktop import devices
from desktop import settings_control, files, media, browser
from desktop.reminders import Reminders, parse as parse_reminder, ACTIONS as REMINDER_ACTIONS


from desktop.intent import normalize, phrase_intent, dictation


def parse(text):
    text = normalize(text)
    device = devices.parse_device(text)
    if device:
        return devices.validate(device)
    typed = re.fullmatch(r'type (.+) into (.+)', text, flags=re.I)
    if typed:
        return {'action':'type_text', 'target':typed[1], 'window':typed[2]}
    if re.fullmatch(r"(?:check(?: for)?|open|show)(?: the| my)? (?:system |windows )?updates?(?: settings)?", text, flags=re.I):
        return {"action": "windows_update", "target": ""}
    patterns = [
        ('brightness', r'(?:set |turn |change )?(?:the |screen |display )?brightness(?: to)? (\d{1,3})(?: percent|%)?'),
        ('focus_window', r'(?:switch to|focus) (.+)'),
        ('minimize_window', r'minimize (.+)'),
        ('maximize_window', r'maximize (.+)'),
        ('restore_window', r'restore (.+)'),
        ('close_window', r'close (.+)'),
        ('inspect_window', r'(?:inspect|read) window (.+)'),
        ('type_text', r'type (.+)'),
        ('press_key', r'press (.+)'),
        ("project_search", r"(?:search|find)(?: in)? (?:my |the )?project(?: for)? (.+)"),
        ("project_read", r"(?:read|show)(?: project)? file (.+)"),
        ("open", r"(?:open|launch|start|bring up|opne|opem) (.+)"),
        ("search", r"(?:search(?: the web)?(?: for)?|look up|google) (.+)"),
        ("remember", r"remember(?: that)? (.+)"),
        ("recall", r"(?:recall|what do you remember about) (.+)"),
        ("note", r"(?:take a note|make a note|save a note|note)(?: that)?[ :]+(.+)"),
        ("volume", r"(?:set |turn )?(?:the )?volume(?: to)? (\d{1,3})(?: percent|%)?"),
    ]
    for action, pattern in patterns:
        match = re.fullmatch(pattern, text, flags=re.I)
        if match:
            return {"action": action, "target": match[1].strip()}
    exact = {"mute": "mute", "mute volume": "mute", "mute the volume": "mute",
             "unmute": "unmute", "unmute volume": "unmute", "unmute the volume": "unmute",
             "volume up": "volume_up", "turn up the volume": "volume_up",
             "volume down": "volume_down", "turn down the volume": "volume_down",
             "lock my computer": "lock", "lock the computer": "lock", "lock my pc": "lock",
             "what time is it": "time", "what's the time": "time", "system status": "status",
             "open my bob": "bob"}
    exact.update({"open my project": "open_project", "open the project": "open_project",
                  "list project files": "project_list", "show project files": "project_list",
                  'list windows':'list_windows', 'show open windows':'list_windows',
                  'list monitors':'list_monitors', 'show monitors':'list_monitors',
                  'brightness up':'brightness_up', 'increase brightness':'brightness_up',
                  'brightness down':'brightness_down', 'lower brightness':'brightness_down'})
    if text.lower() in exact:
        return {"action": exact[text.lower()], "target": ""}
    return None


def safe_url(value):
    parsed = urlparse(value)
    if parsed.scheme not in ("https", "http") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use a complete http:// or https:// address without credentials.")
    return value


class Commands:
    def __init__(self, store):
        self.store = store
        self.reminders = Reminders(store)
        self.explorer_handle = None
        self.browser_handle = None
        self.window_choices = {}
        self.apps = {"notepad": ("exe", "notepad.exe"), "calculator": ("exe", "calc.exe"),
                     "file explorer": ("exe", "explorer.exe"), "settings": ("uri", "ms-settings:")}
        self.aliases = {"calc": "calculator", "explorer": "file explorer", "files": "file explorer",
                        "note pad": "notepad", "vs code": "visual studio code", "vscode": "visual studio code",
                        "chrome": "google chrome", "edge": "microsoft edge"}
        for env in ("PROGRAMDATA", "APPDATA"):
            base = os.environ.get(env)
            if not base:
                continue
            root = Path(base) / "Microsoft/Windows/Start Menu/Programs"
            for path in root.rglob("*.lnk"):
                if not re.search(r"uninstall|remove|repair|setup", path.stem, re.I):
                    self.apps.setdefault(path.stem.lower(), ("shortcut", str(path)))

    def capture_explorer(self):
        """Remember the user's foreground Explorer before a wake brings Bob forward."""
        import win32gui, win32process, psutil
        try:
            handle = win32gui.GetForegroundWindow()
            pid = win32process.GetWindowThreadProcessId(handle)[1]
            if not handle or pid <= 0:
                self.explorer_handle = None
                self.browser_handle = None
                return
            if pid == os.getpid(): return
            process = psutil.Process(pid).name().lower()
            self.explorer_handle = handle if process == 'explorer.exe' else None
            self.browser_handle = handle if process == 'msedge.exe' else None
        except Exception:
            # Focus can disappear between the two Win32 calls. Optional Explorer
            # context must never prevent an ordinary conversation from starting.
            self.explorer_handle = None
            self.browser_handle = None

    def match_app(self, target):
        target = self.aliases.get(target.lower(), target.lower())
        if target in self.apps:
            return target, True
        scores = sorted(((SequenceMatcher(None, target, name).ratio(), name) for name in self.apps), reverse=True)
        if scores and scores[0][0] >= .72 and (len(scores) == 1 or scores[0][0] - scores[1][0] >= .12):
            return scores[0][1], False
        return None, False

    def plan(self, text, identity, _context=None, _defer_files=False):
        typed = dictation(text)
        if typed:
            if typed['target'].lower() in ('it','that','that text','your previous response','the previous response'):
                return None
            return windows.validate(typed['action'],typed['target'],typed['window'])
        text = normalize(text)
        from desktop import tab_tasks
        tab_request = tab_tasks.request(text, _context if _context is not None else self.store.context(identity))
        if tab_request: return tab_request
        site_close = re.fullmatch(r'close (youtube|google|github)(?: tab)?',text,re.I)
        if site_close: return browser.validate({'action':'edge_close_tab','target':site_close[1].lower()})
        if re.fullmatch(r'(?:do|run|perform|try|repeat)(?: the)? (?:same thing(?: as last time)?|that|it)(?: again)?|same as last time|again', text, re.I):
            recent = self.store.recent_actions(identity, 1)
            if not recent:
                return {'action':'clarify','target':"I don't have a previous successful action in this conversation yet."}
            command = dict(recent[0]['command'])
            command.pop('description', None)
            if command.get('action') in {'clarify','time','status','list_windows','list_monitors','audio_status','brightness_status'}:
                command['confirm'] = True
            return command
        followup=re.fullmatch(r'close (?:all (?:those|these|of them)|them|both|the (first|second|third)(?: one| window)?)',text,re.I)
        if followup:
            saved=self.window_choices.get(identity)
            if not saved or time.monotonic()-saved[0]>180:
                return {'action':'clarify','target':'Which windows should I close? Name the app first so I can show the matching windows.'}
            choices=saved[1]
            if followup[1]: choices=choices[{'first':0,'second':1,'third':2}[followup[1].lower()]:][:1]
            if not choices: return {'action':'clarify','target':'That window was not in the list.'}
            plans=[{**windows.validate('close_window',w['title']), '_window_ref':dict(w), 'confirm':i==0,
                     'description':'close the entire window '+w['title']} for i,w in enumerate(choices)]
            plans[0]['description']='close these entire windows (including their browser tabs): '+ '; '.join(w['title'] for w in choices)
            return plans
        if re.match(r"^(?:don't|do not|never|avoid|explain|how\b|what happens|if\b)", text, re.I):
            return None
        reminder = parse_reminder(text)
        if reminder: return self.reminders.validate(reminder)
        canonical, uncertain = phrase_intent(text)
        if canonical:
            result = self.plan(canonical, identity, _context, _defer_files)
            if isinstance(result, dict) and uncertain: result['confirm'] = True
            return result
        context = dict(_context if _context is not None else self.store.context(identity))
        if self.browser_handle and _context is None:
            context['last_window'] = 'Microsoft Edge'
        # Split action clauses, not 'date and time', number words, or quoted file names.
        verbs = r'open|launch|set|lower|raise|increase|decrease|reduce|dim|brighten|turn|switch|type|press|click|maximize|minimize|restore|close|search|find|copy|move|rename|delete|recycle|create|make|list|show|enable|disable|connect|disconnect|reconnect|mute|unmute|volume|brightness|remember|play|pause|resume|stop|seek|skip|rewind|shuffle|repeat|go back|go to|fast forward|refresh|reload|scroll|zoom|visit|navigate|fill|select|pull up|fire up|bump up|dial down'
        pattern = re.compile(r'\s*(?:,\s*(?:and\s+)?|\band then\b|\band\b|\bthen\b)\s*(?=(?:' + verbs + r')\b)', re.I)
        clauses, start = [], 0
        for match in pattern.finditer(text):
            if text[:match.start()].count('"') % 2 == 0:
                clauses.append(text[start:match.start()]); start = match.end()
        clauses.append(text[start:])
        if 1 < len(clauses) <= 12:
            direct = []
            for clause in clauses:
                step = self.plan(clause, identity, context, _defer_files=True)
                direct.append(step)
                if isinstance(step, dict):
                    if step['action'] in ('radio_set','radio_status','settings_set'):
                        context['last_setting'] = step['target']
                    if step['action'] == 'settings_open': context['last_setting'] = step['target']
                    if step['action'] == 'open': context['last_window'] = step['target']
                    if step['action'] in browser.ACTIONS or (step['action'] == 'open' and step['target'] == 'microsoft edge'): context['last_window'] = 'Microsoft Edge'
            if all(direct):
                return direct
            return None
        if len(clauses) > 12:
            raise ValueError('Please request at most twelve actions at a time.')
        moved = re.fullmatch(r'(?:move|put|send) (.+?) (?:to|on) (?:the )?(?:monitor|screen|display) (one|two|three|\d+)',text,re.I)
        if moved:
            number = {'one':'1','two':'2','three':'3'}.get(moved[2].lower(),moved[2])
            return windows.validate('move_window',number,moved[1])
        edge = browser.parse(text, context)
        if edge: return browser.validate(edge)
        playback = media.parse(text)
        if playback:
            return media.validate(playback)
        special = settings_control.parse(text, context)
        if special:
            return special if special['action'] == 'clarify' else settings_control.validate(special)
        file_command = files.parse(text)
        if file_command:
            return files.validate(file_command) if _defer_files else files.prepare(file_command, context)
        # A compound request belongs to the planner, not a greedy single-command
        # regex (which could turn “search X and lower brightness” into one search).
        if re.search(r'\b(?:and|then)\s+(?:then\s+)?(?:open|set|lower|increase|decrease|turn|type|switch|maximize|minimize|close|search|click|press)\b', text, re.I):
            return None
        command = parse(text)
        if not command:
            return None
        if command['action'] in devices.DEVICE_ACTIONS:
            return devices.validate(command)
        if command['action'] in windows.ACTIONS:
            if command['action']=='type_text' and command['target'].lower() in ('it','that','that text','the previous response'):
                return None
            return windows.validate(command['action'], command['target'], command.get('window',''))
        if command["action"] == "open":
            target = command["target"].lower().removeprefix("the ").removeprefix("a ")
            if target in ("it", "that", "it again", "that again"):
                target = self.store.context(identity).get("last_app", "")
                if not target:
                    return {"action": "clarify", "target": "Which application would you like me to open?"}
            if target == "my bob":
                return {"action": "bob", "target": ""}
            if target in ("my project", "the project"):
                return {"action": "open_project", "target": ""}
            folders = {"downloads", "documents", "desktop", "pictures", "music", "videos"}
            if target.removeprefix("my ") in folders:
                return {"action": "folder", "target": target.removeprefix("my ")}
            if target in ("youtube", "google", "github"):
                return {"action": "url", "target": f"https://{target}.com"}
            if re.fullmatch(r"https?://\S+", target):
                return {"action": "url", "target": safe_url(target)}
            name, exact = self.match_app(target)
            if not name:
                return None
            command.update(target=name, confirm=not exact)
        if command["action"] == "lock":
            command["confirm"] = True
        return command

    def execute(self, command, identity):
        action, target = command["action"], command["target"]
        if action in REMINDER_ACTIONS:
            context = self.store.context(identity)
            result = self.reminders.execute(command, context)
            self.store.context(identity, context)
            return result
        if action in browser.ACTIONS:
            context = self.store.context(identity)
            try: result = browser.execute(command, context, self.browser_handle, getattr(self,'cancel',None))
            finally: self.store.context(identity, context)
            return result
        if action in media.ACTIONS:
            context = self.store.context(identity)
            result = media.execute(command, context)
            self.store.context(identity, context)
            return result
        if action in settings_control.ACTIONS or action in files.ACTIONS:
            context = self.store.context(identity)
            if action == 'explorer_selection':
                command = {**command, 'explorer_handle':self.explorer_handle}
            handler = settings_control if action in settings_control.ACTIONS else files
            try:
                return handler.execute(command, context)
            finally:
                self.store.context(identity, context)
        if action in devices.DEVICE_ACTIONS:
            return devices.execute(command)
        if action in windows.ACTIONS:
            context = self.store.context(identity)
            window = command.get('window', '')
            if action.endswith('_window') and not window:
                window = target
            if window.lower() in ('', 'it', 'that', 'this window', 'that window', 'the window', 'current window'):
                window = context.get('last_window', context.get('last_app', ''))
            reference=command.get('_window_ref')
            if reference and reference not in windows.window_inventory():
                raise ValueError('That window changed or closed since it was listed. Name the app again to refresh the choices.')
            try:
                result = windows.execute(action, target, window, reference=reference) if reference else windows.execute(action, target, window)
            except windows.AmbiguousWindows as exc:
                self.window_choices[identity]=(time.monotonic(),exc.matches)
                raise
            if action not in {'brightness','brightness_up','brightness_down','list_windows','list_monitors'}:
                self.store.context(identity, {**context, 'last_window': window})
            return result
        if action == "windows_update":
            os.startfile('ms-settings:windowsupdate')
            self.store.context(identity, {**self.store.context(identity), 'last_window':'Settings'})
            return "Opened Windows Update. Select ‘Check for updates’ there to run a scan. I haven't scanned or installed updates."
        if action in ("project_search", "project_read", "project_list", "open_project"):
            return self.project_action(action, target)
        if action == "clarify":
            return target
        if action == "open":
            if target != 'microsoft edge': self.browser_handle = None
            kind, path = self.apps[target]
            if kind == "exe":
                subprocess.Popen([path])
            else:
                os.startfile(path)
            self.store.context(identity, {**self.store.context(identity), "last_app": target, 'last_window': target})
            return f"Opened {target}."
        if action == "folder":
            folder = files.known_folder(target)
            if not folder.exists():
                return f"I couldn't find your {target} folder at {folder}. It may have been moved."
            os.startfile(str(folder))
            self.store.context(identity, {**self.store.context(identity), 'last_window': folder.name, 'last_folder':str(folder), 'last_files':[]})
            return f"Opened {target}."
        if action in ("url", "search", "bob"):
            url = target if action == "url" else "https://www.google.com/search?q=" + quote_plus(target)
            if action == "bob":
                url = self.store.settings()["bob_url"]
                if not url:
                    return "Add your existing Bob link in Settings first. This opens it in your browser; it does not sync its memory."
            from desktop.web_launch import open_website
            result, handle = open_website(safe_url(url))
            if handle:
                self.browser_handle = handle
                self.store.context(identity, {**self.store.context(identity), 'last_window':'Microsoft Edge', 'edge_handle':handle,
                                              'last_opened_browser':{'handle':handle,'time':time.time()}})
            return result
        if action == "remember":
            parts = re.split(r"\s+is\s+|\s*=\s*|:\s*", target, maxsplit=1, flags=re.I)
            key, value = parts if len(parts) == 2 else ("note " + datetime.now().strftime("%Y%m%d%H%M%S%f"), target)
            self.store.remember(key.removeprefix("my "), value)
            return f"I'll remember: {key} — {value}."
        if action == "recall":
            matches = [f"{m['key']}: {m['value']}" for m in self.store.memories() if target.lower().removeprefix("my ") in m["key"].lower()]
            return "\n".join(matches) or f"I don't have a saved memory about {target}."
        if action == "note":
            folder = self.store.root / "notes"
            folder.mkdir(exist_ok=True)
            name = "Note-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".txt"
            (folder / name).write_text(target, encoding="utf-8")
            return f"Saved your note to {folder / name}."
        if action == "time":
            return datetime.now().strftime("It's %I:%M %p on %A, %B %d.")
        if action == "status":
            import psutil
            return f"CPU usage is {psutil.cpu_percent(interval=.15):.0f}%. Memory usage is {psutil.virtual_memory().percent:.0f}%."
        if action == "lock":
            if not ctypes.windll.user32.LockWorkStation():
                raise RuntimeError("Windows could not lock this session.")
            return "Locking your computer."
        if action in ("mute", "unmute", "volume", "volume_up", "volume_down"):
            import pythoncom
            pythoncom.CoInitialize()
            try:
                from pycaw.pycaw import AudioUtilities
                volume = AudioUtilities.GetSpeakers().EndpointVolume
                if action in ("mute", "unmute"):
                    volume.SetMute(action == "mute", None)
                    return "Muted." if action == "mute" else "Unmuted."
                level = float(target) / 100 if action == "volume" else volume.GetMasterVolumeLevelScalar() + (.1 if action == "volume_up" else -.1)
                if action == "volume" and not 0 <= level <= 1:
                    return "Choose a volume between 0 and 100 percent."
                level = max(0, min(1, level))
                volume.SetMasterVolumeLevelScalar(level, None)
                return f"Volume set to {round(level * 100)}%."
            finally:
                pythoncom.CoUninitialize()
        raise ValueError("That action isn't supported yet.")

    def project_action(self, action, target):
        setting = self.store.settings()["project_path"]
        if not setting:
            return "Choose your project folder in Settings first."
        root = Path(setting).resolve()
        if not root.is_dir():
            return "Your project folder is no longer available. Update it in Settings."
        if action == "open_project":
            os.startfile(str(root))
            return "Opened your project folder."
        if action == "project_read":
            path = (root / target).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                return "Choose an existing file inside your project folder."
            if path.name.startswith(".env") or path.suffix.lower() in (".pem", ".key", ".pfx"):
                return "Credential files are excluded from project reading."
            if path.stat().st_size > 100000:
                return "This file is larger than the 100 KB reading limit. Choose a smaller file."
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeError:
                return "This is not a UTF-8 text file."
            return f"{path.relative_to(root)}\n\n````\n{content[:20000]}\n````" + ("\n[Truncated to 20,000 characters.]" if len(content) > 20000 else "")
        excluded = {".git", "node_modules", "venv", ".venv", "dist", "build", "__pycache__", ".next"}
        matches, scanned = [], 0
        for directory, folders, files in os.walk(root, followlinks=False):
            folders[:] = [f for f in folders if f not in excluded and not (Path(directory) / f).is_symlink()]
            for name in files:
                scanned += 1
                path = Path(directory) / name
                if path.is_symlink() or name.startswith(".env") or path.suffix.lower() in (".pem", ".key", ".pfx"):
                    continue
                relative = str(path.relative_to(root))
                if action == "project_list" or target.lower() in relative.lower():
                    matches.append(relative)
                if len(matches) >= 80 or scanned >= 5000:
                    break
            if len(matches) >= 80 or scanned >= 5000:
                break
        return ("Project files (up to 80 results, scanning up to 5,000 files):\n\n" + "\n".join(f"- `{p}`" for p in matches)) if matches else "No matching file names found in the scanned project files."

    def validate_model_action(self, arguments, identity):
        if not isinstance(arguments, dict):
            raise ValueError("The model proposed an invalid action.")
        action, target = arguments.get("action"), arguments.get("target", "")
        if action in REMINDER_ACTIONS:
            return self.reminders.validate(arguments)
        if action in browser.ACTIONS:
            return browser.validate(arguments)
        if action in media.ACTIONS:
            return media.validate(arguments)
        if action in settings_control.ACTIONS:
            return settings_control.validate(arguments)
        if action in files.ACTIONS:
            return files.validate(arguments)
        if action in devices.DEVICE_ACTIONS:
            return devices.validate(arguments)
        if action in windows.ACTIONS:
            return windows.validate(action, target, arguments.get('window', ''))
        allowed = {"open", "search", "remember", "recall", "note", "volume", "mute", "unmute",
                   "volume_up", "volume_down", "time", "status", "lock", "project_search",
                   "project_read", "project_list", "open_project", "windows_update"}
        if action not in allowed or not isinstance(target, str) or len(target) > 4000:
            raise ValueError("The requested action is outside Bob's supported capabilities.")
        if action == "open":
            plan = self.plan("open " + target, identity)
            if plan is None:
                raise ValueError(f"I couldn't find the application ‘{target}’. Try its Start menu name.")
            return plan
        if action == "volume" and (not target.isdigit() or not 0 <= int(target) <= 100):
            raise ValueError("Volume must be between 0 and 100.")
        if action in {"search", "remember", "recall", "note", "project_read", "project_search"} and not target.strip():
            raise ValueError("The proposed action needs a target. Please be more specific.")
        return {"action": action, "target": target, "confirm": action == "lock"}
