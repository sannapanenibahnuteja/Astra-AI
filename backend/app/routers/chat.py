from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.ai_service import stream_astra
from app.services.command_service import execute_command


router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)



def is_command(message: str):

    commands = [

        "open",

        "launch",

        "start",

    ]


    text = message.lower()


    return any(
        word in text
        for word in commands
    )




@router.post("/stream")
def chat_stream(data: dict):


    message = data.get(
        "message",
        ""
    )



    if is_command(message):


        result = execute_command(
            message
        )


        def command_response():

            yield result["message"]



        return StreamingResponse(
            command_response(),
            media_type="text/plain"
        )



    return StreamingResponse(

        stream_astra(message),

        media_type="text/plain"

    )