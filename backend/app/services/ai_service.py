import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(ENV_PATH)


API_KEY = os.getenv("GEMINI_API_KEY")


print(
    "ASTRA KEY:",
    API_KEY[:10] if API_KEY else "MISSING"
)


client = genai.Client(
    api_key=API_KEY
)


MODEL = "gemini-2.0-flash"


SYSTEM_PROMPT = """
You are Astra.

Astra is an advanced futuristic AI assistant created by Bhanu Teja.

Personality:
- Intelligent
- Calm
- Professional
- Friendly
- Slightly futuristic

You assist with:
- Programming
- AI
- Automation
- Productivity
- General knowledge
- Problem solving

Keep responses concise unless the user requests detail.

Always refer to yourself as Astra.
"""


def _build_prompt(message: str):

    return f"""
{SYSTEM_PROMPT}

User:
{message}
"""


def ask_astra(message: str):

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=_build_prompt(message),
        )

        return response.text


    except Exception as e:

        print(
            "Gemini error:",
            repr(e)
        )

        return (
            "Astra is temporarily unable "
            "to process your request."
        )



def stream_astra(message: str):

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=_build_prompt(message),
        )


        text = response.text


        chunk_size = 40


        for i in range(0, len(text), chunk_size):

            yield text[i:i + chunk_size]


    except Exception as e:

        print(
            "Gemini generation error:",
            repr(e)
        )


        yield (
            "Astra encountered a temporary "
            "intelligence module error."
        )