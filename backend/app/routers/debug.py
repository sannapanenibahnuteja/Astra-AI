from fastapi import APIRouter

from app.services.ai_service import ask_astra

router = APIRouter(
    prefix="/debug",
    tags=["debug"],
)


@router.get("/ai")
def test_ai():

    try:

        response = ask_astra("Say hello in one sentence.")

        return {
            "provider": "Ollama",
            "status": "OK",
            "response": response,
        }

    except Exception as e:

        return {
            "provider": "Ollama",
            "status": "ERROR",
            "error": str(e),
        }