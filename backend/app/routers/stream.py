from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.ai_service import stream_astra


router = APIRouter(
    prefix="/chat",
    tags=["stream"]
)


class ChatRequest(BaseModel):
    message: str



@router.post("/stream")
async def chat_stream(request: ChatRequest):

    return StreamingResponse(
        stream_astra(request.message),
        media_type="text/plain"
    )