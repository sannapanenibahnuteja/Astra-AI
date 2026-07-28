from app.services.ai_service import ask_astra


def search_web(query: str) -> str:
    prompt = f"""
You are Astra Browser.

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

    return ask_astra(prompt)