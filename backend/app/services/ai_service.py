import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from app.memory.memory_service import (
    get_memories,
    save_memory
)


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(ENV_PATH)


API_KEY = os.getenv("GEMINI_API_KEY")


client = genai.Client(
    api_key=API_KEY
)


MODEL = "gemini-2.0-flash"



SYSTEM_PROMPT = """
You are Astra.

You are a futuristic AI assistant.

Personality:
- Intelligent
- Calm
- Professional
- Friendly

Always refer to yourself as Astra.

Use user memories when they are relevant.
"""



def _extract_memory(message):

    text = message.lower()


    triggers = [

        "my name is",

        "i am",

        "i like",

        "my favourite",

        "my favorite",

        "remember that"

    ]


    for trigger in triggers:

        if trigger in text:

            parts = message.split(
                trigger,
                1
            )


            if len(parts) == 2:

                value = parts[1].strip()


                save_memory(
                    trigger,
                    value
                )

                break




def _build_prompt(message):


    memories = get_memories()


    memory_text = ""


    for item in memories:

        memory_text += (
            f"\n{item['key']}: "
            f"{item['value']}"
        )



    return f"""

{SYSTEM_PROMPT}


Known memories:

{memory_text}


User:

{message}

"""




def ask_astra(message):

    _extract_memory(message)


    response = client.models.generate_content(

        model=MODEL,

        contents=_build_prompt(message)

    )


    return response.text




def stream_astra(message):

    _extract_memory(message)


    try:


        response = client.models.generate_content(

            model=MODEL,

            contents=_build_prompt(message)

        )


        text = response.text



        for i in range(
            0,
            len(text),
            40
        ):

            yield text[i:i+40]



    except Exception as e:


        print(
            "Gemini error:",
            repr(e)
        )


        yield (
            "Astra is temporarily unavailable."
        )