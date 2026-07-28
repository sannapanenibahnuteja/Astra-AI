from fastapi import APIRouter

from app.models.browser import (
    BrowserRequest,
    BrowserResponse,
)

from app.services.browser_service import browser_search

router = APIRouter()


@router.post(
    "/browser/search",
    response_model=BrowserResponse,
)
def browser(request: BrowserRequest):
    result = browser_search(request.query)

    return BrowserResponse(
        summary=result
    )