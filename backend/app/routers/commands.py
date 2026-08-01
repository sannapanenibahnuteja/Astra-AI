from fastapi import APIRouter

from app.services.command_service import execute_command

router = APIRouter(
    prefix="/commands",
    tags=["commands"]
)


@router.post("/")
def execute(data: dict):

    message = data.get("message", "").strip()

    if not message:
        return {
            "success": False,
            "message": "No command received"
        }

    return execute_command(message)