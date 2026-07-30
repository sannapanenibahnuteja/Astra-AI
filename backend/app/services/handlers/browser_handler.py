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

    def handle(self, action, target, value, query=None):

        print(
            f"[{self.__class__.__name__}] "
            f"action={action} target={target} value={value} query={query}"
        )

        # -------------------------
        # Open Website
        # -------------------------

        if action == "open":

            if not target:
                return None

            target = target.lower().strip()

            if target not in self.WEBSITES:
                return None

            try:
                browser_manager.open_website(target)
                brain.last_website = target

                return response(
                    True,
                    f"Opening {target.title()}."
                )

            except Exception as e:
                print(e)

                return response(
                    False,
                    f"Couldn't open {target.title()}."
                )

        # -------------------------
        # Search
        # -------------------------

        if action == "search":

            search_query = query or value

            if not search_query:

                search_query = getattr(brain, "last_search", None)

                if not search_query:
                    return response(
                        False,
                        "What would you like to search?"
                    )

            try:

                # Google Search
                if target == "google" or target is None:

                    browser_manager.google_search(search_query)

                    brain.last_search = search_query

                    return response(
                        True,
                        f"Searching Google for '{search_query}'."
                    )

                # YouTube Search
                elif target == "youtube":

                    browser_manager.youtube_search(search_query)

                    brain.last_search = search_query

                    return response(
                        True,
                        f"Searching YouTube for '{search_query}'."
                    )

                # Other supported websites
                elif target in self.WEBSITES:

                    browser_manager.open_website(target)
                    browser_manager.google_search(search_query)

                    brain.last_search = search_query

                    return response(
                        True,
                        f"Searching '{search_query}'."
                    )

                # Default
                else:

                    browser_manager.google_search(search_query)

                    brain.last_search = search_query

                    return response(
                        True,
                        f"Searching Google for '{search_query}'."
                    )

            except Exception as e:
                print(e)

                return response(
                    False,
                    "Search failed."
                )

        return None