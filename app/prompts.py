"""Prompt templates used by the application (kept minimal; structure is enforced via SDK)."""


def blog_post_prompt(search_context: str, keyword: str) -> str:
    """Return a concise content prompt; JSON shape will be enforced with response_schema.

    We keep this prompt free of JSON instructions to rely on Gemini structured output.
    """
    return f"""
You are an expert tech blogger.
Write an insightful ~300-word article about "{keyword}".

Use the recent search results below as factual context. Synthesize ideas; avoid listing.
Include a compelling title and a short 1–2 sentence summary. Write the body in semantic HTML.

SEARCH CONTEXT
---
{search_context}
---
"""
