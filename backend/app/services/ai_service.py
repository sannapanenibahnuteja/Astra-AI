import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-3.6-flash"

SYSTEM_PROMPT = """
You are Astra.

Astra is an advanced futuristic AI operating system created by Bhanu Teja.

Never mention Google, Gemini, or that you are a language model unless directly asked.

Your personality:

- Intelligent
- Confident
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


def _build_prompt(message: str) -> str:
    return f"""
{SYSTEM_PROMPT}

User:
{message}
"""


def ask_astra(message: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=_build_prompt(message),
    )

    return response.text


def stream_astra(message: str):
    response = client.models.generate_content_stream(
        model=MODEL,
        contents=_build_prompt(message),
    )

    for chunk in response:
        if hasattr(chunk, "text") and chunk.text:
            yield chunk.text