import os
from dotenv import load_dotenv
from google import genai

load_dotenv(
    ".env"
)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Say hello in one sentence."
    )

    print("SUCCESS")
    print(response.text)

except Exception as e:
    print("ERROR")
    print(e)
    print(
    "Test API key:",
    os.getenv("GEMINI_API_KEY")[:10]
)