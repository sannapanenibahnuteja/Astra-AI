from fastapi import APIRouter

from app.services.command_service import execute_command


router = APIRouter(
    prefix="/commands",
    tags=["commands"]
)



@router.post("/execute")
def execute(data: dict):

    command = data.get(
        "command",
        ""
    )


    if not command:

        return {
            "success": False,
            "message": "No command received"
        }



    result = execute_command(
        command
    )


    return result