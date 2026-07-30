from dataclasses import dataclass
from typing import Callable
from rapidfuzz import fuzz


@dataclass
class Route:
    keywords: list[str]
    handler: Callable
    requires_keyword: bool = True


class IntentRouter:

    def __init__(self):
        self.routes = []

    def register(
        self,
        keywords,
        handler,
        requires_keyword=True,
    ):

        if isinstance(keywords, str):
            keywords = [keywords]

        self.routes.append(
            Route(
                keywords=keywords,
                handler=handler,
                requires_keyword=requires_keyword,
            )
        )

    def dispatch(self, text: str):

        text = text.lower().strip()

        best_handler = None
        best_score = 0

        for route in self.routes:

            for keyword in route.keywords:

                keyword = keyword.lower()

                if keyword in text:
                    return route.handler(text)

                score = fuzz.partial_ratio(keyword, text)

                if score > best_score:
                    best_score = score
                    best_handler = route.handler

        if best_handler and best_score >= 80:
            return best_handler(text)

        return None


router = IntentRouter()