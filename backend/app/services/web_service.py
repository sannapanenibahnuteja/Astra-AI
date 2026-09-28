from app.services.ai_service import ask_bob


def search_web(query: str) -> str:
    prompt = f"""
You are Bob Browser.

Answer this search query professionally.

Query:
{query}

Requirements:
- Give a direct answer.
- Use markdown.
- Include a short summary.
- Include key points.
- Include useful websites if appropriate.
"""

    return ask_bob(prompt)