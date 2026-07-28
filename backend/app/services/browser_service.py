from app.services.web_service import search_web


def browser_search(query: str):
    return search_web(query)