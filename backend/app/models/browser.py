from pydantic import BaseModel


class BrowserRequest(BaseModel):
    query: str


class BrowserResponse(BaseModel):
    summary: str