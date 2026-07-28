from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest, ChatResponse
from app.services.ai_service import ask_astra, stream_astra

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = ask_astra(request.message)

    return ChatResponse(
        response=reply
    )


@router.post("/chat/stream")
def chat_stream(request: ChatRequest):

    def generate():
        for chunk in stream_astra(request.message):
            if chunk:
                yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )