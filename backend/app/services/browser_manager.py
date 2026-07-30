import subprocess
import time
import webbrowser

import psutil
import requests

DEBUG_PORT = 9222

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

WEBSITES = {
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "chatgpt": "https://chatgpt.com",
    "reddit": "https://www.reddit.com",
    "linkedin": "https://www.linkedin.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
}


def chrome_running():
    for proc in psutil.process_iter(["name"]):
        try:
            if (proc.info["name"] or "").lower() == "chrome.exe":
                return True
        except Exception:
            pass
    return False


def debugging_available():
    try:
        requests.get(f"http://127.0.0.1:{DEBUG_PORT}/json", timeout=1)
        return True
    except Exception:
        return False


def launch_chrome():
    if debugging_available():
        return True

    for chrome in CHROME_PATHS:
        try:
            subprocess.Popen(
                [chrome, f"--remote-debugging-port={DEBUG_PORT}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(2)
            if debugging_available():
                return True
        except Exception:
            continue

    return False


def get_tabs():
    if not debugging_available() and not launch_chrome():
        return []

    try:
        return requests.get(
            f"http://127.0.0.1:{DEBUG_PORT}/json",
            timeout=2,
        ).json()
    except Exception:
        return []


def find_tab(keyword):
    keyword = keyword.lower()

    for tab in get_tabs():
        title = tab.get("title", "").lower()
        url = tab.get("url", "").lower()

        if keyword in title or keyword in url:
            return tab

    return None


def close_tab(keyword):
    tab = find_tab(keyword)

    if not tab:
        return False

    try:
        requests.get(
            f"http://127.0.0.1:{DEBUG_PORT}/json/close/{tab['id']}",
            timeout=2,
        )
        return True
    except Exception:
        return False


def open_website(site):
    site = (site or "").strip().lower()

    if site in WEBSITES:
        webbrowser.open(WEBSITES[site])
        return True

    if not site.startswith(("http://", "https://")):
        site = "https://" + site

    webbrowser.open(site)
    return True


def google_search(query):
    webbrowser.open(
        "https://www.google.com/search?q=" + query.replace(" ", "+")
    )
    return True


def youtube_search(query):
    webbrowser.open(
        "https://www.youtube.com/results?search_query="
        + query.replace(" ", "+")
    )
    return True


def open_multiple(urls):
    for url in urls:
        open_website(url)
    return True