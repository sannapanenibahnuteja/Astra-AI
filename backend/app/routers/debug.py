from fastapi import APIRouter
import os

from dotenv import load_dotenv
from google import genai


load_dotenv(".env")


router = APIRouter(
    prefix="/debug",
    tags=["debug"]
)


@router.get("/gemini")
def test_gemini():

    key = os.getenv("GEMINI_API_KEY")

    print("DEBUG KEY:", key[:10])


    client = genai.Client(
        api_key=key
    )


    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Say hello in one sentence"
    )


    return {
        "key": key[:10],
        "response": response.text
    }