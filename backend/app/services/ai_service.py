from ollama import chat

from app.memory.memory_service import (
    get_memories,
    save_memory,
)

# --------------------------------------------------
# OLLAMA SETTINGS
# --------------------------------------------------

MODEL = "qwen3:8b"

# --------------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------------

SYSTEM_PROMPT = """
You are Astra.

You are a futuristic AI assistant.

Personality:
- Intelligent
- Calm
- Professional
- Friendly

Always refer to yourself as Astra.

Use user memories whenever they are relevant.
"""

# --------------------------------------------------
# MEMORY EXTRACTION
# --------------------------------------------------


def _extract_memory(message):

    text = message.lower()

    triggers = [
        "my name is",
        "i am",
        "i like",
        "my favourite",
        "my favorite",
        "remember that",
    ]

    for trigger in triggers:

        if trigger in text:

            parts = message.split(trigger, 1)

            if len(parts) == 2:

                value = parts[1].strip()

                save_memory(trigger, value)

                break


# --------------------------------------------------
# BUILD CHAT HISTORY
# --------------------------------------------------


def _build_messages(message):

    memories = get_memories()

    memory_text = ""

    for item in memories:

        memory_text += f"{item['key']}: {item['value']}\n"

    return [

        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },

        {
            "role": "system",
            "content": f"""
Known memories:

{memory_text}

Use these memories only when relevant.
""",
        },

        {
            "role": "user",
            "content": message,
        },

    ]


# --------------------------------------------------
# NORMAL RESPONSE
# --------------------------------------------------


def ask_astra(message):

    _extract_memory(message)

    try:

        response = chat(
            model=MODEL,
            messages=_build_messages(message),
        )

        return response["message"]["content"]

    except Exception as e:

        print("Ollama error:", repr(e))

        return "Sorry, I'm having trouble communicating with my local AI."


# --------------------------------------------------
# STREAMING RESPONSE
# --------------------------------------------------


def stream_astra(message):

    _extract_memory(message)

    try:

        stream = chat(
            model=MODEL,
            messages=_build_messages(message),
            stream=True,
        )

        for chunk in stream:

            content = chunk["message"]["content"]

            if content:
                yield content

    except Exception as e:

        print("Ollama streaming error:", repr(e))

        yield "Sorry, I'm having trouble communicating with my local AI."