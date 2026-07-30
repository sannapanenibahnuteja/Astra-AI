from app.services import browser_manager
from app.services.astra_brain import brain


def response(success, message, data=None):
    return {
        "success": success,
        "message": message,
        "data": data,
    }


class BrowserHandler:

    WEBSITES = {
        "google",
        "youtube",
        "github",
        "gmail",
        "chatgpt",
        "facebook",
        "instagram",
        "twitter",
        "x",
        "reddit",
        "linkedin",
    }

    def handle(self, action, target, value):

        # -------------------------
        # Open Website
        # -------------------------

        if action == "open":

            if target in self.WEBSITES:

                browser_manager.open_website(target)

                return response(
                    True,
                    f"Opening {target.title()}."
                )

        # -------------------------
        # Google Search
        # -------------------------

        if action == "search":

            if not value:

                return response(
                    False,
                    "What would you like to search?"
                )

            browser_manager.google_search(value)

            brain.last_search = value

            return response(
                True,
                f"Searching Google for '{value}'."
            )

        # -------------------------
        # YouTube Search
        # -------------------------

        if action == "youtube":

            if not value:

                return response(
                    False,
                    "What would you like to search on YouTube?"
                )

            browser_manager.youtube_search(value)

            brain.last_search = value

            return response(
                True,
                f"Searching YouTube for '{value}'."
            )

        return None