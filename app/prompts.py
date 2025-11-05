"""Prompt templates used by the application.

We expose simple helpers that return template strings for LangChain's
ChatPromptTemplate.from_template, keeping content concerns separate
from chain wiring.
"""


def topic_scout_template() -> str:
    """Template for the "Topic Scout" editor step.

    Variables: {search_context}
    """
    return (
        """
You are an expert news editor. Your goal is to find one specific, interesting story.
Based on the following search results for a broad topic, identify the
SINGLE most interesting, specific, and timely news story or development.

Return ONLY a new, concise Google search query for that specific story.
Do not add any preamble, explanation, or extra text.

Broad Topic Search Results:
---
{search_context}
---

New, Specific Search Query:
"""
    ).strip()


def blog_writer_template() -> str:
    """Template for the "Blog Writer" authoring step.

    Variables: {specific_topic}, {search_context}
    The model is asked to output a JSON with title/content for legacy DB.
    """
    return (
        """
You are an expert tech blogger. Your task is to write a short, insightful blog post
(around 300 words) based on the specific topic and context provided.

The blog post should be about: "{specific_topic}"

Use the following recent search results as your primary context to ensure
the post is up-to-date and factual. Synthesize them into a coherent article.

SEARCH CONTEXT:
---
{search_context}
---

The output must be a single, valid JSON object with two keys: "title" and "content".

Example:
{
  "title": "The Future of AI: New Developments",
  "content": "The world of AI is moving at breakneck speed..."
}
"""
    ).strip()


# Backward-compat prompt used by the non-LangChain generator (kept for reference)
def blog_post_prompt(search_context: str, keyword: str) -> str:
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
