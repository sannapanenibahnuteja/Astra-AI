import webbrowser
import urllib.parse


# Common websites
URLS = {
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "chatgpt": "https://chat.openai.com",
    "reddit": "https://www.reddit.com",
    "linkedin": "https://www.linkedin.com",
    "stackoverflow": "https://stackoverflow.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "x": "https://x.com",
    "twitter": "https://x.com",
    "amazon": "https://www.amazon.in",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
}


def open_website(site: str):
    """
    Opens a known website.
    Returns True if successful.
    """

    site = site.lower().strip()

    if site in URLS:
        webbrowser.open(URLS[site])
        return True

    return False


def search_google(query: str):
    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote(query)
    )

    webbrowser.open(url)


def search_youtube(query: str):
    url = (
        "https://www.youtube.com/results?search_query="
        + urllib.parse.quote(query)
    )

    webbrowser.open(url)


def browser_search(query: str):
    """
    Main browser handler used by browser.py router.
    """

    if not query:
        return "No search query provided."

    query = query.strip()
    lower = query.lower()

    # -----------------------
    # Open websites
    # -----------------------

    if lower in URLS:
        open_website(lower)
        return f"Opened {query.title()}."

    # -----------------------
    # Open website
    # -----------------------

    if lower.startswith("open "):
        site = lower.replace("open ", "", 1).strip()

        if open_website(site):
            return f"Opened {site.title()}."

    # -----------------------
    # Search YouTube
    # -----------------------

    if lower.startswith("youtube "):
        text = query[8:].strip()

        if text:
            search_youtube(text)
            return f"Searching YouTube for '{text}'."

    if lower.startswith("search youtube for "):
        text = query[len("search youtube for "):].strip()

        if text:
            search_youtube(text)
            return f"Searching YouTube for '{text}'."

    # -----------------------
    # Google Search
    # -----------------------

    if lower.startswith("search google for "):
        text = query[len("search google for "):].strip()

        if text:
            search_google(text)
            return f"Searching Google for '{text}'."

    if lower.startswith("google "):
        text = query[7:].strip()

        if text:
            search_google(text)
            return f"Searching Google for '{text}'."

    # -----------------------
    # Default
    # -----------------------

    search_google(query)
    return f"Searching Google for '{query}'."